from tkinter import * #Imports for libaries and methods to be used later
from tkinter import *
from tkinter import messagebox
from PIL import ImageTk, Image as PILImage
from pymongo.mongo_client import MongoClient
import hashlib
from functions import center_window
import json
import os
from dotenv import load_dotenv

#To load the hidden API DB key to be accessed by the code but not seen when published
load_dotenv()

#Hidden API key in env file to ensure no leakage of sensitive information while still accessing DB
client = MongoClient(os.getenv("DBKey"))

#Accessing DB and needed collections
db = client["ia_Database"]
users_collection = db["users"]
sites = db["sites"]

#use pip install pyinstaller, then use pyinstaller main.py to create desktop shortcut when app finished

#Maybe make a password checker show that certain characters cannot be used, or min - max amount of chars, must have capital and symbol

class App:
    def __init__(self):

        self.tk = Tk() #Creating tkinter window and assigining its properties and making it accessible in all methods with self
        self.tk.title("Login") #Gives the title to the window
        self.tk.geometry("1366x900") #Gives the size of the window
        self.tk.iconbitmap(r"Images/oman.ico") #Adds the Oman Icon to the top left of the window
        self.tk.configure(background="#666DEA") #Changes the background color of the application
        center_window(self.tk) #Centering the window with imported function from functions.py

        utitle = Text(self.tk, borderwidth=0, background="#666DEA", height =1, width = 20, font=("Arial", 18, "bold")) #Creating the title for the username entry
        utitle.insert(END, "Enter Your Username") #Inserts the information for the title
        utitle.config(state=DISABLED)
        utitle.place(relx = 0.5, rely = 0.55, anchor = CENTER) #Places the title in the needed postition

        username = Entry(self.tk, width = 50, bg = "white", font=("Arial", 18)) #Requesting username with an entry box
        username.place(relx = 0.5, rely = 0.6, anchor = CENTER)

        ptitle = Text(self.tk, borderwidth=0, background="#666DEA", height =1, width = 20, font=("Arial", 18, "bold")) #Creating the title for the password entry
        ptitle.insert(END, "Enter Your Password")
        ptitle.config(state=DISABLED)
        ptitle.place(relx = 0.5, rely = 0.65, anchor = CENTER)


        password = Entry(self.tk, width = 50, bg = "white", font=("Arial", 18), show="*") #Requesting password with an entry box
        password.place(relx = 0.5, rely = 0.7, anchor = CENTER)

        loginButton = Button( #Creating, placing, and customising the button to login to the application
            self.tk, #Assigns which window the button is on
            text= "Log-In", #Text displayed on the button
            font=("Arial", 16, "bold"), #Style of the text
            command=lambda: login(self, username.get(), password.get()), #Calling the login function to ensure login is correct and to handle opening the new page and closing the login page
            background="black", #BG color
            foreground="white", #FG color
            activebackground="#141414", #BG color when pressed
            activeforeground="#E1D9D1", #FG color when pressed
            cursor="hand2", #Type of cursor when button is hovered over
            borderwidth=2, #Width of the border
            width= 15, #Width of the button
            height = 1 #Height of the button

        )
        loginButton.place(relx = 0.42, rely = 0.9, anchor = CENTER)

        delete_UserBtn = Button( #Creating, placing, and customising the button open the delete user toplevel window
            self.tk,
            text= "Delete User",
            font=("Arial", 16, "bold"),
            command=lambda: delete_User(), #Calling the function to open the toplevel with its functionality
            background="red",
            foreground="white",
            activebackground="#6C1413",
            activeforeground="#E1D9D1",
            cursor="hand2",
            borderwidth=2,
            width= 15,
            height = 1
        )
        delete_UserBtn.place(relx = 0.58, rely = 0.9, anchor = CENTER)

        signupButton = Button( #Creating, placing, and customising the button signup a user to the DB
            self.tk,
            text= "Sign-Up",
            font=("Arial", 16, "bold"),
            command=lambda: signup(username.get(), password.get()), #Calls the signup function
            background="white",
            foreground="black",
            activebackground="#E1D9D1",
            activeforeground="#141414",
            cursor="hand2",
            borderwidth=2,
            width= 15,
            height = 1
        )
        signupButton.place(relx = 0.375, rely = 0.8, anchor = CENTER)

        title = Text(self.tk, borderwidth=0, background="#666DEA", height =1, width = 10, font=("Arial", 36, "bold")) #Title for the login page
        title.insert(END, "Login Page")
        title.config(state=DISABLED)
        title.place(relx = 0.5, rely = 0.45, anchor = CENTER)

        changePasswordButton = Button( #Creating, placing, and customising the button open the change password toplevel window
            self.tk,
            text= "Change Password",
            font=("Arial", 16, "bold"),
            command=lambda: changePassword(), #Calls the method when clicked
            background="white",
            foreground="black",
            activebackground="#E1D9D1",
            activeforeground="#141414",
            cursor="hand2",
            borderwidth=2,
            width= 15,
            height = 1
        )
        changePasswordButton.place(relx = 0.625, rely = 0.8, anchor = CENTER)

        img = PILImage.open("Images/SET.png") #Opens the title image

        imgResized = img.resize((500,250)) #Resizes the image created 

        clbImage = ImageTk.PhotoImage(imgResized) #Saves the image so that it is not garbage collected and can actually be seen
        self.tk.clbImage = clbImage

        slbpanel = Label( #Customises and placesthe image, ensures the transparent background of the image matches the background color instead of just being white
            self.tk,
            image=clbImage,
            background="#666DEA",
            borderwidth=0,
            border=0
            )
        slbpanel.place(relx=0.5, rely= 0.2, anchor=CENTER)

        self.tk.mainloop()
    
