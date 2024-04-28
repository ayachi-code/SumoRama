import pygame
import button
import socket
import random
import peer
import threading
import time

#TODO: Add Lobby portocol to documentation

FPS = 60

SCREEN_WIDTH = 1300
SCREEN_HEIGHT = 800

BUTTONSIZETEXT = 100

class VersusLobby:
    def __init__(self, screen, gameState, peerIP, player, arena):
        pygame.init()
        pygame.font.init()

        self.clock = pygame.time.Clock()
        self.screen = screen
        self.fontOfTitle = pygame.font.SysFont('Comic Sans MS', 75)

        self.gameStateRun = True
        self.gameState = gameState 
        self.peerIP = peerIP
        self.player = player
        self.arena = arena

        self.port = None
        self.peer = None


        self.peerName = ""
        self.peerColor = (255,255,255)

        self.readyUpAcknowledged = None
        self.readyUp = [] # If size is 2 than start
        self.pressedReadyUpButton = False # Used to disable ready up again
        self.peerPressedReadyUp = False 
        self.playerQuit = False

        self.polAck = False

    def setPeerIP(self, ip):
        self.peerIP = ip
    def setPeerPort(self, port):
        self.port = port

    def listenForConnections(self):
        while True:
            data, addr = self.peer.getSocket().recvfrom(1024)
            data = data.decode()
            if self.playerQuit: # Stops thread when player quits
                break

            if "HELLO" in data: # Send handshake back :)
                self.peer.getSocket().sendto("Hi".encode(), addr)
            elif "CONNECT" in data and addr not in self.peer.getConnections(): 
                self.peer.addCoonection(addr)
                self.peerName = data.split(" ")[1] # Peername
                self.peerColor = data.split(" ")[2] # Peer color
                payload = "CONNECT " + self.player.getName() + " " + self.player.getColor() 
                self.peer.getSocket().sendto(payload.encode(), addr)
                send_thread = threading.Thread(target=self.pollPeer, args=(addr,))
                send_thread.start()
            elif data == "READY":
                self.peerPressedReadyUp = True
                self.peer.getSocket().sendto("READY-YES".encode(), addr)
                if addr not in self.readyUp:
                    self.readyUp.append(addr)
            elif "SEQ" in data:
                payload = "ACK " + data.split(" ")[1]
                self.peer.getSocket().sendto(payload.encode(), addr)
            elif "ACK" in data: # We got acknowledged
                self.peer.increaseSequenceNumber()
                self.polAck = True
            elif data == "READY-YES":
                self.readyUpAcknowledged = True
      
    def sendReadyUpToPeer(self, destination):
        maxSendToPeer = 20
        while True:
            if maxSendToPeer <= 0:
                self.readyUpAcknowledged = False
                break

            if self.readyUpAcknowledged == True:
                break

            self.peer.getSocket().sendto("READY",destination)
            time.sleep(0.1)
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
        
    def resetStates(self):
        self.peerName = ""
        if self.peer != None:
            self.peer.resetConnections()
            
        self.readyUp = []
        self.peerPressedReadyUp = False    
        self.pressedReadyUpButton = False
        self.readyUpAcknowledged = None
        self.playerQuit = False
        self.polAck = False
        
    def pollPeer(self, peer): # Poll peer to check if they are in lobby
        maxTimeOut = 2
        while True:
            if maxTimeOut <= 0:
                print("Timeout")
                if self.peerIP != None: # Joiner
                    print("HOST LEFT OHHHHH")
                    self.gameStateRun = False
                    self.gameState.setCurrentState('errorJoin')
                    if self.peer.getSocket():
                        self.peer.getSocket().close()
                        self.resetStates()
                else:
                    print("Client(joiner) is gone")
                    #reset 1v1 peer states
                    self.resetStates()
                break

            if self.polAck:
                maxTimeOut = 2
                self.polAck = False

            if len(self.readyUp) == 2 or self.playerQuit == True:
                break

            payload = "SEQ " + str(self.peer.getSequenceNumber())
            self.peer.getSocket().sendto(payload.encode(), peer) # e.g SEQ 123
            time.sleep(0.1) # Polling speed
            maxTimeOut -= 1

    def run(self):
        #reset states from previous game
        self.resetStates()

        self.gameStateRun = True
        self.peer = peer.Peer('127.0.0.1',  random.randint(6000, 8080)) # Creates peer object
        self.peer.start()

        print(self.peer.getPort())

        receive_thread = threading.Thread(target=self.listenForConnections, daemon=True)
        receive_thread.start()

        if self.peerIP != None: # Joiner
            payload = "CONNECT " + self.player.getName() + " " + self.player.getColor()
            self.peer.getSocket().sendto(payload.encode(), (self.peerIP, self.port)) # Joiner wants to introduce them self to host
   
        while self.gameStateRun:
            if len(self.readyUp) == 2: # 2 players ready-up we can start the game
                self.arena.setPeer(self.peer)
                self.gameState.setCurrentState('versusArena')
                self.gameStateRun = False
                self.playerQuit = True
                print("start versus arena")

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
            
            readyUpHost.draw(self.screen, (0,0,0))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.gameStateRun = False
                    self.playerQuit = True
                    self.peer.resetConnections()
                    self.peer.getSocket().close() # Close socket
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

            pygame.display.update()
            self.clock.tick(FPS)  # Limits FPS