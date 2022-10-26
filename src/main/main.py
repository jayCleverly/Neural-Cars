
import pygame as py
from sim.simulations import Simulation, SaveData, neat, screen_size
import sys


class NeuralCars:
    
    def __init__(self):
        self.setup()
        self.loadImages()
        
        self.screen = py.display.set_mode(screen_size)
        py.display.set_caption("Neural Cars")
        self.clock = py.time.Clock()
        self.mouse = py.mouse.get_pos()
        
        self.font = py.font.SysFont(None, 90)
        self.font2 = py.font.SysFont(None, 35)
        
        
    def setup(self):
        """ 
        This has to be done as matplotlib and pygame dont work properly together therefore the screen size changes whenever a graph is formed.
        It is convenient and effective to use matplotlib so this function has been created to run a fodder simulation with 0 generations.
        This setups the screen size correctly for use by the user.
        """
        
        py.init()
        self.screen = py.display.set_mode(screen_size)
        self.clock = py.time.Clock()
        
        # loads classes and population function
        sim = Simulation(self.screen, self.clock, "src/static/tracks/"+ "Interlagos" + ".png", 0, True)
        population = neat.Population(sim.loadConfig("src/static/sim_content/config.txt"))
                
        # loads in a neat function to get info about each generation
        std_out = neat.StdOutReporter(True)
        population.add_reporter(std_out)
        stat_report = neat.StatisticsReporter()
        population.add_reporter(stat_report)
                
        # runs simulation for a set number of generations
        population.run(sim.runSim, 0)
        
        # saves graphs to temporary storage
        data = SaveData("Interlagos", stat_report, 0)      
        data.formatData()
        
        
    def loadImages(self):
        self.scale = (200, 113)
        self.daytona = py.transform.scale(py.image.load("src/static/tracks/Daytona_500.png").convert(), self.scale)
        self.gilles = py.transform.scale(py.image.load("src/static/tracks/Gilles_Villenueve.png").convert(), self.scale)
        self.interlagos = py.transform.scale(py.image.load("src/static/tracks/Interlagos.png").convert(), self.scale)
        self.le = py.transform.scale(py.image.load("src/static/tracks/Le_Mans.png").convert(), self.scale)
        self.monza = py.transform.scale(py.image.load("src/static/tracks/Monza.png").convert(), self.scale)
        self.silverstone = py.transform.scale(py.image.load("src/static/tracks/Silverstone.png").convert(), self.scale)
        
        
    def buttonClick(self, track, gens):
        # for track choice screen
        if not self.track_chosen:
            self.track_chosen = True
            self.selected_track = track
            
        # for max generation choice screen
        else:
            self.runSimulation(self.selected_track, gens)
            self.finished_setup = True
            
            
    def rightOrLeftBtn(self, current, x, y):
        # allows user to navigate through the visual data
        # right button
        if (screen_size[0] / 2) - self.btn_size[0] + 460 < x < ((screen_size[0] / 2) + 460) and (screen_size[1] / 2) - self.btn_size[1] < y < (screen_size[1] / 2):
            if current == "graph1":
                self.viewing_graph1 = False
                self.viewing_graph2 = True
            elif current == "graph2":
                self.viewing_graph2 = False
                self.viewing_graph3 = True
            else:
                self.viewing_graph3 = False
                self.viewing = False 
        
        # left button
        elif (screen_size[0] / 2) - self.btn_size[0] - 430 < x < ((screen_size[0] / 2) + 430) and (screen_size[1] / 2) - self.btn_size[1] < y < (screen_size[1] / 2):
            if current == "graph2":
                self.viewing_graph2 = False
                self.viewing_graph1 = True
            elif current == "graph3":
                self.viewing_graph3 = False
                self.viewing_graph2 = True
            
            
    def events(self):
        self.mouse = py.mouse.get_pos()
        for self.event in py.event.get():
            # checks to see if user is wanting to quit the game
            if self.event.type == py.QUIT:
                self.quit()
            if self.event.type == py.KEYDOWN:
                if self.event.key == py.K_ESCAPE:
                    self.quit()
            
            if self.event.type == py.MOUSEBUTTONDOWN:
                # checks to see if left mouse has been clicked
                state = py.mouse.get_pressed()
                if state[0]:
                    
                    if not self.sim_running:
                        x, y = self.event.pos
                        
                        # allows user to click on continue button
                        if not self.ready_to_start:
                            if (screen_size[0]/2 - 120) < x < (screen_size[0]/2 - 120) + 240 and (screen_size[1]/2 + 25) < y < (screen_size[1]/2 + 25) + 100:
                                self.ready_to_start = True
                                self.setupSimulation()
                        
                        else:
                            # allows user to click on buttons to setup simulation (track and generation screens)
                            if not self.finished_setup:
                                        
                                # daytona or 10
                                if self.btn1_pos[0] < x < self.btn1_pos[0] + self.scale[0] and self.btn1_pos[1] < y < self.btn1_pos[1] + self.scale[1]:
                                    self.buttonClick("Daytona_500", 10)
                                        
                                # gilles or 25
                                if self.btn2_pos[0] < x < self.btn2_pos[0] + self.scale[0] and self.btn2_pos[1] < y < self.btn2_pos[1] + self.scale[1]:
                                    self.buttonClick("Gilles_Villenueve", 25)
                                            
                                # interlagos or 50
                                if self.btn3_pos[0] < x < self.btn3_pos[0] + self.scale[0] and self.btn3_pos[1] < y < self.btn3_pos[1] + self.scale[1]:
                                    self.buttonClick("Interlagos", 50)
                                        
                                # le mans or 100
                                if self.btn4_pos[0] < x < self.btn4_pos[0] + self.scale[0] and self.btn4_pos[1] < y < self.btn4_pos[1] + self.scale[1]:
                                    self.buttonClick("Le_Mans", 100)
                                        
                                # monza or 250
                                if self.btn5_pos[0] < x < self.btn5_pos[0] + self.scale[0] and self.btn5_pos[1] < y < self.btn5_pos[1] + self.scale[1]:
                                    self.buttonClick("Monza", 250)
                                        
                                # silverstone or 500
                                if self.btn6_pos[0] < x < self.btn6_pos[0] + self.scale[0] and self.btn6_pos[1] < y < self.btn6_pos[1] + self.scale[1]:
                                    self.buttonClick("Silverstone", 500)
                            
                    elif self.sim_running and self.viewing:
                        # allows user to navigate through the data being visualised to them
                        x, y = self.event.pos

                        if self.viewing_graph1:
                            self.rightOrLeftBtn("graph1", x, y)
                        
                        elif self.viewing_graph2:    
                            self.rightOrLeftBtn("graph2", x, y)
                            
                        elif self.viewing_graph3:
                            self.rightOrLeftBtn("graph3", x, y)
                  
                  
    def quit(self):
        py.quit()
        sys.exit()
    
    
    def homeScreen(self):
        self.sim_running = False
        self.ready_to_start = False
    
        while not self.ready_to_start:
            # simple home screen
            self.screen.fill((0,0,0))
            
            # title
            label = self.font.render("Neural Cars", 1, (255, 255, 255))
            self.screen.blit(label, ((screen_size[0]/2) - label.get_size()[0]/2, 225))
            
            label = self.font2.render("Simulate neural network powered cars on a variety of tracks.", 1, (255, 255, 255)) 
            self.screen.blit(label, ((screen_size[0]/2) - label.get_size()[0]/2, 315)) 
                 
            # continue button
            py.draw.rect(self.screen,(255,255,255),[(screen_size[0]/2 - 120),(screen_size[1]/2 + 25),240,100])
            label = self.font2.render("Continue", 1, (0,0,0))
            self.screen.blit(label, (((screen_size[0]/2) - label.get_size()[0]/2), 425))
                        
            self.events()
            py.display.flip()


    def setupSimulation(self):
        self.finished_setup = False
        self.track_chosen = False
        self.gens_chosen = False
        
        while not self.finished_setup:
            if not self.track_chosen:
                # shows a range of tracks for users to choose from
                self.screen.fill((0,0,0))
                    
                # title
                label = self.font2.render("Select a track to simulate on.", 1, (255, 255, 255))
                self.screen.blit(label, ((screen_size[0]/2) - label.get_size()[0]/2, 200))

                # images
                self.btn1_pos = (310, 275)
                self.screen.blit(self.daytona, self.btn1_pos)
                
                self.btn2_pos = (530, 275)
                self.screen.blit(self.gilles, self.btn2_pos)
                
                self.btn3_pos = (750, 275)
                self.screen.blit(self.interlagos, self.btn3_pos)
                    
                self.btn4_pos = (310, 415)
                self.screen.blit(self.le, self.btn4_pos)
                
                self.btn5_pos = (530, 415)
                self.screen.blit(self.monza, self.btn5_pos)
                
                self.btn6_pos = (750, 415)
                self.screen.blit(self.silverstone, self.btn6_pos)
                
            else:
                # shows a range of generations for users to choose from
                self.screen.fill((0,0,0))
                    
                # title
                label = self.font2.render("Choose how many generations to simulate.", 1, (255, 255, 255))
                self.screen.blit(label, ((screen_size[0]/2) - label.get_size()[0]/2, 200))
                    
                # buttons
                # 10
                py.draw.rect(self.screen, (255,255,255), [self.btn1_pos[0], self.btn1_pos[1], self.scale[0], self.scale[1]])
                label = self.font.render("10", 1, (0,0,0))
                self.screen.blit(label, ((self.btn1_pos[0] + 65, self.btn1_pos[1] + 30)))
                
                # 25
                py.draw.rect(self.screen, (255,255,255), [self.btn2_pos[0], self.btn2_pos[1], self.scale[0], self.scale[1]])
                label = self.font.render("25", 1, (0,0,0))
                self.screen.blit(label, ((self.btn2_pos[0] + 65, self.btn2_pos[1] + 30)))
                
                # 50
                py.draw.rect(self.screen, (255,255,255), [self.btn3_pos[0], self.btn3_pos[1], self.scale[0], self.scale[1]])
                label = self.font.render("50", 1, (0,0,0))
                self.screen.blit(label, ((self.btn3_pos[0] + 65, self.btn3_pos[1] + 30)))
                
                # 100
                py.draw.rect(self.screen, (255,255,255), [self.btn4_pos[0], self.btn4_pos[1], self.scale[0], self.scale[1]])
                label = self.font.render("100", 1, (0,0,0))
                self.screen.blit(label, ((self.btn4_pos[0] + 45, self.btn4_pos[1] + 30)))
                
                # 250
                py.draw.rect(self.screen, (255,255,255), [self.btn5_pos[0], self.btn5_pos[1], self.scale[0], self.scale[1]])
                label = self.font.render("250", 1, (0,0,0))
                self.screen.blit(label, ((self.btn5_pos[0] + 45, self.btn5_pos[1] + 30)))
                
                # 500
                py.draw.rect(self.screen, (255,255,255), [self.btn6_pos[0], self.btn6_pos[1], self.scale[0], self.scale[1]])
                label = self.font.render("500", 1, (0,0,0))
                self.screen.blit(label, ((self.btn6_pos[0] + 45, self.btn6_pos[1] + 30)))
                    
            self.events()
            py.display.flip()

            
    def runSimulation(self, track, gens):
        self.sim_running = True
        
        # loads classes and population function
        sim = Simulation(self.screen, self.clock, "src/static/tracks/"+ track + ".png", gens, False)

        population = neat.Population(sim.loadConfig("src/static/sim_content/config.txt"))
                
        # loads in a neat function to get info about each generation
        std_out = neat.StdOutReporter(True)
        population.add_reporter(std_out)
        stat_report = neat.StatisticsReporter()
        population.add_reporter(stat_report)
                
        # runs simulation for a set number of generations
        population.run(sim.runSim, gens)
        
        # saves graphs to temporary storage
        data = SaveData(track, stat_report, gens)      
        data.formatData()
        
        
    def navigateBtn(self, d):
        # creates the left and right buttons for users to navigate with
        self.btn_size = (60,60)
        if d == "l":
            py.draw.rect(self.screen, (255,255,255), [((screen_size[0] / 2) - self.btn_size[0]) - 430, (screen_size[1] / 2) - self.btn_size[1], self.btn_size[0], self.btn_size[1]])
            label = self.font.render("<-", 1, (0,0,0))
            self.screen.blit(label, (((screen_size[0] / 2) - self.btn_size[0] - 430), (screen_size[1] / 2) - self.btn_size[1]))
        
        elif d == "r":
            py.draw.rect(self.screen, (255,255,255), [((screen_size[0] / 2) - self.btn_size[0]) + 460, (screen_size[1] / 2) - self.btn_size[1], self.btn_size[0], self.btn_size[1]])
            label = self.font.render("->", 1, (0,0,0))
            self.screen.blit(label, (((screen_size[0] / 2) - self.btn_size[0] + 460), (screen_size[1] / 2) - self.btn_size[1]))
        
        
    def viewSimData(self):
        # initialises variables to check what graph user is looking at
        self.sim_running = True
        self.viewing = True
        
        self.viewing_graph1 = True
        self.viewing_graph2 = False
        self.viewing_graph3 = False
        
        scale = (640, 480)
        # loads in images from temporary storage
        self.mean_fitness = py.transform.scale(py.image.load("src/main/sim/temporary_storage/mean_fitness.png").convert(), scale)
        self.best_fitness = py.transform.scale(py.image.load("src/main/sim/temporary_storage/best_fitness.png").convert(), scale)
        self.species_change = py.transform.scale(py.image.load("src/main/sim/temporary_storage/species_change.png").convert(), scale)
        
        while self.viewing:
            # allows user to see simulation data visualised in graphs
            self.screen.fill((0,0,0))            
            
            # title
            label = self.font2.render(self.selected_track + " simulation data", 1, (255, 255, 255))
            self.screen.blit(label, ((screen_size[0]/2) - label.get_size()[0]/2, 75))
            
            if self.viewing_graph1:
                # graphs
                self.screen.blit(self.mean_fitness, ((self.mean_fitness.get_size()[0] / 2)-5, 150))
                self.navigateBtn("r")
            
            elif self.viewing_graph2:
                self.screen.blit(self.best_fitness, ((self.best_fitness.get_size()[0] / 2)-5, 150))
                self.navigateBtn("l")
                self.navigateBtn("r")
                
            elif self.viewing_graph3:
                self.screen.blit(self.species_change, ((self.species_change.get_size()[0] / 2)-5, 150))
                self.navigateBtn("l")
                
                # finish button
                py.draw.rect(self.screen, (255,0,0), [((screen_size[0] / 2) - self.btn_size[0]) + 460, (screen_size[1] / 2) - self.btn_size[1], self.btn_size[0], self.btn_size[1]])
                label = self.font2.render("Exit", 1, (255,255,255))
                self.screen.blit(label, (((screen_size[0] / 2) - self.btn_size[0] + 465), (screen_size[1] / 2) - self.btn_size[1] + 20))
                
            self.events()
            py.display.flip()
            

if __name__ == "__main__":
    while True:
        n = NeuralCars()
        n.homeScreen()
        n.viewSimData()
