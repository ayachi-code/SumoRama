import pygame
import button
import input
import socket

SCREEN_WIDTH = 1300
SCREEN_HIGHT = 800

FPS = 60

BUTTONWIDTH = 1000
BUTTONHEIGHT = 150
BUTTONSIZETEXT = 140

class JoinMenu:
    def __init__(self, screen, gameState):
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

        self.ip_input = input.InputBox(SCREEN_WIDTH/7.5,SCREEN_HIGHT/2.335, 700, 32)
        self.ip_port = input.InputBox(SCREEN_WIDTH/1.45,SCREEN_HIGHT/2.335, 140, 32)
        self.input_boxes = [self.ip_input, self.ip_port]
    
    def run(self):
        self.gameStateRun = True
        while self.gameStateRun:
            w,h = pygame.display.get_surface().get_size()
            Join = button.Button(self.buttonColorJoin,SCREEN_WIDTH/7.5,SCREEN_HIGHT/2,BUTTONWIDTH,BUTTONHEIGHT,BUTTONSIZETEXT,'Join')
            back = button.Button(self.buttonColorBack,SCREEN_WIDTH/7.5,SCREEN_HIGHT/1.4,BUTTONWIDTH,BUTTONHEIGHT,BUTTONSIZETEXT,'Back')

            self.screen.fill((153,0,17))

            for box in self.input_boxes:
                box.draw(self.screen)
            # Sumo rama welcome
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
                    if Join.isOver(pos): # Connect to client
                        print("Joining game")
                        print(self.ip_input.getText())
                        # TODO: Connect to given ip and port,
                            # If ip and port not exist show pop up with cannot connect to client, with back button to joinMenu
                            # If ip and port are good, bring client to a lobby screen, where both players are present, lobby has a ready up button. If both clients ready up than the both clients get to see the game scene
                            # Game scene has logic of shrink.py but 2 players, also lockstepping added.
                    elif back.isOver(pos):
                        print("Player quit the menu")
                        self.gameState.setCurrentState('1v1Menu')
                        self.gameStateRun = False
                for box in self.input_boxes:
                    box.handle_event(event)

                    
            pygame.display.update()
            self.clock.tick(FPS)  # Limit to 60 FPS
