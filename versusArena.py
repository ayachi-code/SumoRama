import pygame

FPS = 60

# 1v1 arena code

class VersusArena:
    def __init__(self, screen, gameState, player, peer):
        pygame.init()
        pygame.font.init()
        self.clock = pygame.time.Clock()

        self.screen = screen  # Set display resolution
        self.gameState = gameState
        self.peer = peer
        self.player = player

        self.gameStateRun = True

    def setPeer(self, peer):
        self.peer = peer

    def run(self):
        print(self.peer.getConnections())
        while self.gameStateRun:
            self.screen.fill((255,255,255)) # White screen

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.gameStateRun = False
                    pygame.quit()
                    exit(0)

            pygame.display.update()
            self.clock.tick(FPS)  # Limits FPS