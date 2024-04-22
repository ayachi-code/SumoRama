import pygame
import button

pygame.init()

SCREEN_WIDTH = 1300
SCREEN_HIGHT = 800

# Set up display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HIGHT))  # Set display resolution to 1920x1080
pygame.display.set_caption('Main menu')


clock = pygame.time.Clock()
pygame.font.init()

sumoImg = pygame.image.load("assets/sumoMenu.png").convert_alpha() # Load image transparent
sumoImg = pygame.transform.scale(sumoImg, (200,200)) # Rescales imaeg

run = True
gameScreen = pygame.font.SysFont('Comic Sans MS', 150)

# Press  (164,146,163). Hover (218,211,218).

buttonColor8 = (226,221,220) 
buttonColorVersus = (226,221,220) 
buttonColorQiut = (226,221,220) 

gameButtonWidth = 1000
gameButtonHeight = 150

textSizeButton = 140

while run:
    w,h = pygame.display.get_surface().get_size()
    morePlayerMode = button.Button(buttonColor8,SCREEN_WIDTH/6.5,SCREEN_HIGHT/3.5,gameButtonWidth,gameButtonHeight,textSizeButton,'8 player')
    singleMode = button.Button(buttonColorVersus,SCREEN_WIDTH/6.5,SCREEN_HIGHT/2,gameButtonWidth,gameButtonHeight,textSizeButton,'1v1')
    quitTheGame = button.Button(buttonColorQiut,SCREEN_WIDTH/6.5,SCREEN_HIGHT/1.4,gameButtonWidth,gameButtonHeight,textSizeButton,'Quit')

    screen.fill((153,0,17))
    # Sumo rama welcome
    gameScreen_surface = gameScreen.render('Sumo Rama', True, (255, 255, 255))
    gameScreen_rect = gameScreen_surface.get_rect(center=(SCREEN_WIDTH/1.9, 140))
    screen.blit(gameScreen_surface, gameScreen_rect)

    singleMode.draw(screen, (0,0,0))
    morePlayerMode.draw(screen, (0,0,0))
    quitTheGame.draw(screen, (0,0,0))

    pos = pygame.mouse.get_pos()
    if singleMode.isOver(pos):
        buttonColorVersus = (183,179,183) 
    elif morePlayerMode.isOver(pos):
        buttonColor8 = (183,179,183)
    elif quitTheGame.isOver(pos):
        buttonColorQiut = (183,179,183)
    else:
        buttonColorVersus = (226,221,220)
        buttonColor8 = (226,221,220)
        buttonColorQiut = (226,221,220)


    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.MOUSEBUTTONUP:
            pos = pygame.mouse.get_pos()
            if singleMode.isOver(pos):
                print("Starting 1v1 mode")
            elif morePlayerMode.isOver(pos):
                print("Starting 8 player mode")
            elif quitTheGame.isOver(pos):
                print("Player quit the game")
                run = False

            
    screen.blit(sumoImg, (w/10, 20))
    screen.blit(sumoImg, (w/1.24, 20))

    pygame.display.update()
    clock.tick(60)  # Limit to 60 FPS

pygame.quit()