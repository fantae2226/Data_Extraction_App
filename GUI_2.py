import tkinter as tk 
from tkinter import ttk 
from tkinter import filedialog
import cv2
import numpy as np 
from PIL import Image, ImageTk, ImageEnhance
from enum import Enum

class MyApp:
    def __init__(self):
        self.window = tk.Tk()
        self.window.geometry('1000x800')
        self.window.minsize(width=800,height=600)
        self.window.title('Test App')

        #Create main window grid
        self.window.columnconfigure(0, weight=1)
        self.window.columnconfigure(1, weight=10)
        self.window.rowconfigure(0,weight=1)

        #Create Menus frame
        self.menu_btn_frame = ttk.Frame(self.window, relief='solid')
        self.menu_btn_frame.grid(column=0, row=0, sticky='nsew')

        #Set uo menu frame grid
        self.menu_btn_frame.columnconfigure(0,weight=1)
        self.menu_btn_frame.rowconfigure(0,weight=1)
        self.menu_btn_frame.rowconfigure(1,weight=1)
        self.menu_btn_frame.rowconfigure(2,weight=1)
        self.menu_btn_frame.rowconfigure(3,weight=1)
        self.menu_btn_frame.rowconfigure(4, weight=4)
        

        #Create menu buttons
        self.home_btn = ttk.Button(self.menu_btn_frame, text='Home', command= lambda: self.main_notebook.select(0))
        self.files_btn = ttk.Button(self.menu_btn_frame, text='Files', command= lambda: self.main_notebook.select(1))
        self.process_btn = ttk.Button(self.menu_btn_frame, text='Process', command= lambda: self.main_notebook.select(2))
        self.modify_btn = ttk.Button(self.menu_btn_frame, text='Modify', command= lambda: self.main_notebook.select(3))
        self.empty_space = ttk.Label(self.menu_btn_frame, text='')

        self.home_btn.grid(column=0, row=0, sticky='nsew', pady=50, padx=25)
        self.files_btn.grid(column=0, row=1, sticky='nsew', pady=50, padx=25)
        self.process_btn.grid(column=0, row=2, sticky='nsew', pady=50, padx=25)
        self.modify_btn.grid(column=0, row=3, sticky='nsew', pady=50, padx=25)
        self.empty_space.grid(column=0, row=4, sticky='nsew', pady=25, padx=25)

        #Hide all notebook tabs with style
        hide_tabs = ttk.Style()
        hide_tabs.layout('Tabless.TNotebook.Tab',[])

        #Create notebook frame
        self.main_notebook = ttk.Notebook(self.window, style='Tabless.TNotebook')
        self.main_notebook.grid(column=1,row=0, sticky='nsew')

        # tab_style = ttk.Style()
        # tab_style.configure('Custom.TFrame', background = 'blue')

        #Create main tabs for notebook 
        self.home_tab = Home_Tab(self.main_notebook)
        self.main_notebook.add(self.home_tab, text='Home Tab')

        self.files_tab = Files_Tab(self.main_notebook)
        self.main_notebook.add(self.files_tab, text='Files Tab')

        self.processing_tab = Process_Tab(self.main_notebook)
        self.main_notebook.add(self.processing_tab, text='Process Tab')

        self.modifications_tab = Modify_Tab(self.main_notebook)
        self.main_notebook.add(self.modifications_tab, text='Modify Tab')



    def run_app(self):
        self.window.mainloop()

    pass

#This class will handle all the main widgets contained within the Home tab
class Home_Tab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.file_label = ttk.Label(self, text='This is a class test for home')
        self.file_label.pack()




#This class will handle all the main widgets contained within the Files tab 
class Files_Tab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.file_label = ttk.Label(self, text='This is a class test for files')
        self.file_label.pack()

        #Add parent parameter here so image canvas can access the operating system
        self.parent = parent

        #Image handler class initialized here
        self.image_handler = ImageHandler()

        #Frame to contain the base image selection and info
        self.base_img_frame = ttk.Frame(self)
        self.base_img_frame.pack()

        #Initialize image into image canvas using this button
        self.add_image_btn = ttk.Button(self.base_img_frame, text='Select Img File', command=self.on_add_image)
        self.add_image_btn.pack()

        self.path_name = tk.StringVar()
        self.path_label = ttk.Label(self.base_img_frame, textvariable=self.path_name, font='Calibri 14')
        self.path_label.pack()

        #This frame contains the image canvas and all the widgets that directly control it
        self.image_container = ttk.Frame(self)
        self.image_container.pack()

        self.image_canvas = Image_Canvas(self.image_container, self, parent.master, highlightthickness=2, width=800, height=600, background = 'red')
        self.image_canvas.pack(fill=tk.BOTH, expand=True)

        #Draw and move buttons for image
        self.move_btn = ttk.Button(self.image_container, text='Move', command= lambda: self.image_canvas.set_mode(Mode.MOVE))
        self.move_btn.pack(side='left')

        self.draw_btn = ttk.Button(self.image_container, text='Draw', command= lambda: self.image_canvas.set_mode(Mode.DRAW))
        self.draw_btn.pack(side='right')

        self.clear_btn = ttk.Button(self.image_container, text='Clear', command= lambda: self.image_canvas.clear_canvas())
        self.clear_btn.pack()

    def on_add_image(self):
        img = self.image_handler.open_image()
        print('Img path: ', self.image_handler.image_path)
        self.path_name.set(self.image_handler.image_path)
        self.image_canvas.add_image(img)
        
#This class will handle all the main widgets contained within the Process tab
class Process_Tab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.file_label = ttk.Label(self, text='This is a class test for process')
        self.file_label.pack()

