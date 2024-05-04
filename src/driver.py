import sys

sys.path.append("game")
sys.path.append("lib")
sys.path.append("versus")
sys.path.append("8player")


import pygame
import gameState
import mainMenu
import versusMenu
import joinMenu
import versusLobby
import errorJoin
import player
import random
import versusArena
import gameOverVersus
import lobbyArena
import playerArena

# Path to files in other directory

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
        self.errorJoin = errorJoin.ErrorJoin(self.screen, self.gameStateManager)
        self.gameOverVersus = gameOverVersus.GameOverVersus(self.screen, self.gameStateManager)

        self.versusArena = versusArena.VersusArena(self.screen, self.gameStateManager, self.player, None, self.gameOverVersus)
        self.lobbyVersus = versusLobby.VersusLobby(self.screen, self.gameStateManager, None, self.player, self.versusArena)
        self.joinMenu = joinMenu.JoinMenu(self.screen, self.gameStateManager, self.lobbyVersus)

        # 8 player mode
        self.lobbyArena = lobbyArena.LobbyArena(self.screen, self.gameStateManager, self.player)
        self.gameArena = playerArena.PlayerArena(self.screen, self.gameStateManager, self.player, None, self.gameOverVersus)

        self.states = {'start': self.start, '1v1Menu': self.versusMenu, 'joinMenu': self.joinMenu, 'lobby1v1': self.lobbyVersus, 'errorJoin': self.errorJoin, 'versusArena': self.versusArena, '1v1GameOver': self.gameOverVersus, 'lobbyArena': self.lobbyArena, 'playerArena': self.gameArena}


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