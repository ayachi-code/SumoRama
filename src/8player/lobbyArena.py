import pygame
import socket
import random
import threading
import json
import time

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

MAX_READY_UP = 1 # Number of players that haev to readt up to start a game


class PlayerBox: # The box in the lobby
    def __init__(self, name, screen, width, height):
        self.name = name
        self.screen = screen

        self.color = (255,0,0)
        
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


    def setColor(self, color):
        self.color = color

    def setReadyUp(self, state):
        self.readyUp = state

    def getReadyUp(self):
        return self.readyUp

    def reset(self):
        self.name = None
        self.id = None
        self.readyUp = False

    def draw(self, x,y): 
        pygame.draw.rect(self.screen, (255,255,255), pygame.Rect(x, y, self.width, self.height),  2)
        pygame.draw.rect(self.screen, (255,255,255), pygame.Rect(x, (y+self.height)-50, self.width, 50),  2)
        
        if self.name != None:
            # Draws the box with the info e.g name, player
            gameScreen_surfaceLobbyTitle = self.fontOfTitle.render(self.name, True, (255, 255, 255))
            gameScreen_rectLobbyTitle = gameScreen_surfaceLobbyTitle.get_rect(center=(x+self.width/2,(y+self.height)-25))
            self.screen.blit(gameScreen_surfaceLobbyTitle, gameScreen_rectLobbyTitle)

            pygame.draw.circle(self.screen, self.color,(x+self.width/2, y+(self.height/2)),40)

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
    

        self.selectorImg = pygame.image.load("../assets/selector.png").convert_alpha() # Load image transparent
        self.selectorImg = pygame.transform.scale(self.selectorImg, (100,100)) # Rescales imaeg


        
        self.selectorImgFlipped = pygame.image.load("../assets/selectorFlipped.png").convert_alpha() # Load image transparent
        self.selectorImgFlipped = pygame.transform.scale(self.selectorImgFlipped, (100,100)) # Rescales imaeg

        self.colors = ["RED","BLUE","GREEN","YELLOW", "BLACK"]
        self.currentColor = 0 # Points to the index of the current color that the user is using
        self.confirmedColor = 0


    def rightSelectorClicked(self, pos): #            self.screen.blit(self.selectorImg, (275, (450/2 - 40))) # Right 
        selector_x = 275
        selector_y = (450/2) - 40
        selector_width = self.selectorImg.get_width()
        selector_height = self.selectorImg.get_height()
        return selector_x <= pos[0] <= selector_x + selector_width and selector_y <= pos[1] <= selector_y + selector_height

    def leftSelectorClicked(self, pos): #            self.screen.blit(self.selectorImgFlipped, (25, (450/2 - 40))) # Left
        selector_x = 25
        selector_y = (450/2 - 40)
        selector_width = self.selectorImgFlipped.get_width()
        selector_height = self.selectorImgFlipped.get_height()
        return selector_x <= pos[0] <= selector_x + selector_width and selector_y <= pos[1] <= selector_y + selector_height


    def listener(self):
        while True:
            data, addr = self.sock.recvfrom(65535)
            data = data.decode()

            if self.gameStateRun == False:
                break


            if data.split(" ")[0] == "COLOR":
                color = data.split(" ")[1]
                peerID = data.split(" ")[2]
                for player in self.playerBoxes:
                    if str(player.getId()) == str(peerID):
                        player.setColor(self.convertStringToColor(color))

            
            if "quit" in data: # handeling quits
                leavedID = data.split(" ")[1]
                self.peersInLobby.remove(int(leavedID)) # removes it from peer list
                for box in self.playerBoxes: # removes it from the box
                    if box.getId() == int(leavedID):
                        if box.getReadyUp() == True:
                            self.readyUpCounter -= 1 # Player was ready however, no not because they left
                        box.reset()
                        break
            elif "PEERS" in data: # Peers response with info about all other peers
                # Send updated color to all peers
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

                for peer in connectionInfo: # Sets the peer in the box
                    if peer[1] not in self.peersInLobby:
                        self.peersInLobby.append(peer[1])
                        for box in self.playerBoxes:
                            if box.getId() == None:
                                box.setId(peer[1])
                                box.setName(playerinfo[counter][0])
                                box.setReadyUp(playerinfo[counter][2])
                                break
                                            
                    counter += 1
                
                # send color to all peers
                for player in self.peersInLobby:
                    payload = "COLOR " + self.player.getColor() +  " " + str(self.random_integer)
                    print(payload)
                    self.sock.sendto(payload.encode(), ('127.0.0.1', int(player)))
                    
            if "READY" in data:
                print("Got ready up from " + data.split(" ")[1])
                readyId = int(data.split(" ")[1])
                for peer in self.playerBoxes:
                    if peer.getId() == readyId:
                        print("Readying up")
                        peer.setReadyUp(True)
                        self.readyUpCounter += 1
                        
    def listeningForAckStartUp(self):
        while True:
            data, client_socket = self.sock.recvfrom(4096)
            data = data.decode()
        
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
                break
            if upperBoundSend == 0:
                self.gameStateRun = False
                self.error.setErrorMessage('Matchmaking server is down')
                self.error.setBackButtonDest('start')
                self.gameState.setCurrentState('error')
                break
            
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

    def convertStringToColor(self, color):         # Helper function that converts string color to rgb tuple
        if color == "RED":
            return (255, 0, 0)
        elif color == "BLACK":
            return (0, 0, 0)
        elif color == "GREEN":
            return (0, 255, 0)
        elif color == "BLUE":
            return (0, 0, 255)
        elif color == "YELLOW":
            return (255, 255, 0)
        else:
            return (255, 255, 255)  # Default white characte

    def run(self):
       
        self.initStates()
        
        lister = threading.Thread(target=self.listeningForAckStartUp, daemon=True)
        lister.start()

        sender = threading.Thread(target=self.sendForAckStartUp, daemon=True)
        sender.start()

        while True:    
            if self.serverAck or self.gameStateRun == False:
                break

        lister = threading.Thread(target=self.listener,args=(), daemon=True)
        lister.start()

        while self.gameStateRun:
            self.screen.fill((153,0,17))

            pygame.draw.rect(self.screen, (255,255,255), pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT/10),  2)

            gameScreen_surfaceLobbyTitle = self.fontOfTitle.render('Lobby', True, (255, 255, 255))
            gameScreen_rectLobbyTitle = gameScreen_surfaceLobbyTitle.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/17))
            self.screen.blit(gameScreen_surfaceLobbyTitle, gameScreen_rectLobbyTitle)

            # player wins
            gameScreen_surfaceLobbyTitle = self.fontOfTitlePlayerMain.render('Wins: ' + str(self.player.getWins()), True, (255, 255, 255))
            gameScreen_rectLobbyTitle = gameScreen_surfaceLobbyTitle.get_rect(center=(400/2,SCREEN_HEIGHT/10 + 30))
            self.screen.blit(gameScreen_surfaceLobbyTitle, gameScreen_rectLobbyTitle)

            # The player bigger box
            pygame.draw.rect(self.screen, (255,255,255), pygame.Rect(0, SCREEN_HEIGHT/10, 400, 350),  2)
            pygame.draw.rect(self.screen, (255,255,255), pygame.Rect(0, (SCREEN_HEIGHT/10+350)-50, 400, 50),  2)
            
            gameScreen_surfaceLobbyTitle = self.fontOfTitlePlayerMain.render(self.player.getName(), True, (255, 255, 255))
            gameScreen_rectLobbyTitle = gameScreen_surfaceLobbyTitle.get_rect(center=(400/2,SCREEN_HEIGHT/10 + 325))
            self.screen.blit(gameScreen_surfaceLobbyTitle, gameScreen_rectLobbyTitle)
            
            # The player
            pygame.draw.circle(self.screen, self.convertStringToColor(self.colors[self.currentColor]),(400/2, +(450/2)),70)

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



            #Color Selector
            self.screen.blit(self.selectorImg, (275, (450/2 - 40))) # Right
            self.screen.blit(self.selectorImgFlipped, (25, (450/2 - 40))) # Left

            
            # Confirm color
            confirm = button.Button((255,255,255),138,(450/2) + 100,120,30,40,'Confirm') # The leave button
            confirm.draw(self.screen, (0,0,0))

            # Color indicator
            pygame.draw.circle(self.screen, self.convertStringToColor(self.colors[self.confirmedColor]), (360, 117),30)


            # Status
            if self.readyUpCounter == None:
                gameScreen_surfaceLobbyTitle = self.notifierReadyUp.render('No players :(', True, (255, 255, 255))
                self.readyUpColor = (128,128,128)
            else:
                gameScreen_surfaceLobbyTitle = self.notifierReadyUp.render('Ready up: ' + str((4-self.readyUpCounter))  +' left', True, (255, 255, 255))
                self.readyUpColor = (226,221,220) 


            leave = button.Button((255,255,255),5,45,80,30,40,'Leave') # The leave button
            leave.draw(self.screen, (0,0,0))


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
                        self.readyUpState = True
                        self.readyUpCounter += 1
                        payload = "READY-UP " + str(self.random_integer) 
                        self.sock.sendto(payload.encode(), (self.host_port))
                    elif leave.isOver(pos):
                        self.gameStateRun = False
                        payload = "quit " + str(self.random_integer) 
                        self.sock.sendto(payload.encode(), (self.host_port))
                        self.gameState.setCurrentState('start')
                    elif self.rightSelectorClicked(pos):
                            self.currentColor += 1
                            self.currentColor = self.currentColor % 5 # Makes sure we do not get out of index range
                            if self.colors[self.currentColor] == "BLACK" and self.player.getWins() <= 3: # Player needs 4 wins to unlock the secret skin
                                self.currentColor += 1
                                self.currentColor = self.currentColor % 5

                            self.colors[self.currentColor]
                    elif self.leftSelectorClicked(pos):
                            self.currentColor -= 1
                            self.currentColor = self.currentColor % 5
                            if self.colors[self.currentColor] == "BLACK" and self.player.getWins() <= 3:
                                self.currentColor -= 1
                                self.currentColor = self.currentColor % 5

                            self.colors[self.currentColor]
                    elif confirm.isOver(pos):
                        self.confirmedColor = self.currentColor
                        self.player.setColor(self.colors[self.currentColor])
                        payload = "COLOR " + self.colors[self.currentColor] + " " + str(self.random_integer)
                        for player in self.peersInLobby:
                            self.sock.sendto(payload.encode(), ('127.0.0.1', int(player)))


            pygame.display.update()
            self.clock.tick(FPS)  # Limit to 60 FPS