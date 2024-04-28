import pygame
import random
import player
import threading
import time
import json
import math

FPS = 60

SCREEN_WIDTH = 1300
SCREEN_HEIGHT = 800

# 1v1 arena code

class VersusArena:
    def __init__(self, screen, gameState, player, peer, gameOver):
        pygame.init()
        pygame.font.init()
        self.clock = pygame.time.Clock()

        self.screen = screen  # Set display resolution
        self.gameState = gameState
        self.peer = peer
        self.player = player
        self.gameOver = gameOver

        self.player_circle = {"position": [0,0], "velocity": [0,0], "radius": 40, "name": self.player.getName()} # Contains information about the sumo of the player. e.g position, speed, radius, name

        self.enemy_circle = {"position": [0,0], "velocity": [0,0], "radius": 40, "name": None} # Contains information about the sumo enemy of the player. e.g position, speed, radius, name

        # Define sumo ring properties
        self.sumo_ring_radius = 450  # Larger radius for the sumo ring
        self.sumo_ring_center = [SCREEN_WIDTH/2, SCREEN_HEIGHT/2]  # Center of the screen (1920x1080 resolution) 

        self.circle_radius = 40  # Initial radius of all circles

        # Define rush variables
        self.rush_duration = 0.5  # Rush duration in seconds
        self.rush_speed = 300  # Rush speed in pixels per second
        self.rushing = False
        self.rush_start_time = 0

        # Define shrink variables
        self.shrink_timer = 0
        self.shrink_interval = 5  # Time interval in seconds to shrink the sumo ring
        self.shrink_scale = 0.9  # Scaling factor for shrinking the sumo ring

        #States
        self.gameStateRun = True
        self.playerPositionInit = None
        self.winnerOfTheGame = None # Stores the winner

    def setPeer(self, peer):
        self.peer = peer


    def listenForData(self): # Listens for data, other player
        while True:
            data, addr = self.peer.getSocket().recvfrom(65535) # Max udp size
            data = data.decode()

            if "INIT-OK" == data:
                self.playerPositionInit = True
            elif "INIT" in data: # We get start positions from other peer
                print(data)
                self.enemy_circle['position'] = [int(data.split(" ")[1]), int(data.split(" ")[2])]
                self.enemy_circle['name'] = data.split(" ")[3]
                self.peer.getSocket().sendto("INIT-OK".encode(), addr)
            elif "UPDATE" in data:
                newData = json.loads(data.split(" ",1)[1]) # Format; UPDATE {NEWDATA}
                #print(newData)
                self.enemy_circle = newData

    def sendInitPositions(self, data):
        while True:
            if self.playerPositionInit == True:
                break
            self.peer.getSocket().sendto(data.encode(), list(self.peer.getConnections())[0])
            time.sleep(0.1)


    def initPositions(self):
        randomPointInRing = self.randomPointInCircle(self.sumo_ring_radius-(0.3 * self.sumo_ring_radius), self.sumo_ring_center[0], self.sumo_ring_center[1]) # --> (x,y)

        self.player_circle['position'] = [math.ceil(randomPointInRing[0]),math.ceil(randomPointInRing[1])] # init positions 

        payload = "INIT " + str(math.ceil(randomPointInRing[0])) + " " + str(math.ceil(randomPointInRing[1])) + " " + self.player.getName() # Protocol: INIT playerStartPositon.x playerStartPosition.y NAME 

        sendInit_thread = threading.Thread(target=self.sendInitPositions,args=(payload,), daemon=True)
        sendInit_thread.start()


    def randomPointInCircle(self, radius, centerX, centerY):
        # random angle
        alpha = 2 * math.pi * random.random()
        # random radius
        r = radius * math.sqrt(random.random())
        # calculating coordinates
        x = r * math.cos(alpha) + centerX
        y = r * math.sin(alpha) + centerY
        return (x,y)

    def rush_to_cursor(self):
        # Get current mouse position
        mouse_x, mouse_y = pygame.mouse.get_pos()

        # Calculate direction vector from player circle to cursor
        if self.player_circle is not None:
            direction = [mouse_x - self.player_circle["position"][0], mouse_y - self.player_circle["position"][1]]
            length = math.sqrt(direction[0]**2 + direction[1]**2)

            if length > 0:
                # Normalize direction vector
                direction = [direction[0] / length, direction[1] / length]

                # Calculate rush movement towards cursor
                self.player_circle["velocity"][0] = direction[0] * self.rush_speed
                self.player_circle["velocity"][1] = direction[1] * self.rush_speed

    def handle_collision(self, circle1, circle2):
        distance = math.sqrt((circle1["position"][0] - circle2["position"][0])**2 +
                            (circle1["position"][1] - circle2["position"][1])**2)
        if distance < 2 * self.circle_radius:  # Check collision with diameter (2 * radius)
            # Calculate overlap and direction of collision
            overlap = 2 * self.circle_radius - distance
            collision_direction = [circle2["position"][0] - circle1["position"][0],
                                circle2["position"][1] - circle1["position"][1]]
            collision_length = math.sqrt(collision_direction[0]**2 + collision_direction[1]**2)

            if collision_length > 0:
                # Normalize collision direction
                collision_direction = [collision_direction[0] / collision_length,
                                    collision_direction[1] / collision_length]
                
                # Resolve collision by pushing the circles away
                move_distance = overlap / 2
                circle1["position"][0] -= move_distance * collision_direction[0]
                circle1["position"][1] -= move_distance * collision_direction[1]
                circle2["position"][0] += move_distance * collision_direction[0]
                circle2["position"][1] += move_distance * collision_direction[1]


    def checkIfGameOver(self):
        # Check and handle player circle
        if self.player_circle is not None:
            player_distance_to_center = math.sqrt((self.player_circle["position"][0] - self.sumo_ring_center[0])**2 +
                                                (self.player_circle["position"][1] - self.sumo_ring_center[1])**2)
            if player_distance_to_center + self.player_circle["radius"] > self.sumo_ring_radius:
                self.winnerOfTheGame = self.enemy_circle['name']
                return True # Game Over

        # Checks if other 1v1 peer is out of circle
        distance_to_center = math.sqrt((self.enemy_circle["position"][0] - self.sumo_ring_center[0])**2 +
                                        (self.enemy_circle["position"][1] - self.sumo_ring_center[1])**2)
        if distance_to_center + self.enemy_circle["radius"] > self.sumo_ring_radius:
            self.winnerOfTheGame = self.player.getName()
            return True
       
        return False # Not out of circle
    
    def run(self):
        # start listinng thread
        recv_thread = threading.Thread(target=self.listenForData, daemon=True)
        recv_thread.start()

        print(self.peer.getConnections())

        self.initPositions() # Inits positions from all peers

        while self.gameStateRun:
            self.screen.fill((255,255,255)) # White screen

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.gameStateRun = False
                    pygame.quit()
                    exit(0)
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE and not self.rushing and self.player_circle is not None:
                        self.rushing = True
                        self.rush_start_time = pygame.time.get_ticks()

            # Handle rush movement towards cursor
            if self.rushing and self.player_circle is not None:
                current_time = pygame.time.get_ticks()
                if current_time - self.rush_start_time < self.rush_duration * 1000:  # Check if still within rush duration
                    self.rush_to_cursor()
                else:
                    self.rushing = False  # Stop rushing after duration expires
                    self.player_circle["velocity"] = [0, 0]  # Stop the player circle

            pygame.draw.circle(self.screen, self.player.getColor(), (self.player_circle['position'][0],self.player_circle['position'][1]),40)
            pygame.draw.circle(self.screen, self.player.getColor(), (self.enemy_circle['position'][0],self.enemy_circle['position'][1]),40)

             # Handle player input (move player circle)
            keys = pygame.key.get_pressed()
            if keys[pygame.K_a]:
                self.player_circle['position'][0] -= 3
            if keys[pygame.K_d]:
                self.player_circle['position'][0] += 3
            if keys[pygame.K_w]:
                self.player_circle['position'][1] -= 3
            if keys[pygame.K_s]:
                self.player_circle['position'][1] += 3

            if self.checkIfGameOver() == True and self.playerPositionInit == True: # self.playerPositionInit makes sure players are loaded in before checking if game over
                self.gameStateRun = False
                self.gameState.setCurrentState('1v1GameOver')
                self.gameOver.setWinner(self.winnerOfTheGame)
                
            if self.player_circle is not None:
                self.handle_collision(self.player_circle, self.enemy_circle)

            if self.player_circle is not None:
                self.player_circle["position"][0] += self.player_circle["velocity"][0] * self.clock.get_time() / 1000
                self.player_circle["position"][1] += self.player_circle["velocity"][1] * self.clock.get_time() / 1000

             # Shrink the sumo ring every 5 seconds
            self.shrink_timer += self.clock.get_time() / 1000  # Convert milliseconds to seconds
            if self.shrink_timer >= self.shrink_interval:
                self.sumo_ring_radius *= self.shrink_scale  # Shrink the sumo ring
                self.shrink_timer = 0  # Reset shrink timer

            # Draw sumo ring boundary   
            pygame.draw.circle(self.screen, (255, 0, 0), self.sumo_ring_center, int(self.sumo_ring_radius), 3)

            peerPositionJSON = json.dumps(self.player_circle)

            payload = "UPDATE " + peerPositionJSON            

            self.peer.getSocket().sendto(payload.encode(), list(self.peer.getConnections())[0]) 

            pygame.display.update()
            self.clock.tick(FPS)  # Limits FPS#