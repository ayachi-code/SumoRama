import socket
import threading
import json
import time

SERVER_ADDRESS = '127.0.0.1'
SERVER_PORT = 5378

MAX_PLAYER_LOBBY = 9


sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

sock.bind((SERVER_ADDRESS, SERVER_PORT))

connectedPeers = {} # 'Session1: ['peers']'

print("Rendezvous server is online")

peersStatus = [] # Keeps track the counter used to track if a peer did not response




def sendReadyUp(self, payload):
    while True:
        sock.sendto(payload.encode())

stat = 0

def notifyPeers(message):
    for peer in connectedPeers: # Broadcast new client
        otherPeersKey = []
        otherPeersValue = []

        for targetPeers in connectedPeers:   
            if peer != targetPeers:
                otherPeersKey.append(targetPeers)
                otherPeersValue.append(connectedPeers[targetPeers])

        sock.sendto(message.encode(),peer) # Sends all active peers to the peer

while True:
    data, client_socket = sock.recvfrom(4096)
    
    data = data.decode()

    if "quit" in data:
        print("Player is quiting")
        peerId = data.split(" ")[1]
        connectedPeers.pop(('127.0.0.1', int(peerId)), None)
        payload = "quit " + peerId
        notifyPeers(payload)

    if "HELLO-FROM" in data:
        print("Got a connection :)")
        #print(len(connectedPeers))
        if len(connectedPeers) == MAX_PLAYER_LOBBY-1: # -1 cuz it counts 0
            print("vol?")
            sock.sendto("FULL".encode(), client_socket)
            continue
        else:
            connectedPeers[client_socket] = [data.split(" ")[1], data.split(" ")[2], False]
            print("Sending hello-ok")
            print(client_socket)
            sock.sendto("HELLO-OK".encode(), client_socket)
            if len(connectedPeers) == 1:
                continue

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
        peersStatus = []
        stat = 0
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind((SERVER_ADDRESS, SERVER_PORT))
        continue
    
    if len(connectedPeers) > 1: 
        for peer in connectedPeers: # Broadcast new client
            otherPeersKey = []
            otherPeersValue = []

            for targetPeers in connectedPeers:   
                if peer != targetPeers:
                    otherPeersKey.append(targetPeers)
                    otherPeersValue.append(connectedPeers[targetPeers])

            payload = "PEERS " + json.dumps(otherPeersKey,separators=(',', ':')) + " " + json.dumps(otherPeersValue,separators=(',', ':'))

            sock.sendto(payload.encode(),peer) # Sends all active peers to the peer
