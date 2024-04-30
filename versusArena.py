import pygame
import random
import threading
import time
import json
import math

#TODO: cheat detect polish, player leave, test, FEAUTRES DONE: (Ip address bij host laten zien, background toevoegen aan 1v1 map, Countdown mooier maken, player heeft zwarte border om zich heen, color selector)

#Constants
FPS = 60

SCREEN_WIDTH = 1300
SCREEN_HEIGHT = 800

GAME_TICK_RATE = 1 / FPS  # Game tick rate in seconds
MAX_MOVE_DISTANCE_PER_TICK = 10  # Threashold max allowed move distance

class VersusArena:
    def __init__(self, screen, gameState, player, peer, gameOver):
        pygame.init() # Init pygame
        pygame.font.init() # Init font

        self.gameFont = pygame.font.SysFont('Comic Sans MS', 40)
        self.clock = pygame.time.Clock()

        # Set arguments to class
        self.screen = screen
        self.gameState = gameState
        self.peer = peer
        self.player = player
        self.gameOver = gameOver

        
        self.player_circle = {"position": [0,0], "velocity": [0,0], "radius": 40, "name": self.player.getName(),"score": 0}
        self.enemy_circle = {"position": [0,0], "velocity": [0,0], "radius": 40, "name": None, "score": 0}

        self.sumo_ring_radius = 450
        self.sumo_ring_center = [SCREEN_WIDTH/2, SCREEN_HEIGHT/2]
        self.circle_radius = 40

        # Rush variables
        self.rush_duration = 0.5
        self.rush_speed = 300
        self.rushing = False
        self.rush_start_time = 0

        # Shrink variables
        self.shrink_timer = 0
        self.timerScreen = 10
        self.shrink_interval = 10
        self.shrink_scale = 0.9
        self.colorShrinkTimer = (0,0,0)

        # Game state variables
        self.gameStateRun = True
        self.playerPositionInit = None
        self.winnerOfTheGame = None
        self.score = 0

        # Lockstep simulation variables
        self.game_tick_rate = GAME_TICK_RATE
        self.last_tick_time = 0
        self.lockstep_enabled = True  # Toggle lockstep simulation

        # Cheat detection variables
        self.last_player_position = None
        self.cheat_detection_enabled = True  # Toggle cheat detection

        # State to check if a new round is set
        self.newRoundState = False

    def setPeer(self, peer): # Setter for peer variable
        self.peer = peer

    def listenForData(self): # Listens for incoming data from other peer
        while True:
            data, addr = self.peer.getSocket().recvfrom(65535)
            data = data.decode()

            if "INIT-OK" == data:
                self.playerPositionInit = True
            elif "INIT" in data:
                self.enemy_circle['position'] = [int(data.split(" ")[1]), int(data.split(" ")[2])]
                self.enemy_circle['name'] = data.split(" ")[3]
                self.peer.getSocket().sendto("INIT-OK".encode(), addr)
            elif "UPDATE" in data:
                #print(data)
                newData = json.loads(data.split(" ",1)[1])
                self.enemy_circle = newData

    def sendInitPositions(self, data): # Send init positions to other peer
        while True:
            if self.playerPositionInit == True:
                break
            self.peer.getSocket().sendto(data.encode(), list(self.peer.getConnections())[0])
            time.sleep(0.1)

    def initPositions(self): # Inits position from client perspectuve and starts thread to poll other peer
        randomPointInRing = self.randomPointInCircle(self.sumo_ring_radius-(0.3 * self.sumo_ring_radius), self.sumo_ring_center[0], self.sumo_ring_center[1])
        self.player_circle['position'] = [math.ceil(randomPointInRing[0]),math.ceil(randomPointInRing[1])]

        payload = "INIT " + str(math.ceil(randomPointInRing[0])) + " " + str(math.ceil(randomPointInRing[1])) + " " + self.player.getName()

        sendInit_thread = threading.Thread(target=self.sendInitPositions,args=(payload,), daemon=True)
        sendInit_thread.start()

    def randomPointInCircle(self, radius, centerX, centerY): # Uses circle formula to generate random point on circle
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
                self.enemy_circle["score"] += 1
                return True

        distance_to_center = math.sqrt((self.enemy_circle["position"][0] - self.sumo_ring_center[0])**2 +
                                        (self.enemy_circle["position"][1] - self.sumo_ring_center[1])**2)
        
        if distance_to_center + self.enemy_circle["radius"] > self.sumo_ring_radius:
            self.winnerOfTheGame = self.player.getName()
            self.player_circle["score"] += 1
            self.score += 1
            return True

        return False

    def resetStates(self): # REsets state for different game from same client
        self.player_circle = {"position": [0,0], "velocity": [0,0], "radius": 40, "name": self.player.getName(),"score": 0}
        self.enemy_circle = {"position": [0,0], "velocity": [0,0], "radius": 40, "name": None, "score": 0}
        self.gameStateRun = True
        self.playerPositionInit = None
        self.winnerOfTheGame = None
        self.sumo_ring_radius = 450
        self.score = 0

    def newRound(self): # Sets states for new round, e.g circle is reset
        self.sumo_ring_radius = 450

        randomPointInRingPlayer = self.randomPointInCircle(self.sumo_ring_radius-(0.3 * self.sumo_ring_radius), self.sumo_ring_center[0], self.sumo_ring_center[1])
        randomPointInRingEnemy = self.randomPointInCircle(self.sumo_ring_radius-(0.3 * self.sumo_ring_radius), self.sumo_ring_center[0], self.sumo_ring_center[1])

        self.newRoundState = True
        
        self.player_circle = {"position": [randomPointInRingPlayer[0],randomPointInRingPlayer[1]], "velocity": [0,0], "radius": 40, "name": self.player.getName(), "score": self.player_circle["score"]}
        self.enemy_circle = {"position": [randomPointInRingEnemy[0],randomPointInRingEnemy[1]], "velocity": [0,0], "radius": 40, "name": self.enemy_circle["name"], "score": self.player_circle["score"]}

        self.shrink_timer = 0
        self.colorShrinkTimer = 10

    def displayCountdown(self): # Shows a counter before starting the game, preps player to be ready
        countdown_font = pygame.font.SysFont('Comic Sans MS', 100)
        for i in range(5, 0, -1):
            self.screen.fill((255, 255, 255))

            countdown_text = countdown_font.render(str(i), True, (0, 0, 0))
            text_rect = countdown_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            self.screen.blit(countdown_text, text_rect)
            
            pygame.display.update()
            pygame.time.wait(1000)

    def detectCheat(self):
        if self.last_player_position is not None:
            dx = self.enemy_circle['position'][0] - self.last_player_position[0]
            dy = self.enemy_circle['position'][1] - self.last_player_position[1]
            distance_moved = math.sqrt(dx ** 2 + dy ** 2)
            print(distance_moved)

            if distance_moved > MAX_MOVE_DISTANCE_PER_TICK and self.newRoundState == True: # Cheat detection False positive, random spawn in ring is detected as teleporting
                self.newRoundState = False
            elif distance_moved > MAX_MOVE_DISTANCE_PER_TICK and self.newRoundState == False: # Player moved to fast
                print("Movement to fast, but resolved by lockstep")

        self.last_player_position = self.enemy_circle['position'] # Stores last position

    def run(self):
        self.resetStates()

        recv_thread = threading.Thread(target=self.listenForData, daemon=True)
        recv_thread.start()

        self.initPositions() 

        self.displayCountdown()

        while self.gameStateRun:

            if self.cheat_detection_enabled: # Cheat detection method
                self.detectCheat()

            current_time = time.time()
            delta_time = current_time - self.last_tick_time
            self.last_tick_time = current_time

            if self.lockstep_enabled and delta_time < self.game_tick_rate: # Assures that the game is synced per frame
                time.sleep(self.game_tick_rate - delta_time)

            self.screen.fill((255, 255, 255))

            if self.player_circle["score"] == 3 or self.enemy_circle["score"] == 3:
                print("Game over")
                self.gameStateRun = False
                self.gameState.setCurrentState('1v1GameOver')
                self.gameOver.setWinner(self.winnerOfTheGame)

            if self.checkIfGameOver() == True and self.playerPositionInit:
                print("Round over")
                self.newRound()

            if math.ceil(self.timerScreen - self.shrink_timer) <= 5: # Shows different color depending how close the timer is to the end.
                self.colorShrinkTimer = (255, 0, 0)
            else:
                self.colorShrinkTimer = (0,0,0)

            # Score displayed on screen
            gameScreen_Score = self.gameFont.render('Score: ' + str(self.score), True, (0,0,0))
            gameScreen_rect = gameScreen_Score.get_rect(center=(SCREEN_WIDTH - SCREEN_WIDTH/7, 20))
            self.screen.blit(gameScreen_Score, gameScreen_rect)


            # Time displayed on screen
            gameScreen_waveTimer = self.gameFont.render('0:' + str(math.ceil(self.timerScreen - self.shrink_timer)), True, self.colorShrinkTimer)
            gameScreen_rect = gameScreen_waveTimer.get_rect(center=(SCREEN_WIDTH - 30, 20))
            self.screen.blit(gameScreen_waveTimer, gameScreen_rect)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.gameStateRun = False
                    pygame.quit()
                    exit(0)
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE and not self.rushing and self.player_circle is not None: # Rush state set
                        self.rushing = True
                        self.rush_start_time = pygame.time.get_ticks()

            if self.rushing and self.player_circle is not None: 
                current_time = pygame.time.get_ticks()
                if current_time - self.rush_start_time < self.rush_duration * 1000:
                    self.rush_to_cursor()
                else:
                    self.rushing = False
                    self.player_circle["velocity"] = [0, 0]

            # Draw players on the screen
            pygame.draw.circle(self.screen, self.player.getColor(), (self.player_circle['position'][0],self.player_circle['position'][1]),40)
            pygame.draw.circle(self.screen, self.player.getColor(), (self.enemy_circle['position'][0],self.enemy_circle['position'][1]),40)


            # Movement for player wasd
            keys = pygame.key.get_pressed()
            if keys[pygame.K_a]:
                self.player_circle['position'][0] -= 3
            if keys[pygame.K_d]:
                self.player_circle['position'][0] += 3
            if keys[pygame.K_w]:
                self.player_circle['position'][1] -= 3
            if keys[pygame.K_s]:
                self.player_circle['position'][1] += 3

            if self.player_circle is not None:
                self.handle_collision(self.player_circle, self.enemy_circle) # Collision detection

            if self.player_circle is not None: # Changes position depending on the speed
                self.player_circle["position"][0] += self.player_circle["velocity"][0] * self.clock.get_time() / 1000
                self.player_circle["position"][1] += self.player_circle["velocity"][1] * self.clock.get_time() / 1000

            # Shrink timer updated
            self.shrink_timer += self.clock.get_time() / 1000

            if self.shrink_timer >= self.shrink_interval: # If timer exceeds threshold than make the circle smaller and reset timers.
                self.sumo_ring_radius *= self.shrink_scale
                self.shrink_timer = 0
                self.timerScreen = 10

            pygame.draw.circle(self.screen, (255, 0, 0), self.sumo_ring_center, int(self.sumo_ring_radius), 30) # Draw the sumo ring

            # Sends data to client
            peerPositionJSON = json.dumps(self.player_circle)
            payload = "UPDATE " + peerPositionJSON
            self.peer.getSocket().sendto(payload.encode(), list(self.peer.getConnections())[0])

            pygame.display.update()
            self.clock.tick(FPS) # FPS locked