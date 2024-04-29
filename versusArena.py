import pygame
import random
import threading
import time
import json
import math

FPS = 60

SCREEN_WIDTH = 1300
SCREEN_HEIGHT = 800

class VersusArena:
    def __init__(self, screen, gameState, player, peer, gameOver):
        pygame.init()
        pygame.font.init()

        self.gameFont = pygame.font.SysFont('Comic Sans MS', 40)

        self.clock = pygame.time.Clock()

        self.screen = screen
        self.gameState = gameState
        self.peer = peer
        self.player = player
        self.gameOver = gameOver

        self.player_circle = {"position": [0,0], "velocity": [0,0], "radius": 40, "name": self.player.getName()}
        self.enemy_circle = {"position": [0,0], "velocity": [0,0], "radius": 40, "name": None}

        self.sumo_ring_radius = 450
        self.sumo_ring_center = [SCREEN_WIDTH/2, SCREEN_HEIGHT/2]

        self.circle_radius = 40 # Radius of the player

        #States for rushing
        self.rush_duration = 0.5
        self.rush_speed = 300
        self.rushing = False
        self.rush_start_time = 0

        # States of circle shrink
        self.shrink_timer = 0
        self.timerScreen = 10
        self.shrink_interval = 10
        self.shrink_scale = 0.9
        self.colorShrinkTimer = (0,0,0) # Starts with black

        # Game STates
        self.gameStateRun = True
        self.playerPositionInit = None
        self.winnerOfTheGame = None

    def setPeer(self, peer): # Setter for peer
        self.peer = peer

    def listenForData(self): # Listens for data from peer
        while True:
            data, addr = self.peer.getSocket().recvfrom(65535)
            data = data.decode()

            if "INIT-OK" == data: # Ack from peer
                self.playerPositionInit = True
            elif "INIT" in data: # Init handeling
                self.enemy_circle['position'] = [int(data.split(" ")[1]), int(data.split(" ")[2])]
                self.enemy_circle['name'] = data.split(" ")[3]
                self.peer.getSocket().sendto("INIT-OK".encode(), addr)
            elif "UPDATE" in data: # New data from peer
                newData = json.loads(data.split(" ",1)[1])
                self.enemy_circle = newData

    def sendInitPositions(self, data): # Sends init position to other peer
        while True:
            if self.playerPositionInit == True:
                break
            self.peer.getSocket().sendto(data.encode(), list(self.peer.getConnections())[0])
            time.sleep(0.1) # Sends every 0.1 seconds

    def initPositions(self):
        randomPointInRing = self.randomPointInCircle(self.sumo_ring_radius-(0.3 * self.sumo_ring_radius), self.sumo_ring_center[0], self.sumo_ring_center[1])
        self.player_circle['position'] = [math.ceil(randomPointInRing[0]),math.ceil(randomPointInRing[1])]

        payload = "INIT " + str(math.ceil(randomPointInRing[0])) + " " + str(math.ceil(randomPointInRing[1])) + " " + self.player.getName()

        sendInit_thread = threading.Thread(target=self.sendInitPositions,args=(payload,), daemon=True)
        sendInit_thread.start()

    def randomPointInCircle(self, radius, centerX, centerY): # Uses circle formula to find a random point in a circle
        alpha = 2 * math.pi * random.random()
        r = radius * math.sqrt(random.random())

        x = r * math.cos(alpha) + centerX
        y = r * math.sin(alpha) + centerY
        return (x,y)

    def rush_to_cursor(self):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        if self.player_circle is not None:
            direction = [mouse_x - self.player_circle["position"][0], mouse_y - self.player_circle["position"][1]]
            length = math.sqrt(direction[0]**2 + direction[1]**2)
            if length > 0:
                direction = [direction[0] / length, direction[1] / length]
                self.player_circle["velocity"][0] = direction[0] * self.rush_speed
                self.player_circle["velocity"][1] = direction[1] * self.rush_speed

    def handle_collision(self, circle1, circle2):
        distance = math.sqrt((circle1["position"][0] - circle2["position"][0])**2 +
                            (circle1["position"][1] - circle2["position"][1])**2)
        

        if distance < 2 * self.circle_radius:
            overlap = 2 * self.circle_radius - distance
            collision_direction = [circle2["position"][0] - circle1["position"][0],
                                circle2["position"][1] - circle1["position"][1]]
            
            collision_length = math.sqrt(collision_direction[0]**2 + collision_direction[1]**2)

            if collision_length > 0:
                collision_direction = [collision_direction[0] / collision_length,
                                    collision_direction[1] / collision_length]
                move_distance = overlap / 2

                circle1["position"][0] -= move_distance * collision_direction[0]
                circle1["position"][1] -= move_distance * collision_direction[1]
                circle2["position"][0] += move_distance * collision_direction[0]
                circle2["position"][1] += move_distance * collision_direction[1]

    def checkIfGameOver(self):
        if self.player_circle is not None:
            player_distance_to_center = math.sqrt((self.player_circle["position"][0] - self.sumo_ring_center[0])**2 +
                                                (self.player_circle["position"][1] - self.sumo_ring_center[1])**2)
            

            if player_distance_to_center + self.player_circle["radius"] > self.sumo_ring_radius:
                self.winnerOfTheGame = self.enemy_circle['name']
                return True

        distance_to_center = math.sqrt((self.enemy_circle["position"][0] - self.sumo_ring_center[0])**2 +
                                        (self.enemy_circle["position"][1] - self.sumo_ring_center[1])**2)
        
        if distance_to_center + self.enemy_circle["radius"] > self.sumo_ring_radius:
            self.winnerOfTheGame = self.player.getName()
            return True

        return False

    def resetStates(self):
        self.player_circle = {"position": [0,0], "velocity": [0,0], "radius": 40, "name": self.player.getName()}
        self.enemy_circle = {"position": [0,0], "velocity": [0,0], "radius": 40, "name": None}
        self.gameStateRun = True
        self.playerPositionInit = None
        self.winnerOfTheGame = None
        self.sumo_ring_radius = 450

    def displayCountdown(self):
        countdown_font = pygame.font.SysFont('Comic Sans MS', 100)
        for i in range(5, 0, -1):  # Countdown from 5 to 1 seconds
            self.screen.fill((255, 255, 255))  # Clear the screen, white countdown

            countdown_text = countdown_font.render(str(i), True, (0, 0, 0))
            text_rect = countdown_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            self.screen.blit(countdown_text, text_rect)
            
            pygame.display.update()
            pygame.time.wait(1000)  # Wait every 1 second so counter goes down per second

    def run(self):
        self.resetStates() # Reset previous game states

        # Start listening thread
        recv_thread = threading.Thread(target=self.listenForData, daemon=True)
        recv_thread.start()

        self.initPositions() 

        self.displayCountdown() # Assures sync between clients

        while self.gameStateRun and self.playerPositionInit:
            self.screen.fill((255, 255, 255)) # White screen arena

            if self.checkIfGameOver() == True and self.playerPositionInit == True:
                print("Game over")
                self.gameStateRun = False
                self.gameState.setCurrentState('1v1GameOver')
                self.gameOver.setWinner(self.winnerOfTheGame)


            if math.ceil(self.timerScreen - self.shrink_timer) <= 5:
                self.colorShrinkTimer = (255, 0, 0)
            else:
                self.colorShrinkTimer = (0,0,0)

            gameScreen_waveTimer = self.gameFont.render('0:' + str(math.ceil(self.timerScreen - self.shrink_timer)), True, self.colorShrinkTimer)
            gameScreen_rect = gameScreen_waveTimer.get_rect(center=(SCREEN_WIDTH - 30, 20))
            self.screen.blit(gameScreen_waveTimer, gameScreen_rect)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.gameStateRun = False
                    pygame.quit()
                    exit(0)
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE and not self.rushing and self.player_circle is not None:
                        self.rushing = True
                        self.rush_start_time = pygame.time.get_ticks()

            if self.rushing and self.player_circle is not None:
                current_time = pygame.time.get_ticks()
                if current_time - self.rush_start_time < self.rush_duration * 1000:
                    self.rush_to_cursor()
                else:
                    self.rushing = False
                    self.player_circle["velocity"] = [0, 0]

            pygame.draw.circle(self.screen, self.player.getColor(), (self.player_circle['position'][0],self.player_circle['position'][1]),40)
            pygame.draw.circle(self.screen, self.player.getColor(), (self.enemy_circle['position'][0],self.enemy_circle['position'][1]),40)

            # Player movement wasd
            keys = pygame.key.get_pressed()
            if keys[pygame.K_a]:
                self.player_circle['position'][0] -= 3
            if keys[pygame.K_d]:
                self.player_circle['position'][0] += 3
            if keys[pygame.K_w]:
                self.player_circle['position'][1] -= 3
            if keys[pygame.K_s]:
                self.player_circle['position'][1] += 3

            if self.player_circle is not None: # Collision handeling
                self.handle_collision(self.player_circle, self.enemy_circle)

            if self.player_circle is not None: # Update position based on speed :)
                self.player_circle["position"][0] += self.player_circle["velocity"][0] * self.clock.get_time() / 1000
                self.player_circle["position"][1] += self.player_circle["velocity"][1] * self.clock.get_time() / 1000

            self.shrink_timer += self.clock.get_time() / 1000
            
            if self.shrink_timer >= self.shrink_interval:
                self.sumo_ring_radius *= self.shrink_scale # Makes the circle smaller with the shrink scalar
                self.shrink_timer = 0
                self.timerScreen = 10 # Resets timer back to 10 on screen


            pygame.draw.circle(self.screen, (255, 0, 0), self.sumo_ring_center, int(self.sumo_ring_radius), 30) # Draws the sumo ring

            # Sends player data to other peer
            peerPositionJSON = json.dumps(self.player_circle)
            payload = "UPDATE " + peerPositionJSON
            self.peer.getSocket().sendto(payload.encode(), list(self.peer.getConnections())[0])

            pygame.display.update()
            self.clock.tick(FPS) # Limits game to FPS(60)