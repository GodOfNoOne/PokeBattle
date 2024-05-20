import socket
import threading
import pickle
from Pokemon import pokemon
import random
import time

# Create a socket object
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Get local machine name
host = socket.gethostname()

# Reserve a port for your service
port = 12345

# Bind to the port
server_socket.bind((host, port))

# Start listening for connections
server_socket.listen(2)
print("server is on")

# Initialize a list to hold the client connections
clients = []
pokemon_teams = []


# In your handle_client function
def handle_client(client_socket,addr):
    print(f"Accepted connection from {addr}")
    clients.append(client_socket)
    print(f"there are {len(clients)} clients")
    # Receive the team data from the client
    team_data = recvall(client_socket)
    team = pickle.loads(team_data)
    pokemon_teams.append(team)
    for t in team: print(t)
    if len(clients)==2:
        for c in clients: c.send("start".encode())
        start_battle()



def start_battle():
    # Create instances of the active Pokémon for each team
    team1 = pokemon_teams[0]
    team2 = pokemon_teams[1]
    active_pokemon1 = team1[0]
    active_pokemon2 = team2[0]

    send_pokemon_data(clients[0], active_pokemon1)
    send_pokemon_data(clients[0],active_pokemon2)
    send_pokemon_data(clients[1], active_pokemon2)
    send_pokemon_data(clients[1],active_pokemon1)
    # Conduct the battle
    while True:
        try:
            # Get the moves from the clients
            print("waiting for both clients to send moves")
            action1 = receive_move(clients[0])
            action2 = receive_move(clients[1])
            result=""
            print(action1,action2)
            if "move" in action1 and "move" in action2:
                move1=action1.split(':')[1]
                move2=action2.split(':')[1]

                # Determine the order of moves
                first_pokemon, second_pokemon = pokemon.determine_first_move(active_pokemon1, move1, active_pokemon2, move2)
                # Apply the moves
                if first_pokemon is active_pokemon1:
                    result+=active_pokemon2.damage_calculation(move1, active_pokemon1)
                    time.sleep(0.001)
                    result+=active_pokemon1.damage_calculation(move2, active_pokemon2)
                else:
                    result+=active_pokemon1.damage_calculation(move2, active_pokemon2)
                    time.sleep(0.001)
                    result+=active_pokemon2.damage_calculation(move1, active_pokemon1)
            
            elif "switch" in action1 and "move" in action2:
                switching=action1.split(":")[1]
                for t in team1:
                    if t.Name==switching:
                        result+=f"{active_pokemon1.Name} was switched to {switching}\n"
                        active_pokemon1=t
                
                move=action2.split(":")[1]
                result+=active_pokemon1.damage_calculation(move, active_pokemon2)
            elif "switch" in action2 and "move" in action1:
                switching=action2.split(":")[1]
                for t in team2:
                    if t.Name==switching:
                        result+=f"{active_pokemon2.Name} was switched to {switching}\n"
                        active_pokemon2=t

                move=action1.split(":")[1]
                result+=active_pokemon2.damage_calculation(move, active_pokemon1)
            else:
                switching1=action1.split(":")[1]
                switching2=action2.split(":")[1]
                for t in team2:
                    if t.Name==switching2:
                        result+=f"{active_pokemon2.Name} was switched to {switching2}\n"
                        active_pokemon2=t
                    
                for t in team1:
                    if t.Name==switching1:
                        result+=f"{active_pokemon2.Name} was switched to {switching1}\n"
                        active_pokemon1=t

            
            print(result)
            clients[0].send(result.encode())
            clients[1].send(result.encode())

            
            # Wait for both clients to request the result
            responses = [False, False]
            while not all(responses):
                for i, client in enumerate(clients):
                    response = client.recv(1024).decode()
                    if response == "Give results":
                        responses[i] = True
            print("Sending Pokemon\n")

            # Send Pokémon status after both clients request it
            send_pokemon_data(clients[0], active_pokemon1)
            send_pokemon_data(clients[0], active_pokemon2)
            send_pokemon_data(clients[1], active_pokemon2)
            send_pokemon_data(clients[1], active_pokemon1)

            team_data = pickle.dumps(team1)
            data_len = len(team_data).to_bytes(4, byteorder='big')
            clients[0].sendall(data_len + team_data)

            team_data = pickle.dumps(team2)
            data_len = len(team_data).to_bytes(4, byteorder='big')
            clients[1].sendall(data_len + team_data)

            
            #sending results if someone won, or not
            if not check_team(team1) or not check_team(team2):
                if not check_team(team1):
                    send_result(clients[0],"You Lost")
                    send_result(clients[1],"You Won")
                else:
                    send_result(clients[1],"You Lost")
                    send_result(clients[0],"You Won")
            else:
                send_result(clients[0],"Next Turn")
                send_result(clients[1],"Next Turn")

        except (ConnectionResetError, BrokenPipeError):
            # Handle client disconnection
            if clients[0] in clients:
                clients.remove(clients[0])
                print("Client 1 disconnected. Client 2 wins.")
                result = "Client 2 wins!"
                if clients:
                    for client in clients:
                        try:
                            send_result(client, result)
                        except ConnectionResetError:
                            pass
            else:
                clients.remove(clients[1])
                print("Client 2 disconnected. Client 1 wins.")
                result = "Client 1 wins!"
                if clients:
                    for client in clients:
                        try:
                            send_result(client, result)
                        except ConnectionResetError:
                            pass
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

def receive_move(client):
    # Receive the move choice from the client
    move_data = client.recv(1024)
    move = move_data.decode()
    return move

def send_pokemon_data(client, pokemon):
    # Serialize the Pokémon object
    pokemon_data = pickle.dumps(pokemon)

    data_len = len(pokemon_data).to_bytes(4, byteorder='big')
    client.sendall(data_len + pokemon_data)

def send_result(client, result):
    # Send the result to the client
    client.send(result.encode())

def check_team(team):
    #return false if no pokemon has hp in the team
    for t in team:
        if t.HP>0:
            return True
    return False

while True:
    # Accept a connection
    client_socket, addr = server_socket.accept()
    client_thread = threading.Thread(target=handle_client, args=(client_socket,addr,))
    client_thread.start()

