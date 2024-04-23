import pygame
import button

SCREEN_WIDTH = 1300
SCREEN_HIGHT = 800

FPS = 60

BUTTONWIDTH = 1000
BUTTONHEIGHT = 150
BUTTONSIZETEXT = 140

class VersusMenu:
    def __init__(self, screen, gameState):
        pygame.init()
        pygame.font.init()
        self.clock = pygame.time.Clock()

        self.screen = screen
        # pygame.display.set_caption('1v1 menu')
        
        self.buttonColor8 = (226,221,220) 
        self.buttonColorVersus = (226,221,220) 
        self.buttonColorQuit = (226,221,220) 

        self.gameStateRun = True

        self.gameScreen = pygame.font.SysFont('Comic Sans MS', 150)

        self.gameState = gameState

    
    def run(self):
        self.gameStateRun = True
        while self.gameStateRun:
            w,h = pygame.display.get_surface().get_size()
            morePlayerMode = button.Button(self.buttonColor8,SCREEN_WIDTH/7.5,SCREEN_HIGHT/3.5,BUTTONWIDTH,BUTTONHEIGHT,BUTTONSIZETEXT,'Host')
            singleMode = button.Button(self.buttonColorVersus,SCREEN_WIDTH/7.5,SCREEN_HIGHT/2,BUTTONWIDTH,BUTTONHEIGHT,BUTTONSIZETEXT,'Join')
            quitTheGame = button.Button(self.buttonColorQuit,SCREEN_WIDTH/7.5,SCREEN_HIGHT/1.4,BUTTONWIDTH,BUTTONHEIGHT,BUTTONSIZETEXT,'Back')

            self.screen.fill((153,0,17))
            # Sumo rama welcome
            gameScreen_surface = self.gameScreen.render('Sumo Rama 1v1', True, (255, 255, 255))
            gameScreen_rect = gameScreen_surface.get_rect(center=(SCREEN_WIDTH/1.9, 140))
            self.screen.blit(gameScreen_surface, gameScreen_rect)

            singleMode.draw(self.screen, (0,0,0))
            morePlayerMode.draw(self.screen, (0,0,0))
            quitTheGame.draw(self.screen, (0,0,0))

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
       
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.gameStateRun = False
                    pygame.quit()
                    exit(0)
                if event.type == pygame.MOUSEBUTTONUP:
                    pos = pygame.mouse.get_pos()
                    if singleMode.isOver(pos):
                        print("Join")
                        self.gameState.setCurrentState('joinMenu')
                        self.gameStateRun = False
                    elif morePlayerMode.isOver(pos):
                        print("Host")
                    elif quitTheGame.isOver(pos):
                        print("Player quit the game")
                        self.gameState.setCurrentState('start')
                        self.gameStateRun = False

            pygame.display.update()
            self.clock.tick(60)  # Limit to 60 FPS