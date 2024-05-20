import customtkinter as ctk
from tkinter.ttk import Progressbar,Style
from PIL import Image, ImageOps
import pandas as pd
import requests
from io import BytesIO
from Pokemon import pokemon
import random
import os

pokemove = pd.read_csv(r"DataBases\\bridge_pokemon_moves_MAY_LEARN.csv")
pokemon_dt = pd.read_csv(r"DataBases\\df_pokemon.csv")
pokemon_dt = pokemon_dt.drop(columns=["Species", 'Variant', 'Generation', 'Rarity', 'Evolves_from', 'Has_gender_diff', 'VGC2022_rules', 'Monthly Usage (k)', 'Usage Percent (%)', 'Monthly Rank'])
# pokemon_dt=pokemon_dt.drop_duplicates(subset="ID",keep="first")
pokemon_dt = pokemon_dt.set_index("ID")


class PokemonFrame(ctk.CTkFrame):
    def __init__(self, master, pokemon, pokemon_hp, width=250, height=100, **kwargs):
        super().__init__(master, width=width, height=height, **kwargs)

        self.style = Style()
        self.style.theme_use('clam') 
        self.style.configure("green.Horizontal.TProgressbar", background="green")
        self.style.configure("yellow.Horizontal.TProgressbar", background="yellow")
        self.style.configure("red.Horizontal.TProgressbar", background="red")

        self.pokemon_name_label = ctk.CTkLabel(self, text=pokemon.Name)
        self.pokemon_name_label.pack()

        self.hp_label = ctk.CTkLabel(self, text=f"HP: {pokemon_hp}")
        self.hp_label.pack()

        self.hp_bar = Progressbar(self, length=width, mode='determinate', value=pokemon_hp, maximum=pokemon_hp,style="green.Horizontal.TProgressbar")
        self.hp_bar.pack()

        cond_img = Image.open("Assets/BRN.png")
        self.cond_img = ctk.CTkImage(cond_img, size=(100, 50))
        self.cond_label = ctk.CTkLabel(self, image=self.cond_img, text="")

    def place_condition(self, img):
        self.cond_label.configure(image=ctk.CTkImage(img, size=(100, 50)))
        self.cond_label.pack()

    def clear_condition(self):
        self.cond_label.forget()

    def update_hp(self, new_hp, max_hp=None):
        if max_hp is not None:
            self.hp_bar.configure(maximum=max_hp)

        # Calculate the difference between the current HP and the new HP
        hp_difference = new_hp - self.hp_bar['value']  # Use dictionary-style access

        # Define the number of steps for the animation
        num_steps = 15  # You can adjust this value for smoother or faster animation

        # Calculate the increment for each step
        step_increment = hp_difference / num_steps

        # Update the HP bar gradually
        for step in range(num_steps):
            updated_hp = self.hp_bar['value'] + step_increment
            self.hp_bar.configure(value=updated_hp)
            self.update_hp_color(updated_hp)  # Update the color based on HP value
            self.update_idletasks()  # Force an update of the GUI

            # Add a small delay between steps (you can adjust this value)
            self.after(10)  # 50 milliseconds

        if new_hp >= 0:
            self.hp_bar.configure(value=new_hp)
            self.hp_label.configure(text=f"HP: {new_hp}")
        else:
            self.hp_bar.configure(value=0)
            self.hp_label.configure(text="HP: 0")

    def update_hp_color(self, hp_value):
        # Calculate the HP percentage
        max_hp = self.hp_bar['maximum']
        hp_percentage = (hp_value / max_hp) * 100

        # Set the color based on HP percentage
        if hp_percentage >= 60:
            self.hp_bar.configure(style="green.Horizontal.TProgressbar")
        elif 20 <= hp_percentage < 60:
            self.hp_bar.configure(style="yellow.Horizontal.TProgressbar")
        else:
            self.hp_bar.configure(style="red.Horizontal.TProgressbar")




