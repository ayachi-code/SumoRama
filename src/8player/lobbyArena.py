import pygame
import socket
import random
import threading
import json
import time

#TODO: 1. Player joint dan ziet hij zich zelf in de grote box [x]
#   2. Players worden gelaten zien op scherm wanneer joinen [x]
#   3. Players kunnen ready up doen en wordt gelocked op client [x]
#   3*. Game start sign als er 50% ready is en meer dan 4 players in de game [x]
#   4. Meerder sessions als 1 vol is. --> Player kriijgt bericht als lobby vol is []
#       Tip: Verstuur session id naar client bij handshake [-]
#   5. Player kan leaven bij lobby en werkt [-]
#   6. Gane start als 50 % ready up heeft gedaan [x]
#   7. Acks toevoegen [-]


import sys

sys.path.append("../game") # Debug
sys.path.append("../lib/") # Debug

import player
import button
import peer


SERVER_HOST = '127.0.0.1' # Rendezbvous server host
SERVER_PORT = 5378 # Rendezvous server port

FPS = 60

SCREEN_WIDTH = 1300
SCREEN_HEIGHT = 800

MAX_READY_UP = 1


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
        self.id = None

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
    def __init__(self, screen, gameState, player, arena, error):
        pygame.init()
        pygame.font.init()
        self.clock = pygame.time.Clock()    
        self.fontOfTitle = pygame.font.SysFont('Comic Sans MS', 75)

        self.fontOfTitlePlayerMain = pygame.font.SysFont('Comic Sans MS', 40)

        self.notifierReadyUp = pygame.font.SysFont('Comic Sans MS', 40)

        self.player = player

        self.sock = None
        
        self.screen = screen
        self.gameState = gameState
        self.gameStateRun = True
        self.serverAck = False
        self.arena = arena
        self.error = error

        self.readyUpCounter = None
        self.readyUpState = False
        self.readyUpColor = (226,221,220) 

        self.peersInLobby = []
        self.playerBoxes = [PlayerBox(None, self.screen,300, SCREEN_HEIGHT/3.33), PlayerBox(None, self.screen,300, SCREEN_HEIGHT/3.33 ) , PlayerBox(None, self.screen,300, SCREEN_HEIGHT/3.33 ) , PlayerBox(None, self.screen,300, SCREEN_HEIGHT/3.33 ) , PlayerBox(None, self.screen,300, SCREEN_HEIGHT/3.33 ) , PlayerBox(None, self.screen,300, SCREEN_HEIGHT/3.33 ) , PlayerBox(None, self.screen,300, SCREEN_HEIGHT/3.33 ) , PlayerBox(None, self.screen,300, SCREEN_HEIGHT/3.33 )]

    def _isPlayerInLobby(self):
        for box in self.playerBoxes:
            if box.getId() == True:
                return True
        return False 
    
    # def iAmAlive(self):
    #     while True:
    #         data, addr = sock.recvfrom(65535)
    #         data = data.decode()

    #         if "ALIVE" == data:
    #             payload = "ALIVE-OK " + str(self.random_integer)
    #             sock.sendto(payload.encode(), host_port)
    #             #print("server wants know if im alive")
    
    def listener(self):
        while True:
            data, addr = self.sock.recvfrom(65535)
            data = data.decode()

            if self.gameStateRun == False:
                break
            
            if "quit" in data:
                leavedID = data.split(" ")[1]
                self.peersInLobby.remove(int(leavedID))
                for box in self.playerBoxes:
                    if box.getId() == int(leavedID):
                        if box.getReadyUp() == True:
                            self.readyUpCounter -= 1 # Player was ready however, no not because they left
                        box.reset()
                        break
            elif "PEERS" in data:
                print(data)
                connectionInfo = data.split(" ",1)[1].split(" ")[0]
                playerinfo = data.split(" ",1)[1].split(" ")[1]

                connectionInfo = json.loads(connectionInfo)
                playerinfo = json.loads(playerinfo)

                if self.readyUpCounter == None:
                    self.readyUpCounter = 0
                    for peer in playerinfo:
                        if peer[2] == True:
                            self.readyUpCounter += 1

                counter = 0

                for peer in connectionInfo:
                    if peer[1] not in self.peersInLobby:
                        self.peersInLobby.append(peer[1])
                        for box in self.playerBoxes:
                            if box.getId() == None:
                                box.setId(peer[1])
                                box.setName(playerinfo[counter][0])
                                box.setReadyUp(playerinfo[counter][2])
                                break
                                            
                    counter += 1
                    

            if "READY" in data:
                print("Got ready up from " + data.split(" ")[1])
                readyId = int(data.split(" ")[1])
                for peer in self.playerBoxes:
                    if peer.getId() == readyId:
                        print("Readying up")
                        peer.setReadyUp(True)
                        self.readyUpCounter += 1
                
    def _convertStringToColor(self, color): #Helper function that converts string color to rgb tuple HELPER function 
        if color == "red": 
            return (255,0,0)
        elif color == "BLACK":
            return (255,255,255)
        elif color == "GREEN":
            return (0,255,0)
        elif color == "BLUE":
            return (0,0,255)
        else:
            return (0,0,0) # Default white character
        
    def listeningForAckStartUp(self):
        while True:
            data, client_socket = self.sock.recvfrom(4096)
            data = data.decode()
            print(data)
        
            if self.gameStateRun == False:
                break

            if data == "HELLO-OK":
                print("Hello from server")
                self.serverAck = True
                break
            elif data == "FULL":
                self.gameStateRun = False
                self.serverAck = True
                self.error.setErrorMessage('Lobby is full')
                self.error.setBackButtonDest('start')
                self.gameState.setCurrentState('error')
                break

    def sendForAckStartUp(self):
        upperBoundSend = 7
        while True:
            if self.serverAck or self.gameStateRun == False:
                print("Am i dead?")
                break
            if upperBoundSend == 0:
                self.gameStateRun = False
                self.error.setErrorMessage('Matchmaking server is down')
                self.error.setBackButtonDest('start')
                self.gameState.setCurrentState('error')
                break
            
            print("tst")
            payload = "HELLO-FROM " + self.player.getName() + " " + self.player.getColor()        
            self.sock.sendto(payload.encode(), self.host_port)
            time.sleep(0.1)
            upperBoundSend -= 1

    def initStates(self):

        self.gameStateRun = True
        self.serverAck = False
 
        self.readyUpCounter = None
        self.readyUpState = False
        self.readyUpColor = (226,221,220) 

        self.peersInLobby = []
        self.playerBoxes = [PlayerBox(None, self.screen,300, SCREEN_HEIGHT/3.33), PlayerBox(None, self.screen,300, SCREEN_HEIGHT/3.33 ) , PlayerBox(None, self.screen,300, SCREEN_HEIGHT/3.33 ) , PlayerBox(None, self.screen,300, SCREEN_HEIGHT/3.33 ) , PlayerBox(None, self.screen,300, SCREEN_HEIGHT/3.33 ) , PlayerBox(None, self.screen,300, SCREEN_HEIGHT/3.33 ) , PlayerBox(None, self.screen,300, SCREEN_HEIGHT/3.33 ) , PlayerBox(None, self.screen,300, SCREEN_HEIGHT/3.33 )]
        
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # SOCK_DGRAM for udp

        self.random_number = random.uniform(6000, 10000) # Random port for udp

        self.random_integer = round(self.random_number)

        self.sock.bind((SERVER_HOST, self.random_integer))

        self.host_port = (SERVER_HOST, SERVER_PORT)

            
    def run(self):
       
        self.initStates()
        
        lister = threading.Thread(target=self.listeningForAckStartUp, daemon=True)
        lister.start()

        sender = threading.Thread(target=self.sendForAckStartUp, daemon=True)
        sender.start()
        # sender.join()

        while True:    
            if self.serverAck or self.gameStateRun == False:
                break

        lister = threading.Thread(target=self.listener,args=(), daemon=True)
        lister.start()

        # iamAlive = threading.Thread(target=self.iAmAlive,args=(), daemon=True)
        # iamAlive.start()


        #payload = "HELLO-FROM " + self.player.getName() + " " + self.player.getColor()       
        
        #sock.sendto(payload.encode(), host_port)
 
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
     
            counter = 0
            for i in range(8):  # Iterate over all playerBoxes
                if i < 3:
                    x_offset = 0
                elif i < 6:
                    x_offset = 300
                else:
                    counter += 1
                    x_offset = 600

                if counter == 2:
                    break
                self.playerBoxes[i].draw(x_offset + 400, (SCREEN_HEIGHT/10) + (i % 3) * SCREEN_HEIGHT/3.33)


            if self.readyUpState == True: # Lock ready up
                self.readyUpColor = (128,128,128)
                
            readyUp = button.Button(self.readyUpColor ,0,SCREEN_HEIGHT/10 + 575 ,400,150,60,'Ready up')

            readyUp.draw(self.screen, (0,0,0))

            # Status
            if self.readyUpCounter == None:
                gameScreen_surfaceLobbyTitle = self.notifierReadyUp.render('No players :(', True, (255, 255, 255))
            else:
                gameScreen_surfaceLobbyTitle = self.notifierReadyUp.render('Ready up: ' + str((4-self.readyUpCounter))  +' left', True, (255, 255, 255))


            gameScreen_rectLobbyTitle = gameScreen_surfaceLobbyTitle.get_rect(center=(150, SCREEN_HEIGHT/10 + 450))
            self.screen.blit(gameScreen_surfaceLobbyTitle, gameScreen_rectLobbyTitle)

            if self.readyUpCounter == MAX_READY_UP:
                self.gameStateRun = False
                myPeer = peer.Peer('127.0.0.1',  self.random_integer) # Creates peer object
                myPeer.setSocket(self.sock)

                for port in self.peersInLobby:
                    myPeer.addCoonection(('127.0.0.1', port))
                
                self.arena.setPeer(myPeer)
                self.gameState.setCurrentState('playerArena')

                self.sock.sendto("RESET".encode(), (self.host_port))
                print(myPeer.getConnections())
                print("STARTING ARENA!!")
                continue     

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.gameStateRun = False
                    payload = "quit " + str(self.random_integer) 
                    self.sock.sendto(payload.encode(), (self.host_port))
                    pygame.quit()
                    exit(0)
                if event.type == pygame.MOUSEBUTTONUP:
                    pos = pygame.mouse.get_pos()
                    if readyUp.isOver(pos) and self.readyUpState != True and self.readyUpCounter != None:
                        print("Ready up") 
                        self.readyUpState = True
                        self.readyUpCounter += 1
                        payload = "READY-UP " + str(self.random_integer) 
                        self.sock.sendto(payload.encode(), (self.host_port))

            pygame.display.update()
            self.clock.tick(FPS)  # Limit to 60 FPS
