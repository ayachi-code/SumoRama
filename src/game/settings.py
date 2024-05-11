import pygame
import button
import input

FPS = 60

SCREEN_WIDTH = 1300
SCREEN_HEIGHT = 800

BUTTONWIDTH = 400
BUTTONHEIGHT = 100
BUTTONSIZETEXT = 140

class Settings:
    def __init__(self, screen, gameState, player):
        pygame.init()
        pygame.font.init()

        self.clock = pygame.time.Clock()
        
        self.screen = screen  # Set display resolution
        self.gameState = gameState
        self.player = player

        self.gameStateRun = True
        self.buttonColor = (226,221,220)
        self.buttonColorName = (226,221,220)
        
        self.gameFont = pygame.font.SysFont('Comic Sans MS', 90)
        self.errorFont = pygame.font.SysFont('Comic Sans MS', 45)

        self.username = input.InputBox(SCREEN_WIDTH/4, 50 + 90 + 90 + 90 + 90, SCREEN_WIDTH/2, 50, 60)
        self.errorUserName = False


    def run(self):
        # reset states
        self.gameStateRun = True
        # self.errorUserName = False

        while self.gameStateRun:
            self.screen.fill((153,0,17)) # Red screen

            gameScreen_surface = self.gameFont.render('Settings', True, (255, 255, 255))
            gameScreen_rect = gameScreen_surface.get_rect(center=(SCREEN_WIDTH/2, 50))
            self.screen.blit(gameScreen_surface, gameScreen_rect)


            gameScreen_surface = self.gameFont.render('Game version: 1.0.0 ', True, (255, 255, 255))
            gameScreen_rect = gameScreen_surface.get_rect(center=(SCREEN_WIDTH/2, 50 + 90))
            self.screen.blit(gameScreen_surface, gameScreen_rect)



            gameScreen_surface = self.gameFont.render('Current name: ' + self.player.getName(), True, (255, 255, 255))
            gameScreen_rect = gameScreen_surface.get_rect(center=(SCREEN_WIDTH/2, 50 + 90 + 90))
            self.screen.blit(gameScreen_surface, gameScreen_rect)


            gameScreen_surface = self.gameFont.render('Change name: ', True, (255, 255, 255))
            gameScreen_rect = gameScreen_surface.get_rect(center=(SCREEN_WIDTH/2, 50 + 90 + 90 + 90 + 25))
            self.screen.blit(gameScreen_surface, gameScreen_rect)
            self.username.draw(self.screen)

           
            # Error message
            if self.errorUserName == True:
                gameScreen_surface = self.errorFont.render('Error: username is not accepted!', True, (255, 255, 255))
                gameScreen_rect = gameScreen_surface.get_rect(center=(SCREEN_WIDTH/2, 50 + 90 + 90 + 90 + 90 + 90))
                self.screen.blit(gameScreen_surface, gameScreen_rect)

        
            # Submit name button
            name = button.Button(self.buttonColorName,SCREEN_WIDTH/2 - 85, 50 + 90 + 90 + 90 + 90 + 125,150,70,60,'Submit')
            name.draw(self.screen, (0,0,0))

    
            # Return button
            goBackButton = button.Button(self.buttonColor,SCREEN_WIDTH/2 - BUTTONWIDTH/2,SCREEN_HEIGHT/1.15,BUTTONWIDTH,BUTTONHEIGHT,BUTTONSIZETEXT,'Return')
            goBackButton.draw(self.screen, (0,0,0))

            # Hover effect for button
            pos = pygame.mouse.get_pos()
            if goBackButton.isOver(pos):
                self.buttonColor = (183,179,183)
            elif name.isOver(pos):
                self.buttonColorName = (183,179,183) 
            else:
                self.buttonColor = (226,221,220) 
                self.buttonColorName = (226,221,220) 

            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.gameStateRun = False
                    pygame.quit()
                    exit(0)
                if event.type == pygame.MOUSEBUTTONUP:
                    pos = pygame.mouse.get_pos()
                    if goBackButton.isOver(pos):
                        print("Returning to mainMenu")
                        self.gameState.setCurrentState('start')
                        self.gameStateRun = False
                        
                    elif name.isOver(pos):
                        usernameChosen = self.username.getText()
                        if len(usernameChosen) >= 10:
                            self.errorUserName = True
                        elif " " in usernameChosen:
                            self.errorUserName = True
                        elif usernameChosen == "":
                            self.errorUserName = True
                        else:
                            self.player.setName(self.username.getText())
                            self.errorUserName = False
                self.username.handle_event(event)

            pygame.display.update()
            self.clock.tick(FPS)  # Limit to 60 FPS
