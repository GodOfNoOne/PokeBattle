from CTkScrollableDropdown import *
import customtkinter as ctk
import tkinter as tk
from PIL import Image, ImageTk
import pandas as pd
import requests
from io import BytesIO
import moves_class
from Pokemon import pokemon
import socket
import pickle
import threading
import client_battle
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes


ctk.set_appearance_mode("dark")

#pokemon database
pokemon_dt = pd.read_csv(r"DataBases\\df_pokemon.csv")
pokemon_dt=pokemon_dt.drop(columns=["Species",'Variant','Generation','Evolves_from','Has_gender_diff','VGC2022_rules','Monthly Usage (k)','Usage Percent (%)','Monthly Rank'])
pokemon_dt=pokemon_dt.set_index("ID")
pokemon_dt = pokemon_dt[~pokemon_dt["Name"].str.contains("Mega|Gigantamax")]
pokemon_dt = pokemon_dt[~pokemon_dt["Rarity"].str.contains("legendary|mythical|baby", case=False)]
values=pokemon_dt["Name"].to_list()

pokemove = pd.read_csv(r"DataBases\\bridge_pokemon_moves_MAY_LEARN.csv")
moves_ds=moves_class.get_moves()

def create_room():
    welcome_frame.forget()
    create_frame.pack()

def join_room():
    welcome_frame.forget()
    join_frame.pack()   

def edit_team():
    welcome_frame.forget()
    edit_frame.pack()

def exit_game():  
    s=""
    if welcome_frame.welcome_user.cget('text')!="":
        s=welcome_frame.welcome_user.cget('text').split()[1]
    client_socket.send(f"exit:{welcome_frame.welcome_user.cget('text').split()[1]}".encode())
    root.destroy()


def sign_in():
    welcome_frame.forget()
    signin_frame.pack()

def log_in():
    welcome_frame.forget()
    login_frame.pack()



#submitting the sign in or log in encryted data to the server
def submit(mode,username,password):
    print(f"Username: {username}, Password: {password}")
    if username=="" or password=="": 
        fill_warning=ctk.CTkLabel(signin_frame,text="Please fill in all the fields",font=("Cascadia Code",28))
        fill_warning.place(rely=0.8,relx=0.35)
  
    elif mode=="signin":
        client_socket.send("sign up".encode())
        send_encrypted(client_socket, username)  #Send the encrypted username
        send_encrypted(client_socket, password)  #Send the encrypted password
        data=client_socket.recv(1024).decode()
        if data=="success":
            show_game_buttons()
            back_to_menu(signin_frame)
            welcome_frame.sign_in_button.place_forget()
            welcome_frame.log_in_button.place_forget()
            welcome_frame.welcome_user.configure(text=f"Welcome {username}")
            welcome_frame.welcome_user.place(relx=0.95,rely=0,anchor='ne')
        elif data=="failure":
            username_taken=ctk.CTkLabel(signin_frame,text="Username already taken",font=("Cascadia Code",28))
            username_taken.place(rely=0.8,relx=0.35)
    
    elif mode=="login":
        client_socket.send("log in".encode())
        send_encrypted(client_socket, username) #Send the encrypted username
        send_encrypted(client_socket, password) #Send the encrypted password
        data=client_socket.recv(1024).decode()
        if data=="success":
            client_socket.send("team?".encode())
            data=client_socket.recv(1024).decode()
            if data=="yes":
                team_data=recvall(client_socket)
                team = pickle.loads(team_data)
                class_list_to_gui(team)


            show_game_buttons()
            back_to_menu(login_frame)
            welcome_frame.sign_in_button.place_forget()
            welcome_frame.log_in_button.place_forget()
            welcome_frame.welcome_user.configure(text=f"Welcome {username}")
            welcome_frame.welcome_user.place(relx=0.95,rely=0,anchor='ne')
        elif data=="failure":
            username_taken=ctk.CTkLabel(login_frame,text="Username and\or password are wrong\nor this user is online",font=("Cascadia Code",28))
            username_taken.place(rely=0.8,relx=0.35)

def back_to_menu(frame):
    frame.forget()
    welcome_frame.pack()    


def show_game_buttons():
    welcome_frame.create_room_button.place(rely=0.54,relx=0.35)
    welcome_frame.join_room_button.place(rely=0.64,relx=0.35)
    welcome_frame.edit_team_button.place(rely=0.74,relx=0.35)
    welcome_frame.exit_game_button.place(rely=0.84,relx=0.35)

