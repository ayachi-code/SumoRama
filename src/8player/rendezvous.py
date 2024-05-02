import socket
import threading

SERVER_ADDRESS = '127.0.0.1'
SERVER_PORT = 5378

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

sock.bind((SERVER_ADDRESS, SERVER_PORT))

sock.listen()

print("Rendezvous server is online")

while True:
    client_socket, address = sock.accept()
    print(f'{address}' + " connected to match making sever")
