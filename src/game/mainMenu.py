import pygame
import button

SCREEN_WIDTH = 1300
SCREEN_HIGHT = 800

FPS = 60

BUTTONWIDTH = 1000
BUTTONHEIGHT = 150
BUTTONSIZETEXT = 140

class MainMenu:
    def __init__(self, screen, gameState, player):
        pygame.init()
        pygame.font.init()
        self.clock = pygame.time.Clock()

        self.screen = screen  # Set display resolution

        self.sumoImg = pygame.image.load("../assets/sumoMenu.png").convert_alpha() # Load image transparent
        self.sumoImg = pygame.transform.scale(self.sumoImg, (200,200)) # Rescales imaeg

        self.settingsImg = pygame.image.load("../assets/settings.png").convert_alpha() # Load image transparent
        self.settingsImg = pygame.transform.scale(self.settingsImg, (100,100)) # Rescales imaeg

        
        self.buttonColor8 = (226,221,220) 
        self.buttonColorVersus = (226,221,220) 
        self.buttonColorQuit = (226,221,220) 

        self.gameStateRun = True

        self.gameState = gameState

        self.gameScreen = pygame.font.SysFont('Comic Sans MS', 150)

        self.exit = False

    def run(self):
        self.gameStateRun = True
        while self.gameStateRun:
            w,h = pygame.display.get_surface().get_size()
            morePlayerMode = button.Button(self.buttonColor8,SCREEN_WIDTH/7.5,SCREEN_HIGHT/3.5,BUTTONWIDTH,BUTTONHEIGHT,BUTTONSIZETEXT,'8 player')
            singleMode = button.Button(self.buttonColorVersus,SCREEN_WIDTH/7.5,SCREEN_HIGHT/2,BUTTONWIDTH,BUTTONHEIGHT,BUTTONSIZETEXT,'1v1')
            quitTheGame = button.Button(self.buttonColorQuit,SCREEN_WIDTH/7.5,SCREEN_HIGHT/1.4,BUTTONWIDTH,BUTTONHEIGHT,BUTTONSIZETEXT,'Quit')

            self.screen.fill((153,0,17))
            # Sumo rama welcome
            gameScreen_surface = self.gameScreen.render('Sumo Rama', True, (255, 255, 255))
            gameScreen_rect = gameScreen_surface.get_rect(center=(SCREEN_WIDTH/1.9, 140))
            self.screen.blit(gameScreen_surface, gameScreen_rect)

            singleMode.draw(self.screen, (0,0,0))
            morePlayerMode.draw(self.screen, (0,0,0))
            quitTheGame.draw(self.screen, (0,0,0))

            # Hover effect on the buttons
            pos = pygame.mouse.get_pos()
            if singleMode.isOver(pos):
                self.buttonColorVersus = (183,179,183) 
                self.buttonColor8 = (226,221,220)
                self.buttonColorQuit = (226,221,220)
            elif morePlayerMode.isOver(pos):
                self.buttonColor8 = (183,179,183)
                self.buttonColorVersus = (226,221,220)
                self.buttonColorQuit = (226,221,220)
            elif quitTheGame.isOver(pos):
                self.buttonColorQuit = (183,179,183)
                self.buttonColorVersus = (226,221,220)
                self.buttonColor8 = (226,221,220)
            


            self.screen.blit(self.sumoImg, (w/13, 20))
            self.screen.blit(self.sumoImg, (w/1.21, 20))



            self.screen.blit(self.settingsImg, (0, h/1.15))

            # Event handeling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.gameStateRun = False
                    pygame.quit()
                    exit(0)
                if event.type == pygame.MOUSEBUTTONUP:
                    pos = pygame.mouse.get_pos()
                    if singleMode.isOver(pos):
                        print("Starting 1v1 mode")
                        self.gameState.setCurrentState('1v1Menu')
                        self.gameStateRun = False
                    elif morePlayerMode.isOver(pos):
                        print("Starting 8 player mode")
                        self.gameState.setCurrentState('lobbyArena')
                        self.gameStateRun = False
                    elif quitTheGame.isOver(pos):
                        self.gameStateRun = False
                        pygame.quit()
                        exit(0)
                    elif pos[0] < self.settingsImg.get_width() and pos[1] > SCREEN_HIGHT - self.settingsImg.get_height():
                        print("opening settings")
                        self.gameState.setCurrentState('settings')
                        self.gameStateRun = False


            pygame.display.update()
            self.clock.tick(FPS)  # Limit to 60 FPS


