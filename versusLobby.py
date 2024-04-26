import pygame
import button
import socket
import random
import peer
import threading
import pickle
import base64

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

        self.gameStateRun = True

        self.gameState = gameState

        self.fontOfTitle = pygame.font.SysFont('Comic Sans MS', 75)

        self.peerIP = peerIP
        self.port = None
        self.peer = None

        self.peerName = ""

        self.player = player

        self.readyUp = [] # If size is 2 than start

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
                payload = "CONNECT " + self.player.getName() + " " + self.player.getColor() 
                self.peer.getSocket().sendto(payload.encode(), addr)
            elif "SEND":
                pass


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
            if self.readyUp == 2:
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

            readyUpHost = button.Button((255,255,255),0, SCREEN_HEIGHT - (SCREEN_HEIGHT*0.2),SCREEN_WIDTH/2,SCREEN_HEIGHT/5,BUTTONSIZETEXT,'Ready')

            gameScreen_surfaceLobbyTitle = self.fontOfTitle.render('Not ready', True, (255, 255, 255))
            gameScreen_rectLobbyTitle = gameScreen_surfaceLobbyTitle.get_rect(center=(SCREEN_HEIGHT,SCREEN_WIDTH/1.8))
            self.screen.blit(gameScreen_surfaceLobbyTitle, gameScreen_rectLobbyTitle)

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
                    if readyUpHost.isOver(pos): 
                        print("Ready up")
                        pass
                        # Connect to client
           # if self.gameState.getPlayerType() == 'server': # If player is host, show his ip
            #    gameScreen_surfaceLobbyTitle = self.fontOfTitle.render(self.gameState.getSocket().getHost() + ":" + str(self.gameState.getSocket().getPort()), True, (255, 255, 255))
             #   gameScreen_rectLobbyTitle = gameScreen_surfaceLobbyTitle.get_rect(center=(SCREEN_WIDTH/4, SCREEN_HEIGHT/17))
              #  self.screen.blit(gameScreen_surfaceLobbyTitle, gameScreen_rectLobbyTitle)

               # gameScreen_surfaceLobbyTitle = self.fontOfTitle.render('Bob', True, (255, 255, 255))
                #gameScreen_rectLobbyTitle = gameScreen_surfaceLobbyTitle.get_rect(center=(SCREEN_WIDTH/4, SCREEN_HEIGHT/6))
                #self.screen.blit(gameScreen_surfaceLobbyTitle, gameScreen_rectLobbyTitle)

            pygame.display.update()
            self.clock.tick(FPS)  # Limits FPS
