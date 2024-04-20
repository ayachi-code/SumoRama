import pygame
import math

pygame.init()

# Set up display
screen = pygame.display.set_mode((1920, 1080))  # Set display resolution to 1920x1080
clock = pygame.time.Clock()

# Define constants
circle_radius = 40  # Radius of all circles
player_circle = {"center": [960, 540], "velocity": [0, 0]}  # Player-controlled circle (initially at sumo ring center)
circles = [
    {"center": [800, 300], "velocity": [0, 0]},   # Circle 1
    {"center": [700, 800], "velocity": [0, 0]},   # Circle 2
    {"center": [1100, 800], "velocity": [0, 0]},  # Circle 3
    {"center": [300, 950], "velocity": [0, 0]},   # Circle 4
    {"center": [1200, 700], "velocity": [0, 0]}   # Circle 5
]

# Define sumo ring properties
sumo_ring_radius = 500  # Larger radius for the sumo ring
sumo_ring_center = [960, 540]  # Center of the screen (1920x1080 resolution)

# Define rush variables
rush_duration = 2.0  # Rush duration in seconds
rush_speed = 300  # Rush speed in pixels per second
rushing = False
rush_start_time = 0

def place_circles_in_sumo_ring():
    """Ensure all circles (player and others) are fully inside the sumo ring."""
    global player_circle, circles

    # Check and handle player circle
    if player_circle is not None:
        distance_to_center = math.sqrt((player_circle["center"][0] - sumo_ring_center[0])**2 +
                                       (player_circle["center"][1] - sumo_ring_center[1])**2)
        if distance_to_center > sumo_ring_radius - circle_radius:
            # Player circle is outside the sumo ring, remove it
            player_circle = None

    # Check and handle other circles
    circles_to_remove = []
    for circle in circles:
        distance_to_center = math.sqrt((circle["center"][0] - sumo_ring_center[0])**2 +
                                       (circle["center"][1] - sumo_ring_center[1])**2)
        if distance_to_center > sumo_ring_radius - circle_radius:
            # Mark circle for removal if it has moved outside the sumo ring
            circles_to_remove.append(circle)

    # Remove circles that have moved outside the sumo ring
    for circle in circles_to_remove:
        circles.remove(circle)

def handle_collision(circle1, circle2):
    """Handle collision between two circles."""
    distance = math.sqrt((circle1["center"][0] - circle2["center"][0])**2 +
                         (circle1["center"][1] - circle2["center"][1])**2)
    if distance < 2 * circle_radius:  # Check collision with diameter (2 * radius)
        # Calculate overlap and direction of collision
        overlap = 2 * circle_radius - distance
        collision_direction = [circle2["center"][0] - circle1["center"][0],
                               circle2["center"][1] - circle1["center"][1]]
        collision_length = math.sqrt(collision_direction[0]**2 + collision_direction[1]**2)

        if collision_length > 0:
            # Normalize collision direction
            collision_direction = [collision_direction[0] / collision_length,
                                   collision_direction[1] / collision_length]

            # Resolve collision by pushing the circles away
            move_distance = overlap / 2
            circle1["center"][0] -= move_distance * collision_direction[0]
            circle1["center"][1] -= move_distance * collision_direction[1]
            circle2["center"][0] += move_distance * collision_direction[0]
            circle2["center"][1] += move_distance * collision_direction[1]

def rush_to_cursor():
    """Move the player circle towards the cursor during rush."""
    global rushing
    # Get current mouse position
    mouse_x, mouse_y = pygame.mouse.get_pos()

    # Calculate direction vector from player circle to cursor
    if player_circle is not None:
        direction = [mouse_x - player_circle["center"][0], mouse_y - player_circle["center"][1]]
        length = math.sqrt(direction[0]**2 + direction[1]**2)

        if length > 0:
            # Normalize direction vector
            direction = [direction[0] / length, direction[1] / length]

            # Calculate rush movement towards cursor
            player_circle["velocity"][0] = direction[0] * rush_speed
            player_circle["velocity"][1] = direction[1] * rush_speed

# Main game loop
running = True

while running:
    screen.fill((255, 255, 255))  # Clear screen

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and not rushing and player_circle is not None:
                rushing = True
                rush_start_time = pygame.time.get_ticks()

    # Handle player input (move player circle)
    keys = pygame.key.get_pressed()
    if player_circle is not None:
        if keys[pygame.K_a]:
            player_circle["center"][0] -= 3  # Move left (A key)
        if keys[pygame.K_d]:
            player_circle["center"][0] += 3  # Move right (D key)
        if keys[pygame.K_w]:
            player_circle["center"][1] -= 3  # Move up (W key)
        if keys[pygame.K_s]:
            player_circle["center"][1] += 3  # Move down (S key)

    # Ensure all circles stay inside the sumo ring and remove those that leave
    place_circles_in_sumo_ring()

    # Handle rush movement towards cursor
    if rushing and player_circle is not None:
        current_time = pygame.time.get_ticks()
        if current_time - rush_start_time < rush_duration * 1000:  # Check if still within rush duration
            rush_to_cursor()
        else:
            rushing = False  # Stop rushing after duration expires
            player_circle["velocity"] = [0, 0]  # Stop the player circle

    # Handle collision between player circle and other circles
    if player_circle is not None:
        for circle in circles:
            handle_collision(player_circle, circle)

    # Update player circle position based on velocity
    if player_circle is not None:
        player_circle["center"][0] += player_circle["velocity"][0] * clock.get_time() / 1000
        player_circle["center"][1] += player_circle["velocity"][1] * clock.get_time() / 1000

    # Draw sumo ring boundary
    pygame.draw.circle(screen, (255, 0, 0), sumo_ring_center, sumo_ring_radius, 3)

    # Draw circles
    if player_circle is not None:
        pygame.draw.circle(screen, (0, 0, 255), player_circle["center"], circle_radius)  # Draw player circle in blue
    for circle in circles:
        pygame.draw.circle(screen, (255, 0, 0), circle["center"], circle_radius)  # Draw other circles in red

    pygame.display.flip()
    clock.tick(60)  # Limit to 60 FPS

pygame.quit()
