import pygame
import button

SCREEN_WIDTH = 1300
SCREEN_HIGHT = 800

FPS = 60

BUTTONWIDTH = 1000
BUTTONHEIGHT = 150
BUTTONSIZETEXT = 140


class Game:
    def __init__(self):
        pygame.init()
        pygame.font.init()
        self.clock = pygame.time.Clock()

        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HIGHT))  # Set display resolution
        pygame.display.set_caption('Main menu')

        self.sumoImg = pygame.image.load("assets/sumoMenu.png").convert_alpha() # Load image transparent
        self.sumoImg = pygame.transform.scale(self.sumoImg, (200,200)) # Rescales imaeg

        self.sumoImg = pygame.image.load("assets/sumoMenu.png").convert_alpha() # Load image transparent
        self.sumoImg = pygame.transform.scale(self.sumoImg, (200,200)) # Rescales imaeg

        
        self.buttonColor8 = (226,221,220) 
        self.buttonColorVersus = (226,221,220) 
        self.buttonColorQuit = (226,221,220) 

        self.gameStateRun = True

        self.gameScreen = pygame.font.SysFont('Comic Sans MS', 150)
    def run(self):
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

            pos = pygame.mouse.get_pos()
            if singleMode.isOver(pos):
                self.buttonColorVersus = (183,179,183) 
            elif morePlayerMode.isOver(pos):
                self.buttonColor8 = (183,179,183)
            elif quitTheGame.isOver(pos):
                self.buttonColorQuit = (183,179,183)
            else:
                self.buttonColorVersus = (226,221,220)
                self.buttonColor8 = (226,221,220)
                self.buttonColorQuit = (226,221,220)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.gameStateRun = False
                if event.type == pygame.MOUSEBUTTONUP:
                    pos = pygame.mouse.get_pos()
                    if singleMode.isOver(pos):
                        print("Starting 1v1 mode")
                    elif morePlayerMode.isOver(pos):
                        print("Starting 8 player mode")
                    elif quitTheGame.isOver(pos):
                        print("Player quit the game")
                        self.gameStateRun = False

                    
            self.screen.blit(self.sumoImg, (w/10, 20))
            self.screen.blit(self.sumoImg, (w/1.3, 20))

            pygame.display.update()
            self.clock.tick(FPS)  # Limit to 60 FPS


if __name__ == "__main__":
     game = Game()
     game.run()
     pygame.quit()