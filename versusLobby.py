import pygame

FPS = 60

SCREEN_WIDTH = 1300
SCREEN_HEIGHT = 800

#TODO make lobby

class VersusLobby:
    def __init__(self, screen, gameState):
        pygame.init()
        pygame.font.init()
        self.clock = pygame.time.Clock()
        self.screen = screen
        # pygame.display.set_caption('1v1 menu')
        
        self.gameStateRun = True

        self.gameState = gameState
    def run(self):
        while self.gameStateRun:
            self.screen.fill((153,0,17))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.gameStateRun = False
                    pygame.quit()
                    exit(0)

            pygame.display.update()
            self.clock.tick(FPS)  # Limits FPS


if __name__ == "__main__":
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))  # Set display resolution

    test = VersusLobby(screen, 1)
    test.run()

