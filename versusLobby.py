import pygame
import button
import socket
import random
import peer
import threading
import pickle
import base64
import time

FPS = 60

SCREEN_WIDTH = 1300
SCREEN_HEIGHT = 800

BUTTONSIZETEXT = 100

#TODO make lobby

class VersusLobby:
    def __init__(self, screen, gameState, peerIP, player):
        pygame.init()
        pygame.font.init()

        self.clock = pygame.time.Clock()
        self.screen = screen
        self.fontOfTitle = pygame.font.SysFont('Comic Sans MS', 75)

        self.gameStateRun = True
        self.gameState = gameState
        self.peerIP = peerIP
        self.player = player

        self.port = None
        self.peer = None

        self.peerName = ""
        self.peerColor = (255,255,255)


        self.readyUpAcknowledged = None
        self.readyUp = [] # If size is 2 than start
        self.pressedReadyUpButton = False
        self.peerPressedReadyUp = False

    def setPeerIP(self, ip):
        self.peerIP = ip
    def setPeerPort(self, port):
        self.port = port

    def listenForConnections(self):
        while True:
            data, addr = self.peer.getSocket().recvfrom(1024)
            data = data.decode()
            print(data)
            if "HELLO" in data: # Send handshake back :)
                self.peer.getSocket().sendto("Hi".encode(), addr)
            elif "CONNECT" in data and addr not in self.peer.getConnections(): 
                self.peer.addCoonection(addr)
                self.peerName = data.split(" ")[1] # Peername
                self.peerColor = data.split(" ")[2] # Peer color
                payload = "CONNECT " + self.player.getName() + " " + self.player.getColor() 
                self.peer.getSocket().sendto(payload.encode(), addr)
            elif data == "READY":
                self.peerPressedReadyUp = True
                self.peer.getSocket().sendto("READY-YES".encode(), addr)
                if addr not in self.readyUp:
                    print("My friend readys up okay, first time add to list")
                    self.readyUp.append(addr)
            elif data == "READY-YES":
                self.readyUpAcknowledged = True
            elif "SEND":
                pass

    def sendReadyUpToPeer(self, destination):
        maxSendToPeer = 20
        while True:
            if maxSendToPeer <= 0:
                self.readyUpAcknowledged = False
                break

            if self.readyUpAcknowledged == True:
                break

            self.peer.getSocket().sendto("READY",destination)
            time.sleep(0.5)
            maxSendToPeer -= 1

    def convertStringToColor(self, color): #Helper function that converts string color to rgb tuple
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
        #print("IP " + self.peerIP)
        #print("Port " + str(self.port))
        self.peer = peer.Peer('127.0.0.1',  random.randint(6000, 8080)) # Creates peer object
        self.peer.start()

        print(self.peer.getPort())

        receive_thread = threading.Thread(target=self.listenForConnections)
        receive_thread.start()

        if self.peerIP != None: # Joiner
            # self.peer.addCoonection((self.peerIP, self.port)) # Joiner knows host
            #print(self.player.getColor())
            payload = "CONNECT " + self.player.getName() + " " + self.player.getColor()
            #payload = pickle.dumps("CONNECT") + playerAsString # playerAsString
            self.peer.getSocket().sendto(payload.encode(), (self.peerIP, self.port)) # Joiner wants to introduce them self to host
   
        while self.gameStateRun:
            if len(self.readyUp) == 2:
                print("Starting game")
            
            self.screen.fill((153,0,17))
            pygame.draw.rect(self.screen, (255,255,255), pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT/10),  2)
  
            gameScreen_surfaceLobbyTitle = self.fontOfTitle.render('Lobby', True, (255, 255, 255))
            gameScreen_rectLobbyTitle = gameScreen_surfaceLobbyTitle.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/17))
            self.screen.blit(gameScreen_surfaceLobbyTitle, gameScreen_rectLobbyTitle)

            pygame.draw.rect(self.screen, (255,255,255), pygame.Rect(0, SCREEN_HEIGHT/10, SCREEN_WIDTH/2, SCREEN_HEIGHT),  2)

            pygame.draw.rect(self.screen, (255,255,255), pygame.Rect(0, SCREEN_HEIGHT/10, SCREEN_WIDTH/2, SCREEN_HEIGHT/8),  2) # Name box for host
            pygame.draw.rect(self.screen, (255,255,255), pygame.Rect(SCREEN_WIDTH/2, SCREEN_HEIGHT/10, SCREEN_WIDTH/2, SCREEN_HEIGHT/8),  2) # Name box for joined player


            pygame.draw.rect(self.screen, (255,255,255), pygame.Rect(0, SCREEN_HEIGHT - (SCREEN_HEIGHT*0.2), SCREEN_WIDTH/2, SCREEN_HEIGHT/5),  2) #  box for Ready up Host
            pygame.draw.rect(self.screen, (255,255,255), pygame.Rect(SCREEN_WIDTH/2, SCREEN_HEIGHT - (SCREEN_HEIGHT*0.2), SCREEN_WIDTH/2, SCREEN_HEIGHT/5),  2) #  box for Ready up Host


            # Player color
            pygame.draw.circle(self.screen, self.player.getColor(), (SCREEN_WIDTH/4, SCREEN_HEIGHT/2),100)
            

            if self.peerName != "": # Show player circle if connected
                pygame.draw.circle(self.screen, self.peerColor, (SCREEN_WIDTH - SCREEN_WIDTH/4, SCREEN_HEIGHT/2),100)


                if self.peerPressedReadyUp:
                    gameScreen_surfaceLobbyTitle = self.fontOfTitle.render('Ready', True, (255, 255, 255))
                else:
                    gameScreen_surfaceLobbyTitle = self.fontOfTitle.render('Not ready', True, (255, 255, 255))
                gameScreen_rectLobbyTitle = gameScreen_surfaceLobbyTitle.get_rect(center=(SCREEN_WIDTH - SCREEN_WIDTH/4,SCREEN_WIDTH/1.8))
                self.screen.blit(gameScreen_surfaceLobbyTitle, gameScreen_rectLobbyTitle)

                if self.pressedReadyUpButton == True:
                    readyUpHost = button.Button((128,128,128),0, SCREEN_HEIGHT - (SCREEN_HEIGHT*0.2),SCREEN_WIDTH/2,SCREEN_HEIGHT/5,BUTTONSIZETEXT,'Ready') # Ready up button is shown gray if there is no player joined
                else:
                    readyUpHost = button.Button((255,255,255),0, SCREEN_HEIGHT - (SCREEN_HEIGHT*0.2),SCREEN_WIDTH/2,SCREEN_HEIGHT/5,BUTTONSIZETEXT,'Ready') # Ready up button is shown gray if there is no player joined
            else:
                readyUpHost = button.Button((128,128,128),0, SCREEN_HEIGHT - (SCREEN_HEIGHT*0.2),SCREEN_WIDTH/2,SCREEN_HEIGHT/5,BUTTONSIZETEXT,'Ready') # Ready up button is shown gray if there is no player joined

            # Other player perspective of lobby
            gameScreen_surfaceLobbyTitle = self.fontOfTitle.render(self.peerName, True, (255, 255, 255))
            gameScreen_rectLobbyTitle = gameScreen_surfaceLobbyTitle.get_rect(center=(SCREEN_WIDTH/1.5, SCREEN_HEIGHT/6))
            self.screen.blit(gameScreen_surfaceLobbyTitle, gameScreen_rectLobbyTitle)

            # Current player
            gameScreen_surfaceLobbyTitle = self.fontOfTitle.render(self.player.getName(), True, (255, 255, 255))
            gameScreen_rectLobbyTitle = gameScreen_surfaceLobbyTitle.get_rect(center=(SCREEN_WIDTH/4, SCREEN_HEIGHT/6))
            self.screen.blit(gameScreen_surfaceLobbyTitle, gameScreen_rectLobbyTitle)
            
           # readyUpPlayer = button.Button((255,255,255),SCREEN_WIDTH/2, SCREEN_HEIGHT - (SCREEN_HEIGHT*0.2),SCREEN_WIDTH/2,SCREEN_HEIGHT/5,BUTTONSIZETEXT,'Ready')

            readyUpHost.draw(self.screen, (0,0,0))
            #readyUpPlayer.draw(self.screen, (0,0,0))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.gameStateRun = False
                    pygame.quit()
                    exit(0)
                if event.type == pygame.MOUSEBUTTONUP:
                    pos = pygame.mouse.get_pos()
                    if readyUpHost.isOver(pos) and self.peerName != "" and self.pressedReadyUpButton == False: # If ready up button is clicked AND there is a user joined 
                        self.pressedReadyUpButton = True
                        addressOfPeer = list(self.peer.getConnections())[0]
                        if addressOfPeer != None:
                            self.readyUp.append(self.peer.getPort()) # Appends players unique port to ready up
                            self.peer.getSocket().sendto("READY".encode(), addressOfPeer) # Sends ready to peer, MUST BE ACKNOWLEDGED
                        print("Ready up")
                        # Connect to client

            pygame.display.update()
            self.clock.tick(FPS)  # Limits FPS
