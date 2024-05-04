import pygame


import sys
sys.path.append("../lib/") # Lib import different folder


import button

SCREEN_WIDTH = 1300
SCREEN_HEIGHT = 800

FPS = 60

BUTTONWIDTH = 1000
BUTTONHEIGHT = 150
BUTTONSIZETEXT = 140

class LobbyFull:
    def __init__(self, screen, gameState):
        pygame.init()
        pygame.font.init()
        self.clock = pygame.time.Clock()

        self.screen = screen # Set display resolution
                
        self.buttonColorBack = (226,221,220) 

        self.gameStateRun = True

        self.gameScreen = pygame.font.SysFont('Comic Sans MS', 100)

        self.gameState = gameState

    def run(self):
        self.gameStateRun = True
        while self.gameStateRun:
            self.screen.fill((153,0,17))

            gameScreen_surface = self.gameScreen.render('Error: Lobby is full', True, (255, 255, 255))
            gameScreen_rect = gameScreen_surface.get_rect(center=(SCREEN_WIDTH/1.9, 140))
            self.screen.blit(gameScreen_surface, gameScreen_rect)

            gameScreen_surfaceTwo = self.gameScreen.render('Please try again later', True, (255, 255, 255))
            gameScreen_rectTwo = gameScreen_surfaceTwo.get_rect(center=(SCREEN_WIDTH/1.9, 300))
            self.screen.blit(gameScreen_surfaceTwo, gameScreen_rectTwo)

            back = button.Button(self.buttonColorBack,SCREEN_WIDTH/7.5,SCREEN_HEIGHT/1.6,BUTTONWIDTH,BUTTONHEIGHT,BUTTONSIZETEXT,'Back')
            back.draw(self.screen, (0,0,0))

            pos = pygame.mouse.get_pos()
            if back.isOver(pos):
                self.buttonColorBack = (183,179,183) 
            else:
                self.buttonColorBack = (226,221,220) 

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.gameStateRun = False
                    pygame.quit()
                    exit(0)
                if event.type == pygame.MOUSEBUTTONUP:
                    pos = pygame.mouse.get_pos()
                    if back.isOver(pos): # Backout to join/host menu
                        self.gameState.setCurrentState('start')
                        self.gameStateRun = False
             
            pygame.display.update()
            self.clock.tick(FPS)  # Limit to 60 FPS
