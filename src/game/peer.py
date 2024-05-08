import socket
import threading
import random

class Peer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.connections = set()  # Set to keep track of connected peers (no duplicates)
        self.sequenceNumber = random.randint(1000,9000) # Generetats sequence number

    def start(self):
        # Bind the UDP socket to the host and port
        #print(self.port)
        self.socket.bind((self.host, self.port))
        print(f"Peer {self.host}:{self.port} is listening for incoming messages...")

    def broadCast(self, message): # Broad cast to all other peers
        for peer in self.connections:
            self.socket.sendto(message.encode(), peer)

    def removeConnection(self, con):
        self.connections.remove(con)

    def resetConnections(self):
        self.connections.clear()

    def getSequenceNumber(self):
        return self.sequenceNumber
    
    def increaseSequenceNumber(self):
        self.sequenceNumber += 1
        return self.sequenceNumber
 
    def addCoonection(self, peer):
        self.connections.add(peer) # Adds tuple with connection information

    def getConnections(self):
        return self.connections

    def getSocket(self):
        return self.socket

    def setSocket(self, newSocket):
        self.socket = newSocket

    def getHost(self):
        return self.host
    
    def getPort(self):
        return self.port