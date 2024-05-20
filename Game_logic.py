import customtkinter as ctk
import pandas as pd
from Pokemon import pokemon
import random

pokemove = pd.read_csv(r"DataBases\\bridge_pokemon_moves_MAY_LEARN.csv")
pokemon_dt = pd.read_csv(r"DataBases\\df_pokemon.csv")
pokemon_dt = pokemon_dt.drop(columns=["Species", 'Variant', 'Generation', 'Rarity', 'Evolves_from', 'Has_gender_diff', 'VGC2022_rules', 'Monthly Usage (k)', 'Usage Percent (%)', 'Monthly Rank'])
# pokemon_dt=pokemon_dt.drop_duplicates(subset="ID",keep="first")
pokemon_dt = pokemon_dt.set_index("ID")

selected_pokemon = pokemon(pokemon_dt.loc[pokemon_dt['Name'] == 'Toxapex'])
opponment_pokemon = pokemon(pokemon_dt.loc[pokemon_dt['Name'] == 'Pikachu'])

print(selected_pokemon, '\n', opponment_pokemon, '\n\n')

while selected_pokemon.HP > 0 and opponment_pokemon.HP > 0:
    cmove_s = input(f"{selected_pokemon.Name}'s choice.\n{selected_pokemon.move_list}\nchoose move: ")
    cmove_o = input(f"{opponment_pokemon.Name}'s choice.\n{opponment_pokemon.move_list}\nchoose move: ")

    # Determine the order of Pokemon attacks
    attack_order = pokemon.determine_first_move(selected_pokemon, cmove_s, opponment_pokemon, cmove_o)

    # Execute the moves in the determined order
    first_pokemon, second_pokemon = attack_order
    if first_pokemon is selected_pokemon:
        opponment_pokemon.damage_calculation(cmove_s, selected_pokemon)
        selected_pokemon.damage_calculation(cmove_o, opponment_pokemon)
        
    else:
        selected_pokemon.damage_calculation(cmove_o, opponment_pokemon)
        opponment_pokemon.damage_calculation(cmove_s, selected_pokemon)
    if input("show stats? (y/n)")=="y": print(selected_pokemon, '\n', opponment_pokemon, '\n\n')
