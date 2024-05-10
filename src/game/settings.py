import pygame
import button

FPS = 60

SCREEN_WIDTH = 1300
SCREEN_HEIGHT = 800

BUTTONWIDTH = 400
BUTTONHEIGHT = 100
BUTTONSIZETEXT = 140

class Settings:
    def __init__(self, screen, gameState, player):
        pygame.init()
        pygame.font.init()

        self.clock = pygame.time.Clock()
        
        self.screen = screen  # Set display resolution
        self.gameState = gameState
        self.player = player

        self.gameStateRun = True
        self.buttonColor = (226,221,220)
        
        self.gameFont = pygame.font.SysFont('Comic Sans MS', 90)

    def run(self):
        self.gameStateRun = True

        while self.gameStateRun:
            self.screen.fill((153,0,17)) # Red screen

            gameScreen_surface = self.gameFont.render('Settings', True, (255, 255, 255))
            gameScreen_rect = gameScreen_surface.get_rect(center=(SCREEN_WIDTH/2, 50))
            self.screen.blit(gameScreen_surface, gameScreen_rect)

      
            # Return button
            goBackButton = button.Button(self.buttonColor,SCREEN_WIDTH/2 - BUTTONWIDTH/2,SCREEN_HEIGHT/1.15,BUTTONWIDTH,BUTTONHEIGHT,BUTTONSIZETEXT,'Return')
            goBackButton.draw(self.screen, (0,0,0))

            # Hover effect for button
            pos = pygame.mouse.get_pos()
            if goBackButton.isOver(pos):
                self.buttonColor = (183,179,183) 
            else:
                self.buttonColor = (226,221,220) 

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.gameStateRun = False
                    pygame.quit()
                    exit(0)
                if event.type == pygame.MOUSEBUTTONUP:
                    pos = pygame.mouse.get_pos()
                    if goBackButton.isOver(pos):
                        print("Returning to mainMenu")
                        self.gameState.setCurrentState('start')
                        self.gameStateRun = False

            pygame.display.update()
            self.clock.tick(FPS)  # Limit to 60 FPS
