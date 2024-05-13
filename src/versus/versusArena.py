import pygame
import random
import threading
import time
import json
import math
import button

#TODO: ROADMAP: Possible FEAUTRES for update: Color selector, name change

#Constants
FPS = 60

SCREEN_WIDTH = 1300
SCREEN_HEIGHT = 800

GAME_TICK_RATE = 1 / FPS  # Game tick rate in seconds
MAX_MOVE_DISTANCE_PER_TICK = 20  # Threashold max allowed move distance, I got this value by a lot of testing.

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

        
        # Player circles
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
        self.shrink_scale = 0.90
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

        self.aliveAck = None
        self.gameDonePeer = False

        self.peerColor = (255,0,0) # default color set

        self.round = 1

    def setPeer(self, peer): # Setter for peer variable
        self.peer = peer

    def convertStringToColor(self, color):  # Helper function that converts string color to rgb tuple
        if color == "RED":
            return (255, 0, 0)
        elif color == "BLACK":
            return (0, 0, 0)
        elif color == "GREEN":
            return (0, 255, 0)
        elif color == "BLUE":
            return (0, 0, 255)
        elif color == "YELLOW":
            return (255, 255, 0)
        else:
            return (255, 0, 0)  # Default red characte

    def listenForData(self): # Listens for incoming data from other peer
        while True:
            data, addr = self.peer.getSocket().recvfrom(65535)
            data = data.decode()

            if data == "ALIVE-OK": # We recieved ack from peer
                self.aliveAck = True     
                self.peer.increaseSequenceNumber()
            elif "ALIVE" in data:
                self.peer.getSocket().sendto("ALIVE-OK".encode(), addr)

            if data == "OUT-OF-RING": # ASSURES SYNC OF Circle collision!!
                self.gameDonePeer = True
                self.newRoundState = True

            # Protocool game loop
            if "INIT-OK" == data:
                self.playerPositionInit = True
            elif "INIT" in data:
                self.enemy_circle['position'] = [int(data.split(" ")[1]), int(data.split(" ")[2])]
                self.enemy_circle['name'] = data.split(" ")[3]

                self.peerColor = self.convertStringToColor(data.split(" ")[4])

                self.last_player_position = self.enemy_circle['position'] # Locks in posityion
                self.peer.getSocket().sendto("INIT-OK".encode(), addr)
            elif "UPDATE" in data:
                #print(data)
                newData = json.loads(data.split(" ",1)[1])
                self.enemy_circle = newData
                #self.last_player_position = self.enemy_circle['position']

    def sendInitPositions(self, data): # Send init positions to other peer, at the start of the game
        while True:
            if self.playerPositionInit == True:
                break
            self.peer.getSocket().sendto(data.encode(), list(self.peer.getConnections())[0])
            time.sleep(0.1)

    def initPositions(self): # Inits position from client perspectuve and starts thread to poll other peer
        randomPointInRing = self.randomPointInCircle(self.sumo_ring_radius-(0.3 * self.sumo_ring_radius), self.sumo_ring_center[0], self.sumo_ring_center[1])
        self.player_circle['position'] = [math.ceil(randomPointInRing[0]),math.ceil(randomPointInRing[1])]

        payload = "INIT " + str(math.ceil(randomPointInRing[0])) + " " + str(math.ceil(randomPointInRing[1])) + " " + self.player.getName() + " " + self.player.getColor()

        sendInit_thread = threading.Thread(target=self.sendInitPositions,args=(payload,), daemon=True)
        sendInit_thread.start()
 

    def randomPointInCircle(self, radius, centerX, centerY): # Uses circle formula to generate random point on circle, the circle here is the sumo ring.
        alpha = 2 * math.pi * random.random()
        r = radius * math.sqrt(random.random())

        x = r * math.cos(alpha) + centerX
        y = r * math.sin(alpha) + centerY
        return (x,y)

    def rush_to_cursor(self): # Method for the rush abbility in the game
        mouse_x, mouse_y = pygame.mouse.get_pos()

        if self.player_circle is not None:
            direction = [mouse_x - self.player_circle["position"][0], mouse_y - self.player_circle["position"][1]]
            length = math.sqrt(direction[0]**2 + direction[1]**2)

            if length > 0:
                direction = [direction[0] / length, direction[1] / length]
                self.player_circle["velocity"][0] = direction[0] * self.rush_speed
                self.player_circle["velocity"][1] = direction[1] * self.rush_speed

    def handle_collision(self, circle1, circle2): # Collision between 2 circles
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


    def giveRightPlayerPoints(self): # Give points to the player.
        if self.player_circle is not None:
            player_distance_to_center = math.sqrt((self.player_circle["position"][0] - self.sumo_ring_center[0])**2 + (self.player_circle["position"][1] - self.sumo_ring_center[1])**2)
                
            if player_distance_to_center + self.player_circle["radius"] > self.sumo_ring_radius:
                    return

            distance_to_center = math.sqrt((self.enemy_circle["position"][0] - self.sumo_ring_center[0])**2 + (self.enemy_circle["position"][1] - self.sumo_ring_center[1])**2)
            
            if distance_to_center + self.enemy_circle["radius"] > self.sumo_ring_radius:
                self.winnerOfTheGame = self.player.getName()
                self.player_circle["score"] += 1
                self.score += 1
                return


    def checkIfGameOver(self): # Checks if the game is over, if so than make other peer know.
        if self.player_circle is not None:
            player_distance_to_center = math.sqrt((self.player_circle["position"][0] - self.sumo_ring_center[0])**2 + (self.player_circle["position"][1] - self.sumo_ring_center[1])**2)
            
            if player_distance_to_center + self.player_circle["radius"] > self.sumo_ring_radius:
                self.peer.getSocket().sendto("OUT-OF-RING".encode(), list(self.peer.getConnections())[0])
                return True
 
        return False

    def resetStates(self): # Resets state for different game from same client
        self.player_circle = {"position": [0,0], "velocity": [0,0], "radius": 40, "name": self.player.getName(),"score": 0}
        self.enemy_circle = {"position": [0,0], "velocity": [0,0], "radius": 40, "name": None, "score": 0}
        self.gameStateRun = True
        self.playerPositionInit = None
        self.winnerOfTheGame = None
        self.sumo_ring_radius = 450
        self.score = 0
        self.round = 1
        self.last_player_position = None
        self.aliveAck = None

    def newRound(self): # Sets states for new round, e.g circle is reset
        self.sumo_ring_radius = 450

        randomPointInRingPlayer = self.randomPointInCircle(self.sumo_ring_radius-(0.3 * self.sumo_ring_radius), self.sumo_ring_center[0], self.sumo_ring_center[1])

        self.newRoundState = True
        
        self.player_circle = {"position": [randomPointInRingPlayer[0],randomPointInRingPlayer[1]], "velocity": [0,0], "radius": 40, "name": self.player.getName(), "score": self.player_circle["score"]}

        self.last_player_position = self.enemy_circle['position']

        self.shrink_timer = 0
        self.colorShrinkTimer = 10

    def displayCountdown(self): # Shows a counter before starting the game, preps player to be ready
        countdown_font = pygame.font.SysFont('Comic Sans MS', 150)
        
        tip_font = pygame.font.SysFont('Comic Sans MS', 45)

        gameStartIn_font = pygame.font.SysFont('Comic Sans MS', 140)

        tips = ["Camping is not a good strategy since the circle shrinks","Losing a lot of games in a row? Take a break!", "With the rushing ability comes great responsibility.", "Use WASD keys to move around the map", "With the space key you can rush against players"]

        nextTip = 0

        currentTip = random.choice(tips)

        for i in range(5, 0, -1):
            self.screen.fill((153,0,17))

            gameScreen_surface = countdown_font.render('Sumo Rama', True, (255, 255, 255))
            gameScreen_rect = gameScreen_surface.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/10))
            self.screen.blit(gameScreen_surface, gameScreen_rect)

            gameScreen_surface = gameStartIn_font.render('Game starts in ', True, (255, 255, 255))
            gameScreen_rect = gameScreen_surface.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/3))
            self.screen.blit(gameScreen_surface, gameScreen_rect)

            countdown_text = countdown_font.render(str(i), True, (255, 255, 255))
            text_rect = countdown_text.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 1.75))
            self.screen.blit(countdown_text, text_rect)

            pygame.draw.rect(self.screen, (255,255,255), pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT - (SCREEN_HEIGHT/4)),  4)

            if nextTip % 2 == 0:
                currentTip = random.choice(tips)

            countdown_text = tip_font.render("Tip: " + currentTip, True, (255, 255, 255))
            text_rect = countdown_text.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT // 1.15))
            self.screen.blit(countdown_text, text_rect)

            nextTip += 1
            pygame.display.update()
            pygame.time.wait(1000)

    def detectCheat(self): # Cheat detection for teleporting and score cheating
        if self.last_player_position is not None:
            dx = self.enemy_circle['position'][0] - self.last_player_position[0]
            dy = self.enemy_circle['position'][1] - self.last_player_position[1]
            distance_moved = math.sqrt(dx ** 2 + dy ** 2)

            if self.inSumoRing(self.sumo_ring_center[0], self.sumo_ring_center[1], self.sumo_ring_radius+30, self.enemy_circle['position'][0], self.enemy_circle['position'][1]) == False:
                print("Not in circle cheat...")
                self.score = 3 # Make not cheating player win
                self.player_circle['score'] = 3
                self.winnerOfTheGame = self.player_circle['name']
                return

            if self.enemy_circle['position'][0] == 0 and self.enemy_circle['position'][1] == 0:
                print("origin cheat detected")
                self.score = 3 # Make not cheating player win
                self.player_circle['score'] = 3
                self.winnerOfTheGame = self.player_circle['name']
                return

            if self.enemy_circle['score'] > 4: # Score cheat
                self.score = 3 # Make not cheating player win
                self.player_circle['score'] = 3
                self.winnerOfTheGame = self.player_circle['name']
                return

            if distance_moved > MAX_MOVE_DISTANCE_PER_TICK and self.newRoundState == True: # Cheat detection False positive, random spawn in ring is detected as teleporting
                print("Cheat detection detects new round teleportng" + str(distance_moved))
                self.newRoundState = False
            elif distance_moved > MAX_MOVE_DISTANCE_PER_TICK and self.checkIfGameOver() == False and self.newRoundState == False: # and self.newRoundState == False: # Player moved to fast and this is not a round switch
                print("Movement hack")
                print(distance_moved)
                self.score = 3 # Make not cheating player win
                self.player_circle['score'] = 3
                self.winnerOfTheGame = self.player_circle['name']

        self.last_player_position = self.enemy_circle['position'] # Locks last position

    def inSumoRing(self, circle_x, circle_y, rad, x, y): # Method for checking if a point is in a circle, used to check if sumo is in ring.
        if ((x - circle_x) * (x - circle_x) + (y - circle_y) * (y - circle_y) <= rad * rad):
            return True;
        else:
            return False;

    def isPeerAliveSender(self): # Sends peer alive messages to make sure they are not gone
        isNotAliveCounter = 0
        while True:
            if isNotAliveCounter == 5: # 5 times no response??!!
                # End game, player is gone
                self.winnerOfTheGame = self.player_circle['name']
                self.player_circle["score"] = 3
                break
                
            if self.gameStateRun == False: # Game is over thus kill the thread !
                break
            
            payload = "ALIVE " + str(self.peer.getSequenceNumber())

            self.peer.getSocket().sendto(payload.encode(), list(self.peer.getConnections())[0])
            time.sleep(0.1)

            if self.aliveAck != True:
                isNotAliveCounter += 1
            else:
                self.aliveAck = False # Resets alive ack for new ack
                isNotAliveCounter = 0

    def roundSwitchCountdown(self):  # Countdown that is shown when switching rounds.
        countdown_font = pygame.font.SysFont('Comic Sans MS', 150)
        gameStartIn_font = pygame.font.SysFont('Comic Sans MS', 140)

        bg = None
        sun_image = None


        bg = pygame.image.load("../assets/sumoBc/sumoFloor4.jpg").convert()
        bg = pygame.transform.scale(bg, (SCREEN_WIDTH, SCREEN_HEIGHT))
            
        sun_image = pygame.image.load("../assets/sun.png")
        sun_image = pygame.transform.scale(sun_image, (100, 100))  # Adjust the size as needed

        wave_gif = pygame.image.load("../assets/wave.gif").convert()
        wave_height = 100 + 50 * self.round  
        wave_gif = pygame.transform.scale(wave_gif, (SCREEN_WIDTH, wave_height))

        clock = pygame.time.Clock()  # Create a clock object for controlling frame rate

        for i in range(3, 0, -1):
            self.screen.blit(bg, (0, 0))
            

            gameScreen_surface = gameStartIn_font.render('Round  ' + str(self.round), True, (66, 99, 113))
            gameScreen_rect = gameScreen_surface.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 3))
            self.screen.blit(gameScreen_surface, gameScreen_rect)

            countdown_text = countdown_font.render(str(i), True, (66, 99, 113))
            text_rect = countdown_text.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 1.75))
            self.screen.blit(countdown_text, text_rect)

            self.screen.blit(wave_gif, (0, SCREEN_HEIGHT - wave_height))

            self.screen.blit(sun_image, (0, 0))

            pygame.display.update()
            clock.tick(60)  
            pygame.time.wait(1000)


    def run(self):
        self.resetStates()

        recv_thread = threading.Thread(target=self.listenForData, daemon=True)
        recv_thread.start()

        self.initPositions() 

        self.displayCountdown()

        send_thread = threading.Thread(target=self.isPeerAliveSender, daemon=True)
        send_thread.start()

        bg = pygame.image.load("../assets/sumoBc/sumoFloor4.jpg").convert() # Cool sand background :3
        bg = pygame.transform.scale(bg, (SCREEN_WIDTH, SCREEN_HEIGHT))

        while self.gameStateRun:
            current_time = time.time()
            delta_time = current_time - self.last_tick_time
            self.last_tick_time = current_time

            if self.lockstep_enabled and delta_time < self.game_tick_rate: # Assures that the game is synced per frame
                time.sleep(self.game_tick_rate - delta_time)

            self.screen.blit(bg, (0, 0))

            if self.player_circle["score"] >= 3 or self.enemy_circle["score"] >= 3:
                print("Game over")
                if self.enemy_circle["score"] > self.player_circle["score"]:
                    self.winnerOfTheGame = self.enemy_circle["name"]
                elif self.player_circle["score"] > self.enemy_circle["score"]:
                    self.winnerOfTheGame = self.player_circle["name"]

                self.gameStateRun = False
                self.gameState.setCurrentState('gameOver')
                self.gameOver.setWinner(self.winnerOfTheGame)

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
                elif event.type == pygame.MOUSEBUTTONUP:
                    pos = pygame.mouse.get_pos()
                    if leave.isOver(pos):
                        self.gameStateRun = False
                        pygame.quit()
                        exit(0)


            if self.rushing and self.player_circle is not None: 
                current_time = pygame.time.get_ticks()
                if current_time - self.rush_start_time < self.rush_duration * 1000:
                    self.rush_to_cursor()
                else:
                    self.rushing = False
                    self.player_circle["velocity"] = [0, 0]

            # Draw players on the screen
            if self.player.getColor() == "BLACK":
                pygame.draw.circle(self.screen, (255,255,255), (self.player_circle['position'][0],self.player_circle['position'][1]),45)
            else:
                pygame.draw.circle(self.screen, (0,0,0), (self.player_circle['position'][0],self.player_circle['position'][1]),45)
    
            pygame.draw.circle(self.screen, self.player.getColor(), (self.player_circle['position'][0],self.player_circle['position'][1]),40)



            pygame.draw.circle(self.screen, self.peerColor, (self.enemy_circle['position'][0],self.enemy_circle['position'][1]),40)


            # Score displayed on screen
            gameScreen_Score = self.gameFont.render('Round: ' + str(self.round), True, (0,0,0))
            gameScreen_rect = gameScreen_Score.get_rect(center=(75, 20))
            self.screen.blit(gameScreen_Score, gameScreen_rect)


            # Leave button
            leave = button.Button((255,255,255) ,0,SCREEN_HEIGHT - 25,50,30,25,'Leave')
            leave.draw(self.screen, (0,0,0))


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

                
            if self.cheat_detection_enabled: # Cheat detection method
                self.detectCheat() 

            if self.checkIfGameOver() == True and self.gameStateRun != False or self.gameDonePeer == True:
                self.gameDonePeer = False
                print("Round over")
                self.round += 1
            
                self.giveRightPlayerPoints()

                peerPositionJSON = json.dumps(self.player_circle)
                payload = "UPDATE " + peerPositionJSON
                self.peer.getSocket().sendto(payload.encode(), list(self.peer.getConnections())[0])

                time.sleep(0.1)


                print(self.enemy_circle["score"])
                if self.player_circle["score"] >= 3 or self.enemy_circle["score"] >= 3:
                    print("Game over")
                    if self.enemy_circle["score"] > self.player_circle["score"]:
                        self.winnerOfTheGame = self.enemy_circle["name"]
                    elif self.player_circle["score"] > self.enemy_circle["score"]:
                        self.winnerOfTheGame = self.player_circle["name"]

                    self.gameStateRun = False
                    self.gameState.setCurrentState('gameOver')
                    self.gameOver.setWinner(self.winnerOfTheGame)
                    continue


                self.roundSwitchCountdown()
                self.newRound()

            pygame.display.update()
            self.clock.tick(FPS) # FPS locked