import socket
import threading
import pygame
import time
import random

FPS = 60

SCREEN_WIDTH = 1300
SCREEN_HEIGHT = 800

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

    
    def displayCountdown(self): # Shows a counter before starting the game, preps player to be ready
        countdown_font = pygame.font.SysFont('Comic Sans MS', 150)
        
        tip_font = pygame.font.SysFont('Comic Sans MS', 50)

        gameStartIn_font = pygame.font.SysFont('Comic Sans MS', 140)

        tips = ["Camping is not a good strategy since the circle shrinks","Losing a lot of games in a row? Take a break!", "With the rushing ability comes great responsibility.", "Use WASD keys to move around the map", "With the space key you can rush against players", "Press space to rush against other players!"]

        nextTip = 0

        currentTip = random.choice(tips)

        for i in range(5, 0, -1):
            self.screen.fill((153,0,17))

            gameScreen_surface = countdown_font.render('Sumo Rama', True, (255, 255, 255))
            gameScreen_rect = gameScreen_surface.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/10))
            self.screen.blit(gameScreen_surface, gameScreen_rect)

            gameScreen_surface = gameStartIn_font.render('Game starts in ', True, (255, 255, 255))
            gameScreen_rect = gameScreen_surface.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/3))
            self.screen.blit(gameScreen_surface, gameScreen_rect)

            countdown_text = countdown_font.render(str(i), True, (255, 255, 255))
            text_rect = countdown_text.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 1.75))
            self.screen.blit(countdown_text, text_rect)

            pygame.draw.rect(self.screen, (255,255,255), pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT - (SCREEN_HEIGHT/4)),  4)

            if nextTip % 2 == 0:
                currentTip = random.choice(tips)

            countdown_text = tip_font.render("Tip: " + currentTip, True, (255, 255, 255))
            text_rect = countdown_text.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT // 1.15))
            self.screen.blit(countdown_text, text_rect)

            nextTip += 1
            pygame.display.update()
            pygame.time.wait(1000)


    def run(self):
        

        self.displayCountdown() # Displays a countdown with some very usefull tips!

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


