import pygame
import random
import player
import threading
import time
import json

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

        self.player_circle = {"postion": None, "velocity": [0,0], "radius": 40} # Contains information about the sumo of the player. e.g position, speed, radius
        self.enemy_circle = {"postion": None, "velocity": [0,0], "radius": 40} # Contains information about the sumo enemy of the player. e.g position, speed, radius

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
                self.peerPositions[addr[1]] = dataPeer
                print(self.peerPositions)
                self.peer.getSocket().sendto("INIT-OK".encode(), addr)
            elif "UPDATE" in data:
                #print(data.split(" ", 1)[1])
                newData = json.loads(data.split(" ",1)[1]) # Format; UPDATE {NEWDATA}
                self.peerPositions = newData
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

        peerAddr = list(self.peer.getConnections())[0]

        dataPeer = {
                "x": x,
                "y": y  
            }
        self.peerPositions[self.peer.getPort()] = dataPeer # This adds the player it self to the players position data structure
        payload = "INIT " + str(x) + " " + str(y) # Protocol: INIT playerStartPositon.x playerStartPosition.y 

        sendInit_thread = threading.Thread(target=self.sendInitPositions,args=(payload,), daemon=True)
        sendInit_thread.start()

    
    def run(self):
        # start listinng thread
        recv_thread = threading.Thread(target=self.listenForData, daemon=True)
        recv_thread.start()

        print(self.peer.getConnections())

        self.initPositions() # Inits positions from all peers

        #x = random.randint(0,SCREEN_WIDTH)
        #y = random.randint(0,SCREEN_HEIGHT)

        #payload = "INIT " + str(x) + " " + str(y) # Protocol: INIT playerStartPositon.x playerStartPosition.y 
        #print(list(self.peer.getConnections())[0])


        #self.peer.getSocket().sendto(payload.encode(), list(self.peer.getConnections())[0])
        #self.peer.getSocket().sendto(payload.encode(), list(self.peer.getConnections())[0])



        while self.gameStateRun:
            self.screen.fill((255,255,255)) # White screen

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.gameStateRun = False
                    pygame.quit()
                    exit(0)

            for key, value in self.peerPositions.items(): # Draw the players
                #print(value)
                pygame.draw.circle(self.screen, self.player.getColor(), (value['x'],value['y']),50)

             # Handle player input (move player circle)
            keys = pygame.key.get_pressed()
            if keys[pygame.K_a]:
                #print("A was pressed")
                self.peerPositions[str(self.peer.getPort())]['x'] -= 3
            if keys[pygame.K_d]:
                #print("D was pressed")
                self.peerPositions[str(self.peer.getPort())]['x'] += 3
            if keys[pygame.K_w]:
                #print("W was pressed")
                self.peerPositions[str(self.peer.getPort())]['y'] -= 3
                #print(self.peerPositions[str(self.peer.getPort())]['y'])
            if keys[pygame.K_s]:
                #print("S was pressed")
                self.peerPositions[str(self.peer.getPort())]['y'] += 3

            #pygame.draw.circle(self.screen, self.player.getColor(), (x, y),50)

            # Send data to other client (every frame)

            #print(self.peerPositions)

             # Shrink the sumo ring every 5 seconds
            self.shrink_timer += self.clock.get_time() / 1000  # Convert milliseconds to seconds
            if self.shrink_timer >= self.shrink_interval:
                self.sumo_ring_radius *= self.shrink_scale  # Shrink the sumo ring
                self.shrink_timer = 0  # Reset shrink timer

            # Draw sumo ring boundary
            pygame.draw.circle(self.screen, (255, 0, 0), self.sumo_ring_center, int(self.sumo_ring_radius), 3)

            peerPositionJSON = json.dumps(self.peerPositions)

            payload = "UPDATE " + peerPositionJSON            

            self.peer.getSocket().sendto(payload.encode(), list(self.peer.getConnections())[0]) 

            pygame.display.update()
            self.clock.tick(FPS)  # Limits FPS
