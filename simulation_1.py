from matplotlib import pyplot as plt
import matplotlib.animation as animation
from matplotlib import style
import pygame
import random
import math
import sys
pygame. init()

WIDTH=500
HEIGHT=500
SCREEN= pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pandemic Simulation")

COLOR_DEFINITIONS={
    "grey": (35,35,40),
    "light_grey":(70,70,90),
    "white":(255,248,240),
    "red":(239,71,111),
    "blue":(17,138,178)
}

COLORS = {
    "background": COLOR_DEFINITIONS["grey"],
    "healthy": COLOR_DEFINITIONS["white"],
    "infected": COLOR_DEFINITIONS["red"],
    "immune" : COLOR_DEFINITIONS["blue"],
    "dead" : COLOR_DEFINITIONS["grey"]
}

def moving_average(l, k=7):
    avg=[0 for i in range(k//2)]
    for i in range(k//2,len(l)-k//2):
        sub=l[i-k//2:i+k//2+1]
        avg.append(sum(sub)/len(sub))
    return avg + [0 for i in range(k//2)]



class Cell():
    def __init__(self, row,col):
        self.row = row
        self.col = col
        self.people = []

    def get_neighbouring_cells(self, n_rows, n_cols):
        index = self.row * n_cols + self.col
        N = index - n_cols if self.row > 0 else None
        S = index + n_cols if self.row < n_rows - 1 else None
        W = index - 1 if self.col > 0 else None
        E = index + 1 if self.col < n_cols - 1 else None
        NW = index - n_cols - 1 if self.row > 0 and self.col > 0 else None
        NE = index - n_cols + 1 if self.row > 0 and self.col < n_cols - 1 else None
        SW = index + n_cols - 1 if self.row < n_rows - 1 and self.col > 0 else None
        SE = index + n_cols + 1 if self.row < n_rows - 1 and self.col < n_cols - 1 else None
        return [i for i in [index, N, S, E, W, NW, SW, SE] if i is not None]


class Grid():
    def __init__(self, people, h_size = 10, v_size = 10):
        self.h_size = h_size
        self.v_size = v_size
        self.n_rows = HEIGHT // v_size
        self.n_cols = WIDTH // h_size
        self.cells = []
        for row in range(self.n_rows):
            for col in range(self.n_cols):
                self.cells.append(Cell(row,col))
        self.store_people(people)

    def store_people(self, people):
        for p in people:
            row = int(p.y/self.v_size)
            col = int(p.x/self.h_size)
            index = row * self.n_cols + col
            self.cells[index].people.append(p)
    def show(self, width = 1):
        for c in self.cells:
            x=c.col * self.h_size
            y=c.row * self.v_size
            rect = pygame.Rect(x,y, self.h_size,self.v_size)
            pygame.draw.rect(SCREEN, COLOR_DEFINITIONS["light_grey"], rect, width=width)
class Person:
    def __init__(self):
        self.x = random.uniform(0,WIDTH)
        self.y = random.uniform(0,HEIGHT)
        self.dx = 0
        self.dy = 0
        self.state = "healthy"
        self.recovery_counter = 0
        self.immunity_counter = 0
    
    def show(self , size =2):
        pygame.draw.circle(SCREEN, COLORS[self.state], (self.x , self.y), size)
    
    def move(self , speed = 0.01):

        #ajust position vector
        self.x += self.dx
        self.y += self.dy

        # avoid going out of bounds
        if self.x >= WIDTH:
            self.x = WIDTH -1
            self.dx *= -1
        if self.y >= HEIGHT:
            self.y = HEIGHT -1
            self.dy *= -1
        if self.x <= 0 :
            self.x = 1
            self.dx *= -1
        if self.y <= 0 :
            self.y = 1
            self.dy *= -1
        

        #adjust velocity vector
        self.dx += random.uniform(-speed, speed)
        self.dy += random.uniform(-speed, speed)

    def get_infected(self, value = 500):
        self.state = "infected"
        self.recovery_counter = value

    def recover(self, value=1000):
        self.recovery_counter -= 1
        if self.recovery_counter == 0:
            self.state = "immune"
            self.immunuty_counter = value
    
    def lose_immunity(self):
        self.immunity_counter -= 1
        if self.immunity_counter == 0:
            self.state = "healthy"
    
    def die(self, probability = 0.00002):
        if random.uniform(0,1) < probability:
            self.state = "dead" 


class Pandemic():
    def __init__(self, 
             n_people = int(input("Enter the population")), size = 1 , speed = float(input("Enter the speed of the movement of Virtuals:"))/100,
             infect_dist = eval(input("Enter the infection radius:")), recover_time =eval(input("Enter the recovery time needed")), immune_time = eval(input("enter duration of immunity:")),
             prob_catch =float(input("Enter probability of transmission"))/100, prob_death = eval(input("Enter the probability of death:"))/100):
        self.people = [Person() for i in range(n_people)]
        self.size = size
        self.speed = speed
        self.infect_dist = infect_dist
        self.recover_time = recover_time
        self.immune_time = immune_time
        self.prob_catch = prob_catch
        self.prob_death = prob_death
        self.grid = Grid(self.people)
        self.people[0].get_infected(recover_time)
        self.record = []
        self.over =  False
    
    def update_grid(self):
        self.grid = Grid(self.people)
    
    def slowly_infect_people(self):
         # infect other people
        for p in self.people:
            if p.state == "infected":
                for other in self.people:
                    if other.state == "healthy":
                        dist = math.sqrt((p.x-other.x)**2 + (p.y-other.y)**2)
                        if dist < self.infect_dist :
                            other.get_infected()
    def infect_people(self):
        for c in self.grid.cells:
            # move on if nobody is infected
            states= [p.state for p in c.people]
            if states.count("infected") == 0:
                continue

            # create lists of all / infected / healthy people on the grod
            people_in_area=[]
            for index in c.get_neighbouring_cells(self.grid.n_rows, self.grid.n_cols):
                people_in_area += self.grid.cells[index].people
                infected_people = [p for p in people_in_area if p.state == "infected"]
                healthy_people = [p for p in people_in_area if p.state == "healthy"]

                if len(healthy_people)==0:
                    continue

                # loop through the infected people (and then the healthy people)
                for i in infected_people:
                    for h in healthy_people:
                        dist = math.sqrt((i.x-h.x)**2 + (i.y-h.y)**2)
                        if dist < self.infect_dist :
                            if random.uniform(0,1)< self.prob_catch:
                                h.get_infected(self.recover_time)

    
    def run(self):
        self.update_grid()
        self.infect_people()

        for p in self.people:
            if p.state == "infected":
                p.die(self.prob_death)
                p.recover(self.immune_time)
            if p.state == "immune":
                p.lose_immunity()
            p.move(self.speed)
            p.show(self.size)

    def keep_track(self):
        states = [p.state for p in self.people]
        n_healthy=states.count("healthy")
        n_infected = states.count("infected")
        n_dead = states.count("dead")
        n_recover = states.count("immune")
        self.record.append([n_infected, n_dead, n_healthy,n_recover])
        if n_infected == 0:
            self.over = True

    def summarize(self):
        time_index = range(1,len(self.record)+1)
        infected = [r[0] for r in self.record ]
        dead = [r[1] for r in self.record]
        healthy = [r[2] for r in self.record]
        recover = [r[3] for r in self.record]

        newly_dead= [0]
        for i in range(1,len(dead)):
            newly_dead.append(dead[i]-dead[i-1])
        newly_dead = moving_average(newly_dead,20)
        
        # style.use('fivethirtyeight')

        # fig = plt.figure()
        # ax1 = fig.add_subplot(1,1,1)

        fig, ax = plt.subplots()
        ax.plot(time_index, infected, color ='red', label='Infected')
        ax.plot(time_index,healthy, color='green', label="Susceptible")
        ax.plot(time_index,newly_dead, color='black', label = f"Potential Dead={dead[-1]}")
        ax.plot(time_index,recover, color='blue', label="Recovered")
        ax.set_xlabel("Period")
        ax.set_ylabel("Population")
        plt.legend()
      
       
        fig, ax2 = plt.subplots()
        ax2.plot(time_index, newly_dead, color = 'black')
        ax2.set_xlabel("20-peroid moving average of fatalities", color='black')
        ax2.set_ylabel("Population")
        plt.show()


pandemic = Pandemic()

#pygame loop
clock = pygame.time.Clock()
font = pygame.font.Font("freesansbold.ttf", 32)

animating = True
pausing= False
while animating and not pandemic.over:

    if not pausing:
    
        #set the background color
        SCREEN.fill(COLORS["background"])
    
        pandemic.run()
        pandemic.keep_track()

        #update the screen and the clock
        clock.tick()
        clock_string = str(math.floor(clock.get_fps()))
        text = font.render(clock_string, True, COLOR_DEFINITIONS["blue"], COLORS["background"])
        text_box = text.get_rect(topleft =(8,8))
        SCREEN.blit(text, text_box)
        pygame.display.flip()



    # track user interaction
    for event in pygame.event.get():

        # user closes the pygame window
        if event.type==pygame.QUIT:
            animating= False
        
        #User presses key on keyboard
        if event.type ==pygame.KEYDOWN:

            #escape key to close the animation
            if event.key ==pygame.K_ESCAPE:
                animating = False

            # return key to restart with a new pandemic
            if event.key == pygame.K_RETURN:
                pausing = False
                pandemic =Pandemic()
            
            # space bar to (un)pause the animation
            if event.key == pygame.K_SPACE:
                pausing = not pausing

pandemic.summarize()