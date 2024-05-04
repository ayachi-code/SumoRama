import socket
import threading
import pygame
import time

FPS = 60


class PlayerArena:
    def __init__(self, screen, gameState, peer, player, gameOver):
        pygame.init() # Init pygame
        pygame.font.init() # Init font

        self.gameFont = pygame.font.SysFont('Comic Sans MS', 40)
        self.clock = pygame.time.Clock()

        # Set arguments to class
        self.screen = screen
        self.gameState = gameState
        self.peer = peer
        self.player = player
        self.gameOver = gameOver

        self.gameStateRun = True


    def setPeer(self, newPeer):
        self.peer = newPeer

    def run(self):
        
        while self.gameStateRun:
            print(self.peer.getConnections())
            # current_time = time.time()
            # delta_time = current_time - self.last_tick_time
            # self.last_tick_time = current_time

            # if self.lockstep_enabled and delta_time < self.game_tick_rate: # Assures that the game is synced per frame
            #     time.sleep(self.game_tick_rate - delta_time)

            self.screen.fill((255,255,255))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.gameStateRun = False
                    pygame.quit()
                    exit(0)

            
            pygame.display.update()
            self.clock.tick(FPS) # FPS locked


