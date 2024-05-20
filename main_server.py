import socket
import sqlite3
import threading
import json
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes

# Generate a private key for the server
private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048,
    backend=default_backend()
)

# Generate a public key for the server
public_key = private_key.public_key()

# Function to send the public key to the client
def send_public_key(client_socket):
    public_key_bytes = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    client_socket.send(public_key_bytes)

# Function to decrypt data using the server's private key
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

# Database setup
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

# Function to add a new user to the database
def add_user_to_database(username, encrypted_password_hex):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    # Insert the username and encrypted password into the database
    cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, encrypted_password_hex))
    conn.commit()
    conn.close()

def make_user_online(username,password):
    pass

# Client thread function
def client_thread(client_socket, addr):
    print(f"Connected to {addr}")
    send_public_key(client_socket)  # Send the public key first
    try:
        while True:
            data = client_socket.recv(1024).decode()
            if not data:
                break
            data = json.loads(data)
            action = data['action']
            if action == 'sign_in':
                username = data['username']
                encrypted_password_hex = data['password']
                encrypted_password = bytes.fromhex(encrypted_password_hex)
                password = decrypt_data(encrypted_password)
                add_user_to_database(username, encrypted_password_hex)
                #send approval
            elif action == 'log_in':
                # Handle login logic here
                pass
            else:
                client_socket.sendall(b"Invalid action.")
    except Exception as e:
        print(f"An error occurred with {addr}: {e}")
    finally:
        client_socket.close()
        print(f"Connection closed with {addr}")

# Main server function
def main():
    setup_database()  # Set up the database
    host = 'localhost'
    port = 12345
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen()

    print(f"Server is listening on {host}:{port}")

    try:
        while True:
            client_socket, addr = server_socket.accept()
            threading.Thread(target=client_thread, args=(client_socket, addr)).start()
    except KeyboardInterrupt:
        print("Server is shutting down...")
    finally:
        server_socket.close()

if __name__ == '__main__':
    main()
