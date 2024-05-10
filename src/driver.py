import sys
# Path to files in other directory

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
import player
import random
import versusArena
import lobbyArena
import playerArena
import error
import gameOver

SCREEN_WIDTH = 1300
SCREEN_HEIGHT = 800

FPS = 60

class Game: # Main driver class
    def __init__(self):
        pygame.init()
        pygame.font.init()

        self.clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))  # Set display resolution
    
        self.gameStateManager = gameState.GameState('start')
        pygame.display.set_caption('Sumo Rama')

        randomNumber = random.randint(0, 420)
        userName = "Player" + str(randomNumber)

        # create instances of the game scenes e.g error, main menu etc.

        self.player = player.Player(userName, "red") # Creates player
        self.error = error.Error(self.screen, self.gameStateManager, None, None)

        self.start = mainMenu.MainMenu(self.screen, self.gameStateManager, self.player)
        self.versusMenu = versusMenu.VersusMenu(self.screen, self.gameStateManager, self.player)
        self.gameOver = gameOver.GameOver(self.screen, self.gameStateManager)

        self.versusArena = versusArena.VersusArena(self.screen, self.gameStateManager, self.player, None, self.gameOver)
        self.lobbyVersus = versusLobby.VersusLobby(self.screen, self.gameStateManager, None, self.player, self.versusArena, self.error)
        self.joinMenu = joinMenu.JoinMenu(self.screen, self.gameStateManager, self.lobbyVersus, self.error)

        # 8 player mode
        self.gameArena = playerArena.PlayerArena(self.screen, self.gameStateManager, self.player, self.gameOver)
        self.lobbyArena = lobbyArena.LobbyArena(self.screen, self.gameStateManager, self.player, self.gameArena, self.error)

        self.states = {'gameOver': self.gameOver,'start': self.start, '1v1Menu': self.versusMenu, 'joinMenu': self.joinMenu, 'lobby1v1': self.lobbyVersus, 'versusArena': self.versusArena, 'lobbyArena': self.lobbyArena, 'playerArena': self.gameArena, 'error': self.error} # game states

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