def class_list_to_gui(team):
    pokemon_tabs=edit_frame.pokemon_tabs
    for t in team:
        if t!=None:
            selected=pokemon_dt.where(pokemon_dt["Name"]==t.Name).dropna(how="all")
            url=t.img
            response = requests.get(url)
            img = Image.open(BytesIO(response.content))
            pokemon_img=ctk.CTkImage(img,size=(250,250))
            
            name=t.Name
            type1=t.Type1
            type2=t.Type2
            base_stats=t.get_base_stats()
            evs=t.get_ev()
            moves=t.move_list
            print(name,base_stats,evs,moves)
            for i in range(6):
                if pokemon_tabs.pokemon_names[i]==None:
                    pokemon_tabs.pokemon_names[i]=name
                    pokemon_tabs.pokemon_labels[i].configure(image=pokemon_img)
                    pokemon_type = [type1, type2]
                    for j in range(2):
                        if pokemon_type[j] != "nan":
                            type_img = ctk.CTkImage(Image.open(f"Assets\\Types\\{pokemon_type[j]}.png"), size=(100, 50))
                            pokemon_tabs.type_labels[i][j].configure(image=type_img)
                        else:
                            pokemon_tabs.type_labels[i][j].configure(image=None)
                    for j in range(7):
                        if j<6:
                            pokemon_tabs.base_stat_labels[i][j].configure(text=str(base_stats[j]))
                            if j<6:
                                pokemon_tabs.ev_labels[i][j].insert('end',str(evs[j]))
                        else:
                            pokemon_tabs.base_stat_labels[i][j].configure(text=str(base_stats[j]))
                    for j in range(4):
                        if j<len(moves):
                             pokemon_tabs.moves[i][j]= moves[j]
                             pokemon_tabs.combo_moves[i][j].configure(variable=ctk.StringVar(pokemon_tabs,value=moves[j]),values=pokemon_tabs.movesets[i]["Name"].tolist())
                    break

            



