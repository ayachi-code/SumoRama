import pygame
import button
import input

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
                
        self.buttonColorVersus = (226,221,220) 
        self.buttonColorQuit = (226,221,220) 

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
            Join = button.Button(self.buttonColorVersus,SCREEN_WIDTH/7.5,SCREEN_HIGHT/2,BUTTONWIDTH,BUTTONHEIGHT,BUTTONSIZETEXT,'Join')
            quitTheGame = button.Button(self.buttonColorQuit,SCREEN_WIDTH/7.5,SCREEN_HIGHT/1.4,BUTTONWIDTH,BUTTONHEIGHT,BUTTONSIZETEXT,'Back')

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
            quitTheGame.draw(self.screen, (0,0,0))

            pos = pygame.mouse.get_pos()
            if Join.isOver(pos):
                self.buttonColorVersus = (183,179,183) 
                self.buttonColorQuit = (226,221,220)
            elif quitTheGame.isOver(pos):
                self.buttonColorQuit = (183,179,183)
                self.buttonColorVersus = (226,221,220)
  
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.gameStateRun = False
                    pygame.quit()
                    exit(0)
                if event.type == pygame.MOUSEBUTTONUP:
                    pos = pygame.mouse.get_pos()
                    if Join.isOver(pos):
                        print("Joining game")
                    elif quitTheGame.isOver(pos):
                        print("Player quit the menu")
                        self.gameState.setCurrentState('1v1Menu')
                        self.gameStateRun = False
                for box in self.input_boxes:
                    box.handle_event(event)

                    
            pygame.display.update()
            self.clock.tick(FPS)  # Limit to 60 FPS