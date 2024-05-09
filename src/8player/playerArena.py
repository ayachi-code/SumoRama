import socket
import threading
import pygame
import math
import time
import json
import random
import math
import button
import pdb

#TODO
# Clean code(game over reusable class e.g) add comments
# Add back buttons no death end. 1v1 for example
# Add change name, change color feauture
# Add 8 player round change feautre to 1v1
# Laatste test en code herhalen

FPS = 60

SCREEN_WIDTH = 1300
SCREEN_HEIGHT = 800

GAME_TICK_RATE = 1 / FPS  # Game tick rate in seconds

MAX_ROUND = 4 # Max number of rounds in a game


class PlayerArena:
    def __init__(self, screen, gameState, player, gameOver):
        pygame.init() # Init pygame
        pygame.font.init() # Init font

        self.gameFont = pygame.font.SysFont('Comic Sans MS', 40)
        self.clock = pygame.time.Clock()

        # Set arguments to class
        self.screen = screen
        self.gameState = gameState
        self.peer = None
        self.player = player
        self.gameOver = gameOver

        self.gameStateRun = True

        self.player_circle = {"position": [0,0], "velocity": [0,0], "radius": 40, "name": "a","score": 0, "id": None, "visible": True}
        self.enemy_circles = [ # All possie enemy circles
            
            {"position": [0,0], "velocity": [0,0], "radius": 40, "name": "a","score": 0, "id": None, "visible": True},
            {"position": [0,0], "velocity": [0,0], "radius": 40, "name": "a","score": 0, "id": None, "visible": True},
            {"position": [0,0], "velocity": [0,0], "radius": 40, "name": "a","score": 0, "id": None, "visible": True},
            {"position": [0,0], "velocity": [0,0], "radius": 40, "name": "a","score": 0, "id": None, "visible": True},
            {"position": [0,0], "velocity": [0,0], "radius": 40, "name": "a","score": 0, "id": None, "visible": True},
            {"position": [0,0], "velocity": [0,0], "radius": 40, "name": "a","score": 0, "id": None, "visible": True},
            {"position": [0,0], "velocity": [0,0], "radius": 40, "name": "a","score": 0, "id": None, "visible": True}
        ]


        #rush variable
        self.rush_duration = 0.5
        self.rush_speed = 300
        self.rushing = False
        self.rush_start_time = 0
        
        self.confirmedPositions = []
        self.placedPositionsReciever = []

        self.playerPositionInit = None

        self.sumo_ring_radius = 450
        self.sumo_ring_center = [SCREEN_WIDTH/2, SCREEN_HEIGHT/2]
        self.circle_radius = 40
        self.realtiveSumoSize = self.circle_radius


        # Shrink variables
        self.shrink_timer = 0
        self.timerScreen = 10
        self.shrink_interval = 10
        self.shrink_scale = 0.90
        self.colorShrinkTimer = (0,0,0)

        # Lockstep simulation variables
        self.game_tick_rate = GAME_TICK_RATE
        self.last_tick_time = 0
        self.lockstep_enabled = True  # Toggle lockstep simulation

        self.losers = [] # List that containst the losers of the round :(
        self.suddenDeathCandidates = []

        self.round = 1 # Starts on round 1
        self.suddenDeath = False

    def setPeer(self, newPeer):
        self.peer = newPeer


    def listenData(self):
        while True:
            data, addr = self.peer.getSocket().recvfrom(65535)
            data = data.decode()

            if self.gameStateRun == False:
                break

            if "DELETE" in data:
                peerID = data.split(" ")[1]
                print("Deleting " + peerID)
                if peerID == str(self.peer.getPort()): # Im getting kicked
                    self.gameStateRun = False
                    self.player_circle['id'] = None
                    self.player_circle['visible'] = False
                    self.gameState.setCurrentState('start')
       
                for player in self.enemy_circles:
                    if str(player['id']) == peerID:
                        if (peerID, player['name']) in self.suddenDeathCandidates:
                            self.suddenDeathCandidates.remove((peerID, player['name']))
                        if peerID in self.losers:
                            self.losers.remove(peerID)

                        player['id'] = None
                        player['visible'] = False
                        player['score'] = 0
                        self.peer.removeConnection(('127.0.0.1', int(peerID)))

                        
            if "OUT_OF_RING" in data:
                peerID = data.split(" ")[1]
                print("A peer is out of the ring " + peerID)
                # print(self.losers)
                for player in self.enemy_circles:
                    if player['id'] == peerID:
                        player['visible'] = False
                        break
                if peerID not in self.losers:
                    self.losers.append(peerID) # Adds loser to the loser list

            if "CONFIRM" in data:
                if int(data.split(" ")[1]) not in self.confirmedPositions:
                    self.confirmedPositions.append(int(data.split(" ")[1]))
                
                if len(self.confirmedPositions) >= len(self.peer.getConnections()):
                    self.playerPositionInit = True

            if "INIT" in data:
                print("Got init of positions from " + data.split(" ")[3] + " DATA " + data)
                payload = "CONFIRM " + str(self.peer.getPort())
                xPosition = data.split(" ")[1]
                yPosition = data.split(" ")[2]

                self.peer.getSocket().sendto(payload.encode(), addr) # Confirms position
                
                for enemy in self.enemy_circles:
                    if enemy['id'] == None and int(data.split(" ")[3]) not in self.placedPositionsReciever: # Prevents using more circles than neededl Inits player
                        enemy['id'] = data.split(" ")[3]
                        enemy['position'] = [xPosition, yPosition]
                        self.placedPositionsReciever.append(int(data.split(" ")[3]))
            elif "UPDATE" in data:
                #print(data)
                newData = json.loads(data.split(" ",1)[1])
                peerId = newData['id']
                newPossition = newData['position']

                for peer in self.enemy_circles: # TODO Maybe use hashmap for future update, increases performance
                    if peer['id'] != None and peerId != None:
                        if int(peer['id']) == int(peerId):
                            peer['position'] =  newPossition #newPossition[0]
                            peer['score'] = newData['score']
                            peer['name'] = newData['name']
                            peer['visible'] = newData['visible']

    def displayCountdown(self): # Shows a counter before starting the game, preps player to be ready
        countdown_font = pygame.font.SysFont('Comic Sans MS', 150)
        
        tip_font = pygame.font.SysFont('Comic Sans MS', 50)

        gameStartIn_font = pygame.font.SysFont('Comic Sans MS', 140)

        tips = ["Camping is not a good strategy since the circle shrinks","Losing a lot of games in a row? Take a break!", "With the rushing ability comes great responsibility.", "Use WASD keys to move around the map", "With the space key you can rush against players", "Press space to rush against other players!"]

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

    def sendInitPositions(self, data): # Send init positions to other peer, at the start of the game
        while True:
            if self.playerPositionInit == True:
                break
            print(self.peer.getConnections())
            for peers in self.peer.getConnections():
                self.peer.getSocket().sendto(data.encode(), peers)
            time.sleep(0.1)

    
    def randomPointInCircle(self, radius, centerX, centerY): # Uses circle formula to generate random point on circle, the circle here is the sumo ring.
        alpha = 2 * math.pi * random.random()
        r = radius * math.sqrt(random.random())

        x = r * math.cos(alpha) + centerX
        y = r * math.sin(alpha) + centerY
        return (x,y)

    def initPosition(self):
        randomPointInRing = self.randomPointInCircle(self.sumo_ring_radius-(0.3 * self.sumo_ring_radius), self.sumo_ring_center[0], self.sumo_ring_center[1])
        self.player_circle['position'] = [math.ceil(randomPointInRing[0]),math.ceil(randomPointInRing[1])]

        payload = "INIT " + str(math.ceil(randomPointInRing[0])) + " " + str(math.ceil(randomPointInRing[1])) + " " + str(self.peer.getPort())

        sendInit_thread = threading.Thread(target=self.sendInitPositions,args=(payload,), daemon=True)
        sendInit_thread.start()

    
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
        circle1["position"][0] = float( circle1["position"][0])
        circle1["position"][1] = float( circle1["position"][1])
        circle2["position"][0] = float( circle2["position"][0])
        circle2["position"][1] = float( circle2["position"][1])

        distance = math.sqrt(( float(circle1["position"][0]) - float(circle2["position"][0]))**2 +
                            (float(circle1["position"][1]) - float(circle2["position"][1]))**2)
        

        if distance < 2 * self.realtiveSumoSize:
            overlap = 2 * self.realtiveSumoSize - distance
            collision_direction = [ float(circle2["position"][0]) - float(circle1["position"][0]),
                                float(circle2["position"][1]) - float(circle1["position"][1])]
            
            collision_length = math.sqrt(collision_direction[0]**2 + collision_direction[1]**2)

            if collision_length > 0:
                collision_direction = [collision_direction[0] / collision_length,
                                    collision_direction[1] / collision_length]
                move_distance = overlap / 2

                circle1["position"][0] -= float(move_distance * collision_direction[0])
                circle1["position"][1] -= float(move_distance * collision_direction[1])
                circle2["position"][0] += float(move_distance * collision_direction[0])
                circle2["position"][1] += float(move_distance * collision_direction[1])

    def checkIfOutOfRing(self): # Checks if the game is over, if so than make other peer know.
        if self.player_circle is not None:
            player_distance_to_center = math.sqrt((self.player_circle["position"][0] - self.sumo_ring_center[0])**2 + (self.player_circle["position"][1] - self.sumo_ring_center[1])**2)
                
            if player_distance_to_center + self.player_circle["radius"] > self.sumo_ring_radius:
                return True
    
        return False
    
    def newRound(self):
        self.sumo_ring_radius = 450

        randomPointInRingPlayer = self.randomPointInCircle(self.sumo_ring_radius-(0.3 * self.sumo_ring_radius), self.sumo_ring_center[0], self.sumo_ring_center[1])

        self.player_circle = {"position": [randomPointInRingPlayer[0],randomPointInRingPlayer[1]], "velocity": [0,0], "radius": 40, "name": self.player.getName(), "score": self.player_circle["score"], "visible": True, "id": self.peer.getPort()}
        for enemy in self.enemy_circles: # Shows all players again
            if enemy['visible'] == False:
                enemy['visible'] = True

        self.losers = [] # New round new chances, resets the loser list
        self.colorShrinkTimer = (0,0,0)
        self.start_time = time.time()

    def getMaxScore(self):
        max_score = self.player_circle['score']  # Start with the player's score

        for enemy_circle in self.enemy_circles:
            if enemy_circle['score'] > max_score:
                max_score = enemy_circle['score']

        return max_score
    
    def resetStates(self): # reset states for new game
        self.player_circle = {"position": [0,0], "velocity": [0,0], "radius": 40, "name": self.player.getName(),"score": 0, "visible": True}
        self.enemy_circles = [ # All possie enemy circles
            {"position": [0,0], "velocity": [0,0], "radius": 40, "name": "a","score": 0, "id": None, "visible": True},
            {"position": [0,0], "velocity": [0,0], "radius": 40, "name": "a","score": 0, "id": None, "visible": True},
            {"position": [0,0], "velocity": [0,0], "radius": 40, "name": "a","score": 0, "id": None, "visible": True},
            {"position": [0,0], "velocity": [0,0], "radius": 40, "name": "a","score": 0, "id": None, "visible": True},
            {"position": [0,0], "velocity": [0,0], "radius": 40, "name": "a","score": 0, "id": None, "visible": True},
            {"position": [0,0], "velocity": [0,0], "radius": 40, "name": "a","score": 0, "id": None, "visible": True},
            {"position": [0,0], "velocity": [0,0], "radius": 40, "name": "a","score": 0, "id": None, "visible": True}
        ]
        self.sumo_ring_radius = 450
        self.losers = []
          
        self.confirmedPositions = []
        self.placedPositionsReciever = []

        self.playerPositionInit = None

        self.circle_radius = 40
        self.realtiveSumoSize = self.circle_radius

        self.round = 1 # Starts on round 1
        self.suddenDeath = False

    def roundSwitchCountdown(self): 
        print("showing round switch")
        countdown_font = pygame.font.SysFont('Comic Sans MS', 150)
        gameStartIn_font = pygame.font.SysFont('Comic Sans MS', 140)

        bg = None
        sun_image = None

        if self.suddenDeath == True:
            bg = pygame.image.load("../assets/sumoBc/suddenDeath.jpg").convert()
            bg = pygame.transform.scale(bg, (SCREEN_WIDTH, SCREEN_HEIGHT))

            sun_image = pygame.image.load("../assets/moon.png")
            sun_image = pygame.transform.scale(sun_image, (100, 100))  # Adjust the size as needed
        else:
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


            if self.suddenDeath:
                gameScreen_surface = gameStartIn_font.render('sudden death round!  ', True, (0, 0, 0))
                gameScreen_rect = gameScreen_surface.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 3))
                self.screen.blit(gameScreen_surface, gameScreen_rect)

                countdown_text = countdown_font.render(str(i), True, (0, 0, 0))
                text_rect = countdown_text.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 1.75))
                self.screen.blit(countdown_text, text_rect)
            else:
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

    def inSumoRing(self, circle_x, circle_y, rad, x, y): # Method for checking if a point is in a circle, used to check if sumo is in ring.
        if ((x - circle_x) * (x - circle_x) + (y - circle_y) * (y - circle_y) <= rad * rad):
            return True;
        else:
            return False;
    
    def cheatDetection(self):
        
        for enemy in self.enemy_circles:
            # if enemy['id'] != None:
            #     print(enemy)
            if enemy['id'] != None  and enemy['visible'] == True and self.inSumoRing(self.sumo_ring_center[0], self.sumo_ring_center[1], self.sumo_ring_radius+40, enemy['position'][0], enemy['position'][1]) == False:
                payload = "DELETE " + str(enemy['id']) # A player was cheating kicking the player out of the game
                self.peer.broadCast(payload)
                self.peer.removeConnection(('127.0.0.1',int(enemy['id'])))
                enemy['id'] = None
                enemy['visible'] = False
                print("The other player is not in circle")
                print(enemy['position'][0], enemy['position'][1])
                continue
            if enemy['score'] > 5 and enemy['id'] != None:
                payload = "DELETE " + str(enemy['id']) # A player was cheating kicking the player out of the game
                self.peer.broadCast(payload)
                self.peer.removeConnection(('127.0.0.1',int(enemy['id'])))
                enemy['id'] = None
                enemy['visible'] = False
                enemy['score'] = 0
                print("The other player is score cheating")
                return

    def run(self):
        self.resetStates()
        print("arena?")
        print(self.peer.getPort())
        print("player name: " + self.player.getName())


        self.gameStateRun = True

        self.player_circle['id'] = self.peer.getPort()

        listener = threading.Thread(target=self.listenData, daemon=True)
        listener.start()

        self.initPosition()

        self.displayCountdown() # Displays a countdown with some very usefull tips!

        start_time = time.time() # Starts timer

        bg = pygame.image.load("../assets/sumoBc/sumoFloor4.jpg").convert() # Cool sand background :3
        bg = pygame.transform.scale(bg, (SCREEN_WIDTH, SCREEN_HEIGHT))

        while self.gameStateRun:

            current_time = time.time()
            elapsed_time = current_time - start_time

            remaining_time = max(0, 10 - math.ceil(elapsed_time))  # Calculate remaining time

            delta_time = current_time - self.last_tick_time
            self.last_tick_time = current_time

            if self.lockstep_enabled and delta_time < self.game_tick_rate: # Assures that the game is synced per frame
                time.sleep(self.game_tick_rate - delta_time)


            self.screen.blit(bg, (0, 0))

            if len(self.peer.getConnections()) == 0:
                print("You're the only player left thus the winner")
                self.peer = None
                self.gameStateRun = False
                self.gameState.setCurrentState('gameOver')
                self.gameOver.setWinner(self.player.getName())
                continue


            if len(self.losers) == len(self.suddenDeathCandidates)-1 and self.suddenDeath == True:
                print(self.enemy_circles)
                print("Game is over and the winner is")
                if self.player_circle['visible'] == True and self.player_circle['id'] != None:
                    winner = self.player_circle['name']
                else:
                    for player in self.enemy_circles:
                        if player['visible'] == True and player['id'] != None:
                            winner = player['name']
                            break
                    
                self.gameStateRun = False
                self.gameState.setCurrentState('gameOver')
                self.gameOver.setWinner(winner)
                self.resetStates()
                continue

            if self.checkIfOutOfRing() and self.player_circle['visible'] == True:
                self.player_circle['visible'] = False
                self.losers.append(str(self.peer.getPort())) # Add yourself as a loser
                payload = "OUT_OF_RING " + str(self.peer.getPort())
                self.peer.broadCast(payload)

            if math.ceil(remaining_time) <= 5: # Shows different color depending how close the timer is to the end.
                self.colorShrinkTimer = (255, 0, 0)
            else:
                self.colorShrinkTimer = (0,0,0)


            if len(self.losers) == len(self.peer.getConnections()) and self.suddenDeath == False:
                print("round over")
                print(self.losers)
                print(self.peer.getConnections())

                if str(self.peer.getPort()) not in self.losers: # I am not a loser hehe, I am a winner! Thus give ne the point...
                    #print("got a point")
                    self.player_circle['score'] += 1 # Increases winners score with 1     

                self.round += 1 # Increases roudn counter

                if self.round == MAX_ROUND and self.suddenDeath == False:
                    print("game over")
                    peerPositionJSON = json.dumps(self.player_circle)
                    
                    payload = "UPDATE " + peerPositionJSON
                    for enemyPlayer in self.enemy_circles:
                        if enemyPlayer['id'] != None:
                            self.peer.getSocket().sendto(payload.encode(), ('127.0.0.1', int(enemyPlayer['id'])))
                        
                    
                    #self.roundSwitchCountdown() # Special sudden death countdown...
                    
                    time.sleep(0.1) # Perhaps add a 3 second count down COMING SOON

                    maxScore = self.getMaxScore()
                    winner = []

                    print(maxScore)
                    if self.player_circle['score'] == maxScore and self.player_circle['id'] != None:
                        winner.append((str(self.player_circle['id']), self.player_circle['name']))
             
                    for player in self.enemy_circles:
                        if player['score'] == maxScore and player['id'] != None:
                            winner.append((str(player['id']), player['name']))

                    if len(winner) == 1: # There is one winner in the game
                        self.gameStateRun = False
                        self.gameState.setCurrentState('gameOver')
                        # print(winner)
                        self.gameOver.setWinner(winner[0][1])
                        self.resetStates()
                        continue
                    else: # suddend death round
                        print("Sudden death")
                        self.suddenDeathCandidates = winner
                        self.suddenDeath = True
                        self.newRound()
                        print(winner)
                        if (str(self.peer.getPort()), self.player_circle['name']) not in winner:
                            print("Hide")
                            self.player_circle['visible'] = False
                else:
                    self.newRound()

                self.roundSwitchCountdown()
                start_time = time.time() # resets countdown
   
            if self.suddenDeath == True:
                # Score displayed on screen
                gameScreen_Score = self.gameFont.render('Sudden death round', True, (0,0,0))
                gameScreen_rect = gameScreen_Score.get_rect(center=(140, 20))
                self.screen.blit(gameScreen_Score, gameScreen_rect)

                if self.player_circle['visible'] == False:
                    print("showing spec mode")
                    gameScreen = self.gameFont.render('Spectating mode', True, (0,0,0))
                    gameScreen_rect = gameScreen.get_rect(center=(SCREEN_WIDTH - SCREEN_WIDTH/7, 20))
                    self.screen.blit(gameScreen, gameScreen_rect)



            else:
                # Score displayed on screen
                gameScreen_Score = self.gameFont.render('Round: ' + str(self.round), True, (0,0,0))
                gameScreen_rect = gameScreen_Score.get_rect(center=(75, 20))
                self.screen.blit(gameScreen_Score, gameScreen_rect)

            if self.player_circle['visible'] == False and self.suddenDeath == False:
                gameScreen = self.gameFont.render('Spectating mode', True, (0,0,0))
                gameScreen_rect = gameScreen.get_rect(center=(260, 20))
                self.screen.blit(gameScreen, gameScreen_rect)


            if self.suddenDeath == False:
                # Score displayed on screen
                gameScreen_Score = self.gameFont.render('Score: ' + str(self.player_circle['score']), True, (0,0,0))
                gameScreen_rect = gameScreen_Score.get_rect(center=(SCREEN_WIDTH - SCREEN_WIDTH/7, 20))
                self.screen.blit(gameScreen_Score, gameScreen_rect)

            # Time displayed on screen
            gameScreen_waveTimer = self.gameFont.render('0:' + str(remaining_time), True, self.colorShrinkTimer)
            gameScreen_rect = gameScreen_waveTimer.get_rect(center=(SCREEN_WIDTH - 30, 20))
            self.screen.blit(gameScreen_waveTimer, gameScreen_rect)


            # Leave button
            leave = button.Button((255,255,255) ,0,SCREEN_HEIGHT - 25,50,30,25,'Leave')

            leave.draw(self.screen, (0,0,0))


            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.gameStateRun = False
                    self.player_circle['id'] = None
                    self.player_circle['visible'] = False
                    self.player_circle['score'] = 0
                    payload = "DELETE " + str(self.peer.getPort())
                    self.peer.broadCast(payload)
                    pygame.quit()
                    exit(0)
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE and not self.rushing and self.player_circle is not None and self.player_circle['visible']: # Rush state set
                        self.rushing = True
                        self.rush_start_time = pygame.time.get_ticks()
                elif event.type == pygame.MOUSEBUTTONUP:
                    pos = pygame.mouse.get_pos()
                    if leave.isOver(pos):
                        print("Ima head out") 
                        self.gameStateRun = False
                        self.player_circle['id'] = None
                        self.player_circle['visible'] = False
                        self.player_circle['score'] = 0
                        payload = "DELETE " + str(self.peer.getPort())
                        self.peer.broadCast(payload)
                        self.gameState.setCurrentState('start')
                        
                      
            if self.rushing and self.player_circle is not None: 
                current_time = pygame.time.get_ticks()
                if current_time - self.rush_start_time < self.rush_duration * 1000:
                    self.rush_to_cursor()
                else:
                    self.rushing = False
                    self.player_circle["velocity"] = [0, 0]


            if self.player_circle['visible'] == True: # Prevents ghost players
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
                for enemyPlayer in self.enemy_circles:
                    if enemyPlayer != None:
                        self.handle_collision(self.player_circle, enemyPlayer) # Collision detection

            if self.player_circle is not None: # Changes position depending on the speed
                self.player_circle["position"][0] += self.player_circle["velocity"][0] * self.clock.get_time() / 1000
                self.player_circle["position"][1] += self.player_circle["velocity"][1] * self.clock.get_time() / 1000


            self.realtiveSumoSize = self.circle_radius - len(self.peer.getConnections()) * 2.5

            if self.player_circle['visible'] == True:
                pygame.draw.circle(self.screen, (0,0,0), (self.player_circle['position'][0],self.player_circle['position'][1]),self.realtiveSumoSize+5)
                pygame.draw.circle(self.screen, (255,0,0), (self.player_circle['position'][0],self.player_circle['position'][1]),self.realtiveSumoSize)


            for playerEnemy in self.enemy_circles:
                if playerEnemy['id'] != None and playerEnemy['visible'] == True:
                    pygame.draw.circle(self.screen, (255,0,0), (int(playerEnemy['position'][0]),int(playerEnemy['position'][1])),self.realtiveSumoSize)

            
            if elapsed_time >= self.shrink_interval: # If timer exceeds threshold than make the circle smaller and reset timers.
                self.sumo_ring_radius *= self.shrink_scale
                start_time = time.time()  # Reset the timer
    
            pygame.draw.circle(self.screen, (255, 0, 0), self.sumo_ring_center, int(self.sumo_ring_radius), 30) # Draw the sumo ring

            #  # Sends data to client
            peerPositionJSON = json.dumps(self.player_circle)
            # print(peerPositionJSON)
            payload = "UPDATE " + peerPositionJSON
            for enemyPlayer in self.enemy_circles:
                if enemyPlayer['id'] != None:
                    self.peer.getSocket().sendto(payload.encode(), ('127.0.0.1', int(enemyPlayer['id'])))

            self.cheatDetection()

            pygame.display.update()
            self.clock.tick(FPS) # FPS locked
