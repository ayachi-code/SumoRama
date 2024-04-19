import pygame
from pygame.locals import *

pygame.init()

SCREEN_WIDTH = 1080
SCREEN_HEIGHT = 720

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

run = True

while run:
  for event in pygame.event.get():
    if event.type == QUIT:
      run = False

  screen.fill((255, 255, 255)) # White background
  pygame.display.update()
  # pygame.display.flip()

pygame.quit()