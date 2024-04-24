import socket
import threading

class Peer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connections = []  # List to keep track of connected peers

    def start(self):
        # Start listening for incoming connections
        self.socket.bind((self.host, self.port))
        self.socket.listen(10) # Max 10 connections 
        print(f"Peer {self.host}:{self.port} is listening for incoming connections...")

        # Thread to accept incoming connections
        accept_thread = threading.Thread(target=self.accept_connections)
        accept_thread.start()

    def accept_connections(self):
        while True:
            client_socket, client_address = self.socket.accept()
            print(f"Accepted connection from {client_address}")
            self.connections.append(client_socket)

            # Start a new thread to handle communication with the connected peer
            thread = threading.Thread(target=self.handle_client, args=(client_socket,))
            thread.start()

    def handle_client(self, client_socket):
        while True:
            try:
                data = client_socket.recv(1024)
                if not data:
                    break
                message = data.decode('utf-8')
                print(f"Received message from {client_socket.getpeername()}: {message}")
            except ConnectionResetError:
                break

    def connect_to_peer(self, peer_host, peer_port):
        # Connect to another peer
        peer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            peer_socket.connect((peer_host, peer_port))
            print(f"Connected to peer {peer_host}:{peer_port}")
            self.connections.append(peer_socket)

            # Start a new thread to handle communication with the connected peer
            thread = threading.Thread(target=self.handle_client, args=(peer_socket,))
            thread.start()
        except ConnectionRefusedError:
            print(f"Connection to {peer_host}:{peer_port} refused")

    def send_message(self, message):
        # Send message to all connected peers
        for connection in self.connections:
            try:
                connection.send(message.encode('utf-8'))
            except ConnectionResetError:
                print(f"Connection to {connection.getpeername()} reset unexpectedly")

    def getHost(self):
        return self.host
    
    def getPort(self):
        return self.port