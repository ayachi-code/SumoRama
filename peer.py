import socket
import threading

class Peer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.connections = set()  # Set to keep track of connected peers (no duplicates)

    def start(self):
        # Bind the UDP socket to the host and port
        self.socket.bind((self.host, self.port))
        print(f"Peer {self.host}:{self.port} is listening for incoming messages...")

        # Thread to handle incoming messages
        receive_thread = threading.Thread(target=self.receive_messages)
        receive_thread.start()

    def receive_messages(self):
        while True:
            data, client_address = self.socket.recvfrom(1024)
            message = data.decode('utf-8')
            print(f"Received message from {client_address}: {message}")

            if "HELLO-FROM" in message: # Handshake 
                self.socket.sendto("yoo".encode(), client_address)

            # Add the client address to connections (no need to check duplicates in UDP)
            self.connections.add(client_address)

    def send_message(self, message):
        # Send message to all connected peers
        message_bytes = message.encode('utf-8')
        for address in self.connections:
            self.socket.sendto(message_bytes, address)

    def getSocket(self):
        return self.socket

    def getHost(self):
        return self.host
    
    def getPort(self):
        return self.port