class Pokemon_Tabs(ctk.CTkTabview):
    def __init__(self, master,width=1000,height=800, **kwargs):
        super().__init__(master,width=width,height=800, **kwargs)

        def insert_method(e,tab,i):
            selected=pokemon_dt.where(pokemon_dt["Name"]==e).dropna(how="all")
            url=selected["image_url"].iloc[0]
            response = requests.get(url)
            img = Image.open(BytesIO(response.content))
            pokemon_img=ctk.CTkImage(img,size=(250,250))
            self.pokemon_labels[i].configure(image=pokemon_img)
            self.pokemon_names[i] = e

            chosed_moves= pokemove.where(pokemove['Pokemon']==e).dropna(how='all')
            moveset = chosed_moves.merge(moves_ds,left_on="Move",right_on="Name")
            self.movesets[i]=moveset.drop(columns=['Pokemon','Move','Introducted_in'])

            for j in range(4):
                self.combo_moves[i][j].configure(variable=ctk.StringVar(self,value=""),values=self.movesets[i]["Name"].tolist())


            pokemon_type = [str(selected["Type1"].iloc[0]), str(selected["Type2"].iloc[0])]
            for j in range(2):
                if pokemon_type[j] != "nan":
                    type_img = ctk.CTkImage(Image.open(f"Assets\\Types\\{pokemon_type[j]}.png"), size=(100, 50))
                    self.type_labels[i][j].configure(image=type_img)
                else:
                    self.type_labels[i][j].configure(image=None)

            # Update base stats
            stats = ["HP", "Attack", "Defense", "Sp. Atk", "Sp. Def", "Speed", "Total"]
            for j, stat in enumerate(stats):
                base_stat=selected[stat].iloc[0]
                self.base_stat_labels[i][j].configure(text=str(int(base_stat)))  # Update base stat
                # Reset EV
                self.ev_labels[i][j].delete('0', 'end')
                self.ev_labels[i][j].configure(placeholder_text="85")


        def validate_ev(P):
            if str.isdigit(P) and int(P) <= 252:
                return True
            elif P == "":
                return True
            else:
                return False
        
        def update_moves(e, i, j):
            self.moves[i][j] = e
            chosed_moves= pokemove.where(pokemove['Pokemon']==self.pokemon_names[i]).dropna(how='all')
            moveset = chosed_moves.merge(moves_ds,left_on="Move",right_on="Name")
            self.movesets[i]=moveset.drop(columns=['Pokemon','Move','Introducted_in'])
            for k in range(4):
                self.movesets[i] = self.movesets[i][self.movesets[i]["Name"] != self.moves[i][k]] 
            for k in range(4):
                self.combo_moves[i][k].configure(values=self.movesets[i]["Name"].tolist())

        
        def check_submit():
            for i in range(6):
                sum = 0
                for j in range(6):
                    if self.ev_labels[i][j].get() == "":
                        sum+=85
                    else:
                        sum+=int(self.ev_labels[i][j].get())
                if sum > 510:
                    return f"Pokemon {i+1}: EVs exceed 510"
                if self.moves[i]==[None]*4 and self.pokemon_names[i]!=None:
                    return f"Pokemon {i+1}: No moves selected"
            return "all good"
                

        
        def subnit_team():
            name=""
            ev=[0,0,0,0,0,0]
            moves=[None,None,None,None]

            if check_submit()=="all good":
                for i in range(6):
                    if self.pokemon_names[i] != None:
                        name=self.pokemon_names[i]
                        for j in range(6):
                            if self.ev_labels[i][j].get() == "":
                                ev[j] = 85
                            else:
                                ev[j] = int(self.ev_labels[i][j].get())
                        for j in range(4):
                            moves[j]=self.moves[i][j]
                        print(name,ev,moves)
                        self.team[i] = pokemon(pokemon_dt.where(pokemon_dt["Name"]==name).dropna(how="all"))
                        self.team[i].set_Ev(ev)
                        self.team[i].set_moves(moves)
                client_socket.send(f"edit team:{welcome_frame.welcome_user.cget('text').split()[1]}".encode())
                team_data = pickle.dumps(self.team)
                data_len = len(team_data).to_bytes(4, byteorder='big')
                client_socket.sendall(data_len + team_data)
                
            else:
                print(check_submit())
        

        for i in range(6):
            self.add(f"Pokemon {i+1}")
        self.team = [None] * 6
        self.pokemon_labels = [None] * 6
        self.pokemon_names = [None] * 6
        self.type_labels = [[None, None] for _ in range(6)]
        self.ev_labels = [[None]*7 for _ in range(6)]  # 2D list of labels for EV values
        self.base_stat_labels = [[None]*7 for _ in range(6)]  # 2D list of labels for base stats
        self.combo_moves = [[None]*4 for _ in range(6)]  # 2D list of comboboxes for moves
        self.moves = [[None]*4 for _ in range(6)] # 2D list of move names
        self.movesets = [None]*6
        self.submit_button = ctk.CTkButton(master=self, text="Submit Team", command=subnit_team)
        self.submit_button.place(relx=0.5, rely=0.9, anchor='center')
        selected=pokemon_dt.where(pokemon_dt["Name"]=="Bulbasaur").dropna(how="all")
        url='https://img.pokemondb.net/sprites/sword-shield/icon/bulbasaur.png'
        response = requests.get(url)
        img = Image.open(BytesIO(response.content))
        img=ctk.CTkImage(img,size=(250,250))
        for i in range(6):
            tab=self.tab(f"Pokemon {i+1}")
            
            # Create a new frame for the pokemon entry and label
            pokemon_frame = ctk.CTkFrame(master=tab)
            pokemon_frame.place(relx=0, rely=0)
            pokemon_type = [str(selected["Type1"].iloc[0]), str(selected["Type2"].iloc[0])]  
            for j in range(2):
                if pokemon_type[j] != "nan":
                    type_img=ctk.CTkImage(Image.open(f"Assets\\Types\\{pokemon_type[j]}.png"),size=(100,50))
                    type_label=ctk.CTkLabel(master=pokemon_frame,image=type_img,text="")
                    type_label.grid(row=0,column=2+j,padx=5,pady=5)
                    self.type_labels[i][j]=type_label

            chosed_moves= pokemove.where(pokemove['Pokemon']=="Bulbasaur").dropna(how='all')
            moveset = chosed_moves.merge(moves_ds,left_on="Move",right_on="Name")
            self.movesets[i]=moveset.drop(columns=['Pokemon','Move','Introducted_in'])

            pokemon_entry = ctk.CTkComboBox(master=pokemon_frame,values=values,variable=ctk.StringVar(tab,"Choose a pokemon"),state="readonly",command=lambda e, i=i: insert_method(e,tab,i))
            pokemon_entry.grid(row=0, column=0, padx=5, pady=5)
            self.pokemon_labels[i] = ctk.CTkLabel(master=pokemon_frame, text="",image=img)
            self.pokemon_labels[i].grid(row=0, column=1, padx=5, pady=5)

            # Create a new frame for the table
            table_frame = ctk.CTkFrame(master=tab)
            table_frame.place(relx=0.25, rely=0.4)

            # Create table
            stats = ["HP", "Attack", "Defense", "Sp. Atk", "Sp. Def", "Speed", "Total"]
            for j, stat in enumerate(stats):
                ctk.CTkLabel(master=table_frame, text=stat).grid(row=0, column=j+1, padx=10, pady=10)  # Column headers
                ctk.CTkLabel(master=table_frame, text="Base stat").grid(row=1, column=0, padx=10, pady=10)  # Row header for base stat
                base_stat=selected[stat].iloc[0]
                base_stat_label = ctk.CTkLabel(master=table_frame,text=str(int(base_stat)))
                base_stat_label.grid(row=1, column=j+1, padx=10, pady=10)
                self.base_stat_labels[i][j] = base_stat_label  # Store reference to base stat label
                ctk.CTkLabel(master=table_frame, text="EV").grid(row=2, column=0, padx=10, pady=10)  # Row header for EV

                vcmd = (self.register(validate_ev), '%P')
                ev_entry = ctk.CTkEntry(master=table_frame, width=50,placeholder_text="85", validate="key", validatecommand=vcmd)
                total_ev = ctk.CTkLabel(master=table_frame, text="")
                if stat == "Total":
                    total_ev.grid(row=2, column=j+1, padx=10, pady=10)
                else:
                    ev_entry.grid(row=2, column=j+1, padx=10, pady=10)
                self.ev_labels[i][j] = ev_entry

            # Create a new frame for the moves
            moves_frame = ctk.CTkFrame(master=tab, width=250, height=250)
            moves_frame.place(relx=0.7, rely=0)
            for j in range(4):
                move_entry = ctk.CTkComboBox(master=moves_frame, values=self.movesets[i]["Name"].tolist(), state="readonly",command=lambda e, i=i, j=j: update_moves(e, i, j))
                move_entry.place(rely=float(f"0.{j+1}"), relx=0.25)
                self.combo_moves[i][j] = move_entry





