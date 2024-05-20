import random
from sklearn import tree
from Pokemon import pokemon
import pandas as pd
import os
import numbers as np

pokemove = pd.read_csv(r"DataBases\\bridge_pokemon_moves_MAY_LEARN.csv")
pokemon_dt = pd.read_csv(r"DataBases\\df_pokemon.csv")
pokemon_dt = pokemon_dt.drop(columns=["Species", 'Variant', 'Generation', 'Rarity', 'Evolves_from', 'Has_gender_diff', 'VGC2022_rules', 'Monthly Usage (k)', 'Usage Percent (%)', 'Monthly Rank'])
# pokemon_dt=pokemon_dt.drop_duplicates(subset="ID",keep="first")
pokemon_dt = pokemon_dt.set_index("ID")


class DecisionTreeAIAgent:
    def __init__(self, pokemon, team):
        self.pokemon = pokemon
        self.team = team
        self.action_space = get_action_space(pokemon)
        
        # Initialize the decision tree with a simple decision stump or a random tree
        self.decision_tree = tree.DecisionTreeClassifier(max_depth=1, random_state=42)
        
        # Fit the decision tree to a dummy dataset
        dummy_states = [(0,) * len(get_initial_state(self.pokemon, opponent_pokemon))]
        dummy_actions = [random.choice(self.action_space)]
        self.decision_tree.fit(dummy_states, dummy_actions)

    def train(self, num_episodes):
        states = []
        actions = []

        for episode in range(num_episodes):
            # Initialize the game state
            state = get_initial_state(self.pokemon, opponent_pokemon)
            done = False

            while not done:
                # Choose an action based on the current state and the decision tree
                action = self.choose_action(state)

                # Take the action and observe the next state and reward
                next_state, reward, done = take_action(self.pokemon, opponent_pokemon, action)

                # Update the decision tree
                states.append(state)
                actions.append(action)

                state = next_state

            # Fit the decision tree to the collected data
            self.decision_tree.fit(states, actions)

            # Save the decision tree after each episode
            self.save_decision_tree(f"DT/decision_tree_{episode}.pkl")

    def choose_action(self, state):
        # Use the decision tree to predict the best action for the current state
        action = self.decision_tree.predict([state])
        return action

    def save_decision_tree(self, filename):
        # Save the decision tree to a file
        import pickle
        os.makedirs("DT", exist_ok=True)  # Create the "DT" folder if it doesn't exist
        with open(filename, 'wb') as f:
            pickle.dump(self.decision_tree, f)

    def load_decision_tree(self, filename):
        # Load the decision tree from a file
        import pickle
        with open(filename, 'rb') as f:
            self.decision_tree = pickle.load(f)

def get_action_space(pokemon):
    action_space = []

    # Add available moves as actions
    for move in pokemon.move_list:
        action_space.append(("attack", move))

    # Add the option to switch Pokemon
    action_space.append(("switch",))

    return action_space

def get_initial_state(my_pokemon, opponent_pokemon):
    """
    Returns the initial state of the game as a tuple.
    """
    state = (
        my_pokemon.HP, my_pokemon.Attack, my_pokemon.Defense, my_pokemon.Special_attack, my_pokemon.Special_defense, my_pokemon.Speed,
        opponent_pokemon.HP, opponent_pokemon.Attack, opponent_pokemon.Defense, opponent_pokemon.Special_attack, opponent_pokemon.Special_defense, opponent_pokemon.Speed,
        my_pokemon.burn, my_pokemon.paralyze, my_pokemon.poison, my_pokemon.freeze, my_pokemon.confuse,
        opponent_pokemon.burn, opponent_pokemon.paralyze, opponent_pokemon.poison, opponent_pokemon.freeze, opponent_pokemon.confuse
    )
    return state

def take_action(my_pokemon, opponent_pokemon, action):
    """
    Performs the given action and returns the next state, reward, and whether the battle is done or not.
    """
    if isinstance(action, np.ndarray):
        # The action is a NumPy array, so we need to extract the value
        action = action[0]

    if action[0] == "attack":
        # Perform the attack move
        move_name = action[1]
        result = opponent_pokemon.damage_calculation(move_name, my_pokemon)
        opponent_damage = -opponent_pokemon.HP
        my_damage = my_pokemon.damage_calculation(opponent_pokemon.move_list[random.randint(0, 3)], opponent_pokemon)
        reward = opponent_damage + my_damage

    elif action[0] == "switch":
        # Switch to the next available Pokemon
        available_pokemon = [p for p in my_pokemon.team if p.HP > 0 and p != my_pokemon]
        if available_pokemon:
            my_pokemon = random.choice(available_pokemon)
            reward = 0
        else:
            # No available Pokemon to switch to
            reward = -1000  # Assign a large negative reward

    # Get the next state
    next_state = get_initial_state(my_pokemon, opponent_pokemon)

    # Check if the battle is done
    done = (my_pokemon.HP <= 0) or (opponent_pokemon.HP <= 0)

    return next_state, reward, done

# Usage example
my_team = [pokemon(pokemon_dt.loc[pokemon_dt['Name'] == 'Toxapex']),
           pokemon(pokemon_dt.loc[pokemon_dt['Name'] == 'Charizard']),
           pokemon(pokemon_dt.loc[pokemon_dt['Name'] == 'Pikachu']),
           pokemon(pokemon_dt.loc[pokemon_dt['Name'] == 'Alakazam']),
           pokemon(pokemon_dt.loc[pokemon_dt['Name'] == 'Hariyama']),
           pokemon(pokemon_dt.loc[pokemon_dt['Name'] == 'Dragonite'])]

my_pokemon = my_team[0]
opponent_pokemon = pokemon(pokemon_dt.loc[pokemon_dt['Name'] == 'Toucannon'])

ai_agent = DecisionTreeAIAgent(my_pokemon, my_team)
ai_agent.train(num_episodes=1000)

# Test the trained AI agent
ai_pokemon = my_team[0]
opponent_pokemon = pokemon(pokemon_dt.loc[pokemon_dt['Name'] == 'Venusaur'])

while ai_pokemon.HP > 0 and opponent_pokemon.HP > 0:
    state = get_initial_state(ai_pokemon, opponent_pokemon)
    action = ai_agent.choose_action(state)
    if action[0] == "attack":
        # The AI chose to attack
        result = opponent_pokemon.damage_calculation(action[1], ai_pokemon)
        ai_pokemon.damage_calculation(opponent_pokemon.move_list[random.randint(0, 3)], opponent_pokemon)
    else:
        # The AI chose to switch Pokemon
        ai_pokemon = action[1]

    # Print the result or update the game state
    print(ai_pokemon)
    print(opponent_pokemon)