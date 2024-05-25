import socket
import threading
import pickle
from Pokemon import pokemon
import random
import time
import server_battle
from test import Game_Server

# Create a socket object
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Get local machine name
host = socket.gethostname()

# Reserve a port for your service
port = 6969

# Bind to the port
server_socket.bind((host, port))

# Start listening for connections
server_socket.listen()
print("server is on")

# Initialize a list to hold the client connections
clients = []
server_ports = [12345]

# In your handle_client function
def handle_client(client_socket,addr):
    print(f"Accepted connection from {addr}")
    clients.append(client_socket)
    print(f"there are {len(clients)} clients")

    while True:
        data=client_socket.recv(1024).decode()
        if "edit team" in data:
            team_data = recvall(client_socket)
            team = pickle.loads(team_data)
            for t in team: 
                if t!=None: print(t)
                
        elif "create room" in data:
            generated_port = random.choice([p for p in range(12345, 23456) if p not in server_ports])
            client_socket.send(f"{generated_port}".encode())
            server_ports.append(generated_port)
            game_server = Game_Server(host, generated_port)
            game_thread = threading.Thread(target=game_server.start_server)
            game_thread.start()

            #connect to the game server
            game_client= socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            print(f"connecting to {host}:{generated_port}")
            game_client.connect((host,generated_port))
            data=game_client.recv(1024).decode()
            if data=="connected":
                print(f"connected to {generated_port}")
                game_client.send("start".encode())

        elif "join room" in data:
            client_socket.send(",".join(str(p) for p in server_ports).encode())
            data=client_socket.recv(1024).decode()
            if "connect me to" in data:
                print(f"connected to {data.split()[-1]}")
                game_port = int(data.split()[-1])
                client_socket.send("connected".encode())
                

def recvall(sock):
    # First, receive the message length (assume it's a 4-byte integer)
    msg_len_data = b''
    while len(msg_len_data) < 4:
        chunk = sock.recv(4 - len(msg_len_data))
        if not chunk:
            raise RuntimeError("Socket connection broken")
        msg_len_data += chunk

    msg_len = int.from_bytes(msg_len_data, byteorder='big')

    # Now, receive the actual message data
    data = b''
    while len(data) < msg_len:
        chunk = sock.recv(msg_len - len(data))
        if not chunk:
            raise RuntimeError("Socket connection broken")
        data += chunk

    return data


while True:
    # Accept a connection
    client_socket, addr = server_socket.accept()
    client_thread = threading.Thread(target=handle_client, args=(client_socket,addr,))
    client_thread.start()