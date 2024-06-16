# Application Name: BMI Calculator
# Programmer Name: Anwar Ansari
# Date Modified: 16/06/2024
# Time-Duration: 3 days

# importing Necessary libraries
from PIL import Image
from tkinter import messagebox as msg, ttk, END
from customtkinter import *
import mysql.connector as mysql
from numpy import linspace
import matplotlib.pyplot as plot
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Creating a connection with database
db = mysql.connect(host='localhost', user='newroot', port=3306) # For localhost
# db = mysql.connect(host='SG-sand-slug-8025-8915-mysql-master.servers.mongodirector.com', user='sgroot', password='28^D8BZ9Bk0O1Tym', port=3306) # For online Database

# Creating the Main class of the program
class BMI_Calc(CTk):
    # Size of windows
    win_width, win_height = 600, 500

    def __init__(self):
        super().__init__()
        self.geometry(f"{self.win_width}x{self.win_height}") # Size of tkinter Window
        self.title("BMI Calculator")  # Title of the Application
        self.resizable(0, 0) # Window would not be resizeable
        self._set_appearance_mode(mode_string="Dark")
        self.wm_iconbitmap(r"Bin\CalcLogo2.ico")

        # Max and Min size of Window
        self.maxsize(self.win_width, self.win_height)
        self.minsize(self.win_width, self.win_height)
        
        # Creating Variables for storing the user inputs
        self.Gen, self.unit, self.theme = StringVar(), StringVar(), StringVar()
        self.Gen.set("Male")
        self.unit.set("Metric")
        self.theme.set("Dark")

        self.setElement()
        self.query = db.cursor()
        # Creating database if not exists for localhost:
        self.query.execute('show databases;')
        if ('bmi_database',) not in self.query.fetchall():
            self.query.execute('create database bmi_database;')

        # For online database;
        # self.query.execute('create database BMI_Database;')
        # Creating table if not exists
        self.query.execute('use BMI_Database;')
        self.query.execute('show tables;')
        if ('bmi_data',) not in self.query.fetchall():
            self.query.execute('create table BMI_Data (Id int not null AUTO_INCREMENT primary key, Time_Stamp timestamp Default(Current_TimeStamp), UserName varchar(30) not null, Age int not null, weight double not null, height double not null, unit varchar(10) not null, gender varchar(10) not null, bmi double not null);')

        # On closing the main windows the mainloop should be stopped
        self.protocol('WM_DELETE_WINDOW', self.quit)

    # Method to set required elements
    def setElement(self):
        # Creating label to display image
        CTkLabel(self, text="", image=CTkImage(Image.open("Bin/CalcText.png"), size=(400, 150))).place(x=130, y=0)
        CTkLabel(self, text="", image=CTkImage(Image.open("Bin/CalcLogo.png"), size=(50, 50))).place(x=100, y=50)
        # Creating Entry and Label for getting user inputs
        try:
            self.createLabel('Name:', 50, 150)
            self.UName = self.createEntry("Enter your name:", 50, 180)
            self.createLabel('Age::', 350, 150)
            self.Age = self.createEntry("Enter your age:", 350, 180)
            self.createLabel('Weight:', 50, 230)
            self.weight = self.createEntry("Enter your weight(Kg):", 50, 260)
            self.createLabel('Height:', 350, 230)
            self.height = self.createEntry("Enter your height(cm):", 350, 260)
        except Exception:
            pass
        # Creating Drop Dwon, Buttons and their Label
        self.createLabel('Gender:', 50, 310)
        CTkOptionMenu(self, 200, 30, 5, variable=self.Gen, fg_color="#05b4ea", values=["Male", "Female", "Other"], dropdown_fg_color="#05b4ea").place(x=50, y=340)
        CTkButton(self, command=self.Submit, text="", corner_radius=55, fg_color="transparent", hover=False, image=CTkImage(Image.open("bin/CalcBtn.png"), size=(220, 50))).place(x=320, y=320)
        self.createLabel('Unit:', 50, 390)
        CTkOptionMenu(self, 200, 30, 5, variable=self.unit, fg_color="#05b4ea", values=["Metric", "US Unit"], dropdown_fg_color="#05b4ea", command=lambda text: self.click(text)).place(x=50, y=420)
        CTkButton(self, command=self.History, text="", corner_radius=55, fg_color="transparent", hover=False, image=CTkImage(Image.open("bin/History.png"), size=(210, 50))).place(x=330, y=400)
        CTkButton(self, command=self.About, text="", corner_radius=55, fg_color="transparent", hover=False, image=CTkImage(Image.open("bin/About.png"), size=(30, 30))).place(x=0, y=0)
        CTkOptionMenu(self, 100, 30, 5, variable=self.theme, fg_color="#282828", values=["Dark", "Light"], command=lambda text: self.Change(text)).place(x=500, y=0)

    # Method to select unit from drop down
    def click(self, text):
        if self.unit.get() == "US Unit":
            self.weight.configure(placeholder_text="Enter your weight(pounds):")
            self.height.configure(placeholder_text="Enter your height(Feets.Inches):")
        else:
            self.weight.configure(placeholder_text="Enter your weight(kg):")
            self.height.configure(placeholder_text="Enter your height(cm):")

    # Method ot change appearance mode from the select item of drop down
    def Change(self, text):
        self._set_appearance_mode(self.theme.get())
        if self.theme.get() == "Dark":
            for widget in self.winfo_children():
                widget.configure(bg_color="#242424")
                if str(widget)[:-1].endswith("label"):
                    widget.configure(text_color="white")
                if str(widget).endswith("menu3"):
                    widget.configure(fg_color="#242424", text_color="white")
        elif self.theme.get() == "Light":
            for widget in self.winfo_children():
                if str(widget)[:-1].endswith("label"):
                    widget.configure(text_color="black")
                if str(widget).endswith("menu3"):
                    widget.configure(fg_color="#ebebeb", text_color="black")
                
                widget.configure(bg_color="#ebebeb")

    # Method to create Entry
    def createEntry(self, placeholder, x, y):
        entry = CTkEntry(self, 201, 30, 5, text_color="white", placeholder_text=placeholder, placeholder_text_color="white", fg_color="#05b4ea")
        entry.place(x=x, y=y)
        return entry
    
    # Method to create Label
    def createLabel(self, text, x, y):
        CTkLabel(self, text=text).place(x=x, y=y)

    # Method to submit the data into the databse and perform required operations
    def Submit(self):
        try:
            # All fields mandatory validation
            if self.UName.get()=="" or self.Age.get()=="" or self.weight.get()=="" or self.height.get()=="" or self.Gen.get()=="":
                raise MissingDetailsException("Details are Missing!")
            self.name, self.age, self.Weight, self.Height, self.gen, self.Unit= self.UName.get(), int(self.Age.get()), float(self.weight.get()), float(self.height.get()), self.Gen.get(), self.unit.get()
            # Logic for calculating BMI
            if self.Unit == "Metric":
                self.bmi = self.Weight / ((self.Height/100)**2)
            else:
                self.bmi = 703 * (self.Weight / ((self.Height)**2))
            
            # Inserting the data into table
            self.query.execute(f"insert into BMI_Data (UserName, Age, weight, height, unit, gender, bmi) values('{self.name}', {self.age}, {self.Weight}, {self.Height}, '{self.Unit}', '{self.gen}', {self.bmi});")
            db.commit()

            # Method to for displaying Graph
            visual = Visualization()
            visual.Graph(self.bmi)
        except MissingDetailsException:
            msg.showwarning("Some Details are not filled", "Please! Fill all the required fields!")
        except ValueError as e:
            msg.showwarning("Some Details are not correct", "Please! Fill valid details!")
    
    # Method to Show History Record from the database
    def History(self):
        Visual = Visualization()
        Visual.Histroy()

    # Method to show about section
    def About(self):
        msg.showinfo("About Me", "A BMI Calculator by Anwar Ansari\nEmail: stark.97861@gmail.com\nLinkedIn: https://www.linkedin.com/in/anwar-ansari-84b07a24a/\nGithub: https://github.com/Anwar1094")

