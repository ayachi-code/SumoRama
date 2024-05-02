import pygame
import socket
import random
import threading
import json

import sys
sys.path.append("../game") # Debug
import player

SERVER_HOST = '127.0.0.1' # Rendezbvous server host
SERVER_PORT = 5378 # Rendezvous server port

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # SOCK_DGRAM for udp

random_number = random.uniform(6000, 10000) # Random port for udp

random_integer = round(random_number)

sock.bind((SERVER_HOST, random_integer))

host_port = (SERVER_HOST, SERVER_PORT)

print(random_integer)

FPS = 60

SCREEN_WIDTH = 1300
SCREEN_HEIGHT = 800


class PlayerBox:
    def __init__(self, name, readyUp, screen):
        self.name = name
        self.readyUp = readyUp
        self.screen = screen
        
        self.fontOfTitle = pygame.font.SysFont('Comic Sans MS', 30)

        
        # Sizes of the box
        self.height = SCREEN_HEIGHT/3.33
        self.width = 300

    def reset(self):
        self.name = None
        self.readyUp = None

    def draw(self, x,y):
        pygame.draw.rect(self.screen, (255,255,255), pygame.Rect(x, y, self.width, self.height),  2)
        pygame.draw.rect(self.screen, (255,255,255), pygame.Rect(x, (y+self.height)-50, self.width, 50),  2)
        
        gameScreen_surfaceLobbyTitle = self.fontOfTitle.render('player1000', True, (255, 255, 255))
        gameScreen_rectLobbyTitle = gameScreen_surfaceLobbyTitle.get_rect(center=(x+self.width/2,(y+self.height)-25))
        self.screen.blit(gameScreen_surfaceLobbyTitle, gameScreen_rectLobbyTitle)

        pygame.draw.circle(self.screen, (255,0,0),(x+self.width/2, y+(self.height/2)),40)

        pygame.draw.rect(self.screen, (0,200,0), pygame.Rect(x, y, self.width/4, 50))
        pygame.draw.rect(self.screen, (0,0,0), pygame.Rect(x, y, self.width/4, 52), 2)


class LobbyArena:
    def __init__(self, screen, gameState, player):
        pygame.init()
        pygame.font.init()
        self.clock = pygame.time.Clock()    
        self.fontOfTitle = pygame.font.SysFont('Comic Sans MS', 75)

        self.player = player
        
        self.screen = screen
        self.gameState = gameState
        self.gameStateRun = True

        self.peersInLobby = []

    def listener(self):
        while True:
            data, addr = sock.recvfrom(65535)
            data = data.decode()
            if "PEERS" in data:
                self.peersInLobby = json.loads(data.split(" ",1)[1])
                print(self.peersInLobby)

    def run(self):
        payload = "HELLO-FROM " + self.player.getName() + " " + self.player.getColor()        
        sock.sendto(payload.encode(), host_port)

        lister = threading.Thread(target=self.listener,args=(), daemon=True)
        lister.start()

        player = PlayerBox("Bilal", None, self.screen)

        while self.gameStateRun:
            self.screen.fill((153,0,17))

            pygame.draw.rect(self.screen, (255,255,255), pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT/10),  2)


            gameScreen_surfaceLobbyTitle = self.fontOfTitle.render('Lobby', True, (255, 255, 255))
            gameScreen_rectLobbyTitle = gameScreen_surfaceLobbyTitle.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/17))
            self.screen.blit(gameScreen_surfaceLobbyTitle, gameScreen_rectLobbyTitle)

            for i in range(0,3): # Prints the boxes on the screen
                player.draw(0, (SCREEN_HEIGHT/10) + i * SCREEN_HEIGHT/3.33)
                player.draw(300,(SCREEN_HEIGHT/10) + i * SCREEN_HEIGHT/3.33)
                if i != 2:
                    player.draw(600,(SCREEN_HEIGHT/10) + i * SCREEN_HEIGHT/3.33)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.gameStateRun = False
            

            pygame.display.update()
            self.clock.tick(FPS)  # Limit to 60 FPS
            

if __name__ == "__main__":
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))  # Set display resolution
    game = LobbyArena(screen, None, player.Player("Player69", "RED"))
    game.run()
