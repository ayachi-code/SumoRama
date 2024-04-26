import pygame
import gameState
import mainMenu
import versusMenu
import joinMenu
import versusLobby
import errorJoin
import player
import random

SCREEN_WIDTH = 1300
SCREEN_HEIGHT = 800

FPS = 60

class Game:
    def __init__(self):
        pygame.init()
        pygame.font.init()

        self.clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))  # Set display resolution
    
        self.gameStateManager = gameState.GameState('start')
        pygame.display.set_caption('Sumo Rama')


        randomNumber = random.randint(0, 420)
        userName = "Player" + str(randomNumber)

        self.player = player.Player(userName, "red") # Creates player

        self.start = mainMenu.MainMenu(self.screen, self.gameStateManager, self.player)
        self.versusMenu = versusMenu.VersusMenu(self.screen, self.gameStateManager, self.player)
        self.lobbyVersus = versusLobby.VersusLobby(self.screen, self.gameStateManager, None, self.player)
        self.joinMenu = joinMenu.JoinMenu(self.screen, self.gameStateManager, self.lobbyVersus, self.player)
        self.errorJoin = errorJoin.ErrorJoin(self.screen, self.gameStateManager)

        self.states = {'start': self.start, '1v1Menu': self.versusMenu, 'joinMenu': self.joinMenu, 'lobby1v1': self.lobbyVersus, 'errorJoin': self.errorJoin}

        self.gameStateRun = True
    def run(self):
         while self.gameStateRun:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.gameStateRun = False

            self.states[self.gameStateManager.getCurrentState()].run()
 

if __name__ == "__main__":
     game = Game()
     game.run()
     pygame.quit()