import pygame
import socket
import random
import threading
import json

#TODO: 1. Player joint dan ziet hij zich zelf in de grote box
#   2. Players worden gelaten zien op scherm wanneer joinen
#   3. Players kunnen ready up doen en wordt gelocked op client
#   4. Meerder sessions als 1 vol is.
#       Tip: Verstuur session id naar client bij handshake
#   5. Player kan leaven bij lobby en werkt
#   6. Gane start als 50 % ready up heeft gedaan


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
    def __init__(self, name, readyUp, screen, width, height):
        self.name = name
        self.readyUp = readyUp
        self.screen = screen
        
        self.fontOfTitle = pygame.font.SysFont('Comic Sans MS', 30)

        
        # Sizes of the box
        self.width = width
        self.height = height

        #self.height = SCREEN_HEIGHT/3.33
        #self.width = 300

    def reset(self):
        self.name = None
        self.readyUp = None

    def draw(self, x,y):
        pygame.draw.rect(self.screen, (255,255,255), pygame.Rect(x, y, self.width, self.height),  2)
        pygame.draw.rect(self.screen, (255,255,255), pygame.Rect(x, (y+self.height)-50, self.width, 50),  2)
        
        if self.name != None:
            gameScreen_surfaceLobbyTitle = self.fontOfTitle.render('player1000', True, (255, 255, 255))
            gameScreen_rectLobbyTitle = gameScreen_surfaceLobbyTitle.get_rect(center=(x+self.width/2,(y+self.height)-25))
            self.screen.blit(gameScreen_surfaceLobbyTitle, gameScreen_rectLobbyTitle)

            pygame.draw.circle(self.screen, (255,0,0),(x+self.width/2, y+(self.height/2)),40)

            pygame.draw.rect(self.screen, (255,0,0), pygame.Rect(x, y, self.width/4, 50))
            pygame.draw.rect(self.screen, (0,0,0), pygame.Rect(x, y, self.width/4, 52), 2)


class LobbyArena:
    def __init__(self, screen, gameState, player):
        pygame.init()
        pygame.font.init()
        self.clock = pygame.time.Clock()    
        self.fontOfTitle = pygame.font.SysFont('Comic Sans MS', 75)

        self.fontOfTitlePlayerMain = pygame.font.SysFont('Comic Sans MS', 40)

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
        
        player = PlayerBox("a", None, self.screen,300, SCREEN_HEIGHT/3.33)

        while self.gameStateRun:
            self.screen.fill((153,0,17))

            pygame.draw.rect(self.screen, (255,255,255), pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT/10),  2)

            gameScreen_surfaceLobbyTitle = self.fontOfTitle.render('Lobby', True, (255, 255, 255))
            gameScreen_rectLobbyTitle = gameScreen_surfaceLobbyTitle.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/17))
            self.screen.blit(gameScreen_surfaceLobbyTitle, gameScreen_rectLobbyTitle)

            # The player bigger box
            pygame.draw.rect(self.screen, (255,255,255), pygame.Rect(0, SCREEN_HEIGHT/10, 400, 350),  2)
            pygame.draw.rect(self.screen, (255,255,255), pygame.Rect(0, (SCREEN_HEIGHT/10+350)-50, 400, 50),  2)
            
            gameScreen_surfaceLobbyTitle = self.fontOfTitlePlayerMain.render('player1000', True, (255, 255, 255))
            gameScreen_rectLobbyTitle = gameScreen_surfaceLobbyTitle.get_rect(center=(400/2,SCREEN_HEIGHT/10 + 325))
            self.screen.blit(gameScreen_surfaceLobbyTitle, gameScreen_rectLobbyTitle)

            pygame.draw.circle(self.screen, (255,0,0),(400/2, +(450/2)),70)

            pygame.draw.rect(self.screen, (255,0,0), pygame.Rect(0, SCREEN_HEIGHT/10, 350/4, 50))
            pygame.draw.rect(self.screen, (0,0,0), pygame.Rect(0, SCREEN_HEIGHT/10, 350/4, 52), 2)

            # Other peers
            for i in range(0,3): # Prints the boxes on the screen
                player.draw(0+400, (SCREEN_HEIGHT/10) + i * SCREEN_HEIGHT/3.33)
                player.draw(300+400,(SCREEN_HEIGHT/10) + i * SCREEN_HEIGHT/3.33)
                if i == 0:
                    player.draw(600+400,(SCREEN_HEIGHT/10) + i * SCREEN_HEIGHT/3.33)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.gameStateRun = False
            

            pygame.display.update()
            self.clock.tick(FPS)  # Limit to 60 FPS
            

if __name__ == "__main__":
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))  # Set display resolution
    game = LobbyArena(screen, None, player.Player("Player69", "RED"))
    game.run()
