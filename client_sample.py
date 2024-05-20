import socket
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
import json

# Function to connect to the server
def connect_to_server(host, port):
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((host, port))
        return client_socket
    except ConnectionRefusedError:
        print("Failed to connect to the server.")
        return None

# Function to receive the public key from the server
def receive_public_key(client_socket):
    public_key_data = client_socket.recv(4096)  # Adjust buffer size as needed
    public_key = serialization.load_pem_public_key(public_key_data, backend=default_backend())
    return public_key

# Function to encrypt the password using the received public key
def encrypt_password(public_key, password):
    encrypted_password = public_key.encrypt(
        password.encode(),
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return encrypted_password

# Main function to start the client application
def main():
    client_socket = connect_to_server('localhost', 12345)
    if client_socket:
        print("Connected to the server. Receiving the public key...")
        public_key = receive_public_key(client_socket)  # Receive the public key first
        username = input("Enter your username: ")
        password = input("Enter your password: ")
        encrypted_password = encrypt_password(public_key, password)  # Encrypt the password
        sign_in_data = {
            'action': 'sign_in',
            'username': username,
            'password': encrypted_password.hex()  # Convert to hexadecimal
        }
        client_socket.sendall(json.dumps(sign_in_data).encode())  # Send sign-in data as JSON
        # Handle server response
        # ...
        client_socket.close()

if __name__ == "__main__":
    main()
