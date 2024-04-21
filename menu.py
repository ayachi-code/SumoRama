import pygame
import button

SCREEN_WIDTH = 1920
SCREEN_HIGHT = 1080

# Set up display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HIGHT))  # Set display resolution to 1920x1080
clock = pygame.time.Clock()
pygame.font.init()

pygame.init()

run = True
gameScreen = pygame.font.SysFont('Comic Sans MS', 200)

# Press  (164,146,163). Hover (218,211,218).

buttonColor8 = (226,221,220) 
buttonColorVersus = (226,221,220) 
buttonColorQiut = (226,221,220) 


while run:
    morePlayerMode = button.Button(buttonColor8,SCREEN_WIDTH/3.5,SCREEN_HIGHT/4,800,100,'8 player')
    singleMode = button.Button(buttonColorVersus,SCREEN_WIDTH/3.5,SCREEN_HIGHT/2.5,800,100,'1v1')
    quitTheGame = button.Button(buttonColorQiut,SCREEN_WIDTH/3.5,SCREEN_HIGHT/1.75,800,100,'Quit')

    screen.fill((153,0,17))
    # Sumo rama welcome
    gameScreen_surface = gameScreen.render('Sumo Rama', True, (255, 255, 255))
    gameScreen_rect = gameScreen_surface.get_rect(center=(SCREEN_WIDTH/2, 100))
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


    pygame.display.update()
    clock.tick(60)  # Limit to 60 FPS

pygame.quit()