#This class will handle all the main widgets contained within the Modify tab
class Modify_Tab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.file_label = ttk.Label(self, text='This is a class test for modify')
        self.file_label.pack()



class ImageHandler:

    def __init__(self):
        self.original_img = None
        self.current_img = None
        self.zoom_level = 1
        self.image_path = None

    def open_image(self):
        filepath = filedialog.askopenfilename()
        if not filepath:
            print('No file path')
        
        self.image_path = filepath
        print(self.image_path)

        self.original_img = Image.open(filepath)
        self.original_img = self.img_enhancer(self.original_img)
        return ImageTk.PhotoImage(self.original_img)
    
    def set_image(self, image_path):
        self.original_img = Image.open(image_path)
        self.original_img = self.img_enhancer(self.original_img)
        self.current_img = self.original_img.copy()
    
    def get_current_img(self):
        return self.current_img
    
    def get_tk_img(self):
        return ImageTk.PhotoImage(self.current_img)

    def img_enhancer(self, image):
        contrast = ImageEnhance.Contrast(image)
        image = contrast.enhance(2.5)

        brightness = ImageEnhance.Brightness(image)
        image = brightness.enhance(1.2)

        sharpness = ImageEnhance.Sharpness(image)
        image = sharpness.enhance(2.0)

        return image 
    
    def zoom(self, factor):
        self.zoom_level *= factor
        new_width = int(self.original_img.width * self.zoom_level)
        new_height = int(self.original_img.height * self.zoom_level)

        self.current_img = self.original_img.resize((new_width,new_height), Image.LANCZOS)

class Mode(Enum):
    MOVE = 1
    DRAW = 2

class Image_Canvas(tk.Canvas):

    def __init__(self, master, app, main_app, **kwargs):
        self.app = app
        self.main_app = main_app
        super().__init__(master=master, **kwargs)
        #Initialize key coordinates
        self.start_x = 0
        self.start_y = 0
        self.end_x = 0
        self.end_y = 0

        #Img vars
        self.img_id = None 

        #Img tk reference to prevent it from being garbage collected
        self.tk_img = None

        #Initialize box...I know writing this is redundant but this code is a mess at this point
        self.box = None

        #Initialize default mode
        self.mode = self.set_mode(Mode.MOVE)
        
       

        #initialize all mandatory keybindings
        self.bind("<Configure>", self.on_resize)
        self.bind_all("<MouseWheel>", self.on_mousewheel) #Windows and Max binds
        self.bind("<Button-4>", self.on_mousewheel) #Linux up bind
        self.bind("<Button-5>", self.on_mousewheel) #Linux down bind


    def set_mode(self, mode):
        self.mode = mode
        if self.mode == Mode.MOVE:
            self.bind("<ButtonPress-1>", self.on_button_press)
            self.bind("<B1-Motion>", self.on_move_press)
            self.unbind("<ButtonRelease-1>")

            if self.box:
                self.delete(self.box)
        if self.mode == Mode.DRAW:
            self.bind("<ButtonPress-1>", self.on_draw_press)
            self.bind("<B1-Motion>", self.on_draw_move)
            self.bind("<ButtonRelease-1>", self.on_draw_release)
    
    def on_button_press(self, event):
        self.scan_mark(event.x, event.y)
    
    def on_move_press(self, event):
        self.scan_dragto(event.x, event.y, gain=1)
    
    def on_draw_press(self, event):
        self.start_x = self.canvasx(event.x)
        self.start_y = self.canvasy(event.y)

    def on_draw_move(self, event):
        self.end_x = self.canvasx(event.x)
        self.end_y = self.canvasy(event.y)

        if self.box:
            self.delete(self.box)
        
        self.box = self.create_rectangle(self.start_x, self.start_y,
                                         self.end_x, self.end_y)
    
    def on_draw_release(self, event):
        zoom = self.app.image_handler.zoom_level
        start_x = self.start_x / zoom
        start_y = self.start_y / zoom
        end_x = self.end_x /zoom 
        end_y = self.end_y / zoom 

        print(f"Region Coords: Start_x:{start_x}, Stary_y:{start_y}, End_x:{end_x}, End_y:{end_y}")

    def on_resize(self, event):
        if self.app.image_handler.get_current_img() is not None:
            self.config(scrollregion=self.bbox('all'))

    def on_mousewheel(self, event):
        
        if self.img_id:
            factor = 1
            system = self.main_app.tk.call('tk', 'windowingsystem')

            if system == 'win32': #Windows sys
                print("windows works")
                factor = 1.1 if event.delta > 0 else 0.9
            elif system == 'aqua': #MacOs system
                factor = 1.1 if event.delta < 0 else 0.9  
                print('Mac Works')
            else: #Unix System
                if event.num == 4: #Scroll up on Unix
                    factor = 1.1
                    print("Unix works up")
                elif event.num == 5: #Scroll down on Unix
                    factor = 0.9
                    print('Unix works down')    

            self.app.image_handler.zoom(factor)
            self.tk_img = self.app.image_handler.get_tk_img()
            self.itemconfig(self.img_id, image = self.tk_img)
            self.config(scrollregion=(0,0, self.tk_img.width() , self.tk_img.height()))   #


    def add_image(self, tk_img):
        self.delete('all')

        self.tk_img = tk_img

        self.img_id = self.create_image(0,0, image=self.tk_img, anchor = 'nw')
     
        self.config(scrollregion=(0,0, self.tk_img.width(), self.tk_img.height())) #, tk_img.width, tk_img.height
    
    def clear_canvas(self):
        self.delete('all')
        self.img_id = None 
        self.app.image_handler.image_path = None

app = MyApp()
app.run_app()