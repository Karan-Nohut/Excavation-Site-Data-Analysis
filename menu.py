from tkinter import * #Imports for libaries and methods to be used later
from tkinter import messagebox, filedialog
import tkinter as tk
from functions import center_window
from pymongo.mongo_client import MongoClient
import numpy as np
import matplotlib.pyplot as plt
from shapely.geometry import Point
import geopandas as gpd
from PIL import ImageTk, Image as PILImage
import geoplot as gplt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import geojson
import json
from shapely import Polygon
import tempfile
import sys
import os
from io import BytesIO
import base64
import lasio
from dotenv import load_dotenv

load_dotenv() #To load the hidden API DB key to be accessed by the code but not seen when published

client = MongoClient(os.getenv("DBKey")) #Hidden API key in env file to ensure no leakage of sensitive information while still accessing DB

db = client["ia_Database"] #Accessing DB and needed collections
users_collection = db["users"]
sites = db["sites"]

class menu:
    def __init__(self, username):
        self.user = username #Creating variables to be accessed throughout the menu class

        self.file = users_collection.find_one({"username": self.user}) #Gets the geojson str data from the Db, replaces all ' with " for correct formatting, creates temp file to be used without making a local file
        geoStr = self.file.get("geojson")
        geoStr = geoStr.replace("'", '"')
        with tempfile.NamedTemporaryFile(delete=False, suffix='.geojson') as temp_file:
            temp_file.write(geoStr.encode('utf-8')) #Converts to bits to be read
            temp_file.flush()
            self.gdf = gpd.read_file(temp_file.name) #Gets name of temp file to be accessed in all other methods

        self.t = Tk() #Creates menu tk screen and gives it properties
        self.t.title("Menu Screen")
        self.t.geometry("1366x900")
        self.t.iconbitmap(r"Images/oman.ico")
        self.t.configure(background="#BFE2C2")
        center_window(self.t)
        
        switchUserBtn = Button( #Switch user button using switchUser method
        self.t,
        text= "Switch User",
        font=("Arial", 16, "bold"),
        command=lambda: self.switchUser(self.t),
        background="white",
        foreground="black",
        activebackground="#E1D9D1",
        activeforeground="#141414",
        cursor="hand2",
        borderwidth=2,
        width= 15,
        height = 1
        )
        switchUserBtn.place(relx = 0.0875, rely = 0.1, anchor = CENTER)

        uploadFileBtn = Button( #Upload file button using uploadFile method
        self.t,
        text= "Upload File",
        font=("Arial", 16, "bold"),
        command=lambda: self.uploadFile(),
        background="white",
        foreground="black",
        activebackground="#E1D9D1",
        activeforeground="#141414",
        cursor="hand2",
        borderwidth=2,
        width= 15,
        height = 1

        )
        uploadFileBtn.place(relx = 0.9125, rely = 0.1, anchor = CENTER)
        
        #Plots the gotten data from DB to showcase the map of Oman and the created sites and adjusts its color and places it
        fig, ax = plt.subplots(figsize=(9,9))
        gplt.polyplot(self.gdf, ax=ax, edgecolor ="black", facecolor="#BFE2C2")
        fig.subplots_adjust(left=0, right=1, top=1, bottom=0, wspace=0, hspace=0)

        #Draws the canvas where the plot will be shown
        self.canvas = FigureCanvasTkAgg(fig, master=self.t)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.canvas._tkcanvas.place(relx = 0.5, rely = 0.5, anchor = CENTER)

        #Creates and places the Matplot toolbar to be used on the map of Oman
        toolbarFrame = Frame(master=self.t)
        toolbarFrame.place(anchor = S, relx = 0.5, rely = 1)
        toolbar = NavigationToolbar2Tk(self.canvas, toolbarFrame)
        
        #When the canvas is left-clicked the onClick function is checked
        fig.canvas.callbacks.connect('button_press_event', self.onClick)

        # add color to points
        # make DB store JSON files not string,
        # when zooming or smth it still registers clicks

        self.t.protocol("WM_DELETE_WINDOW", self.onClose) #Ensures the program properly closes when the x button is clicked while a process is occuring
        self.t.mainloop() #Runs the tk window

    #Checks if the click is within the Oman polygon to check if the clicked X-Y is a excavation site so that its information can be showcased
    def onClick(self, event):
        if not event.xdata or not event.ydata:
            return

        clicked_point = Point(event.xdata, event.ydata)

        #Finds files that belong to this specific user to iterate through
        for file in sites.find({"username": self.user}):
            site = file.get("sitePoly")
            #Loads the geojson from the DB
            site_json = json.loads(site)

            #Gets only the polygon data from the accessed geojson file
            site_geometry = site_json.get('geometry')

            if site_geometry['type'] == 'Polygon':
                #Converts coordiantes into a polygon that can be checked if a point exists in it
                polygon = Polygon(site_geometry['coordinates'][0])

                #If the point is inside this polygon we open the toplevel window showing the excavation site data
                if polygon.contains(clicked_point):
                    #Creates a toplevel window to get the X-Y entry and process it
                    edit = Toplevel()
                    edit.title("Edit Excavation Site")
                    edit.geometry("1200x1000")
                    edit.iconbitmap(r"Images/oman.ico")
                    edit.configure(bg="grey")
                    center_window(edit)

                    foundSite = sites.find_one({"sitePoly": site,})

                    siteName = Text(edit, borderwidth=0, background="grey", height =1, width = 25, font=("Arial", 20, "bold")) #Title for the password entry
                    siteName.insert(END, "Name: " + foundSite.get("Name"))
                    siteName.config(state=DISABLED)
                    siteName.place(relx = 0.5, rely = 0.05, anchor = CENTER)

                    siteDate = Text(edit, borderwidth=0, background="grey", height =1, width = 20, font=("Arial", 20, "bold")) #Title for the password entry
                    siteDate.insert(END, " Date: " + foundSite.get("Date"))
                    siteDate.config(state=DISABLED)
                    siteDate.place(relx = 0.3, rely = 0.8, anchor = CENTER)

                    siteState = Text(edit, borderwidth=0, background="grey", height =1, width = 20, font=("Arial", 20, "bold")) #Title for the password entry
                    siteState.insert(END, "State: " + foundSite.get("State"))
                    siteState.config(state=DISABLED)
                    siteState.place(relx = 0.7, rely = 0.8, anchor = CENTER)

                    siteLatitude = Text(edit, borderwidth=0, background="grey", height =1, width = 19, font=("Arial", 20, "bold")) #Title for the password entry
                    siteLatitude.insert(END, "Latitude: " + str(foundSite.get("Latitude")))
                    siteLatitude.config(state=DISABLED)
                    siteLatitude.place(relx = 0.3, rely = 0.9, anchor = CENTER)

                    siteLongitude = Text(edit, borderwidth=0, background="grey", height =1, width = 20, font=("Arial", 20, "bold")) #Title for the password entry
                    siteLongitude.insert(END, "Longitude: " + str(foundSite.get("Longitude")))
                    siteLongitude.config(state=DISABLED)
                    siteLongitude.place(relx = 0.7, rely = 0.9, anchor = CENTER)

                    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp_png:
                        temp_png.write(foundSite.get("Diagrams"))
                        temp_pngname = temp_png.name  # Get the file's name

                    diagramImg = PILImage.open(temp_pngname) #Opens the title image
                    
                    diagramImgResized = diagramImg.resize((925,625)) #Resizes the image created
                    diagramImgResized.save(temp_pngname, "PNG")
                    
                    pngImage = ImageTk.PhotoImage(diagramImgResized) #Saves the image so that it is not garbage collected and can actually be seen
                    edit.pngImage = pngImage

                    pngImagepanel = Label( #Customises and placesthe image, ensures the transparent background of the image matches the background color instead of just being white
                        edit,
                        image=pngImage,
                        background="white",
                        borderwidth=0,
                        border=0
                        )
                    pngImagepanel.place(relx=0.5, rely= 0.4, anchor=CENTER)

                    #Ensures two windows are not opened if an overlapping site is created
                    break
        
    def onClose(self): #Closes the window, the DB client access, all all other functions
        self.t.destroy()
        client.close()
        sys.exit()

    def switchUser(self, menu: Tk,): #Closes the tk window and opens the login window to change account logged into
        menu.destroy()
        os.system("python main.py")

    def uploadFile(self): #Takes an upload of a .las file to be proccessed
        uploadFile = Toplevel() #Creates a new toplevel window on the main window to delete user
        uploadFile.title("Upload File Screen")
        uploadFile.geometry("1000x750")
        uploadFile.iconbitmap(r"Images/oman.ico")
        uploadFile.configure(bg="#FFE4E1")
        center_window(uploadFile) #Centers the toplevel to the middle of the screen

        GRMaxCoe = Entry(uploadFile,  width = 10, bg = "white", font=("Arial", 17)) 
        GRMaxCoe.place(relx = 0.3, rely = 0.2, anchor = CENTER)
        GRMaxCoetitle = Text(uploadFile, borderwidth=0, background="white", height =1, width = 22, font=("Arial", 18, "bold")) 
        GRMaxCoetitle.insert(END, "GR Maximum Multiplier")
        GRMaxCoetitle.config(state=DISABLED)
        GRMaxCoetitle.place(relx = 0.3, rely = 0.1, anchor = CENTER)

        GRMinCoe = Entry(uploadFile, width = 10, bg = "white", font=("Arial", 17)) 
        GRMinCoe.place(relx = 0.7, rely = 0.2, anchor = CENTER)
        GRMinCoetitle = Text(uploadFile, borderwidth=0, background="white", height =1, width = 22, font=("Arial", 18, "bold"))
        GRMinCoetitle.insert(END, "GR Minimum Multiplier")
        GRMinCoetitle.config(state=DISABLED)
        GRMinCoetitle.place(relx = 0.7, rely = 0.1, anchor = CENTER)

        VSHCoe = Entry(uploadFile,  width = 10, bg = "white", font=("Arial", 18)) 
        VSHCoe.place(relx = 0.8, rely = 0.4, anchor = CENTER)
        VSHCoetitle = Text(uploadFile, borderwidth=0, background="white", height =1, width = 19, font=("Arial", 18, "bold")) 
        VSHCoetitle.insert(END, "Clay Bound Porosity")
        VSHCoetitle.config(state=DISABLED)
        VSHCoetitle.place(relx = 0.8, rely = 0.3, anchor = CENTER)

        matrixDensityCoe = Entry(uploadFile,  width = 10, bg = "white", font=("Arial", 18)) 
        matrixDensityCoe.place(relx = 0.5, rely = 0.4, anchor = CENTER)
        matrixDensityCoeetitle = Text(uploadFile, borderwidth=0, background="white", height =1, width = 13, font=("Arial", 18, "bold")) 
        matrixDensityCoeetitle.insert(END, "Matrix Density")
        matrixDensityCoeetitle.config(state=DISABLED)
        matrixDensityCoeetitle.place(relx = 0.5, rely = 0.3, anchor = CENTER)

        fluidDensityCoe = Entry(uploadFile,  width = 10, bg = "white", font=("Arial", 18)) 
        fluidDensityCoe.place(relx = 0.2, rely = 0.4, anchor = CENTER)
        fluidDensityCoetitle = Text(uploadFile, borderwidth=0, background="white", height =1, width = 12, font=("Arial", 18, "bold")) 
        fluidDensityCoetitle.insert(END, "Fluid Density")
        fluidDensityCoetitle.config(state=DISABLED)
        fluidDensityCoetitle.place(relx = 0.2, rely = 0.3, anchor = CENTER)

        SWCoe = Entry(uploadFile, width = 10, bg = "white", font=("Arial", 18)) 
        SWCoe.place(relx = 0.2, rely = 0.6, anchor = CENTER)
        SWCoetitle = Text(uploadFile, borderwidth=0, background="white", height =1, width = 4, font=("Arial", 18, "bold")) 
        SWCoetitle.insert(END, "RW")
        SWCoetitle.config(state=DISABLED)
        SWCoetitle.place(relx = 0.2, rely = 0.5, anchor = CENTER)

        a = Entry(uploadFile, width = 10, bg = "white", font=("Arial", 18)) 
        a.place(relx = 0.4, rely = 0.6, anchor = CENTER)
        atitle = Text(uploadFile, borderwidth=0, background="white", height =1, width = 1, font=("Arial", 18, "bold")) 
        atitle.insert(END, "a")
        atitle.config(state=DISABLED)
        atitle.place(relx = 0.4, rely = 0.5, anchor = CENTER)

        m = Entry(uploadFile, width = 10, bg = "white", font=("Arial", 18)) 
        m.place(relx = 0.6, rely = 0.6, anchor = CENTER)
        mtitle = Text(uploadFile, borderwidth=0, background="white", height =1, width = 2, font=("Arial", 18, "bold"))
        mtitle.insert(END, "m")
        mtitle.config(state=DISABLED)
        mtitle.place(relx = 0.6, rely = 0.5, anchor = CENTER)

        n = Entry(uploadFile, width = 10, bg = "white", font=("Arial", 18))
        n.place(relx = 0.8, rely = 0.6, anchor = CENTER)
        ntitle = Text(uploadFile, borderwidth=0, background="white", height =1, width = 1, font=("Arial", 18, "bold")) 
        ntitle.insert(END, "n")
        ntitle.config(state=DISABLED)
        ntitle.place(relx = 0.8, rely = 0.5, anchor = CENTER)

        VHSLimit = Entry(uploadFile, width = 10, bg = "white", font=("Arial", 18)) 
        VHSLimit.place(relx = 0.2, rely = 0.8, anchor = CENTER)
        VHSLimittitle = Text(uploadFile, borderwidth=0, background="white", height =1, width = 11, font=("Arial", 18, "bold")) 
        VHSLimittitle.insert(END, "VSh Cut Off")
        VHSLimittitle.config(state=DISABLED)
        VHSLimittitle.place(relx = 0.2, rely = 0.7, anchor = CENTER)

        PHIELimit = Entry(uploadFile, width = 10, bg = "white", font=("Arial", 18)) 
        PHIELimit.place(relx = 0.5, rely = 0.8, anchor = CENTER)
        PHIELimittitle = Text(uploadFile, borderwidth=0, background="white", height =1, width = 12, font=("Arial", 18, "bold"))
        PHIELimittitle.insert(END, "PHIE Cut Off")
        PHIELimittitle.config(state=DISABLED)
        PHIELimittitle.place(relx = 0.5, rely = 0.7, anchor = CENTER)

        SWLimit = Entry(uploadFile, width = 10, bg = "white", font=("Arial", 18)) #
        SWLimit.place(relx = 0.8, rely = 0.8, anchor = CENTER)
        SWLimittitle = Text(uploadFile, borderwidth=0, background="white", height =1, width = 10, font=("Arial", 17, "bold")) 
        SWLimittitle.insert(END, "Sw Cut Off")
        SWLimittitle.config(state=DISABLED)
        SWLimittitle.place(relx = 0.8, rely = 0.7, anchor = CENTER)

        uploadFileButton = Button( #Button to call the function
        uploadFile,
        text= "Upload File",
        font=("Arial", 16, "bold"),
        command=lambda: self.uploadFileGo(GRMaxCoe.get(), GRMinCoe.get(), VSHCoe.get(), matrixDensityCoe.get(), fluidDensityCoe.get(), a.get(), m.get(), n.get(), SWCoe.get(), VHSLimit.get(), PHIELimit.get(), SWLimit.get()),
        background="black",
        foreground="white",
        activebackground="#141414",
        activeforeground="#E1D9D1",
        cursor="hand2",
        borderwidth=2,
        width= 15,
        height = 1
        )
        uploadFileButton.place(relx = 0.5, rely = 0.9, anchor = CENTER)

    def uploadFileGo(self, GRMaxCoe, GRMinCoe, VSHCoe, matrixDensityCoe, fluidDensityCoe, a, m, n, SWCoe, VHSLimit, PHIELimit, SWLimit):
        try:
            # Try to convert the input to a float to check if valid input
            float(GRMaxCoe)
            float(GRMinCoe)
            float(VSHCoe)
            float(SWCoe)
            float(VHSLimit)
            float(PHIELimit)
            float(SWLimit)
            float(a)
            float(n)
            float(m)
            float(fluidDensityCoe)
            float(matrixDensityCoe)
        except ValueError:
            # If the conversion fails show an error message
            messagebox.showerror("Fail", "One or More of the Entries are Invalid")
            return
        plt.close(1)
        self.createDiagrams(GRMaxCoe, GRMinCoe, VSHCoe, matrixDensityCoe, fluidDensityCoe, a, m, n, SWCoe, VHSLimit, PHIELimit, SWLimit)

    #Checks if the entered X-Y is inside the real world borders of Oman before trying to create a site
    def checkBorderValid(self, longitude, latitude):
        plt.close('all')
        for polygon in self.gdf.itertuples():
            #Checks each polygon to see if X-Y falls within its borders
            if polygon.geometry.contains(Point(longitude, latitude)):
                return True
        return False

    def createSite(self, las_file): #Window to enter X-Y shows up
        #if the x-y coords are not in the file then this wont work

        latitude = las_file.well.LATI.value
        longitude = las_file.well.LONG.value
        
        try:
            # Try to convert the input to a float to check if valid input
            float(latitude)
            float(longitude)
        except ValueError:
            # If the conversion fails show an error message
            messagebox.showerror("Fail", "Latitude or Longitude is Not a Number")
            return
        
        if self.checkBorderValid(longitude, latitude): #Checks if the X-Y is valid with checkBorderValid method to continue process 
            newSite = geojson.Polygon([[ #Creats a new polygon as an octogon around the inputted X-Y so that it can be seen on the Map with 8 points that are the same distance from the middle
                [float(longitude) + 0.05656854249, float(latitude)],
                [float(longitude) + 0.04, float(latitude) + 0.04],
                [float(longitude), float(latitude) + 0.05656854249],
                [float(longitude) - 0.04, float(latitude) + 0.04],
                [float(longitude) - 0.05656854249, float(latitude)],
                [float(longitude) - 0.04, float(latitude) - 0.04],
                [float(longitude), float(latitude) - 0.05656854249],
                [float(longitude) + 0.04, float(latitude) - 0.04],
                [float(longitude) + 0.05656854249, float(latitude)]
            ]])

            newPoly = geojson.Feature(geometry=newSite, properties={}) #The points are created as a new polygon
            strPoly = geojson.dumps(newPoly) #Takes the new polygons data and makes it into a Json String
            sites.insert_one({"username": self.user, "sitePoly": str(newPoly)})
            geostr = self.file.get("geojson") #Accesses the DB geojson string data, again formats it by replacing ' with ", then loads the data as a Json String to be edited
            geostr = geostr.replace("'", '"') 
            geojson_data = json.loads(geostr)

            geojson_data['features'].append(json.loads(strPoly)) #Adds the new polygon to the file 

            geostr = json.dumps(geojson_data)
            users_collection.find_one_and_update({"username": self.user}, {"$set": {"geojson": geostr}}) #Updates the database with the new polygon or new site that has been added to the map
            
            #Reads the data from the DB and formats it properly into the GEOJSON format
            self.file = users_collection.find_one({"username": self.user})
            geoStr = self.file.get("geojson")
            geoStr = geoStr.replace("'", '"')

            #A temp file containing the accessed data is created to be used and then deleted when the app is closed
            with tempfile.NamedTemporaryFile(delete=False, suffix='.geojson') as temp_file:
                temp_file.write(geoStr.encode('utf-8'))
                temp_file.flush()
                self.gdf = gpd.read_file(temp_file.name)
            
            #Replots the data update the map
            fig, ax = plt.subplots(figsize=(9,9))
            gplt.polyplot(self.gdf, ax=ax, edgecolor ="black", facecolor="#BFE2C2")
            fig.subplots_adjust(left=0, right=1, top=1, bottom=0, wspace=0, hspace=0)
            self.canvas = FigureCanvasTkAgg(fig, master=self.t)
            self.canvas.draw()
            self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
            self.canvas._tkcanvas.place(relx = 0.5, rely = 0.5, anchor = CENTER)
            toolbarFrame = Frame(master=self.t)
            toolbarFrame.place(anchor = S, relx = 0.5, rely = 1)
            toolbar = NavigationToolbar2Tk(self.canvas, toolbarFrame)
            fig.canvas.callbacks.connect('button_press_event', self.onClick) 

            return
        else: #User case checking to let the user know their X-Y is not in Oman
            messagebox.showerror("Fail", "X-Y Coordinates Not in Oman")
            return
    def createDiagrams(self, GRMaxCoe, GRMinCoe, VSHCoe, matrixDensityCoe, fluidDensityCoe, a, m, n, SWCoe, VHSLimit, PHIELimit, SWLimit):
        #using LASIO we open the las file by opening file explorer
        file = filedialog.askopenfilename(filetypes=[("LAS Files", "*.las")])
        las = lasio.read(file)
        #Using pandas we create a dataframe containing the data inside of the las file to be accessed by matplot
        well = las.df()
        well.head()
        well.reset_index(inplace=True)
        well.head()
        #Creates the size and title of the figures
        fig1, bx = plt.subplots(1,7, figsize=(16, 8))
        plt.subplots_adjust(left=0.05, right=0.95, wspace=0.15)
        plt.suptitle("Well Data Plots", fontsize=16)
        #Plots the first track using the dataframe by making data equal to well, and accessing the curves of GR and DEPT that were in the las file
        bx[0].plot("GR", "DEPT", data=well, color="green")
        bx[0].set_xlabel("Gamma")
        bx[0].set_ylabel("Depth")
        bx[0].set_title("GR")
        bx[0].invert_yaxis()

        bx[1].plot("BS", "DEPT", data=well, color="black")
        bx[1].plot("CALI", "DEPT", data=well, color="red")
        bx[1].set_xlabel("BS / Caliper")
        bx[1].set_title("Washout")
        bx[1].fill_betweenx(well["DEPT"], well["BS"], well["CALI"], color="yellow", alpha=0.3)
        bx[1].set_yticks([])
        bx[1].invert_yaxis()

        parax1 = bx[2].twinx().twiny()
        parax1.plot("RHOZ", "DEPT", data=well, color="red")
        parax1.set_xticks([])
        parax1.set_yticks([])
        parax1.invert_yaxis()

        parax2 = bx[2].twinx().twiny()
        parax2.plot("TNPH", "DEPT", data=well, color="blue")
        parax2.set_xticks([])
        parax2.set_yticks([])
        parax2.set_xlim(0.45, -0.15)
        parax2.invert_yaxis()

        parax3 = bx[2].twinx().twiny()
        parax3.plot("PEFZ", "DEPT", data=well, color="pink")
        parax3.set_xticks([])
        parax3.set_yticks([])
        parax3.set_xlim(0, 10)
        parax3.invert_yaxis()

        bx[2].set_xlabel("RHOZ / TNPH")
        bx[2].set_title("Shale / Matrix")
        bx[2].set_xticks([])
        bx[2].set_yticks([])
        bx[2].invert_yaxis()

        bx[3].plot("RLA1", "DEPT", data=well, color="blue", linewidth=0.5)
        bx[3].plot("RLA2", "DEPT", data=well, color="black", linewidth=0.5)
        bx[3].plot("RLA3", "DEPT", data=well, color="orange", linewidth=0.5)
        bx[3].plot("RLA4", "DEPT", data=well, color="pink", linewidth=0.5)
        bx[3].plot("RLA5", "DEPT", data=well, color="purple", linewidth=0.5)
        bx[3].plot("RT", "DEPT", data=well, color="red")
        bx[3].plot("RXO", "DEPT", data=well, color="green")
        bx[3].set_xlim(0.2,2000)
        bx[3].set_xscale("log")
        bx[3].set_xlabel("Resistivity")
        bx[3].set_title("Resistivity")
        bx[3].set_yticks([])
        bx[3].invert_yaxis()

        GRmin = well["GR"].min()
        GRmax = well["GR"].max()
        VSH = (well["GR"] - GRmin*float(GRMinCoe)) / (GRmax*float(GRMaxCoe) - GRmin*float(GRMinCoe))
        PHIT_D = (float(matrixDensityCoe)-well["RHOZ"]) / (float(matrixDensityCoe) - float(fluidDensityCoe))
        PHIT_N = well["TNPH"]
        PHIT  = (PHIT_D+PHIT_N) / 2
        PHIE = (PHIT-(VSH*float(VSHCoe)))

        bx[4].plot(VSH, "DEPT", data=well, color = "green")

        parax4 = bx[4].twinx().twiny()
        parax4.plot(PHIT,"DEPT", data=well, color = "grey")
        parax4.plot(PHIE,"DEPT", data=well, color = "blue")
        parax4.set_xticks([])
        parax4.set_yticks([])
        parax4.set_xlim(1,0)
        parax4.invert_yaxis()

        bx[4].set_xlim(0,1)
        bx[4].set_xlabel("VMin")
        bx[4].set_title("Volumes")
        bx[4].set_yticks([])
        bx[4].set_xticks([])
        bx[4].fill_betweenx(well["DEPT"], VSH, color="green", alpha = 0.3)
        bx[4].fill_betweenx(well["DEPT"], VSH, 1-PHIT, color="yellow", alpha = 0.3)
        bx[4].fill_betweenx(well["DEPT"], 1-PHIT, 1-PHIE, color="black")
        bx[4].invert_yaxis()

        SW = np.power((float(SWCoe)*float(a)) / ((well["RT"] * PHIE**float(m))), (1/float(n)))

        bx[5].plot(SW, "DEPT", data=well, color = "purple")
        bx[5].set_xlim(1,0)
        bx[5].set_xlabel("SW")
        bx[5].set_title("Water Saturation")
        bx[5].set_yticks([])
        bx[5].invert_yaxis()

        net_pay = np.where((VSH < float(VHSLimit)) & (PHIE > float(PHIELimit)) & (SW < float(SWLimit)), 1, 0)
        res_pay = np.where((VSH < float(VHSLimit)) & (PHIE > float(PHIELimit)), 4, 5)
        bx[6].plot(net_pay, "DEPT", data=well, color = "black")
        bx[6].plot(res_pay, "DEPT", data=well, color = "black")
        bx[6].set_xlim(5,0)
        bx[6].set_xlabel("Res Pay")
        bx[6].set_title("Net/Res Pay")
        bx[6].set_yticks([])
        bx[6].fill_betweenx(well["DEPT"], net_pay, color="red")
        bx[6].fill_betweenx(well["DEPT"], 5, res_pay, color="green")
        bx[6].invert_yaxis()

        buffer = BytesIO()
        # Move the buffer's cursor to the beginning
        buffer.seek(0)

        # Store the PNG data as a variable
        plt.savefig(buffer, format="png")
        png_data = buffer.getvalue()
        plt.show()
        buffer.close()
        well.head()
        
        well.plot
        plt.close()  # Close the figure to free memory
        plt.show(block=True)

        self.createSiteTopLevel = Toplevel() #Creates a new toplevel window on the main window to delete user
        self.createSiteTopLevel.title("Confirm")
        self.createSiteTopLevel.geometry("850x200")
        self.createSiteTopLevel.iconbitmap(r"Images/oman.ico")
        self.createSiteTopLevel.configure(bg="#FDAA48")
        center_window(self.createSiteTopLevel) #Centers the toplevel to the middle of the screen

        confirmtitle = Text(self.createSiteTopLevel, borderwidth=0, background="#FDAA48", height =1, width = 62, font=("Arial", 17, "bold")) #Title for the password entry
        confirmtitle.insert(END, "Would You Like to Save The Coefficents and Create the Excavation Site?")
        confirmtitle.config(state=DISABLED)
        confirmtitle.place(relx = 0.5, rely = 0.3, anchor = CENTER)

        yesButton = Button( #Button to call the function
        self.createSiteTopLevel,
        text= "Yes",
        font=("Arial", 16, "bold"),
        command=lambda: self.yesButtonFunction(las, png_data),
        background="black",
        foreground="white",
        activebackground="#141414",
        activeforeground="#E1D9D1",
        cursor="hand2",
        borderwidth=2,
        width= 15,
        height = 1
        )
        yesButton.place(relx = 0.5, rely = 0.7, anchor = CENTER)

    def yesButtonFunction(self, las, png_data):
        self.createSite(las)
        self.updataExcavationSites(las, png_data)
        self.createSiteTopLevel.destroy()

    def updataExcavationSites(self, las, png_data):
        latitude = las.well.LATI.value
        longitude = las.well.LONG.value
        point = Point(longitude, latitude)

        #Finds files that belong to this specific user to iterate through
        for file in sites.find({"username": self.user}):
            site = file.get("sitePoly")
            #Loads the geojson from the DB
            site_json = json.loads(site)

            #Gets only the polygon data from the accessed geojson file
            site_geometry = site_json.get('geometry')

            if site_geometry['type'] == 'Polygon':
                #Converts coordiantes into a polygon that can be checked if a point exists in it
                polygon = Polygon(site_geometry['coordinates'][0])

                if polygon.contains(point):
                    well_name = las.sections["Well"].WELL.value
                    well_date = las.sections["Well"].date.value
                    well_state = las.sections["Well"].STAT.value
                    sites.find_one_and_update({"sitePoly": site}, {"$set": {"Date": well_date, "Name": well_name, "State": well_state, "Latitude": latitude, "Longitude": longitude, "Diagrams": png_data}})
    
    def get_base64_encoded_image(image_path):
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode('utf-8')
    # #do later bc excavation sites are stored altogether in the users file, so that needs to be accessed and change which i cba to do now
    # def deleteExcavationSite(self, latitude, longitude):
    #     point = Point(longitude, latitude)

    #     #Finds files that belong to this specific user to iterate through
    #     for file in sites.find({"username": self.user}):
    #         site = file.get("sitePoly")
    #         #Loads the geojson from the DB
    #         site_json = json.loads(site)

    #         #Gets only the polygon data from the accessed geojson file
    #         site_geometry = site_json.get('geometry')

    #         if site_geometry['type'] == 'Polygon':
    #             #Converts coordiantes into a polygon that can be checked if a point exists in it
    #             polygon = Polygon(site_geometry['coordinates'][0])

    #             if polygon.contains(point):
    #                 sites.find_one_and_delete({"username": self.user})