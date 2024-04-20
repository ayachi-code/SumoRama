import pygame
import math

pygame.init()

# Set up display
screen = pygame.display.set_mode((800, 600))
clock = pygame.time.Clock()

# Define constants
circle_radius = 40  # Radius of all circles
player_circle = {"center": [200, 200], "velocity": [0, 0]}  # Player-controlled circle
circles = [
    {"center": [400, 200], "velocity": [0, 0]},  # Circle 1
    {"center": [300, 400], "velocity": [0, 0]},  # Circle 2
    {"center": [500, 400], "velocity": [0, 0]},  # Circle 3
    {"center": [150, 450], "velocity": [0, 0]},  # Circle 4
    {"center": [600, 350], "velocity": [0, 0]}   # Circle 5
]

# Define rush variables
rush_duration = 0.9  # Rush duration in seconds
rush_speed = 200  # Rush speed in pixels per second
rushing = False
rush_start_time = 0

def rush_to_cursor():
    # Get current mouse position
    mouse_x, mouse_y = pygame.mouse.get_pos()

    # Calculate direction vector from player circle to cursor
    direction = [mouse_x - player_circle["center"][0], mouse_y - player_circle["center"][1]]
    length = math.sqrt(direction[0]**2 + direction[1]**2)

    if length > 0:
        # Normalize direction vector
        direction = [direction[0] / length, direction[1] / length]

        # Calculate rush movement towards cursor
        player_circle["center"][0] += direction[0] * rush_speed * clock.get_time() / 1000
        player_circle["center"][1] += direction[1] * rush_speed * clock.get_time() / 1000

        # Check collision with other circles during rush
        for circle in circles:
            distance = math.sqrt((player_circle["center"][0] - circle["center"][0])**2 +
                                 (player_circle["center"][1] - circle["center"][1])**2)
            if distance < circle_radius * 2:  # Check collision with diameter (2 * radius)
                # Calculate overlap and direction of collision
                overlap = (circle_radius * 2) - distance
                collision_direction = [circle["center"][0] - player_circle["center"][0],
                                       circle["center"][1] - player_circle["center"][1]]
                collision_length = math.sqrt(collision_direction[0]**2 + collision_direction[1]**2)

                if collision_length > 0:
                    # Normalize collision direction
                    collision_direction = [collision_direction[0] / collision_length,
                                           collision_direction[1] / collision_length]

                    # Resolve collision by pushing the other circle away
                    move_distance = overlap / 2
                    player_circle["center"][0] -= move_distance * collision_direction[0]
                    player_circle["center"][1] -= move_distance * collision_direction[1]
                    circle["center"][0] += move_distance * collision_direction[0]
                    circle["center"][1] += move_distance * collision_direction[1]

# Main game loop
running = True

while running:
    screen.fill((255, 255, 255))  # Clear screen

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and not rushing:
                rushing = True
                rush_start_time = pygame.time.get_ticks()

    # Handle rush movement towards cursor
    if rushing:
        current_time = pygame.time.get_ticks()
        if current_time - rush_start_time < rush_duration * 1000:  # Check if still within rush duration
            rush_to_cursor()
        else:
            rushing = False  # Stop rushing after duration expires

    # Handle player input (normal movement)
    keys = pygame.key.get_pressed()
    if not rushing:  # Only move player if not rushing towards cursor
        if keys[pygame.K_a]:
            player_circle["center"][0] -= 3  # Move left (A key)
        if keys[pygame.K_d]:
            player_circle["center"][0] += 3  # Move right (D key)
        if keys[pygame.K_w]:
            player_circle["center"][1] -= 3  # Move up (W key)
        if keys[pygame.K_s]:
            player_circle["center"][1] += 3  # Move down (S key)

    # Draw circles
    pygame.draw.circle(screen, (0, 0, 255), player_circle["center"], circle_radius)  # Draw player circle in blue
    for circle in circles:
        pygame.draw.circle(screen, (255, 0, 0), circle["center"], circle_radius)  # Draw other circles in red

    pygame.display.flip()
    clock.tick(60)  # Limit to 60 FPS

pygame.quit()
