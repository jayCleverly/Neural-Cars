
import base64
import sys, neat, math, time, sqlite3
from matplotlib import pyplot as plt
import pygame as py

# constant variables
screen_size = [1280, 720]
border_colour = (255, 255, 255, 255)

car_size_x = 35
car_size_y = 35


class Car:
    def __init__(self):
        self.sprite = py.image.load('src/static/sim_content/car.png').convert()
        self.sprite = py.transform.scale(self.sprite, (car_size_x, car_size_y))
        self.rotated_sprite = self.sprite 

        # start position
        self.position = [465, 610]
        self.angle = 0
        self.speed = 0
        self.speed_set = False

        # calculates center point
        self.center = [self.position[0] + car_size_x / 2, self.position[1] + car_size_y / 2]
        self.radars = []

        # checks to see which cars are alive and the distance travelled
        self.alive = True
        self.distance = 0

    def draw(self, screen):
        screen.blit(self.rotated_sprite, self.position)
        self.drawRadar(screen)
        
    def drawRadar(self, screen):
        for radar in self.radars:
            position = radar[0]
            py.draw.line(screen, (0, 255, 0), self.center, position, 1)
            py.draw.circle(screen, (0, 255, 0), position, 5)
            
    def rotateCenter(self, image, angle):
        # this rotates the rectangle
        rectangle = image.get_rect()
        rotated_image = py.transform.rotate(image, angle)
        
        # copies the rectangle and gets its centerpoint
        rotated_rectangle = rectangle.copy()
        rotated_rectangle.center = rotated_image.get_rect().center
        
        # creates the new surface referencing the parent sprite
        rotated_image = rotated_image.subsurface(rotated_rectangle).copy()
        return rotated_image
            
    def movement(self):
        # this sets the speed to 10 for the first time
        if not self.speed_set:
            self.speed = 10
            self.speed_set = True
            
        # get the rotated sprite and move the x direction
        self.rotated_sprite = self.rotateCenter(self.sprite, self.angle)
        self.rect = self.rotated_sprite.get_rect()
        self.position[0] += math.cos(math.radians(360 - self.angle)) * self.speed
        
        # don't let the car go closer than 20 px to the edge of track
        self.position[0] = max(self.position[0], 20)
        self.position[0] = min(self.position[0], screen_size[0] - 80)
        
        # increase the distance
        self.distance += self.speed
        
        # do the same for the y position
        self.position[1] += math.sin(math.radians(360 - self.angle)) * self.speed
        self.position[1] = max(self.position[1], 20)
        self.position[1] = min(self.position[1], screen_size[0] - 80)
        
        # calculates new center value
        self.center = [int(self.position[0]) + car_size_x / 2, int(self.position[1]) + car_size_y / 2]
        
    def getReward(self):
        # calculates reward given
        return self.distance / (car_size_x / 2)
        
    def calcCorners(self):
        # calculates four corners
        length = 0.5 * car_size_x
        
        left_top = [self.center[0] + math.cos(math.radians(360 - (self.angle + 30))) * length, 
                    self.center[1] + math.sin(math.radians(360 - (self.angle + 30))) * length]
        right_top = [self.center[0] + math.cos(math.radians(360 - (self.angle + 150))) * length, 
                     self.center[1] + math.sin(math.radians(360 - (self.angle + 150))) * length]
        left_bottom = [self.center[0] + math.cos(math.radians(360 - (self.angle + 210))) * length, 
                       self.center[1] + math.sin(math.radians(360 - (self.angle + 210))) * length]
        right_bottom = [self.center[0] + math.cos(math.radians(360 - (self.angle + 330))) * length,
                        self.center[1] + math.sin(math.radians(360 - (self.angle + 330))) * length]
        
        corners = [left_top, right_top, left_bottom, right_bottom]
        return corners
    
    def checkCollision(self, sim_track):
        self.alive = True
        for point in self.calcCorners():
            # if any of the corners touch the broder colour, that car is eliminated
            if sim_track.get_at((int(point[0]), int(point[1]))) == border_colour:
                self.alive = False
                break
            
    def isAlive(self):
        return self.alive
            
    def calcRadars(self, degree, length):
        # calculates positions of radars from centerpoints
        x = int(self.center[0] + math.cos(math.radians(360 - (self.angle + degree))) * length)
        y = int(self.center[1] + math.sin(math.radians(360 - (self.angle + degree))) * length)
        return x, y
            
    def checkRadars(self, degree, sim_track):
        length = 0
        x, y = self.calcRadars(degree, length)
        
        # while cars don't hit border colour and length < 250, cars go further
        # calls function to calculate radar positions
        while not sim_track.get_at((x, y)) == border_colour and length < 250:
            length += 1
            x, y = self.calcRadars(degree, length)
            
        # calculate distance to border and append to radars list
        dist = int(math.sqrt(math.pow(x - self.center[0], 2) + math.pow(y - self.center[1], 2)))
        self.radars.append([(x, y), dist])
            
    def getData(self):
        # gets the distances to border
        radars = self.radars
        return_values = [0,0,0,0,0]
        
        for i, radar in enumerate(radars):
            return_values[i] = int(radar[1] / 30)
        return return_values
            
    def update(self, sim_track):
        self.movement()

        # checks for collisions and clears radars
        self.checkCollision(sim_track)
        self.radars.clear()
        
        # from -90 to 120, with step size 45, check radar
        for d in range(-90, 120, 45):
            self.checkRadars(d, sim_track)
        

