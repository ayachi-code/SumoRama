import socket
import threading
import json
import time

SERVER_ADDRESS = '127.0.0.1'
SERVER_PORT = 5378

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

sock.bind((SERVER_ADDRESS, SERVER_PORT))

connectedPeers = {} # 'Session1: ['peers']'

allSessions = ['session1']

currentSession = 'session1' # Start session

print("Rendezvous server is online")


acknowledgedPeersAlve = []

acknowledgedPeersReady = []

peersStatus = [] # Keeps track the counter used to track if a peer did not response


# def isPeerAlive():
#     while True:
#         for session in allSessions: # Sends alive to all peers
#             for peer in connectedPeers[session]:
#                 sock.sendto("ALIVE".encode(), peer[0])

#         time.sleep(0.1)
#         # If not ack decrease with 1

#         #print(acknowledgedPeers)

#         AcknowledgedPeers = [] # Reset it


# sendAlive = threading.Thread(target=isPeerAlive, daemon=True)
# sendAlive.start()


def isPeerAliveReciever():
    while True:
        data, client_socket = sock.recvfrom(4096)
        data = data.decode()
        #print(data)

        if "ALIVE-OK" in data:
            acknowledgedPeersAlve.append(data.split(" ")[1])



def sendReadyUp(self, payload):
    while True:
        sock.sendto(payload.encode())


#sendAliveReciever = threading.Thread(target=isPeerAliveReciever, daemon=True)
#sendAliveReciever.start()

stat = 0


while True:
    data, client_socket = sock.recvfrom(4096)
    
    data = data.decode()
    #print(data)

    # if "ALIVE-OK" in data:
    #     acknowledgedPeersAlve.append(data.split(" ")[1])
    if "HELLO-FROM" in data:
        print("Got a connection :)")
        connectedPeers[client_socket] = [data.split(" ")[1], data.split(" ")[2], False]
        #connectedPeers.append(client_socket: {data.split(" ")[1],data.split(" ")[2],False} ) # Appends client socket to the session
        sock.sendto("HELLO-OK".encode(), client_socket)
        #print(connectedPeers)

    if "READY-UP" in data: # A peer readys up send it to all other peers
        # Send ready up to all other peers
        print("READYYY UPPP")
        connectedPeers[client_socket][2] = True

        for peer in connectedPeers:
            if peer != client_socket: # Not resending to same peer
                print("sending ready up")
                payload = "READY-OK " + data.split(" ")[1]
                sock.sendto(payload.encode(), peer)
                stat = 1
        
        if stat == 1:
            stat = 0
            continue

    if "RESET" in data:
        print("Resetting for new lobby")
        connectedPeers = {}

    
    if len(connectedPeers) > 1: 
        for peer in connectedPeers: # Broadcast new client
            otherPeersKey = []
            otherPeersValue = []

            for targetPeers in connectedPeers:   
                if peer != targetPeers:
                    otherPeersKey.append(targetPeers)
                    otherPeersValue.append(connectedPeers[targetPeers])

            #print(connectedPeers[peer])
            payload = "PEERS " + json.dumps(otherPeersKey,separators=(',', ':')) + " " + json.dumps(otherPeersValue,separators=(',', ':'))

            sock.sendto(payload.encode(),peer) # Sends all active peers to the peer













