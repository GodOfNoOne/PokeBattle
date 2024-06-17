import socket
import threading
import pickle
from Pokemon import pokemon
import random
import time

class Game_Server:
    def __init__(self, host=socket.gethostname(), port=6969):
        self.host = host
        self.port = port
        self.server_socket = None
        self.main_server_socket = None
        self.clients = []
        self.pokemon_teams = []
    def start_server(self):
        # Create a socket object
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(1)
        print(f"Game server is on {self.host}:{self.port}")
        self.main_server_socket, addr = self.server_socket.accept()
        print("Connected to main server")
        self.main_server_socket.send("connected".encode())
        data = self.main_server_socket.recv(1024).decode()
        if data == "start":
            self.start_game()

    def start_game(self):
        print(f"Waiting for 2 self.clients on {self.host}:{self.port}")
        self.server_socket.listen(2)
        # Accept connections from two self.clients
        while True:
            # Accept a connection
            client_socket, addr = self.server_socket.accept()
            client_thread = threading.Thread(target=self.handle_client, args=(client_socket, addr, self.port,))
            client_thread.start()

    def handle_client(self, client_socket, addr, port):
        print(f"Accepted connection from {addr} in port {port}")
        self.clients.append(client_socket)
        print(f"There are {len(self.clients)} self.clients")
        # Receive the team data from the client
        team_data = self.recvall(client_socket)
        team = pickle.loads(team_data)
        self.pokemon_teams.append(team)
        if len(self.clients) == 2:
            for c in self.clients:
                c.send("start".encode())
            print(f"Game starts on port {port}")
            self.start_battle(self.clients, self.pokemon_teams)

    def start_battle(self, clients, pokemon_teams):
        # Create instances of the active Pokémon for each team
        team1 = self.pokemon_teams[0]
        team2 = self.pokemon_teams[1]
        active_pokemon1 = team1[0]
        active_pokemon2 = team2[0]

        self.send_pokemon_data(self.clients[0], active_pokemon1)
        self.send_pokemon_data(self.clients[0], active_pokemon2)
        self.send_pokemon_data(self.clients[1], active_pokemon2)
        self.send_pokemon_data(self.clients[1], active_pokemon1)
        # Conduct the battle
        while True:
            try:
                # Get the moves from the self.clients
                print("Waiting for both self.clients to send moves")
                action1 = self.receive_move(self.clients[0])
                action2 = self.receive_move(self.clients[1])
                result = ""
                print(action1, action2)
                if "move" in action1 and "move" in action2:
                    move1 = action1.split(':')[1]
                    move2 = action2.split(':')[1]

                    # Determine the order of moves
                    first_pokemon, second_pokemon = pokemon.determine_first_move(active_pokemon1, move1, active_pokemon2, move2)
                    # Apply the moves
                    if first_pokemon is active_pokemon1:
                        result += active_pokemon2.damage_calculation(move1, active_pokemon1)
                        time.sleep(0.001)
                        result += active_pokemon1.damage_calculation(move2, active_pokemon2)
                    else:
                        result += active_pokemon1.damage_calculation(move2, active_pokemon2)
                        time.sleep(0.001)
                        result += active_pokemon2.damage_calculation(move1, active_pokemon1)

                elif "switch" in action1 and "move" in action2:
                    switching = action1.split(":")[1]
                    for t in team1:
                        if t.Name == switching:
                            result += f"{active_pokemon1.Name} was switched to {switching}\n"
                            active_pokemon1 = t

                    move = action2.split(":")[1]
                    result += active_pokemon1.damage_calculation(move, active_pokemon2)
                elif "switch" in action2 and "move" in action1:
                    switching = action2.split(":")[1]
                    for t in team2:
                        if t.Name == switching:
                            result += f"{active_pokemon2.Name} was switched to {switching}\n"
                            active_pokemon2 = t

                    move = action1.split(":")[1]
                    result += active_pokemon2.damage_calculation(move, active_pokemon1)
                else:
                    switching1 = action1.split(":")[1]
                    switching2 = action2.split(":")[1]
                    for t in team2:
                        if t.Name == switching2:
                            result += f"{active_pokemon2.Name} was switched to {switching2}\n"
                            active_pokemon2 = t

                    for t in team1:
                        if t.Name == switching1:
                            result += f"{active_pokemon2.Name} was switched to {switching1}\n"
                            active_pokemon1 = t

                print(result)
                self.send_result(self.clients[0], result)
                self.send_result(self.clients[1], result)

                # Wait for both self.clients to request the result
                responses = [False, False]
                while not all(responses):
                    for i, client in enumerate(self.clients):
                        response = client.recv(1024).decode()
                        if response == "Give results":
                            responses[i] = True
                print("Sending Pokemon\n")

                # Send Pokémon status after both self.clients request it
                self.send_pokemon_data(self.clients[0], active_pokemon1)
                self.send_pokemon_data(self.clients[0], active_pokemon2)
                self.send_pokemon_data(self.clients[1], active_pokemon2)
                self.send_pokemon_data(self.clients[1], active_pokemon1)

                team_data = pickle.dumps(team1)
                data_len = len(team_data).to_bytes(4, byteorder='big')
                self.clients[0].sendall(data_len + team_data)

                team_data = pickle.dumps(team2)
                data_len = len(team_data).to_bytes(4, byteorder='big')
                self.clients[1].sendall(data_len + team_data)

                # Sending results if someone won, or not
                if not self.check_team(team1) or not self.check_team(team2):
                    if not self.check_team(team1):
                        self.send_result(self.clients[0], "You Lost")
                        self.send_result(self.clients[1], "You Won")
                    else:
                        self.send_result(self.clients[1], "You Lost")
                        self.send_result(self.clients[0], "You Won")
                else:
                    self.send_result(self.clients[0], "Next Turn")
                    self.send_result(self.clients[1], "Next Turn")

            except Exception as e:
                print(f"An error occurred: {e}")
                print(len(self.clients))
                try:
                    self.send_result(self.clients[0], "You Won")
                    self.send_result(self.clients[1], "You Won")
                    print(f"Sent result to {self.clients[0]}")
                except:
                    pass
                break

    def recvall(self, sock):
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

    def receive_move(self, client):
        # Receive the move choice from the client
        move_data = client.recv(1024)
        move = move_data.decode()
        return move

    def send_pokemon_data(self, client, pokemon):
        # Serialize the Pokémon object
        pokemon_data = pickle.dumps(pokemon)

        data_len = len(pokemon_data).to_bytes(4, byteorder='big')
        client.sendall(data_len + pokemon_data)

    def send_result(self, client, result):
        # Send the result to the client
        client.send(result.encode())

    def check_team(self, team):
        # Return false if no pokemon has hp in the team
        for t in team:
            if t.HP > 0:
                return True
        return False