class Simulation:
    def __init__(self, screen, clock, sim_track, gens, is_setup):
        self.screen = screen
        self.clock = clock
        self.track = py.image.load(sim_track)
        self.max_gen = gens
        self.setup = is_setup
        
        # keep track of different generations
        self.current_generation = 0
        self.generations = []
        
    def loadConfig(self, config_path):
        config = neat.config.Config(neat.DefaultGenome,
            neat.DefaultReproduction,
            neat.DefaultSpeciesSet,
            neat.DefaultStagnation,
            config_path)
    
        return config
    
    def events(self):
        # exits on quit event
        for event in py.event.get():
            if event.type == py.QUIT:
                self.quit()
            if event.type == py.KEYDOWN:
                if event.key == py.K_ESCAPE:
                    self.quit()

    def quit(self):
        py.quit()
        sys.exit()
        
    def runSim(self, genomes, config):      
        cars = []
        nets = []
        
        # intialises car and data objects in lists
        for i, g in genomes:
            net = neat.nn.FeedForwardNetwork.create(g, config)
            nets.append(net)
            g.fitness = 0

            cars.append(Car())

        # appends the different generations
        self.current_generation += 1
        self.generations.append(self.current_generation)
        
        # counter to limit time
        counter = time.time()
        
        while True:
            self.events()
            
            # for each car get the action it takes
            for i, car in enumerate(cars):
                output = nets[i].activate(car.getData())
                choice = output.index(max(output))
                
                # decides what to do based on car choices
                if choice == 0:
                    # goes left
                    car.angle += 10
                elif choice == 1:
                    # goes right
                    car.angle -= 10
                elif choice == 2:
                    # slows down
                    if(car.speed - 2 >= 12):
                        car.speed -= 2
                else:
                    # speeds up
                    car.speed += 2

            # checks to see if car is still alive
            # increases fitness if they are and break loop if not
            still_alive = 0
            for i, car in enumerate(cars):
                if car.isAlive():
                    still_alive += 1
                    car.update(self.track)
                    genomes[i][1].fitness += car.getReward()

            if still_alive == 0:
                break

            # breaks loop after 6 seconds
            counter_check = time.time()
            if counter_check - counter >= 6:
                break
            
            if not self.setup:
                # draws track and cars on screen
                self.screen.blit(self.track, (0,0))
                for car in cars:
                    if car.isAlive():
                        car.draw(self.screen)
                
                # displays current generation to the user
                font = py.font.Font(None, 32)
                text = font.render("Generation: " + str(self.current_generation) + " / " + str(self.max_gen), True, (0,0,0))
                self.screen.blit(text, (10, 10))

            py.display.flip()
            self.clock.tick(45)


class SaveData:
    def __init__(self, name, stat_reporter, max_gens):
        self.name = name
        self.stat_reporter = stat_reporter
        self.gens = max_gens
        
    def formatData(self):
        # gets list of generation ids from list
        self.generation_list = []
        for i in range(self.gens):
            self.generation_list.append(i)
        
        # gets fitness data for each generation from neat stat reporter function
        self.mean_fitness = self.stat_reporter.get_fitness_mean()
        self.best_fitness = [x.fitness for x in self.stat_reporter.most_fit_genomes]
        
        self.average_fitnesses = []
        self.top_fitnesses = []
        
        # makes the data more readbable and understandable when in a graph
        for i in self.mean_fitness:
            x = i / 100
            x = "{:.2f}".format(x)
            self.average_fitnesses.append(float(x))

        for i in self.best_fitness:
            j = i / 100
            j = "{:.2f}".format(j)
            self.top_fitnesses.append(float(j))
            
        # gets species ids from dictionary data from neat std out reporter function
        self.species = []
        for gen_data in self.stat_reporter.generation_statistics:
            
            # unpacks data and finds most evolved species
            keys = [*gen_data]
            self.species.append(max(keys))
    
        # loading in graphs
        self.formatImages()
        
    def graph(self, type, title, file_name, xlabel, ylabel, xdata, ydata, color):
        plt.title(title)
        # annotating the axis
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
              
        if type == "scatter":
            # scattering the data
            plt.scatter(xdata, ydata, color=color, s=6)

        elif type == "line":
            # plotting the data
            plt.plot(xdata, ydata, color=color)
        
        plt.savefig("src/main/sim/temporary_storage/" + file_name + ".png")
        plt.close()
        
    def formatImages(self):
        # creating the graphs
        mean_fitness = "mean_fitness" 
        best_fitness = "best_fitness"
        species_change = "species_change"
        
        # mean fitness graph
        self.graph("scatter", "Mean Fitness", mean_fitness, "Generations", "Fitness", self.generation_list, self.average_fitnesses, "red")
        # best fitness graph
        self.graph("scatter", "Best Fitness", best_fitness, "Generations", "Fitness", self.generation_list, self.top_fitnesses, "red")
        # species change graph
        self.graph("line", "Species Evolution", species_change, "Generations", "Species ID", self.generation_list, self.species, "red")
        