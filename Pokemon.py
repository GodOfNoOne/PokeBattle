import pandas as pd
import random
import moves_class

#type chart
type_chart=pd.read_csv(r"DataBases\\bridge_type_type_MOVE_EFFECTIVENESS_ON_POKEMON.csv")
type_chart["Damage Multiplier"].fillna(1,inplace=True)
type_chart['Damage Multiplier'] = type_chart['Damage Multiplier'].replace('½', '0.5').astype(float)

#pokemon database
pokemon_dt = pd.read_csv(r"DataBases\\df_pokemon.csv")
pokemon_dt=pokemon_dt.drop(columns=["Species",'Variant','Generation','Rarity','Evolves_from','Has_gender_diff','VGC2022_rules','Monthly Usage (k)','Usage Percent (%)','Monthly Rank'])
#pokemon_dt=pokemon_dt.drop_duplicates(subset="ID",keep="first")
pokemon_dt=pokemon_dt.set_index("ID")

pokemove = pd.read_csv(r"DataBases\\bridge_pokemon_moves_MAY_LEARN.csv")

#moves database
moves_ds=moves_class.get_moves()

class pokemon:
    
    def set_Ev(self,evs=[85,85,85,85,85,85]):
        hp,atk,defense,sp_atk,sp_def,spd=evs
        self.HP=(self.HP*2+hp//4)+110
        self.Attack=(self.Attack*2+atk//4)+5
        self.Defense=(self.Defense*2+defense//4)+5
        self.Special_attack=(self.Special_attack*2+sp_atk//4)+5
        self.Special_defense=(self.Special_defense*2+sp_def//4)+5
        self.Speed=(self.Speed*2+spd//4)+5
    
    def set_moves(self,moves):
        self.move_list=moves
        chosed_moves= pokemove.where(pokemove['Pokemon']==self.Name).dropna(how='all')
        self.moveset = chosed_moves.merge(moves_ds,left_on="Move",right_on="Name")
        self.moveset=self.moveset.drop(columns=['Pokemon','Move','Introducted_in'])
        self.moveset=self.moveset.where(self.moveset["Name"].isin(moves)).dropna(how='all')
        

        self.move_list=self.moveset["Name"].tolist()
    def __init__(self, df):
        self.df = df
        self.Name = str(df["Name"].values[0])
        self.Type1 = str(df["Type1"].values[0])
        self.Type2 = str(df["Type2"].values[0])
        self.HP = int(df["HP"].values[0])
        self.Attack = int(df["Attack"].values[0])
        self.Defense = int(df["Defense"].values[0])
        self.Special_attack = int(df["Sp. Atk"].values[0])
        self.Special_defense = int(df["Sp. Def"].values[0])
        self.Speed = int(df["Speed"].values[0])
        self.mult_stages = [0,0,0,0,0] #atk,def,spatk,spdef,spd
        self.img= str(df["image_url"].values[0])
        self.max_HP = self.HP
        self.initial_Attack = self.Attack
        self.initial_Defense = self.Defense
        self.initial_Special_attack = self.Special_attack
        self.initial_Special_defense = self.Special_defense
        self.initial_Speed = self.Speed
        self.weather = "Clear"
        self.has_physical_screen=False
        self.has_special_screen = False

        self.status_turns=0
        self.burn=False
        self.paralyze=False
        self.poison=False
        self.freeze=False
        self.confuse= False
        self.flinch=False


        chosed_moves= pokemove.where(pokemove['Pokemon']==self.Name).dropna(how='all')
        self.moveset = chosed_moves.merge(moves_ds,left_on="Move",right_on="Name")
        self.moveset=self.moveset.drop(columns=['Pokemon','Move','Introducted_in'])
        self.moveset=self.moveset.head(4)
        self.move_list=self.moveset["Name"].tolist()
                 

    def TypeAffective(self, t):
        m1,m2=1,1
        if t in type_chart["Def. Pokemon Type"].unique():
            effect1 = type_chart[(type_chart["Atk. Move Type"] == t) & (type_chart["Def. Pokemon Type"] == self.Type1)]
            if not effect1.empty:
                m1 = effect1["Damage Multiplier"].iloc[0]
            
            if self.Type2!="nan":
                effect2 = type_chart[(type_chart["Atk. Move Type"] == t) & (type_chart["Def. Pokemon Type"] == self.Type2)]
                if not effect2.empty:
                    m2 = effect2["Damage Multiplier"].iloc[0]
        return m1*m2
    
    def weather_handle(self,t):

        if self.weather=="Clear": return 1
        elif self.weather=="Sunny":
            if t=="Fire":return 1.5
            elif t=="Water":return 0.5
            return 1
        elif self.weather=="Rainy":
            if t=="Fire":return 0.5
            elif t=="Water":return 1.5
            return 1
        return 1
    
    def has_status_effect(self):
        if self.burn or self.paralyze or self.poison or self.freeze or self.confuse: return True

        else:
            return False

    #handling stages manipulation
    def handle_stages(self,stage):
        if stage==3: return 2.5
        elif stage==2: return 2
        elif stage ==1: return 1.5
        elif stage==-1: return 0.66
        elif stage==-2: return 0.5
        elif stage==-3: return 0.4
        else: return 1

        #add the switch mechanic to the first determination: if someone switches, he will always be first, if both switch it doesn't metter, else first by move.
    def determine_first_move(pokemon1, move1, pokemon2, move2):
        if move1 in pokemon1.moveset["Name"].unique() and move2 in pokemon2.moveset["Name"].unique():
            move1=moves_ds.where(moves_ds["Name"] == move1).dropna(how="all")
            move2=moves_ds.where(moves_ds["Name"] == move2).dropna(how="all")
        # Check if either Pokemon has the first effect
            has_first_effect1 = "first" in move1.get("Move_effect", "")
            has_first_effect2 = "first" in move2.get("Move_effect", "")

            if has_first_effect1 and not has_first_effect2:
                # Only pokemon1 has the first effect
                return [pokemon1, pokemon2]
            elif not has_first_effect1 and has_first_effect2:
                # Only pokemon2 has the first effect
                return [pokemon2, pokemon1]
            elif has_first_effect1 and has_first_effect2:
                # Both Pokemon have the first effect, compare Speed stats
                if pokemon1.Speed > pokemon2.Speed:
                    return [pokemon1, pokemon2]
                elif pokemon1.Speed < pokemon2.Speed:
                    return [pokemon2, pokemon1]
                else:
                    # If Speed is the same, randomly choose order
                    return random.sample([pokemon1, pokemon2], 2)
            else:
                # Neither Pokemon has the first effect, compare Speed stats
                if pokemon1.Speed > pokemon2.Speed:
                    return [pokemon1, pokemon2]
                elif pokemon1.Speed < pokemon2.Speed:
                    return [pokemon2, pokemon1]
                else:
                    # If Speed is the same, randomly choose order
                    return random.sample([pokemon1, pokemon2], 2)
        else: print("error: Move not found")
    
    def handle_status_effects(self):
        if self.burn or self.poison:
            effect= "burn" if self.burn else "poison"
            if self.status_turns>0:
                d=int(self.max_HP*random.uniform(0.03,0.08))
                self.HP-=d
                self.status_turns-=1
                return (f"{self.Name} took {d} damage from the {effect}!\n")
            else:
                if self.burn: self.burn=False 
                else: self.poison=False
                return (f"{self.Name} is no longer {effect}ed.\n")
        elif self.paralyze or self.confuse:
            effect= "paralyze" if self.paralyze else "confuse"
            if self.status_turns>0: self.status_turns-=1
            else: 
                if self.paralyze: self.paralyze=False 
                else: self.confuse=False
                return (f"{self.Name} is no longer {effect}d\n")
        elif self.freeze:
            if self.status_turns>0:
                d = int(random.uniform(0.01, 0.05) * self.max_HP) if random.random() <= 0.5 else 0
                self.HP-=d
                self.status_turns-=1
                return (f"{self.Name} took {d} damage from freeze\n")
            else:
                self.freeze=False
                return (f"{self.Name} is no longer freezing\n")
        return ""

    #handaling all kinds of effects
    def handle_effect(self, move, op_pokemon,damage=0):
        if move in op_pokemon.moveset["Name"].unique():
            selected_move = moves_ds.where(moves_ds["Name"] == move).dropna(how="all")
            effect_string = selected_move["Move_effect"].iloc[0]
            prob = selected_move["Prob"].iloc[0]
            effects_list = effect_string.split(',')

            stat_index_map = {
                "attack": 0,
                "defense": 1,
                "special attack": 2,
                "special defense": 3,
                "speed": 4
            }

            def update_stat(pokemon, stat, index):
                initial_stat = getattr(pokemon, f"initial_{str.capitalize(stat).replace(' ', '_')}")
                stage = pokemon.mult_stages[index]
                multiplier = pokemon.handle_stages(stage)
                new_stat = int(initial_stat * multiplier)
                setattr(pokemon, str.capitalize(stat).replace(' ', '_'), new_stat)
                s= (f"{pokemon.Name}'s {stat} was {initial_stat}, but now it is {new_stat}. The {stat} stage is {stage}\n")
                return s

            def apply_status_effect(effect, probability):
                if self.has_status_effect()==False:
                    if pd.isna(probability) or probability == 100.0:
                        apply_effect = True
                    else:
                        apply_effect = random.random() <= (probability / 100)
                    if apply_effect:
                        self.status_turns= random.randint(2,5)
                        setattr(self, f"{effect}", True)
                        return (f"{self.Name} is {effect}ed for {self.status_turns} turns\n")
                else:
                    s = "burn" if self.burn else "paralyze" if self.paralyze else "poison" if self.poison else "freeze" if self.freeze else "confuse" if self.confuse else ""
                    return (f"{self.Name} is already {s}end and cannot be {effect}ed.\n")
                return ""
            for e in effects_list:
                if "stat change" in e:
                    e = e[14:-1].split('/')
                    whom = e[0]
                    effect_type = e[1]
                    stat = e[2]

                    if stat in stat_index_map:
                        index = stat_index_map[stat]
                        if whom == "opponent": pokemon = self
                        else: pokemon = op_pokemon
                        # Check probability
                        if pd.isna(prob) or prob == 100.0: apply_effect = True
                        else: apply_effect = random.random() <= (prob / 100)

                        if apply_effect:
                            if effect_type == "lower" and pokemon.mult_stages[index] > -3:
                                pokemon.mult_stages[index] -= 1
                            elif effect_type == "raise" and pokemon.mult_stages[index] < 3:
                                pokemon.mult_stages[index] += 1

                            s=update_stat(pokemon, stat, index)
                            return s
                elif e in ["paralyze", "burn", "poison", "freeze", "confuse"]:
                    return apply_status_effect(e,prob)

                elif "drain" in e:
                    d=int(damage*0.5)
                    if op_pokemon.HP-d<op_pokemon.max_HP: op_pokemon.HP+=d
                    else: op_pokemon.HP=op_pokemon.max_HP
                    return (f"{op_pokemon.Name} drained {d} hp from {move}\n")
                elif "multihit" in e:
                    hits = random.randint(2,5)
                    for _ in range(hits):
                        self.damage_calculation(move, op_pokemon, multihit=True)

                elif "recoil" in e:
                    d=int(damage*random.uniform(0.25,0.33))
                    op_pokemon.HP-=d
                    return (f"{op_pokemon.Name} got {d} damage from recoil\n")
                elif "flinch" in e:
                    if pd.isna(prob) or prob == 100.0:
                        apply_effect = True
                    else:
                        apply_effect = random.random() <= (prob / 100)
                    if apply_effect:
                        if not self.flinch: self.flinch=True
                        else: return ("already flinched\n")
                elif "critical" in e:
                    pass
                elif "traps" in e:
                    pass
                return ""
                

                    
                
                

    #damage to self (with move that the opponment did to the user)
    def damage_calculation(self,move,op_pokemon,multihit=False):
        if move in op_pokemon.moveset["Name"].unique():
            selected_move= moves_ds.where(moves_ds["Name"]==move).dropna(how="all")
            if (op_pokemon.paralyze or op_pokemon.freeze) and random.randint(0,100)<25:
                effect= "paralyze" if op_pokemon.paralyze else "freeze"
                return (f"{op_pokemon.Name} can't move due to {effect}\n{self.handle_status_effects()}")
            elif op_pokemon.confuse and random.randint(0,100)<10:
                d=int(self.max_HP*random.uniform(0.03,0.08))
                op_pokemon.HP-=d
                return (f"{op_pokemon.Name} is confused and he dealt {d} damage to himself\n")
            elif op_pokemon.flinch:
                op_pokemon.flinch=False
                return (f"{op_pokemon.Name} flinched\n{self.handle_status_effects()}")

            else:
                if "Status" in selected_move["Damage_class"].iloc[0]:
                    s= (f"{op_pokemon.Name} used {move}, a status move\n\n")
                    s+=self.handle_effect(move,op_pokemon)
                    s+=self.handle_status_effects()
                    return s
                elif "Special" in selected_move["Damage_class"].iloc[0]:
                    power = float(selected_move["Power"])
                    a_d = op_pokemon.Special_attack/self.Special_defense
                    burn= 0.5 if op_pokemon.burn else 1
                    screen = 0.5 if self.has_special_screen else 1
                    critical = 2 if random.randint(0,255)<self.Speed/2 else 1
                    rand = random.randint(85,100)/100
                    move_type = selected_move["Type"].iloc[0]
                    weather=self.weather_handle(move_type)
                    stab = 1.5 if op_pokemon.Type1 in move_type or op_pokemon.Type2 in move_type else 1
                    type_effect = self.TypeAffective(move_type)
                    #print(f'power: {power}\nburn: {burn}\nscreen: {screen}\ncritical: {critical}\nrand: {rand}\nstab: {stab}\neffectivness: {type_effect}')
                    damage=int(((42*power*a_d/50)*burn*screen*weather+2)*critical*rand*stab*type_effect)
                    self.HP-=damage

                    s = (f"{op_pokemon.Name} used {move}, a special move, and done {damage} damage to {self.Name}\n" +
                    ("It's super effective\n" if type_effect > 1 else "") +
                    ("It's not very effective\n" if type_effect < 1 else "") +
                    ("A critical hit\n\n" if critical == 2 else "\n\n"))
                    
                    if not multihit:
                        s+=self.handle_effect(move,op_pokemon,damage)
                        s+=self.handle_status_effects()
                    return (s)
                else:
                    power = float(selected_move["Power"])
                    a_d = op_pokemon.Attack/self.Defense
                    burn= 0.5 if op_pokemon.burn else 1
                    screen = 0.5 if self.has_physical_screen else 1
                    critical = 2 if random.randint(0,255)<self.Speed/2 else 1
                    rand = random.randint(85,100)/100
                    move_type = selected_move["Type"].iloc[0]
                    weather=self.weather_handle(move_type)
                    stab = 1.5 if op_pokemon.Type1 in move_type or op_pokemon.Type2 in move_type else 1
                    type_effect = self.TypeAffective(move_type)
                    #print(f'power: {power}\nburn: {burn}\nscreen: {screen}\ncritical: {critical}\nweather: {weather}\nrand: {rand}\nstab: {stab}\neffectivness: {type_effect}')
                    damage=int(((42*power*a_d/50)*burn*screen*weather+2)*critical*rand*stab*type_effect)
                    self.HP-=damage

                    s = (f"{op_pokemon.Name} used {move}, a physical move, and done {damage} damage to {self.Name}\n" +
                    ("It's super effective\n" if type_effect > 1 else "") +
                    ("It's not super effective\n" if type_effect < 1 else "") +
                    ("A critical hit\n\n" if critical == 2 else "\n\n"))

                    if not multihit: 
                        s+=self.handle_effect(move,op_pokemon,damage)
                        s+=self.handle_status_effects()

                    return (s)  
        else:
            return (f"No such move was found\npokemon: {op_pokemon.Name}. move: {move}")
            

    def __str__(self):
        if self.Type2 == "nan":
            return f"Name: {self.Name}\nType 1: {self.Type1}\nHP: {self.HP}\nAttack: {self.Attack}\nDefense: {self.Defense}\nSpecial Attack: {self.Special_attack}\nSpecial Defense: {self.Special_defense}\nSpeed: {self.Speed}\n{self.moveset}\n\n"
        return f"Name: {self.Name}\nType 1: {self.Type1}\nType 2: {self.Type2}\nHP: {self.HP}\nAttack: {self.Attack}\nDefense: {self.Defense}\nSpecial Attack: {self.Special_attack}\nSpecial Defense: {self.Special_defense}\nSpeed: {self.Speed}\n{self.moveset}\n\n"

#pokemon handle
selected_pokemon = pokemon(pokemon_dt.loc[pokemon_dt['Name'] == 'Charizard'])
opponment_pokemon = pokemon(pokemon_dt.loc[pokemon_dt['Name']=='Blastoise'])
#print(f"Bug type moves are {selected_pokemon.IsAffective('Bug')} times stronger to {selected_pokemon.Name}")
'''
selected_pokemon.set_Ev()
opponment_pokemon.set_Ev()
print(selected_pokemon,'\n',opponment_pokemon)
selected_pokemon.damage_calculation("Aqua Jet",opponment_pokemon)
opponment_pokemon.damage_calculation("Fire Fang",selected_pokemon)
print(selected_pokemon,'\n',opponment_pokemon)
'''

