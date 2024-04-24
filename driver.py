import pygame
import gameState
import mainMenu
import versusMenu
import joinMenu
import versusLobby

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


        self.start = mainMenu.MainMenu(self.screen, self.gameStateManager)
        self.versusMenu = versusMenu.VersusMenu(self.screen, self.gameStateManager)
        self.joinMenu = joinMenu.JoinMenu(self.screen, self.gameStateManager)
        self.lobbyVersus = versusLobby.VersusLobby(self.screen, self.gameStateManager)

        self.states = {'start': self.start, '1v1Menu': self.versusMenu, 'joinMenu': self.joinMenu, 'lobby1v1': self.lobbyVersus}

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