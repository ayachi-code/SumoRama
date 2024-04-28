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
    def __init__(self, screen, gameState, player, peer):
        pygame.init()
        pygame.font.init()
        self.clock = pygame.time.Clock()

        self.screen = screen  # Set display resolution
        self.gameState = gameState
        self.peer = peer
        self.player = player

        self.peerPositions = {} # Contains x,y positions of peers

        self.player_circle = {"position": [0,0], "velocity": [0,0], "radius": 40} # Contains information about the sumo of the player. e.g position, speed, radius

        self.enemy_circle = {"position": [0,0], "velocity": [0,0], "radius": 40} # Contains information about the sumo enemy of the player. e.g position, speed, radius

        # Define sumo ring properties
        self.sumo_ring_radius = 450  # Larger radius for the sumo ring
        self.sumo_ring_center = [SCREEN_WIDTH/2, SCREEN_HEIGHT/2]  # Center of the screen (1920x1080 resolution) 

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

    def setPeer(self, peer):
        self.peer = peer

    def listenForData(self): # Listens for data, other player
        while True:
            data, addr = self.peer.getSocket().recvfrom(65535) # Max udp size
            data = data.decode()

            if "INIT-OK" == data:
                self.playerPositionInit = True
            elif "INIT" in data: # We get start positions from other peer
                dataPeer = {
                    "x": int(data.split(" ")[1]),
                    "y": int(data.split(" ")[2])  
                }
                
                self.enemy_circle['position'] = [int(data.split(" ")[1]), int(data.split(" ")[2])]
                
                self.peerPositions[addr[1]] = dataPeer

                print(self.peerPositions)
                self.peer.getSocket().sendto("INIT-OK".encode(), addr)
            elif "UPDATE" in data:
                #print(data.split(" ", 1)[1])
                newData = json.loads(data.split(" ",1)[1]) # Format; UPDATE {NEWDATA}
                self.enemy_circle = newData
                #print("Got new data from peer")

            #print(data)

    def sendInitPositions(self, data):
        while True:
            if self.playerPositionInit == True:
                break
            #print("Sending positions " + data)
            self.peer.getSocket().sendto(data.encode(), list(self.peer.getConnections())[0])
            time.sleep(0.1)


    def initPositions(self):
        x = random.randint(0,SCREEN_WIDTH)
        y = random.randint(0,SCREEN_HEIGHT)

        dataPeer = { 
                "x": x,
                "y": y  
        }

        self.player_circle['position'] = [x,y] # init positions

        self.peerPositions[self.peer.getPort()] = dataPeer # This adds the player it self to the players position data structure
        payload = "INIT " + str(x) + " " + str(y) # Protocol: INIT playerStartPositon.x playerStartPosition.y 

        sendInit_thread = threading.Thread(target=self.sendInitPositions,args=(payload,), daemon=True)
        sendInit_thread.start()

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


           # for key, value in self.peerPositions.items(): # Draw the players
                #print(value)
            #    pygame.draw.circle(self.screen, self.player.getColor(), (value['x'],value['y']),50)

            pygame.draw.circle(self.screen, self.player.getColor(), (self.player_circle['position'][0],self.player_circle['position'][1]),40)
            pygame.draw.circle(self.screen, self.player.getColor(), (self.enemy_circle['position'][0],self.enemy_circle['position'][1]),40)

             # Handle player input (move player circle)
            keys = pygame.key.get_pressed()
            if keys[pygame.K_a]:
                #print("A was pressed")
                print(self.enemy_circle)
                print(self.player_circle)
                #self.peerPositions[str(self.peer.getPort())]['x'] -= 3
                self.player_circle['position'][0] -= 3
            if keys[pygame.K_d]:
                #print("D was pressed")
                #self.peerPositions[str(self.peer.getPort())]['x'] += 3
                self.player_circle['position'][0] += 3

            if keys[pygame.K_w]:
                #print("W was pressed")
                #self.peerPositions[str(self.peer.getPort())]['y'] -= 3
                self.player_circle['position'][1] -= 3

                #print(self.peerPositions[str(self.peer.getPort())]['y'])
            if keys[pygame.K_s]:
                #print("S was pressed")
                #self.peerPositions[str(self.peer.getPort())]['y'] += 3
                self.player_circle['position'][1] += 3

            #pygame.draw.circle(self.screen, self.player.getColor(), (x, y),50)

            # Send data to other client (every frame)

            #print(self.peerPositions)

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
            self.clock.tick(FPS)  # Limits FPS