class SwitchOrMove(ctk.CTkFrame):
    TYPE_COLORS = {
        'Normal': '#A8A77A',
        'Fire': '#EE8130',
        'Water': '#6390F0',
        'Electric': '#F7D02C',
        'Grass': '#7AC74C',
        'Ice': '#96D9D6',
        'Fighting': '#C22E28',
        'Poison': '#A33EA1',
        'Ground': '#E2BF65',
        'Flying': '#A98FF3',
        'Psychic': '#F95587',
        'Bug': '#A6B91A',
        'Rock': '#B6A136',
        'Ghost': '#735797',
        'Dragon': '#6F35FC',
        'Dark': '#705746',
        'Steel': '#B7B7CE',
        'Fairy': '#D685AD',
    }

    def cache_team_images(self, team):
        image_paths = []  # Create an empty list to store image paths
        for pokemon in team:
            if pokemon.HP >= 0:
                url = pokemon.img
                res = requests.get(url)
                img = Image.open(BytesIO(res.content))
                image_path = f"Cached_Images/{pokemon.Name}.png"
                img.save(image_path)
                image_paths.append(image_path)  # Add the image path to the list
        return image_paths  # Return the list of image paths


    def __init__(self, master, team_pokemon, selected_pokemon, opponent_pokemon, **kwargs):
        super().__init__(master, **kwargs)
        self.team = team_pokemon
        self.selected_pokemon = selected_pokemon
        self.opponent_pokemon = opponent_pokemon
        self.master = master
        self.cache_team_images(self.team)

        self.configure(width=375, height=300)
        self.attack_button = ctk.CTkButton(self, text="Attack", command=lambda: self.show_moveset(self.selected_pokemon.move_list, self.selected_pokemon.moveset))
        self.attack_button.place(relx=0, rely=0)

        self.switch_button = ctk.CTkButton(self, text="Switch", command=self.show_team)
        self.switch_button.place(relx=0, rely=0.15)

        self.button1 = ctk.CTkButton(self, text="none", command=lambda: self.perform_move(self.master, self.button1.cget("text"), self.selected_pokemon, self.opponent_pokemon))
        self.button2 = ctk.CTkButton(self, text="none", command=lambda: self.perform_move(self.master, self.button2.cget("text"), self.selected_pokemon, self.opponent_pokemon))
        self.button3 = ctk.CTkButton(self, text="none", command=lambda: self.perform_move(self.master, self.button3.cget("text"), self.selected_pokemon, self.opponent_pokemon))
        self.button4 = ctk.CTkButton(self, text="none", command=lambda: self.perform_move(self.master, self.button4.cget("text"), self.selected_pokemon, self.opponent_pokemon))

        self.pokebutton1 = ctk.CTkButton(self, width=100, height=100)
        self.pokebutton2 = ctk.CTkButton(self, width=100, height=100)
        self.pokebutton3 = ctk.CTkButton(self, width=100, height=100)
        self.pokebutton4 = ctk.CTkButton(self, width=100, height=100)
        self.pokebutton5 = ctk.CTkButton(self, width=100, height=100)
        self.pokebutton6 = ctk.CTkButton(self, width=100, height=100)

        self.infobox = ctk.CTkTextbox(self, width=325, height=100)

    def return_def(self):
        self.switch_button.place(relx=0, rely=0.15)
        self.attack_button.place(relx=0, rely=0)

        self.return_button.place_forget()
        self.infobox.place_forget()
        for i in range(1, 5):  # Loop through the attack buttons
            b = getattr(self, f'button{i}')
            b.place_forget()  # Forget the button
        for i in range(1, 7):
            b = getattr(self, f'pokebutton{i}')
            b.place_forget()

    def perform_move(self, master, move, sel, opp):
        result = opp.damage_calculation(move, sel)
        result += f"\n{sel.damage_calculation(opp.move_list[random.randint(0, 3)], opp)}"

        master.result_box.configure(state="normal")
        master.result_box.delete('0.0', "end")
        master.result_box.insert("0.0", result)
        master.result_box.configure(state="disabled")

        master.m_pokemon_frame.update_hp(sel.HP)
        master.e_pokemon_frame.update_hp(opp.HP)

        self.switch_button.place(relx=0, rely=0.15)
        self.attack_button.place(relx=0, rely=0)

        if sel.has_status_effect():
            img_dir = "BRN" if sel.burn else "PAR" if sel.paralyze else "PSN" if sel.poison else "FRZ" if sel.freeze else ""
            if img_dir != "":
                img = Image.open(f"Assets/{img_dir}.png")
                master.m_pokemon_frame.place_condition(img)
        else:
            master.m_pokemon_frame.clear_condition()

        if opp.has_status_effect():
            img_dir = "BRN" if opp.burn else "PAR" if opp.paralyze else "PSN" if opp.poison else "FRZ" if opp.freeze else ""
            if img_dir != "":
                img = Image.open(f"Assets/{img_dir}.png")
                master.e_pokemon_frame.place_condition(img)
        else:
            master.e_pokemon_frame.clear_condition()

        if sel.HP <= 0:
            self.return_def()
            self.show_team(show_return=False)
        else:
            self.return_def()

    def show_moveset(self, moves, moveset):
        self.switch_button.place_forget()
        self.attack_button.place_forget()
        i = 0
        for m in moves:
            if i <= 4:  # Only update the buttons if there are 4 or fewer moves
                b = getattr(self, f'button{i+1}')
                b.configure(text=m, fg_color=self.TYPE_COLORS.get(moveset["Type"].iloc[i]))
                b.bind('<Enter>', lambda event, move=m: self.show_move_info(move, moveset))
                b.bind('<Leave>', lambda event: self.clear_move_info())
                b.place(relx=0, rely=0.15 * i)
                i += 1

        self.return_button = ctk.CTkButton(self, text="return", command=self.return_def)
        self.return_button.place(relx=0.5, rely=0)

        self.infobox.place(rely=0.6, relx=0.05)
        self.infobox.configure(state="disabled")

    def show_move_info(self, move, moveset):
        move_info = moveset.loc[moveset['Name'] == move]
        info_text = f"Name: {move_info['Name'].iloc[0]}\nType: {move_info['Type'].iloc[0]}\nPower: {move_info['Power'].iloc[0]}\nEffect: {move_info['Effect'].iloc[0]}"
        self.infobox.configure(state="normal")
        self.infobox.delete('1.0', 'end')
        self.infobox.insert('1.0', info_text)
        self.infobox.configure(state="disabled")

    def clear_move_info(self):
        self.infobox.configure(state="normal")
        self.infobox.delete('1.0', 'end')
        self.infobox.configure(state="disabled")

    def show_team(self, show_return=True):
        team = self.team
        self.switch_button.place_forget()
        self.attack_button.place_forget()
        i = 0
        counter = 0
        for t in team:
            if t.HP >= 0 and t!=self.selected_pokemon:
                img = Image.open(f"Cached_Images/{t.Name}.png")
                img = ctk.CTkImage(img, size=(100, 100))

                setattr(self, f'pokebutton{i + 1}', ctk.CTkButton(self, width=100, height=100, text="", image=img, command=lambda p=t: self.switch_pokemon(p)))
                b = getattr(self, f'pokebutton{i + 1}')
                b.configure(image=img, text="")
                if counter <= 2:
                    b.place(relx=counter * 0.33, rely=0)
                else:
                    b.place(relx=(counter - 3) * 0.33, rely=0.5)
                i += 1
                counter += 1
        if show_return:
            self.return_button = ctk.CTkButton(self, text="return", command=self.return_def)
            self.return_button.place(relx=0.25, rely=0.9)

    def switch_pokemon(self, new_pokemon):
        self.selected_pokemon = new_pokemon
        self.master.m_pokemon_frame.pokemon_name_label.configure(text=new_pokemon.Name)
        self.master.m_pokemon_frame.update_hp(new_pokemon.HP,max_hp=new_pokemon.max_HP)

        m_url = new_pokemon.img
        m_response = requests.get(m_url)
        m_img = Image.open(BytesIO(m_response.content))
        m_img = ImageOps.mirror(m_img)
        m_pokemon_img = ctk.CTkImage(m_img, size=(250, 250))
        self.master.m_pokemon_label.configure(image=m_pokemon_img)
        self.return_def()

        self.master.m_pokemon_frame.clear_condition()

        if new_pokemon.has_status_effect():
            img_dir = "BRN" if new_pokemon.burn else "PAR" if new_pokemon.paralyze else "PSN" if new_pokemon.poison else "FRZ" if new_pokemon.freeze else ""
            if img_dir != "":
                img = Image.open(f"Assets/{img_dir}.png")
                self.master.m_pokemon_frame.place_condition(img)



