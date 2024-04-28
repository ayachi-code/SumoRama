import pygame
import button


FPS = 60

SCREEN_WIDTH = 1300
SCREEN_HEIGHT = 800

BUTTONWIDTH = 1000
BUTTONHEIGHT = 150
BUTTONSIZETEXT = 140



class GameOverVersus:
    def __init__(self, screen, gameState):
        pygame.init()
        pygame.font.init()

        self.clock = pygame.time.Clock()
        
        self.screen = screen  # Set display resolution
        self.gameState = gameState

        self.gameStateRun = True
        self.buttonColor = (226,221,220)
        
        self.gameFont = pygame.font.SysFont('Comic Sans MS', 130)

        self.winner = "" # Stores the winner

    def setWinner(self, winner):
        self.winner = winner

    def resetWinner(self):
        self.winner = ""

    def getWinner(self):
        return self.winner

    def run(self):
        self.gameStateRun = True
        while self.gameStateRun:
            self.screen.fill((153,0,17)) # Red screen

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.gameStateRun = False
                    pygame.quit()
                    exit(0)


            gameScreen_surface = self.gameFont.render('GAME OVER!!!!!', True, (255, 255, 255))
            gameScreen_rect = gameScreen_surface.get_rect(center=(SCREEN_WIDTH/1.9, 140))
            self.screen.blit(gameScreen_surface, gameScreen_rect)

            gameScreen_surfaceTwo = self.gameFont.render(self.winner + ' won the game', True, (255, 255, 255))
            gameScreen_rectTwo = gameScreen_surfaceTwo.get_rect(center=(SCREEN_WIDTH/1.9, 300))
            self.screen.blit(gameScreen_surfaceTwo, gameScreen_rectTwo)

            # Return button
            goBackButton = button.Button(self.buttonColor,SCREEN_WIDTH/7.5,SCREEN_HEIGHT/1.75,BUTTONWIDTH,BUTTONHEIGHT,BUTTONSIZETEXT,'Return')
            goBackButton.draw(self.screen, (0,0,0))

            # Hover effect for button
            pos = pygame.mouse.get_pos()
            if goBackButton.isOver(pos):
                self.buttonColor = (183,179,183) 
            else:
                self.buttonColor = (226,221,220) 
        
            pygame.display.update()
            self.clock.tick(FPS)  # Limit to 60 FPS


#if __name__ == "__main__":
#    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))  # Set display resolution
#    game = GameOverVersus(screen, None)
#    game.run()