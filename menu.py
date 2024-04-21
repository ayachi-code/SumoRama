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
gameScreen = pygame.font.SysFont('Comic Sans MS', 100)

morePlayerMode = button.Button((255, 255, 255),SCREEN_HIGHT/2,SCREEN_HIGHT/4,800,100,'8 player')
singleMode = button.Button((255, 255, 255),SCREEN_HIGHT/2,SCREEN_HIGHT/2.5,800,100,'1v1')
quitTheGame = button.Button((255, 255, 255),SCREEN_HIGHT/2,SCREEN_HIGHT/1.75,800,100,'Quit')


while run:
    screen.fill((0,0,0))
    # Sumo rama welcome
    gameScreen_surface = gameScreen.render('Sumo Rama', True, (255, 255, 255))
    gameScreen_rect = gameScreen_surface.get_rect(center=(SCREEN_WIDTH/2, 100))
    screen.blit(gameScreen_surface, gameScreen_rect)

    singleMode.draw(screen, (0,0,0))
    morePlayerMode.draw(screen, (0,0,0))
    quitTheGame.draw(screen, (0,0,0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.MOUSEBUTTONUP:
            pos = pygame.mouse.get_pos()
            if singleMode.isOver(pos):
                print("Starting 1v1 mode")
            elif morePlayerMode.isOver(pos):
                print("Starting 8 player mode")


    button.Button((100,100,100),300,300,100,100,"heyy")

    pygame.display.update()
    clock.tick(60)  # Limit to 60 FPS