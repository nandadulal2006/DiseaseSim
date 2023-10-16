import numpy as np
from ODESolver import ForwardEuler
import matplotlib.pyplot as plt
import matplotlib.backends.backend_tkagg as tkagg 
from tkinter import *

class SIR:
    def __init__(self, nu, beta, S0, I0, R0):
        if isinstance(nu, (float, int)):
            self.nu = lambda t: nu
        elif callable(nu):
            self.nu = nu

        if isinstance(beta, (float, int)):
            self.beta = lambda t: beta
        elif callable(beta):
            self.beta = beta

        self.initial_conditions = [S0, I0, R0]

    def __call__(self, u, t):
        S, I, _ = u
        return np.asarray([
            -self.beta(t) * S * I,
            self.beta(t) * S * I - self.nu(t) * I,
            self.nu(t) * I
        ])

def run_simulation():
    transmission = float(entry_transmission.get()) / 100000
    recovery = float(entry_recovery.get()) / 1000
    population = float(entry_population.get())

    sir = SIR(recovery, transmission, population, 1, 0)
    solver = ForwardEuler(sir)
    solver.set_initial_condition(sir.initial_conditions)

    time_steps = np.linspace(0, 60, 1001)
    u, t = solver.solve(time_steps)

    ax.clear()
    ax.plot(t, u[:, 0], label='Susceptible')
    ax.plot(t, u[:, 1], label='Infected')
    ax.plot(t, u[:, 2], label='Recovered')
    ax.set_xlabel(f"Time (days)")
    ax.set_ylabel("No. of People ")
    ax.legend()
    canvas.draw()

    max_infected = max(u[:, 1])
    outbreak_threshold = population * 0.1

    if max_infected > outbreak_threshold:
        days_until_outbreak = np.argmax(u[:, 1] > outbreak_threshold)
        result_label.config(text=f"Warning: Potential outbreak detected! {days_until_outbreak} days until the outbreak.")
    else:
        result_label.config(text="No potential outbreak detected.")

app = Tk()
app.title("Disease Dynamics Prediction")

frame = Frame(app)
frame.pack(side=LEFT, padx=10, pady=10)

entry_transmission = Entry(frame, width=10)
entry_transmission.grid(row=0, column=1)
entry_recovery = Entry(frame, width=10)
entry_recovery.grid(row=1, column=1)
entry_population = Entry(frame, width=10)
entry_population.grid(row=2, column=1)

label_transmission = Label(frame, text="Transmission Rate (/day):")
label_transmission.grid(row=0, column=0)
label_recovery = Label(frame, text="Recovery Rate (/day):")
label_recovery.grid(row=1, column=0)
label_population = Label(frame, text="Population:")
label_population.grid(row=2, column=0)

simulate_button = Button(frame, text="Simulate", command=run_simulation)
simulate_button.grid(row=3, column=0, columnspan=2)

result_label = Label(frame, text="")
result_label.grid(row=4, column=0, columnspan=2)

fig = plt.figure(figsize=(6, 4), dpi=100)
ax = fig.add_subplot(111)

canvas = tkagg.FigureCanvasTkAgg(fig, master=app) # Use FigureCanvasTkAgg
canvas.get_tk_widget().pack(side=RIGHT, fill=BOTH, expand=True)

app.mainloop()
