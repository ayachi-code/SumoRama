import socket
import threading
import pygame
import math
import time
import json
import random

FPS = 60

SCREEN_WIDTH = 1300
SCREEN_HEIGHT = 800

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

        self.player_circle = {"position": [0,0], "velocity": [0,0], "radius": 40, "name": "a","score": 0, "id": None}
        self.enemy_circles = [ # All possie enemy circles
            
            {"position": [0,0], "velocity": [0,0], "radius": 40, "name": "a","score": 0, "id": None},
            {"position": [0,0], "velocity": [0,0], "radius": 40, "name": "a","score": 0, "id": None},
            {"position": [0,0], "velocity": [0,0], "radius": 40, "name": "a","score": 0, "id": None},
            {"position": [0,0], "velocity": [0,0], "radius": 40, "name": "a","score": 0, "id": None},
            {"position": [0,0], "velocity": [0,0], "radius": 40, "name": "a","score": 0, "id": None},
            {"position": [0,0], "velocity": [0,0], "radius": 40, "name": "a","score": 0, "id": None},
            {"position": [0,0], "velocity": [0,0], "radius": 40, "name": "a","score": 0, "id": None},
        ]
        
        self.confirmedPositions = []
        self.placedPositionsReciever = []

        self.playerPositionInit = None

        self.sumo_ring_radius = 450
        self.sumo_ring_center = [SCREEN_WIDTH/2, SCREEN_HEIGHT/2]
        self.circle_radius = 40


    def setPeer(self, newPeer):
        self.peer = newPeer


    def listenData(self):
        while True:
            data, addr = self.peer.getSocket().recvfrom(65535)
            data = data.decode()
            if "CONFIRM" in data:
                if int(data.split(" ")[1]) not in self.confirmedPositions:
                    self.confirmedPositions.append(int(data.split(" ")[1]))
                
                if len(self.confirmedPositions) == len(self.peer.getConnections()):
                    self.playerPositionInit = True

            if "INIT" in data:
                print("Got init of positions from " + data.split(" ")[3] + " DATA " + data)
                payload = "CONFIRM " + str(self.peer.getPort())
                xPosition = data.split(" ")[1]
                yPosition = data.split(" ")[2]

                self.peer.getSocket().sendto(payload.encode(), addr) # Confirms position
                
                for enemy in self.enemy_circles:
                    if enemy['id'] == None and int(data.split(" ")[3]) not in self.placedPositionsReciever: # Prevents using more circles than needed
                        enemy['id'] = data.split(" ")[3]
                        enemy['position'] = [xPosition, yPosition]
                        self.placedPositionsReciever.append(int(data.split(" ")[3]))
            elif "UPDATE" in data:
                newData = json.loads(data.split(" ",1)[1])
                peerId = newData['id']
                newPossition = newData['position']

                for peer in self.enemy_circles: # TODO Maybe use hashmap for future update, increases performance
                    # print(str(peer['id']) + "==" + str(peerId))
                    if peer['id'] != None:
                        if int(peer['id']) == int(peerId):
                            # print("updating")
                            peer['position'] = newPossition

                #print(newData)


                # if int(data.split(" ")[3]) not in self.placedPositionsReciever:
                #     self.placedPositionsReciever.append(int(data.split(" ")[3]))


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
        
        
    def run(self):

        #self.displayCountdown() # Displays a countdown with some very usefull tips!

        #print("My connection info " + str(self.peer.getPort()))

        self.player_circle['id'] = self.peer.getPort()

        listener = threading.Thread(target=self.listenData, daemon=True)
        listener.start()

        self.initPosition()

        self.displayCountdown() # Displays a countdown with some very usefull tips!

        # print(self.peer.getPort())

        # print(self.peer.getConnections().get(0))
        
        # for peers in self.peer.getConnections():
        #     payload = "Hi bro my id is " + str(self.peer.getPort())
        #     print(peers)
        #     self.peer.getSocket().sendto("hi".encode(), peers)


        while self.gameStateRun:
            #print(self.enemy_circles)
            #print(self.peer.getConnections())
            # current_time = time.time()
            # delta_time = current_time - self.last_tick_time
            # self.last_tick_time = current_time

            # if self.lockstep_enabled and delta_time < self.game_tick_rate: # Assures that the game is synced per frame
            #     time.sleep(self.game_tick_rate - delta_time)

            self.screen.fill((255,255,255))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.gameStateRun = False
                    pygame.quit()
                    exit(0)

            
            keys = pygame.key.get_pressed()
            if keys[pygame.K_a]:
                self.player_circle['position'][0] -= 3
            if keys[pygame.K_d]:
                self.player_circle['position'][0] += 3
            if keys[pygame.K_w]:
                self.player_circle['position'][1] -= 3
            if keys[pygame.K_s]:
                self.player_circle['position'][1] += 3


            pygame.draw.circle(self.screen, (255,0,0), (self.player_circle['position'][0],self.player_circle['position'][1]),20)

            pygame.draw.circle(self.screen, (255, 0, 0), self.sumo_ring_center, int(self.sumo_ring_radius), 30) # Draw the sumo ring
            
            for playerEnemy in self.enemy_circles:
                # print(player['id'])
                if playerEnemy['id'] != None:
                    # print((playerEnemy['position'][0]))
                    pygame.draw.circle(self.screen, (255,0,0), (int(playerEnemy['position'][0]),int(playerEnemy['position'][1])),20)

            
            #pygame.draw.circle(self.screen, self.player.getColor(), (self.enemy_circle['position'][0],self.enemy_circle['position'][1]),40)

            #  # Sends data to client
            peerPositionJSON = json.dumps(self.player_circle)
            payload = "UPDATE " + peerPositionJSON
            for enemyPlayer in self.enemy_circles:
                if enemyPlayer['id'] != None:
                    self.peer.getSocket().sendto(payload.encode(), ('127.0.0.1', int(enemyPlayer['id'])))

            #self.peer.getSocket().sendto(payload.encode(), list(self.peer.getConnections())[0])


            pygame.display.update()
            self.clock.tick(FPS) # FPS locked


