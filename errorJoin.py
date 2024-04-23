import pygame
import button

SCREEN_WIDTH = 1300
SCREEN_HEIGHT = 800

FPS = 60

BUTTONWIDTH = 1000
BUTTONHEIGHT = 150
BUTTONSIZETEXT = 140

class ErrorJoin:
    def __init__(self):
        pygame.init()
        pygame.font.init()
        self.clock = pygame.time.Clock()

        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))  # Set display resolution
                
        self.buttonColorBack = (226,221,220) 

        self.gameStateRun = True

        self.gameScreen = pygame.font.SysFont('Comic Sans MS', 150)

    def run(self):
        self.gameStateRun = True
        while self.gameStateRun:
            self.screen.fill((153,0,17))

            gameScreen_surface = self.gameScreen.render('Error could not join peer', True, (255, 255, 255))
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
             
            pygame.display.update()
            self.clock.tick(FPS)  # Limit to 60 FPS

#if __name__ == "__main__":
 #   test = ErrorJoin()
  #  test.run()