import pygame
import socket
import random
import threading
import json

#TODO: 1. Player joint dan ziet hij zich zelf in de grote box [x]
#   2. Players worden gelaten zien op scherm wanneer joinen [x]
#   3. Players kunnen ready up doen en wordt gelocked op client [x]
#   3*. Game start sign als er 50% ready is en meer dan 4 players in de game
#   4. Meerder sessions als 1 vol is.
#       Tip: Verstuur session id naar client bij handshake
#   5. Player kan leaven bij lobby en werkt
#   6. Gane start als 50 % ready up heeft gedaan


import sys
sys.path.append("../game") # Debug
sys.path.append("../lib/") # Debug

import player
import button


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
    def __init__(self, name, screen, width, height):
        self.name = name
        self.screen = screen
        
        self.fontOfTitle = pygame.font.SysFont('Comic Sans MS', 30)

        self.id = None # Unique id to identify a box
        self.readyUp = False

        # Sizes of the box
        self.width = width
        self.height = height

        #self.height = SCREEN_HEIGHT/3.33
        #self.width = 300

    def getId(self):
        return self.id
    
    def setId(self, newId):
        self.id = newId

    def getName(self):
        return self.name
    
    def setName(self, newName):
        self.name = newName

    def setReadyUp(self, state):
        self.readyUp = state

    def getReadyUp(self):
        return self.readyUp

    def reset(self):
        self.name = None
        self.readyUp = False

    def draw(self, x,y):
        pygame.draw.rect(self.screen, (255,255,255), pygame.Rect(x, y, self.width, self.height),  2)
        pygame.draw.rect(self.screen, (255,255,255), pygame.Rect(x, (y+self.height)-50, self.width, 50),  2)
        
        if self.name != None:
            gameScreen_surfaceLobbyTitle = self.fontOfTitle.render(self.name, True, (255, 255, 255))
            gameScreen_rectLobbyTitle = gameScreen_surfaceLobbyTitle.get_rect(center=(x+self.width/2,(y+self.height)-25))
            self.screen.blit(gameScreen_surfaceLobbyTitle, gameScreen_rectLobbyTitle)

            pygame.draw.circle(self.screen, (255,0,0),(x+self.width/2, y+(self.height/2)),40)

            if self.readyUp == False:
                pygame.draw.rect(self.screen, (255,0,0), pygame.Rect(x, y, self.width/4, 50))
            elif self.readyUp == True:
                pygame.draw.rect(self.screen, (0,255,0), pygame.Rect(x, y, self.width/4, 50))

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

        self.readyUpState = False
        self.readyUpColor = (226,221,220) 

        self.peersInLobby = []
        self.playerBoxes = [PlayerBox(None, self.screen,300, SCREEN_HEIGHT/3.33), PlayerBox(None, self.screen,300, SCREEN_HEIGHT/3.33 ) , PlayerBox(None, self.screen,300, SCREEN_HEIGHT/3.33 ) , PlayerBox(None, self.screen,300, SCREEN_HEIGHT/3.33 ) , PlayerBox(None, self.screen,300, SCREEN_HEIGHT/3.33 ) , PlayerBox(None, self.screen,300, SCREEN_HEIGHT/3.33 ) , PlayerBox(None, self.screen,300, SCREEN_HEIGHT/3.33 ) , PlayerBox(None, self.screen,300, SCREEN_HEIGHT/3.33 )]

    def _isPlayerInLobby(self):
        for box in self.playerBoxes:
            if box.getId() == True:
                return True
        return False 
    
    def listener(self):
        while True:
            data, addr = sock.recvfrom(65535)
            data = data.decode()
            if "PEERS" in data:
                peerInformation = json.loads(data.split(" ",1)[1])
                for peer in peerInformation:
                    if peer[0][1] not in self.peersInLobby:
                        #print(peer)
                        self.peersInLobby.append(peer[0][1])
                        for box in self.playerBoxes:
                            if box.getId() == None:
                                box.setId(peer[0][1])
                                box.setName(peer[1][0])
                                break
            if "READY" in data:
                print("Got ready up from " + data.split(" ")[1])
                readyId = int(data.split(" ")[1])
                for peer in self.playerBoxes:
                    if peer.getId() == readyId:
                        print("Readying up")
                        peer.setReadyUp(True)
                
    def _convertStringToColor(self, color): #Helper function that converts string color to rgb tuple HELPER function 
        if color == "RED": 
            return (255,0,0)
        elif color == "BLACK":
            return (255,255,255)
        elif color == "GREEN":
            return (0,255,0)
        elif color == "BLUE":
            return (0,0,255)
        else:
            return (0,0,0) # Default white character

    def run(self):
        payload = "HELLO-FROM " + self.player.getName() + " " + self.player.getColor()        
        sock.sendto(payload.encode(), host_port)

        lister = threading.Thread(target=self.listener,args=(), daemon=True)
        lister.start()
        
        #player = PlayerBox("a", None, self.screen,300, SCREEN_HEIGHT/3.33)

        while self.gameStateRun:
            self.screen.fill((153,0,17))

            pygame.draw.rect(self.screen, (255,255,255), pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT/10),  2)

            gameScreen_surfaceLobbyTitle = self.fontOfTitle.render('Lobby', True, (255, 255, 255))
            gameScreen_rectLobbyTitle = gameScreen_surfaceLobbyTitle.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/17))
            self.screen.blit(gameScreen_surfaceLobbyTitle, gameScreen_rectLobbyTitle)

            # The player bigger box
            pygame.draw.rect(self.screen, (255,255,255), pygame.Rect(0, SCREEN_HEIGHT/10, 400, 350),  2)
            pygame.draw.rect(self.screen, (255,255,255), pygame.Rect(0, (SCREEN_HEIGHT/10+350)-50, 400, 50),  2)
            
            gameScreen_surfaceLobbyTitle = self.fontOfTitlePlayerMain.render(self.player.getName(), True, (255, 255, 255))
            gameScreen_rectLobbyTitle = gameScreen_surfaceLobbyTitle.get_rect(center=(400/2,SCREEN_HEIGHT/10 + 325))
            self.screen.blit(gameScreen_surfaceLobbyTitle, gameScreen_rectLobbyTitle)

            pygame.draw.circle(self.screen, self._convertStringToColor(self.player.getColor()),(400/2, +(450/2)),70)

            if self.readyUpState == True:
                pygame.draw.rect(self.screen, (0,255,0), pygame.Rect(0, SCREEN_HEIGHT/10, 350/4, 50))
            else:
                pygame.draw.rect(self.screen, (255,0,0), pygame.Rect(0, SCREEN_HEIGHT/10, 350/4, 50))

            pygame.draw.rect(self.screen, (0,0,0), pygame.Rect(0, SCREEN_HEIGHT/10, 350/4, 52), 2)
     
            for i in range(8):  # Iterate over all playerBoxes
                if i < 3:
                    x_offset = 0
                elif i < 6:
                    x_offset = 300
                else:
                    x_offset = 600
                self.playerBoxes[i].draw(x_offset + 400, (SCREEN_HEIGHT/10) + (i % 3) * SCREEN_HEIGHT/3.33)


            if self.readyUpState == True: # Lock ready up
                self.readyUpColor = (128,128,128)
                
            readyUp = button.Button(self.readyUpColor ,0,SCREEN_HEIGHT/10 + 575 ,400,150,60,'Ready up')

            readyUp.draw(self.screen, (0,0,0))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.gameStateRun = False
                if event.type == pygame.MOUSEBUTTONUP:
                    pos = pygame.mouse.get_pos()
                    if readyUp.isOver(pos):
                        print("Ready up")
                        self.readyUpState = True
                        # Notify other peers trough rendezvous protocol
                        payload = "READY-UP " + str(random_integer) 
                        sock.sendto(payload.encode(), (host_port))
            
            pygame.display.update()
            self.clock.tick(FPS)  # Limit to 60 FPS
            

if __name__ == "__main__":
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))  # Set display resolution
    game = LobbyArena(screen, None, player.Player("Player69", "RED"))
    game.run()
