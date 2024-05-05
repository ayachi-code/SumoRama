import pygame
import button
import socket
import threading
import peer
import random

SCREEN_WIDTH = 1300
SCREEN_HIGHT = 800

FPS = 60

BUTTONWIDTH = 1000
BUTTONHEIGHT = 150
BUTTONSIZETEXT = 140

class VersusMenu:
    def __init__(self, screen, gameState, player):
        pygame.init()
        pygame.font.init()
        self.clock = pygame.time.Clock()

        self.screen = screen
        # pygame.display.set_caption('1v1 menu')
        
        self.buttonColorHost = (226,221,220) 
        self.buttonColorJoin = (226,221,220) 
        self.buttonColorBack = (226,221,220) 

        self.gameStateRun = True

        self.gameScreen = pygame.font.SysFont('Comic Sans MS', 150)

        self.gameState = gameState

    
    def run(self):
        self.gameStateRun = True
        while self.gameStateRun:
            w,h = pygame.display.get_surface().get_size()
            host = button.Button(self.buttonColorHost,SCREEN_WIDTH/7.5,SCREEN_HIGHT/3.5,BUTTONWIDTH,BUTTONHEIGHT,BUTTONSIZETEXT,'Host')
            join = button.Button(self.buttonColorJoin,SCREEN_WIDTH/7.5,SCREEN_HIGHT/2,BUTTONWIDTH,BUTTONHEIGHT,BUTTONSIZETEXT,'Join')
            back = button.Button(self.buttonColorBack,SCREEN_WIDTH/7.5,SCREEN_HIGHT/1.4,BUTTONWIDTH,BUTTONHEIGHT,BUTTONSIZETEXT,'Back')

            self.screen.fill((153,0,17))
            # Sumo rama welcome
            gameScreen_surface = self.gameScreen.render('Sumo Rama 1v1', True, (255, 255, 255))
            gameScreen_rect = gameScreen_surface.get_rect(center=(SCREEN_WIDTH/1.9, 140))
            self.screen.blit(gameScreen_surface, gameScreen_rect)

            host.draw(self.screen, (0,0,0))
            join.draw(self.screen, (0,0,0))
            back.draw(self.screen, (0,0,0))

            pos = pygame.mouse.get_pos()
            if host.isOver(pos):
                self.buttonColorHost = (183,179,183) 
                self.buttonColorJoin = (226,221,220)
                self.buttonColorBack = (226,221,220)
            elif join.isOver(pos):
                self.buttonColorJoin = (183,179,183)
                self.buttonColorHost = (226,221,220)
                self.buttonColorBack = (226,221,220)
            elif back.isOver(pos):
                self.buttonColorBack = (183,179,183)
                self.buttonColorHost = (226,221,220)
                self.buttonColorJoin = (226,221,220)
       
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.gameStateRun = False
                    pygame.quit()
                    exit(0)
                if event.type == pygame.MOUSEBUTTONUP:
                    pos = pygame.mouse.get_pos()
                    if join.isOver(pos):
                        print("Join")
                        self.gameState.setCurrentState('joinMenu')
                        self.gameStateRun = False
                    elif host.isOver(pos):
                        self.gameState.setCurrentState('lobby1v1')
                        self.gameStateRun = False
                    elif back.isOver(pos):
                        print("Player quit the game")
                        self.gameState.setCurrentState('start')
                        self.gameStateRun = False

            pygame.display.update()
            self.clock.tick(60)  # Limit to 60 FPS