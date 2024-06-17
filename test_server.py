import socket
import threading
import pickle
from Pokemon import pokemon
import random
import time
import server_battle
from server_battle import Game_Server
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
import sqlite3


# Generate a private key for the server
private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048,
    backend=default_backend()
)

# Generate a public key for the server
public_key = private_key.public_key()


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
server_ports = []

# In your handle_client function
def handle_client(client_socket,addr):
    print(f"Accepted connection from {addr}")
    clients.append(client_socket)
    print(f"there are {len(clients)} clients")

    while True:
        data=client_socket.recv(1024).decode()
        print(data)
        if "give public key" in data:
            send_public_key(client_socket)

        elif "sign up" in data:
            encrypted_username = recvall(client_socket)
            decrypted_username = decrypt_data(encrypted_username)
            username = decrypted_username

            encrypted_password = recvall(client_socket)

            if check_sign_in(username):
                client_socket.send("failure".encode())
            else:
                add_user_to_database(username, encrypted_password)
                client_socket.send("success".encode()) 

        elif "log in" in data:
            encrypted_username = recvall(client_socket)
            decrypted_username = decrypt_data(encrypted_username)
            username = decrypted_username

            encrypted_password = recvall(client_socket)

            if check_login(username, decrypt_data(encrypted_password)):
                client_socket.send("success".encode())
                data=client_socket.recv(1024).decode()
                if "team" in data:
                    team = get_team_data(username)
                    if team!=None:
                        client_socket.send("yes".encode())
                        time.sleep(0.01)
                        team_data = pickle.dumps(team)
                        team_data_len = len(team_data).to_bytes(4, byteorder='big')
                        client_socket.sendall(team_data_len + team_data)
            else:
                client_socket.send("failure".encode())

            

        elif "edit team" in data:
            team_data = recvall(client_socket)
            username = data.split(":")[-1]
            print(f"team data received from {username}")
            save_team_data(team_data,username)
            get_team_data(username)
                
        elif "create room" in data:
            generated_port = random.choice([p for p in range(12345, 23456) if p not in server_ports])
            username = data.split(":")[-1]
            if get_team_data(username)!=None:
                client_socket.send("ok".encode())
                data=client_socket.recv(1024).decode()
                if data=="give code":
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
            else:
                client_socket.send("no team".encode())

        elif "join room" in data:
            username = data.split(":")[-1]
            if get_team_data(username)!=None:
                print("team found")
                client_socket.send("ok".encode())
                data=client_socket.recv(1024).decode()
                if "get rooms" in data:
                    print("sending rooms")
                    s=",".join(str(p) for p in server_ports) if len(server_ports)>0 else "no rooms"
                    print(s)
                    client_socket.send(s.encode())
                    data=client_socket.recv(1024).decode()
                    if "connect me to" in data:
                        print(f"connected to {data.split()[-1]}")
                        client_socket.send("connected".encode())
                        time.sleep(0.01)
                        print("sending team")
                        team = get_team_data(username)
                        team_data = pickle.dumps(team)
                        team_data_len = len(team_data).to_bytes(4, byteorder='big')
                        client_socket.sendall(team_data_len + team_data)
                    else:
                        print("no connection")
            else:
                client_socket.send("no team".encode())

        elif "exit" in data:
            print(f"closing connection with {addr}")
            username = data.split(":")[-1]
            print(f"{username} is exiting")
            conn = sqlite3.connect('users.db')
            cursor = conn.cursor()
            cursor.execute('UPDATE users SET status="offline" WHERE username=?', (username,))
            conn.commit()
            conn.close()
            client_socket.close()
            clients.remove(client_socket)
            break
                

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

def setup_database():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''
    DROP TABLE IF EXISTS users
                   ''')
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL,
        current_team TEXT,
        status TEXT CHECK(status IN ('online', 'offline')) NOT NULL DEFAULT 'offline',
        last_fought_against TEXT
    )
    ''')
    conn.commit()
    conn.close()

def check_sign_in(username):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE username=?', (username,))
    user = cursor.fetchone()
    if user:  return True
    conn.close()
    return False

def check_login(username, password):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE username=?', (username,))
    user = cursor.fetchone()
    if user: 
        status=user[4]
        decrypted_password=decrypt_data(user[2])
        print(decrypted_password, status)
        if status=="offline" and password==decrypted_password:
            cursor.execute('UPDATE users SET status="online" WHERE username=?', (username,))
            conn.commit()
            return True
    conn.close()
    return False

def add_user_to_database(username, encrypted_password_hex):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    # Insert the username and encrypted password into the database
    cursor.execute('INSERT INTO users (username, password, status) VALUES (?, ?, "online")', (username, encrypted_password_hex))
    conn.commit()
    conn.close()


def send_public_key(client_socket):
    public_key_data = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    public_key_data = pickle.dumps(public_key_data)
    public_key_data_len = len(public_key_data).to_bytes(4, byteorder='big')
    client_socket.sendall(public_key_data_len + public_key_data)

def decrypt_data(encrypted_password):
    decrypted_password = private_key.decrypt(
        encrypted_password,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return decrypted_password.decode()

def save_team_data(team,username):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET current_team=? WHERE username=?', (team, username))
    conn.commit()
    conn.close()

def get_team_data(username):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT current_team FROM users WHERE username=?', (username,))
    team_data = cursor.fetchone()
    conn.close()
    if team_data[0]==None: 
        print("No team data found")
        return None
    team=pickle.loads(team_data[0])
    return team



setup_database()
while True:
    # Accept a connection
    client_socket, addr = server_socket.accept()
    client_thread = threading.Thread(target=handle_client, args=(client_socket,addr,))
    client_thread.start()