def login(self, user: str, pwd: str):

    if user == "" or pwd == "": #Checks if the username or password entry is empty to showcase an error message
        messagebox.showerror("Invalid", "Username or Password is Empty.")
        return
    
    #Hashes the username and password for security
    hashed_pwd = hashlib.sha256(pwd.encode()).hexdigest()
    hashed_user = hashlib.sha256(user.encode()).hexdigest()

    if users_collection.find_one({"username": hashed_user, "password": hashed_pwd}): #Checks the MongoDB database for a matching username and password combination to create a new menu class starting the app and destroys the login page window
        from menu import menu
        self.tk.destroy()
        userMenu = menu(hashed_user) #Instantiates the menu class to start the menu script
        return
    messagebox.showerror("Invalid", "Incorrect Password/Username") #Error message if matching username and password is not found in the DB
    return

def signup(newusername: str, newpassword: str):

    hashed_newpassword = hashlib.sha256(newpassword.encode()).hexdigest() #Hashes the username and password for security
    hashed_newusername = hashlib.sha256(newusername.encode()).hexdigest()

    #Checks if the username or password entry is empty to showcase an error message
    if newusername == "" or newpassword == "":
        messagebox.showerror("Invalid", "Username or Password is Empty.")
        return
    
    #Checks if the username already exists to ensure their are no repeated usernames
    if users_collection.find_one({'username': hashed_newusername}):
        messagebox.showerror("Invalid", "Username already exists.")
        return
    
    with open('OmanMap.geojson', 'r') as f: #Opens the geojson file and loads it into the gdf variable
        file = f.read()
    gdf = json.loads(file)

    #Creates a new user with the username, password, and string of the geojson file
    users_collection.insert_one({"username": hashed_newusername, "password": hashed_newpassword, "geojson": str(gdf)})

    messagebox.showinfo("Success", "User Signed Up") #Tells user they have signed up

def changePassword():

    changePwd = Toplevel() #Creates a new toplevel window to be on top of the existing window
    changePwd.title("Change Password Screen")
    changePwd.geometry("500x500")
    changePwd.iconbitmap(r"Images/oman.ico")
    changePwd.configure(bg="grey")
    center_window(changePwd) #Centers the window

    title = Text(changePwd, borderwidth=0, background="grey", height =1, width = 16, font=("Arial", 36, "bold")) #Creates the title
    title.insert(END, "Change Password")
    title.config(state=DISABLED)
    title.place(relx = 0.5, rely = 0.10, anchor = CENTER)

    user = Entry(changePwd, width = 30, bg = "white", font=("Arial", 18)) #Requests the users username with an entry
    user.place(relx = 0.5, rely = 0.3, anchor = CENTER)

    usertitle = Text(changePwd, borderwidth=0, background="grey", height =1, width = 20, font=("Arial", 18, "bold")) #Titles the entry box of the username request
    usertitle.insert(END, "Enter Old Username")
    usertitle.config(state=DISABLED)
    usertitle.place(relx = 0.5, rely = 0.2, anchor = CENTER)

    oldpwd = Entry(changePwd, show="*", width = 30, bg = "white", font=("Arial", 18)) #Requests the users old password with an entry
    oldpwd.place(relx = 0.5, rely = 0.5, anchor = CENTER)

    oldpwdtitle = Text(changePwd, borderwidth=0, background="grey", height =1, width = 20, font=("Arial", 18, "bold")) #Titles the entry box of the old password request
    oldpwdtitle.insert(END, "Enter Old Password")
    oldpwdtitle.config(state=DISABLED)
    oldpwdtitle.place(relx = 0.5, rely = 0.4, anchor = CENTER)

    newpwd = Entry(changePwd, show="*", width = 30, bg = "white", font=("Arial", 18)) #Requests the users new password with an entry
    newpwd.place(relx = 0.5, rely = 0.7, anchor = CENTER)

    newpwdtitle = Text(changePwd, borderwidth=0, background="grey", height =1, width = 20, font=("Arial", 18, "bold")) #Titles the entry box of the new password request
    newpwdtitle.insert(END, "Enter New Password")
    newpwdtitle.config(state=DISABLED)
    newpwdtitle.place(relx = 0.5, rely = 0.6, anchor = CENTER)

    GoButton = Button( #Button to confirm their information and change the password
    changePwd,
    text= "Change Password",
    font=("Arial", 16, "bold"),
    command=lambda: changePasswordGo(changePwd, user, newpwd, oldpwd), #Calls the function to check if the information is valid
    background="white",
    foreground="black",
    activebackground="#E1D9D1",
    activeforeground="#141414",
    cursor="hand2",
    borderwidth=2,
    width= 15,
    height = 1
    )
    GoButton.place(relx = 0.5, rely = 0.9, anchor = CENTER)

