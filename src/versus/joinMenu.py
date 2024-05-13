import pygame
import button
import input
import peer
import versusLobby
import socket
import threading
import time

SCREEN_WIDTH = 1300
SCREEN_HIGHT = 800

FPS = 60

BUTTONWIDTH = 1000
BUTTONHEIGHT = 150
BUTTONSIZETEXT = 140

class JoinMenu:
    def __init__(self, screen, gameState, lobbyVersus, error):
        pygame.init()
        pygame.font.init()
        self.clock = pygame.time.Clock()

        self.screen = screen
                
        self.buttonColorJoin = (226,221,220) 
        self.buttonColorBack = (226,221,220) 

        self.gameStateRun = True

        self.gameScreen = pygame.font.SysFont('Comic Sans MS', 150)
        self.portIpFont = pygame.font.SysFont('Comic Sans MS', 75)
        self.portIpPortFont = pygame.font.SysFont('Comic Sans MS', 75)

        self.gameState = gameState
        self.lobbyVersus = lobbyVersus
        self.error = error

        self.ip_input = '127.0.0.1' # input.InputBox(SCREEN_WIDTH/7.5,SCREEN_HIGHT/2.335, 700, 32)
        self.ip_port = input.InputBox(SCREEN_WIDTH/1.45,SCREEN_HIGHT/2.335, 140, 32,32)
        self.input_boxes = [self.ip_port] # [self.ip_input, self.ip_port]

        self.hostAck = None
        self.socketCon = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def sendHostRequest(self):
        handshakeMessage = "HELLO Host"
        maxRequestSend = 3
        try:
            while True:
                if self.hostAck == True:
                    print("Stopping sending for check if excist host")
                    break
                if maxRequestSend <= 0:
                    self.hostAck = False
                    break
                self.socketCon.sendto(handshakeMessage.encode(), ('127.0.0.1', int(self.ip_port.getText())))
                time.sleep(0.1)
                maxRequestSend -= 1
        except Exception as e:
            print(e)
            self.gameStateRun = False
            self.error.setErrorMessage('could not join peer')
            self.error.setBackButtonDest('joinMenu')
            self.gameState.setCurrentState('error')

    def listenToHost(self):
        while True:
            data, addr = self.socketCon.recvfrom(1024)
            #print(data)
            if "Hi" in data.decode():
                print("Host does excist")
                self.hostAck = True
                break
    
    def run(self):
        self.gameStateRun = True
        self.hostAck = None
        while self.gameStateRun:
            Join = button.Button(self.buttonColorJoin,SCREEN_WIDTH/7.5,SCREEN_HIGHT/2,BUTTONWIDTH,BUTTONHEIGHT,BUTTONSIZETEXT,'Join')
            back = button.Button(self.buttonColorBack,SCREEN_WIDTH/7.5,SCREEN_HIGHT/1.4,BUTTONWIDTH,BUTTONHEIGHT,BUTTONSIZETEXT,'Back')

            self.screen.fill((153,0,17))

            for box in self.input_boxes:
                box.draw(self.screen)

            # Draw text
            gameScreen_surface = self.gameScreen.render('Join game', True, (255, 255, 255))
            gameScreen_rect = gameScreen_surface.get_rect(center=(SCREEN_WIDTH/1.9, 140))
            self.screen.blit(gameScreen_surface, gameScreen_rect)

            gameScreen_surfaceIP = self.portIpFont.render('IP address', True, (255, 255, 255))
            gameScreen_rectIP = gameScreen_surfaceIP.get_rect(center=(SCREEN_WIDTH/4, 300))
            self.screen.blit(gameScreen_surfaceIP, gameScreen_rectIP)

            gameScreen_surfaceIP_Port = self.portIpPortFont.render('Port', True, (255, 255, 255))
            gameScreen_rectIP_Port = gameScreen_surfaceIP_Port.get_rect(center=(SCREEN_WIDTH/1.35, 300))
            self.screen.blit(gameScreen_surfaceIP_Port, gameScreen_rectIP_Port)

            Join.draw(self.screen, (0,0,0))
            back.draw(self.screen, (0,0,0))

            # Hover effect
            pos = pygame.mouse.get_pos()
            if Join.isOver(pos):
                self.buttonColorJoin = (183,179,183) 
                self.buttonColorBack = (226,221,220)
            elif back.isOver(pos):
                self.buttonColorBack = (183,179,183)
                self.buttonColorJoin = (226,221,220)
  
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.gameStateRun = False
                    pygame.quit()
                    exit(0)
                if event.type == pygame.MOUSEBUTTONUP:
                    pos = pygame.mouse.get_pos()
                    if Join.isOver(pos): # Connect to client (Join event listener)
                        print("Joining game")
                        try:
                            # Check does Host exist
                            send_thread = threading.Thread(target=self.sendHostRequest, daemon=True)
                            send_thread.start()
                            recv_thread = threading.Thread(target=self.listenToHost, daemon=True)
                            recv_thread.start()

                            while True:
                                if self.hostAck:
                                    break
                                elif self.hostAck == False:
                                    raise Exception
                  
                            self.lobbyVersus.setPeerIP('127.0.0.1')
                            self.lobbyVersus.setPeerPort(int(self.ip_port.getText()))

                            self.gameState.setCurrentState('lobby1v1')
                            self.gameStateRun = False
                        except Exception as e: # Show error screen
                            print(e)
                            self.gameStateRun = False
                            self.error.setErrorMessage('could not join peer')
                            self.error.setBackButtonDest('joinMenu')
                            self.gameState.setCurrentState('error')
                    elif back.isOver(pos):
                        print("Player quit the menu")
                        self.gameState.setCurrentState('1v1Menu')
                        self.gameStateRun = False
                for box in self.input_boxes:
                    box.handle_event(event)

                
            pygame.display.update()
            self.clock.tick(FPS)  # Limit to 60 FPSFR