class Game_Screen(ctk.CTkFrame):
    def __init__(self, master,team, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(width=1920, height=1080)
        selected_pokemon = team[0]
        opponent_pokemon = pokemon(pokemon_dt.loc[pokemon_dt['Name'] == 'Toucannon'])

        m_url = selected_pokemon.img
        m_response = requests.get(m_url)
        m_img = Image.open(BytesIO(m_response.content))
        m_img = ImageOps.mirror(m_img)
        m_pokemon_img = ctk.CTkImage(m_img, size=(250, 250))
        self.m_pokemon_label = ctk.CTkLabel(master=self, image=m_pokemon_img, text="")
        self.m_pokemon_label.place(relx=0.3, rely=0.5)

        e_url = opponent_pokemon.img
        e_response = requests.get(e_url)
        e_img = Image.open(BytesIO(e_response.content))
        e_pokemon_img = ctk.CTkImage(e_img, size=(250, 250))
        e_pokemon_label = ctk.CTkLabel(master=self, image=e_pokemon_img, text="")
        e_pokemon_label.place(relx=0.55, rely=0)

        vs_img = Image.open(r"Assets/vs_img.png")
        vs_img = ctk.CTkImage(vs_img, size=(1200, 200))
        vs_label = ctk.CTkLabel(self, image=vs_img, text="")
        vs_label.place(rely=0.3, relx=0.18)

        self.result_box = ctk.CTkTextbox(self, width=1500, height=200)
        self.result_box.insert('0.0', "THIS IS A RESULTS TEXT BOX")
        self.result_box.configure(state="disabled")
        self.result_box.place(relx=0.1, rely=0.8)

        self.m_pokemon_frame = PokemonFrame(self, selected_pokemon, selected_pokemon.HP, width=250, height=150)
        self.m_pokemon_frame.place(relx=0.45, rely=0.6)

        self.switchormove = SwitchOrMove(self,team, selected_pokemon, opponent_pokemon)
        self.switchormove.place(relx=0.6, rely=0.5)

        self.e_pokemon_frame = PokemonFrame(self, opponent_pokemon, opponent_pokemon.HP,width=250, height=150)
        self.e_pokemon_frame.place(relx=0.4, rely=0.1)


# setting root
ctk.set_appearance_mode("dark")
root = ctk.CTk()
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

res = f"{screen_width}x{screen_height}"
root.title("PokeBattle")
root.geometry("1920x1080")
# root.attributes("-fullscreen", "True")
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)

my_team = [pokemon(pokemon_dt.loc[pokemon_dt['Name'] == 'Toxapex']),
                   pokemon(pokemon_dt.loc[pokemon_dt['Name'] == 'Charizard']),
                   pokemon(pokemon_dt.loc[pokemon_dt['Name'] == 'Pikachu']),
                   pokemon(pokemon_dt.loc[pokemon_dt['Name'] == 'Alakazam']),
                   pokemon(pokemon_dt.loc[pokemon_dt['Name'] == 'Hariyama']),
                   pokemon(pokemon_dt.loc[pokemon_dt['Name'] == 'Dragonite'])
                   ]

game = Game_Screen(root,team=my_team)
game.pack()

root.mainloop()
image_paths = SwitchOrMove.cache_team_images(None,my_team)
for image_path in image_paths:
        os.remove(image_path)