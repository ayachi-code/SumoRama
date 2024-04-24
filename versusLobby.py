import pygame
import button

FPS = 60

SCREEN_WIDTH = 1300
SCREEN_HEIGHT = 800

BUTTONSIZETEXT = 100

#TODO make lobby

class VersusLobby:
    def __init__(self, screen, gameState):
        pygame.init()
        pygame.font.init()
        self.clock = pygame.time.Clock()
        self.screen = screen

        self.gameStateRun = True

        self.gameState = gameState

        self.fontOfTitle = pygame.font.SysFont('Comic Sans MS', 75)
    def run(self):
        while self.gameStateRun:
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
            
            readyUpPlayer = button.Button((255,255,255),SCREEN_WIDTH/2, SCREEN_HEIGHT - (SCREEN_HEIGHT*0.2),SCREEN_WIDTH/2,SCREEN_HEIGHT/5,BUTTONSIZETEXT,'Ready')

            readyUpHost.draw(self.screen, (0,0,0))
            readyUpPlayer.draw(self.screen, (0,0,0))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.gameStateRun = False
                    pygame.quit()
                    exit(0)

            pygame.display.update()
            self.clock.tick(FPS)  # Limits FPS


if __name__ == "__main__":
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))  # Set display resolution

    test = VersusLobby(screen, 1)
    test.run()

