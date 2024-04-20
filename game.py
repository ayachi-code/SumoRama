import pygame
from pygame.locals import *

pygame.init()

SCREEN_WIDTH = 1080
SCREEN_HEIGHT = 720

fps = 60  # Increased FPS for smoother animation
clock = pygame.time.Clock()

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

run = True

x = 50
y = 50
velocity_x = 0
velocity_y = 0
acceleration = 300  # Adjust this value for desired acceleration speed

while run:
    dt = clock.tick(fps) / 1000  # dt in seconds

    for event in pygame.event.get():
        if event.type == QUIT:
            run = False

    # Handle key events for movement
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        velocity_x = -acceleration * dt
    elif keys[pygame.K_RIGHT]:
        velocity_x = acceleration * dt
    else:
        velocity_x = 0
    
    if keys[pygame.K_UP]:
        velocity_y = -acceleration * dt
    elif keys[pygame.K_DOWN]:
        velocity_y = acceleration * dt
    else:
        velocity_y = 0

    # Update position based on velocity
    x += velocity_x
    y += velocity_y

    # Keep the circle within the screen boundaries
    x = max(25, min(x, SCREEN_WIDTH - 25))
    y = max(25, min(y, SCREEN_HEIGHT - 25))

    # Clear the screen
    screen.fill((255, 255, 255))

    # Draw the circle
    pygame.draw.circle(screen, (255, 0, 0), (int(x), int(y)), 25)

    # Update the display
    pygame.display.flip()

pygame.quit()
