import socket
import threading
import json

SERVER_ADDRESS = '127.0.0.1'
SERVER_PORT = 5378

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

sock.bind((SERVER_ADDRESS, SERVER_PORT))

connectedPeers = {'session1': []} # 'Session1: ['peers']'

currentSession = 'session1' # Start session

print("Rendezvous server is online")


def handler():
    while True:
        pass


while True:
    data, client_socket = sock.recvfrom(4096)
    print(client_socket)

    data = data.decode()

    if "HELLO-FROM" in data:
        print("Got a connection :)")
        #print(data.split(" ")[2])
        #sock.sendto("HELLO-OK", client_socket)
        connectedPeers[currentSession].append((client_socket, (data.split(" ")[1],data.split(" ")[2]))) # Appends client socket to the session
        #print(connectedPeers[currentSession])

    if len(connectedPeers[currentSession]) > 1: 
        for peer in connectedPeers[currentSession]: # Broadcast new client
            otherPeers = []
            for targetPeers in connectedPeers[currentSession]:
                if peer != targetPeers:
                    otherPeers.append(targetPeers)
            payload = "PEERS " + json.dumps(otherPeers)
            #print(payload)
            sock.sendto(payload.encode(),peer[0]) # Sends all active peers to the peer