def changePasswordGo(changePwd: Tk, user: Entry, newpwd: Entry, oldpwd: Entry):

    username = user.get() #Gets the username, old password, and new password from the entries
    oldpassword = oldpwd.get()
    newpassword = newpwd.get()

    if username == "" or newpassword == "" or oldpassword == "": #If the entries are empty an error message is shown
        messagebox.showerror("Invalid", "Username or Password is Empty.")
        return

    hashed_oldpwd = hashlib.sha256(oldpassword.encode()).hexdigest() #Entries are hashed for security
    hashed_newpwd = hashlib.sha256(newpassword.encode()).hexdigest()
    hashed_username = hashlib.sha256(username.encode()).hexdigest()

    if users_collection.find_one({"username": hashed_username, "password": hashed_oldpwd}): #Checks if the username and password combination exists and changes the old password to the new password
        users_collection.update_one({"username": hashed_username},{'$set': {'password': hashed_newpwd}})
        changePwd.destroy() #Closes the toplevel
        messagebox.showinfo("Success", "Password Changed") #Shows success message to the client
        return
    changePwd.destroy()
    messagebox.showerror("Invalid", "Username and Password Doesn't Exist, or is Invalid") #Shows an error message meaning the username and password combination does not exist
    return

def delete_User():
    deleteUser = Toplevel() #Creates a new toplevel window on the main window to delete user
    deleteUser.title("Delete User Screen")
    deleteUser.geometry("500x500")
    deleteUser.iconbitmap(r"Images/oman.ico")
    deleteUser.configure(bg="#D3494E")
    center_window(deleteUser) #Centers the toplevel to the middle of the screen

    title = Text(deleteUser, borderwidth=0, background="#D3494E", height =1, width = 11, font=("Arial", 36, "bold")) #Gives the title to the toplevel
    title.insert(END, "Delete User")
    title.config(state=DISABLED)
    title.place(relx = 0.5, rely = 0.1, anchor = CENTER)

    user = Entry(deleteUser, width = 30, bg = "white", font=("Arial", 18)) #Entry for the username
    user.place(relx = 0.5, rely = 0.4, anchor = CENTER)

    usertitle = Text(deleteUser, borderwidth=0, background="#D3494E", height =1, width = 14, font=("Arial", 18, "bold")) #Title for the username entry
    usertitle.insert(END, "Enter Username")
    usertitle.config(state=DISABLED)
    usertitle.place(relx = 0.5, rely = 0.3, anchor = CENTER)

    pwd = Entry(deleteUser, show="*", width = 30, bg = "white", font=("Arial", 18)) #Entry for the password
    pwd.place(relx = 0.5, rely = 0.6, anchor = CENTER)

    pwdtitle = Text(deleteUser, borderwidth=0, background="#D3494E", height =1, width = 14, font=("Arial", 18, "bold")) #Title for the password entry
    pwdtitle.insert(END, "Enter Password")
    pwdtitle.config(state=DISABLED)
    pwdtitle.place(relx = 0.5, rely = 0.5, anchor = CENTER)

    GoButton = Button( #Button to call the function
    deleteUser,
    text= "Confirm",
    font=("Arial", 16, "bold"),
    command=lambda: deleteUserGo(user.get(), pwd.get(), deleteUser),
    background="black",
    foreground="white",
    activebackground="#141414",
    activeforeground="#E1D9D1",
    cursor="hand2",
    borderwidth=2,
    width= 15,
    height = 1
    )
    GoButton.place(relx = 0.5, rely = 0.8, anchor = CENTER)

def deleteUserGo(user, pwd, deleteUser):

    hashed_pwd = hashlib.sha256(pwd.encode()).hexdigest() #Hashes the entries to ensure the correct values are being checked as the data in the DB is also hashed
    hashed_user = hashlib.sha256(user.encode()).hexdigest()

    #Checks if the username and password combination exists and deletes the users file
    if users_collection.find_one({"username": hashed_user, "password": hashed_pwd}):
        #Deletes the users file in the users_collection
        users_collection.delete_one({"username": hashed_user})
        #Deletes all excavation sites created by this user
        sites.delete_many({"username": hashed_user})
        messagebox.showinfo("Success", "User Deleted")
        deleteUser.destroy()
        return
    #Showcases error message meaning username and password combination does not work
    messagebox.showerror("Invalid", "Username and Password Doesn't Exist, or is Invalid")
    deleteUser.destroy()
    return

main = App() #Calls the class to start the script