class Welcome_Screen(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(width=1920,height=1080)
        # Welcome image
        welcome_Image=ctk.CTkImage(Image.open("Assets\Welcome_img.png"),size=(1024,434))
        welcome_label = ctk.CTkLabel(master=self, image=welcome_Image,text="")
        welcome_label.place(rely=0.1,relx=0.2)

        # Sign in and Log in buttons
        self.sign_in_button = ctk.CTkButton(self, text="Sign In", command=sign_in,font=("Cascadia Code",36))
        self.sign_in_button.place(relx=0.5, rely=0.5, anchor='center')

        self.log_in_button = ctk.CTkButton(self, text="Log In", command=log_in,font=("Cascadia Code",36))
        self.log_in_button.place(relx=0.5, rely=0.6, anchor='center')

        self.welcome_user=ctk.CTkLabel(self,text="",font=("Cascadia Code",28))

        # Buttons under the image
        self.create_room_button = ctk.CTkButton(self, text="Create Room", command=create_room,width=500,height=50,font=("Cascadia Code",28))
        
        self.join_room_button = ctk.CTkButton(self, text="Join Room", command=join_room,width=500,height=50,font=("Cascadia Code",28))
        
        self.edit_team_button = ctk.CTkButton(self, text="Edit Team", command=edit_team,width=500,height=50,font=("Cascadia Code",28))
        
        self.exit_game_button = ctk.CTkButton(self, text="Exit Game", command=exit_game,width=500,height=50,font=("Cascadia Code",28))

class Log_In(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(width=1920,height=1080)
        login_Img=ctk.CTkImage(Image.open("Assets\Log_in.png"),size=(712,325))
        login_lable= ctk.CTkLabel(self,text="",image=login_Img)
        login_lable.place(rely=0,relx=0.3)

        username_img= ctk.CTkImage(Image.open(r"Assets\\username.png"),size=(341,115))
        username_lable=ctk.CTkLabel(self,text="",image=username_img)
        username_lable.place(rely=0.3,relx=0.4)
        username_entry=ctk.CTkEntry(self, placeholder_text="Your Username",width=200,height=37)
        username_entry.place(rely=0.4,relx=0.44)

        password_img= ctk.CTkImage(Image.open(r"Assets\Password.png"),size=(341,115))
        password_lable=ctk.CTkLabel(self,text="",image=password_img)
        password_lable.place(rely=0.5,relx=0.4)
        password_entry=ctk.CTkEntry(self, placeholder_text="Your password",width=200,height=37)
        password_entry.configure(show='*')
        password_entry.place(rely=0.6,relx=0.44)
        
        #If I want to I can add the eye thing to the password

        back_button=ctk.CTkButton(self,text="Back To Menu",command=lambda: back_to_menu(self),font=("Cascadia Code",28))
        back_button.place(relx=0,rely=0)

        submit_btn=ctk.CTkButton(self,text="Submit", command=lambda: submit('login',username_entry.get(),password_entry.get()),width=500,height=50,font=("Cascadia Code",28))
        submit_btn.place(rely=0.7,relx=0.35)


class Sign_In(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(width=1920,height=1080)
        signin_Img=ctk.CTkImage(Image.open("Assets\Sign_in.png"),size=(712,325))
        signin_lable= ctk.CTkLabel(self,text="",image=signin_Img)
        signin_lable.place(rely=0,relx=0.3)

        username_img= ctk.CTkImage(Image.open(r"Assets\\username.png"),size=(341,115))
        username_lable=ctk.CTkLabel(self,text="",image=username_img)
        username_lable.place(rely=0.3,relx=0.4)
        username_entry=ctk.CTkEntry(self, placeholder_text="Your Username",width=200,height=37)
        username_entry.place(rely=0.4,relx=0.44)

        password_img= ctk.CTkImage(Image.open(r"Assets\Password.png"),size=(341,115))
        password_lable=ctk.CTkLabel(self,text="",image=password_img)
        password_lable.place(rely=0.5,relx=0.4)
        password_entry=ctk.CTkEntry(self, placeholder_text="Your password",width=200,height=37)
        password_entry.configure(show='*')
        password_entry.place(rely=0.6,relx=0.44)
        
        #If I want to I can add the eye thing to the password

        back_button=ctk.CTkButton(self,text="Back To Menu",command=lambda: back_to_menu(self),font=("Cascadia Code",28))
        back_button.place(relx=0,rely=0)

        submit_btn=ctk.CTkButton(self,text="Submit", command=lambda: submit('signin',username_entry.get(),password_entry.get()),width=500,height=50,font=("Cascadia Code",28))
        submit_btn.place(rely=0.7,relx=0.35)

class Join_Room(ctk.CTkFrame):

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(width=1920,height=1080)
        room_Img=ctk.CTkImage(Image.open("Assets\Join_room.png"),size=(712,325))
        room_lable= ctk.CTkLabel(self,text="",image=room_Img)
        room_lable.place(rely=0,relx=0.3)

        room_id_img= ctk.CTkImage(Image.open(r"Assets\\room_code.png"),size=(341,115))
        room_id_lable=ctk.CTkLabel(self,text="",image=room_id_img)
        room_id_lable.place(rely=0.3,relx=0.4)
        self.room_id_entry=ctk.CTkEntry(self, placeholder_text="Room ID",width=200,height=37)
        self.room_id_entry.place(rely=0.4,relx=0.44)
        
        #If I want to I can add the eye thing to the password

        back_button=ctk.CTkButton(self,text="Back To Menu",command=lambda: back_to_menu(self),font=("Cascadia Code",28))
        back_button.place(relx=0,rely=0)

        submit_btn=ctk.CTkButton(self,text="Submit", command=self.subnit_join,width=500,height=50,font=("Cascadia Code",28))
        submit_btn.place(rely=0.7,relx=0.35)

    def subnit_join(self):
        def subnit_join_thread(self):
            client_socket.send(f"join room:{welcome_frame.welcome_user.cget('text').split()[1]}".encode())
            data=client_socket.recv(1024).decode()

            if data=="ok":
                client_socket.send("get rooms".encode())
                data=client_socket.recv(1024) # Wait for server to send all the room codes
                print(data.decode())
                if self.room_id_entry.get() in data.decode().split(","): # Check if the room exists
                    client_socket.send(f"connect me to {self.room_id_entry.get()}".encode())
                    data=client_socket.recv(1024)
                    if "connected" in data.decode():
                        team_data=recvall(client_socket)
                        team = pickle.loads(team_data)
                        print(f"Connected to room {self.room_id_entry.get()}")
                        join_frame.forget()
                        client_battle.start_game(host=socket.gethostname(),port=int(self.room_id_entry.get()),root=root,team=team)
                elif data.decode()=="no rooms":
                    client_socket.send("room does not exist".encode())
                    no_room=ctk.CTkLabel(self,text="No rooms available",font=("Cascadia Code",28))
                    no_room.place(rely=0.8,relx=0.35)
                else:
                    client_socket.send("room does not exist".encode())
                    no_room=ctk.CTkLabel(self,text="Room does not exist",font=("Cascadia Code",28))
                    no_room.place(rely=0.8,relx=0.35)
            else:
                no_team=ctk.CTkLabel(self,text="You need to have a team to join a room",font=("Cascadia Code",28))
                no_team.place(rely=0.8,relx=0.35)
        threading.Thread(target=subnit_join_thread,args=(self,)).start()

class Create_Room(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(width=1920,height=1080)
        room_Img=ctk.CTkImage(Image.open("Assets\Create_Room.png"),size=(712,325))
        room_lable= ctk.CTkLabel(self,text="",image=room_Img)
        room_lable.place(rely=0,relx=0.3)

        back_button=ctk.CTkButton(self,text="Back To Menu",command=lambda: back_to_menu(self),font=("Cascadia Code",28))
        back_button.place(relx=0,rely=0)

        self.generate_code_btn=ctk.CTkButton(self,text="Generate Room Code", command=self.generate_code,width=500,height=50,font=("Cascadia Code",28))
        self.generate_code_btn.place(rely=0.3,relx=0.35)

        self.start_game_btn=ctk.CTkButton(self,text="Start Game",width=500,height=50,font=("Cascadia Code",28))

        self.generate_code_text=ctk.CTkTextbox(self,width=500,height=50)
        self.generate_code_text.place(rely=0.4,relx=0.35)
        self.generate_code_text.configure(state="normal")
        self.generate_code_text.insert("end","Click on Generate Room Code to get your room code")
        self.generate_code_text.configure(state="disabled")

    def generate_code(self):
        def generate_code_thread(self):
            client_socket.send(f"create room:{welcome_frame.welcome_user.cget('text').split()[1]}".encode())
            data=client_socket.recv(1024).decode()
            if data=="ok":
                client_socket.send("give code".encode())
                data=client_socket.recv(1024).decode()
                print(f"Room code: {data}")
                self.generate_code_btn.place_forget()
                self.start_game_btn.place(rely=0.3,relx=0.35)
                self.generate_code_text.configure(state="normal")
                self.generate_code_text.delete("0.0","end")
                self.generate_code_text.insert("end",f"Your room code is: {data}")
                self.generate_code_text.configure(state="disabled")
            else:
                print(data)
                no_team=ctk.CTkLabel(self,text="You need to have a team to create a room",font=("Cascadia Code",28))
                no_team.place(rely=0.8,relx=0.35)
        threading.Thread(target=generate_code_thread,args=(self,)).start()



class Edit_Screen(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(width=1920,height=1080)
        self.edit_team_image=ctk.CTkImage(Image.open("Assets\Edit_Team_img.png"),size=(512,268))
        self.edit_team_label=ctk.CTkLabel(self,image=self.edit_team_image,text="")
        self.edit_team_label.place(rely=0,relx=0.35)
        self.pokemon_tabs=Pokemon_Tabs(master=self)
        self.pokemon_tabs.place(relx=0.25,rely=0.25)
        back_button=ctk.CTkButton(self,text="Back To Menu",command=lambda: back_to_menu(self),font=("Cascadia Code",28))
        back_button.place(relx=0,rely=0)



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

def send_encrypted(sock, data):
    encrypted_data = public_key.encrypt(
        data.encode(),
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    encrypted_data_len = len(encrypted_data).to_bytes(4, byteorder='big')
    sock.sendall(encrypted_data_len + encrypted_data)

#setting root
root = ctk.CTk()
root.title("PokeBattle")
root.geometry("1920x1080")
root.attributes("-fullscreen", "True")
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)

#creating the client
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((socket.gethostname(), 6969))
print("Connected to server")
client_socket.send("give public key".encode())
data=recvall(client_socket)
public_key = serialization.load_pem_public_key(data, backend=default_backend())
print(f"Public key received: {public_key}")

signed_in=False

#setting welcome frame
welcome_frame= Welcome_Screen(root)
welcome_frame.pack()

#setting edit team frame
edit_frame=Edit_Screen(root)
#setting log\sign in frames
login_frame = Log_In(root)
signin_frame=Sign_In(root)
#setting join room frame
join_frame=Join_Room(root)
#setting create room frame
create_frame=Create_Room(root)
root.mainloop()