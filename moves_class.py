import pandas as pd
import re

# Read your dataset
pokemove = pd.read_csv(r"DataBases\\bridge_pokemon_moves_MAY_LEARN.csv")
moves_ds = pd.read_csv(r"DataBases\df_moves.csv")
moves_ds.rename(columns={"Prob. (%)": "Prob"}, inplace=True)
moves_ds = moves_ds.dropna(subset=["Damage_class"])
moves_ds["Effect"] = moves_ds["Effect"].astype(str).str.lower()
moves_ds= moves_ds[~((moves_ds["Damage_class"].isin(["Special", "Physical"])) & (moves_ds["Power"].isna()))]

# Define regular expression patterns for different effect types
lower_stat_pattern = r"(?i)lowers? ?\w* (opponent's|user's|target's) (\w+)"
raise_stat_pattern = r"(?i)raises? ?\w* (opponent's|user's) (\w+)"
special_stat_pattern = r"(?i)lowers? ?\w* (opponent's|user's|target's) special (\w+)|raises? ?\w* (opponent's|user's|target's) special (\w+)"
hit_multiple= r"(?i)Hits (\d)-(\d) times"
status_condition= r"(?i)(poison|paralyze|burn|freeze|confuse)"
traps = r"(?i)traps? opponent"
recoil = r"(?i)receives? recoil damage"
atk_first=r"(?i)(attacks|goes) first"
high_crit=r"(?i)high critical hit ratio"
flinch=r"(?i)cause flinch"
drain=r"(?i)hp inflicted"
recover=r'(?i)recovers half its max hp'

# Define a function to translate move effects using regular expressions
def translate_effect(effect):
    lower_match = re.search(lower_stat_pattern, effect)
    raise_match = re.search(raise_stat_pattern, effect)
    special_match = re.search(special_stat_pattern, effect)
    hit_multiple_match = re.search(hit_multiple, effect)
    status_condition_match = re.search(status_condition, effect)
    traps_match = re.search(traps, effect)
    recoil_match = re.search(recoil, effect)
    atk_first_match = re.search(atk_first, effect)
    high_crit_match=re.search(high_crit,effect)
    flinch_match=re.search(flinch,effect)
    drain_match=re.search(drain,effect)
    recover_match=re.search(recover,effect)
    move_effect=""
    effects = []


    if special_match:
        whom = special_match.group(1) or special_match.group(3)
        #print(type(special_match.group(4)))
        stat = f"special {special_match.group(4)}" if special_match.group(2)==None else f"special {special_match.group(2)}"
        effect_type = "lower" if special_match.group(1) else "raise"
        whom = whom.replace("target", "opponent")
        effects.append(f"stat change: ({whom[:-2]}/{effect_type}/{stat})")
    elif raise_match:
        whom = raise_match.group(1)
        stat = raise_match.group(2)
        effect_type = "raise"
        whom = whom.replace("target", "opponent")
        effects.append(f"stat change: ({whom[:-2]}/{effect_type}/{stat})")
    elif lower_match:
        whom = lower_match.group(1)
        stat = lower_match.group(2)
        effect_type = "lower"
        whom = whom.replace("target", "opponent")
        effects.append(f"stat change: ({whom[:-2]}/{effect_type}/{stat})")

    if hit_multiple_match:
        effects.append("multihit")
    if status_condition_match:
        effects.append(status_condition_match.group(1))
    if traps_match:
        effects.append("traps")
    if recoil_match:
        effects.append("recoil")
    if atk_first_match:
        effects.append("first")
    if high_crit_match:
        effects.append("critical")
    if flinch_match:
        effects.append("flinch")
    if drain_match:
        effects.append("drain")
    if recover_match:
        effects.append("recover")

    # Combine all effects into a comma-separated string
    move_effect += ",".join(effects)
    if move_effect=="":
        move_effect="nan"

    return move_effect

# Apply the translation function to create the Move_effect column
moves_ds["Move_effect"] = moves_ds["Effect"].apply(translate_effect)
moves_ds = moves_ds.where((moves_ds["Move_effect"] != "nan") | (moves_ds["Damage_class"] != "Status")).dropna(how="all")

chosed_moves= pokemove.where(pokemove['Pokemon']=="Pikachu").dropna(how='all')
moveset = chosed_moves.merge(moves_ds,left_on="Move",right_on="Name")
moveset=moveset.drop(columns=['Pokemon','Move','Introducted_in'])
moveset

def get_moves():
    return moves_ds