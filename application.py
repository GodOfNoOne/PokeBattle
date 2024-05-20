from CTkScrollableDropdown import *
import customtkinter as ctk
import tkinter as tk
from PIL import Image, ImageTk
import pandas as pd
import requests
from io import BytesIO


ctk.set_appearance_mode("dark")

#pokemon database
pokemon_dt = pd.read_csv(r"DataBases\\df_pokemon.csv")
pokemon_dt=pokemon_dt.drop(columns=["Species",'Variant','Generation','Rarity','Evolves_from','Has_gender_diff','VGC2022_rules','Monthly Usage (k)','Usage Percent (%)','Monthly Rank'])
#pokemon_dt=pokemon_dt.drop_duplicates(subset="ID",keep="first")
pokemon_dt=pokemon_dt.set_index("ID")
pokemon_dt["Name"]=pokemon_dt["Name"].str.lower()
values=pokemon_dt["Name"].str.lower().to_list()

def create_room():
    print("Create Room")

def join_room():
    print("Join Room")

def edit_team():
    welcome_frame.forget()
    edit_frame.pack()

def battle_pc():
    print("Battle PC")

def sign_in():
    welcome_frame.forget()
    signin_frame.pack()

def log_in():
    welcome_frame.forget()
    login_frame.pack()

def submit(mode,username,password):
    print(f"{mode}\nusername: {username}\npassword: {password}")

def back_to_menu(frame):
    frame.forget()
    welcome_frame.pack()



class Welcome_Screen(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(width=1920,height=1080)
        # Welcome image
        welcome_Image=ctk.CTkImage(Image.open("Assets\Welcome_img.png"),size=(1024,434))
        welcome_label = ctk.CTkLabel(master=self, image=welcome_Image,text="")
        welcome_label.place(rely=0.1,relx=0.2)

        # Sign in and Log in buttons
        sign_in_button = ctk.CTkButton(self, text="Sign In", command=sign_in,font=("Cascadia Code",28))
        sign_in_button.place(relx=0.95, rely=0, anchor='ne')

        log_in_button = ctk.CTkButton(self, text="Log In", command=log_in,font=("Cascadia Code",28))
        log_in_button.place(relx=0.85, rely=0, anchor='ne')

        # Buttons under the image
        create_room_button = ctk.CTkButton(self, text="Create Room", command=create_room,width=500,height=50,font=("Cascadia Code",28))
        create_room_button.place(rely=0.54,relx=0.35)

        join_room_button = ctk.CTkButton(self, text="Join Room", command=join_room,width=500,height=50,font=("Cascadia Code",28))
        join_room_button.place(rely=0.64,relx=0.35)

        edit_team_button = ctk.CTkButton(self, text="Edit Team", command=edit_team,width=500,height=50,font=("Cascadia Code",28))
        edit_team_button.place(rely=0.74,relx=0.35)

        battle_pc_button = ctk.CTkButton(self, text="Battle PC", command=battle_pc,width=500,height=50,font=("Cascadia Code",28))
        battle_pc_button.place(rely=0.84,relx=0.35)

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

class Pokemon_Tabs(ctk.CTkTabview):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(width=1000,height=500)
        self.add("Pokemon 1")
        self.add("Pokemon 2")
        self.add("Pokemon 3")
        self.add("Pokemon 4")
        self.add("Pokemon 5")
        self.add("Pokemon 6")

        def insert_method(e,entry,label):
            entry.delete(0, 'end')
            entry.insert(0, e)
            selected=pokemon_dt.where(pokemon_dt["Name"]==e).dropna(how="all")
            url=selected["image_url"].iloc[0]
            response = requests.get(url)
            img = Image.open(BytesIO(response.content))
            pokemon_img=ctk.CTkImage(img,size=(250,250))
            label.configure(image=pokemon_img)
        
        pokemon_entry1=ctk.CTkEntry(master = self.tab("Pokemon 1"))
        pokemon_entry1.pack()
        url='https://img.pokemondb.net/sprites/sword-shield/icon/bulbasaur.png'
        response = requests.get(url)
        img = Image.open(BytesIO(response.content))
        pokemon_img=ctk.CTkImage(img,size=(250,250))
        pokemon_label= ctk.CTkLabel(self.tab("Pokemon 1"),text="",image=pokemon_img)
        pokemon_label.pack()
        pokemon_entry2=ctk.CTkEntry(master = self.tab("Pokemon 2"))
        pokemon_entry2.pack()
        pokemon_entry3=ctk.CTkEntry(master = self.tab("Pokemon 3"))
        pokemon_entry3.pack()
        pokemon_entry4=ctk.CTkEntry(master = self.tab("Pokemon 4"))
        pokemon_entry4.pack()
        pokemon_entry5=ctk.CTkEntry(master = self.tab("Pokemon 5"))
        pokemon_entry5.pack()
        pokemon_entry6=ctk.CTkEntry(master = self.tab("Pokemon 6"))
        pokemon_entry6.pack()
        CTkScrollableDropdown(pokemon_entry1, values=values, command=lambda e: insert_method(e,pokemon_entry1,pokemon_label),
                            autocomplete=True)
        
        #MAKE IT WITH THREADS
        
        '''CTkScrollableDropdown(pokemon_entry2, values=values, command=lambda e: insert_method(e,pokemon_entry2),
                            autocomplete=True)'''
        '''
        CTkScrollableDropdown(pokemon_entry3, values=values, command=lambda e: insert_method(e,pokemon_entry3),
                            autocomplete=True)
        CTkScrollableDropdown(pokemon_entry4, values=values, command=lambda e: insert_method(e,pokemon_entry4),
                            autocomplete=True)
        CTkScrollableDropdown(pokemon_entry5, values=values, command=lambda e: insert_method(e,pokemon_entry5),
                            autocomplete=True)
        CTkScrollableDropdown(pokemon_entry6, values=values, command=lambda e: insert_method(e,pokemon_entry6),
                            autocomplete=True)'''

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

 

#setting root
root = ctk.CTk()
root.title("PokeBattle")
root.geometry("1920x1080")
#root.attributes("-fullscreen", "True")
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)


#setting welcome frame
welcome_frame= Welcome_Screen(root)
welcome_frame.pack()

#setting edit team frame
edit_frame=Edit_Screen(root)
#setting log\sign in frames
login_frame = Log_In(root)
signin_frame=Sign_In(root)

root.mainloop()