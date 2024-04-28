import pygame

FPS = 60

SCREEN_WIDTH = 1300
SCREEN_HEIGHT = 800


class GameOverVersus:
    def __init__(self, screen, gameState):
        pygame.init()
        pygame.font.init()
        self.clock = pygame.time.Clock()
        
        self.screen = screen  # Set display resolution
        self.gameState = gameState

        self.gameStateRun = True

    def run(self):
        self.gameStateRun = True
        while self.gameStateRun:
            self.screen.fill((153,0,17)) # Red screen
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.gameStateRun = False
                    pygame.quit()
                    exit(0)
            
            pygame.display.update()
            self.clock.tick(FPS)  # Limit to 60 FPS


if __name__ == "__main__":
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))  # Set display resolution
    game = GameOverVersus(screen, None)
    game.run()