# Class for display Graph and History
class Visualization(CTkToplevel):
    win_width, win_height = 960, 500
    # Creating data points for arrow
    data = {}
    x = 3.14
    for i in linspace(0, 60, 60):
        x -= 0.05
        data[str(i)[:str(i).index(".")]] = x

    def __init__(self, *args, **kwags):
        super().__init__(*args, **kwags)
        self.geometry(f"{self.win_width}x{self.win_height}")
        # Removing default Titlebar
        self.overrideredirect(True)
        # Creating a fake Titlebar
        title_bar = CTkFrame(self, width=1535, height=30, bg_color="black", border_width=1)
        title_bar.place(x=0, y=0)
        CTkLabel(title_bar, text="", image=CTkImage(Image.open("Bin/Calc..png"), size=(20,20))).place(x=5, y=0)
        CTkButton(title_bar, command=self.back, fg_color="transparent", width=15, hover_color="black", text="", image=CTkImage(Image.open("Bin/Close.png"), size=(18,18))).place(x=1500, y=0)
        CTkLabel(title_bar, text="BMI Calculator", font=("Lucida Handwriting", 12), text_color="white").place(x=30, y=0)

    # Method for creating graph
    def Graph(self, bmi):
        self.state('zoomed')
        import numpy as np
        colors = ["red", "yellow", "green", "skyblue"]
        values = ["", 40, 25, 18.5, 0]
        CTkLabel(self, text="", image=CTkImage(Image.open("Bin/White.jpg"), size=(1535,300))).place(x=0, y=30)
        CTkLabel(self, text="", fg_color="transparent", image=CTkImage(Image.open("Bin/BMILogo.jpg"), size=(800,200))).place(x=450,y=30)
        try:
            # Creating a Figure
            self.fig = plot.figure(num=101, figsize=(20, 10), frameon=False)
            ax = self.fig.add_subplot(projection="polar") # Creating polar axises in the Figure
            self.canvas = FigureCanvasTkAgg(self.fig, self) #Creating Canvas
            # Creating Axes bars
            ax.bar(x=[0, 0.79, 1.57, 2.35], width=0.79, height=0.5, bottom=2, edgecolor="white", align="edge", color=colors)
            # Labeling the Bars
            self.over = plot.annotate("OverWeight", xy=(0.2, 1.90), rotation=-70, color="white", fontweight="bold", fontsize=12)
            self.mid = plot.annotate("Mid-OverWeight", xy=(1.4, 1.80), rotation=-25, color="white", fontweight="bold", fontsize=12)
            self.norm = plot.annotate("Normal", xy=(2.1, 2.25), rotation=20, color="white", fontweight="bold", fontsize=12)
            self.under = plot.annotate("UnderWeight", xy=(2.95, 2.29), rotation=70, color="white", fontweight="bold", fontsize=12)
            plot.axis('off')
            for loc, val in zip([0, 0.79, 1.57, 2.35, 3.12], values):
                plot.annotate(val, xy=(loc, 2.5), ha="right" if val=="" or val <=20 else "left")
            # Creating Arrow
            arrow = plot.annotate(str(bmi)[:str(bmi).index(".")+3], xytext=(0,0), xy=(self.data[str(int(bmi))], 2.1),
                        arrowprops=dict(arrowstyle="wedge, tail_width=0.4", color="black", shrinkA=0),
                        bbox=dict(boxstyle="circle", facecolor="black", linewidth=2.0,),
                        fontsize=20, color="white", ha="center")
            self.canvas.get_tk_widget().place(x=0, y=300)
        except Exception as e:
            pass

    # Method to close all Windows
    def back(self):
        self.quit()

    # Method for creating History
    def Histroy(self):
        self.state('zoomed')
        self.query = db.cursor()
        # Creating Table from Treeview
        table = ttk.Treeview(self, columns=('Sr.No.', 'TimeStamp', 'Name', 'Age', 'Weight', 'Height', 'Unit', 'Gender', 'BMI'), show="headings")
        # Creating Table Headings
        table.heading('Sr.No.', text="Sr.No.")
        table.heading('TimeStamp', text="TimeStamp")
        table.heading('Name', text="Name")
        table.heading('Age', text="Age")
        table.heading('Weight', text="Weight")
        table.heading('Height', text="Height")
        table.heading('Unit', text="Unit")
        table.heading('Gender', text="Gender")
        table.heading('BMI', text="BMI")
        table.pack(fill=BOTH, expand=True, anchor=NE, pady=30)
        # Inserting data to the table from the database
        self.query.execute("select * from bmi_data;")
        for item in self.query.fetchall():
            table.insert(parent='', index=END, values=item)

# Exception class for Missing Details Validation
class MissingDetailsException(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

# Executing the Main Applications
if __name__ == "__main__":
    calc = BMI_Calc()
    calc.mainloop()
