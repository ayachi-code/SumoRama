import pygame
import button
import input

pygame.init()

SCREEN_WIDTH = 1300
SCREEN_HIGHT = 800

# Set up display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HIGHT))  # Set display resolution to 1920x1080
pygame.display.set_caption('1v1 menu')


clock = pygame.time.Clock()
pygame.font.init()

sumoImg = pygame.image.load("assets/sumoMenu.png").convert_alpha() # Load image transparent
sumoImg = pygame.transform.scale(sumoImg, (200,200)) # Rescales imaeg

run = True
gameScreen = pygame.font.SysFont('Comic Sans MS', 150)

portIpFont = pygame.font.SysFont('Comic Sans MS', 75)
portIpPortFont = pygame.font.SysFont('Comic Sans MS', 75)


# Press  (164,146,163). Hover (218,211,218).

buttonColor8 = (226,221,220) 
buttonColorVersus = (226,221,220) 
buttonColorQiut = (226,221,220) 

gameButtonWidth = 1000
gameButtonHeight = 150

textSizeButton = 140


ip_input = input.InputBox(SCREEN_WIDTH/7.5,SCREEN_HIGHT/2.335, 700, 32)
ip_port = input.InputBox(SCREEN_WIDTH/1.45,SCREEN_HIGHT/2.335, 140, 32)
input_boxes = [ip_input, ip_port]

while run:

    w,h = pygame.display.get_surface().get_size()
    Join = button.Button(buttonColorVersus,SCREEN_WIDTH/7.5,SCREEN_HIGHT/2,gameButtonWidth,gameButtonHeight,textSizeButton,'Join')
    quitTheGame = button.Button(buttonColorQiut,SCREEN_WIDTH/7.5,SCREEN_HIGHT/1.4,gameButtonWidth,gameButtonHeight,textSizeButton,'Back')

    screen.fill((153,0,17))

    for box in input_boxes:
        box.draw(screen)
    # Sumo rama welcome
    gameScreen_surface = gameScreen.render('Join game', True, (255, 255, 255))
    gameScreen_rect = gameScreen_surface.get_rect(center=(SCREEN_WIDTH/1.9, 140))
    screen.blit(gameScreen_surface, gameScreen_rect)

    gameScreen_surfaceIP = portIpFont.render('IP address', True, (255, 255, 255))
    gameScreen_rectIP = gameScreen_surfaceIP.get_rect(center=(SCREEN_WIDTH/4, 300))
    screen.blit(gameScreen_surfaceIP, gameScreen_rectIP)

    gameScreen_surfaceIP_Port = portIpPortFont.render('Port', True, (255, 255, 255))
    gameScreen_rectIP_Port = gameScreen_surfaceIP_Port.get_rect(center=(SCREEN_WIDTH/1.35, 300))
    screen.blit(gameScreen_surfaceIP_Port, gameScreen_rectIP_Port)



    Join.draw(screen, (0,0,0))
    quitTheGame.draw(screen, (0,0,0))

    pos = pygame.mouse.get_pos()
    if Join.isOver(pos):
        buttonColorVersus = (183,179,183) 
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
            if Join.isOver(pos):
                print("Joining game")
            elif quitTheGame.isOver(pos):
                print("Player quit the game")
                run = False
        for box in input_boxes:
            box.handle_event(event)

            
    pygame.display.update()
    clock.tick(60)  # Limit to 60 FPS

pygame.quit()