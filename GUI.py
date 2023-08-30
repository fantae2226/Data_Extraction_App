import tkinter as tk
import cv2
import numpy as np
from tkinter import filedialog
from PIL import Image, ImageTk, ImageEnhance
from Extraction_Algorithm import capture_region, preprocessing



class App:
    def __init__(self) -> None:
        
        self.current_btn = None
        self.current_pg = None
        self.file_lb = None
        self.original_img = None
        self.tk_img = None
        self.img_label = None
        self.image_canvas = None
        self.root = tk.Tk()
        self.root.geometry('1000x800')
        self.root.title('License Extraction')

        self.container = tk.Frame(self.root)
        self.container.pack(fill='both', expand=True)

        self.container.grid_columnconfigure(0, weight=0)
        self.container.grid_columnconfigure(1, weight=1)
        self.container.grid_rowconfigure(0,weight=1)

        self.options_frame = tk.Frame(self.container, bg='#c3c3c3')
        self.options_frame.grid(row=0, column=0, sticky='nsew')

        self.options_frame.grid_rowconfigure(0, weight=1)
        self.options_frame.grid_rowconfigure(1,weight=1)
        # self.options_frame.pack(side=tk.LEFT, fill=tk.Y)
        # self.options_frame.pack_propagate(False)
        # self.options_frame.configure(width=100)
        
        self.button_frame = tk.Frame(self.options_frame, bg='#c3c3c3')
        self.button_frame.grid(row=0, column=0, sticky='nsew')
       
        self.home_btn = self.make_btn(self.button_frame,'Home', '#158aff', 2, '#c3c3c3', 0, 0)
        self.files_btn = self.make_btn(self.button_frame,'Files', '#158aff', 2, '#c3c3c3', 1, 0)

        #Set buttons to weight 0 so they stay the same size
        self.button_frame.grid_rowconfigure(0,weight=0)
        self.button_frame.grid_rowconfigure(1,weight=0)

        #Set everthin else to weight 1 so it expands with window
        self.button_frame.grid_rowconfigure(2,weight=1)
        self.button_frame.grid_columnconfigure(0,weight=1)

        self.main_frame = tk.Frame(self.container, highlightbackground='black',highlightthickness=2, bg='#4e6096')
        # self.main_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        # self.main_frame.pack_propagate(False)
        self.main_frame.grid(row=0,column=1, sticky='nsew')

        # self.main_frame.grid_rowconfigure(0, weight=1)
        # self.main_frame.grid_columnconfigure(1,weight=1)

        # self.root.grid_columnconfigure(1, weight=1)
        # self.root.grid_rowconfigure(0,weight=1)

        self.indicate(None, 'Home')
    
    def run(self):
        self.root.mainloop()

    def indicate(self, lb, txt):
        #global current_btn, current_pg
        if self.current_btn:
            self.current_btn.config(bg='#c3c3c3')
        if self.current_pg:
            self.current_pg.pack_forget()
        if lb:
            lb.config(bg='#158aff')
        self.current_btn = lb
        self.current_pg = self.page(txt)
        
    def enhance_img(self, image):
        contrast = ImageEnhance.Contrast(image)
        image = contrast.enhance(2.5)

        brightness = ImageEnhance.Brightness(image)
        image = brightness.enhance(1.2)

        sharpness = ImageEnhance.Sharpness(image)
        image = sharpness.enhance(2.0)

        return image

    def open_file(self):
        #global file_lb, original_img, image_canvas
        filepath = filedialog.askopenfilename()
        self.file_lb.config(text=filepath)

        self.original_img = Image.open(filepath)
        self.original_img = self.enhance_img(self.original_img)

        if self.image_canvas is not None:
            self.image_canvas.original_img = None
            self.image_canvas.add_image(self.original_img, ImageTk.PhotoImage(self.original_img))



    def page(self, txt):
        #global file_lb, img_label, image_canvas
        home_frame = tk.Frame(self.main_frame, bg='#4e6096')

        lb = tk.Label(home_frame, text=f'{txt} Page \n\n This is a test', font=('Bold', 30), bg='#4e6096')
        lb.pack()

        if txt == 'Files':
            open_btn = tk.Button(home_frame, text='Select File',bg='#6f7382', command=self.open_file)
            open_btn.pack()

            self.file_lb = tk.Label(home_frame, text="",bg='#4e6096')
            self.file_lb.pack()

            move_btn = tk.Button(home_frame, text='Move', bg='#6f7382',command=lambda: self.image_canvas.set_mode('Move'))
            move_btn.pack(side=tk.BOTTOM)

            draw_btn = tk.Button(home_frame, text='Draw',bg='#6f7382', command=lambda: self.image_canvas.set_mode('Draw'))
            draw_btn.pack(side=tk.BOTTOM)

            self.img_label = tk.Label(home_frame, image=None)
            self.img_label.pack()

            self.image_canvas = ImageCanvas(home_frame, self, highlightthickness=2, width=800, height=600)
            self.image_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

            scroll_x = tk.Scrollbar(home_frame, orient='horizontal',bg='#6f7382', command=self.image_canvas.xview)
            scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
            self.image_canvas.configure(xscrollcommand=scroll_x.set)
            scroll_y = tk.Scrollbar(home_frame, orient='vertical',bg='#6f7382', command=self.image_canvas.yview)
            scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
            self.image_canvas.configure(yscrollcommand=scroll_y.set)


        # home_frame.pack(pady=20)
        home_frame.grid(row=0,column=1, sticky='nsew', padx=20,pady=20)
        return home_frame

    #Worthless method, delete later
    def make_btn(self, frame, txt, foreground, border, background, row, col):
        #global current_btn
        text = txt
        # label = tk.Label(frame,text='', bg=background)
        # label.place(x=x_pos-7, y=y_pos, width=5, height=40)
        btn = tk.Button(frame, text=txt, font=('Bold', 15), fg=foreground, bd=border, bg=background, command=lambda: self.indicate(btn, text))
        btn.grid(row=row,column=col, sticky='nsew', padx=10, pady=10)
        return btn


# self.root = tk.Tk()



# indicate(None, 'Home')
# home_frame = page('Home')
# self.root.mainloop()






class ImageCanvas(tk.Canvas):
    def __init__(self, master, app, **kwargs):
        self.app = app
        super().__init__(master=master, **kwargs)
        # tk.Canvas.__init__(self, master=master, **kwargs)
        # self.bind("<ButtonPress-1>", self.on_button_press)
        # self.bind("<B1-Motion>", self.on_move_press)
        self.bind("<Configure>", self.on_resize)
        self.bind_all("<MouseWheel>", self.on_mousewheel) #For Windows and MacOs
        self.bind("<Button-4>", self.on_mousewheel) #For Linux Up
        self.bind("<Button-5>", self.on_mousewheel) # For Linux Down

        self.img = None
        self.img_id  = None
        self.start_x = 0
        self.start_y = 0
        self.end_x = 0
        self.end_y = 0
        self.box = None
        self.mode = 'Move' #Defailt mode
        self.zoom_level = 1
        self.original_img = None
        self.regions_captured = None

    def set_mode(self, mode):
        self.mode = mode
        if self.mode == 'Move':
            self.bind("<ButtonPress-1>", self.on_button_press)
            self.bind("<B1-Motion>", self.on_move_press)
            self.unbind("<ButtonRelease-1>")
            if self.box:
                self.delete(self.box)  
        elif self.mode == 'Draw':
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
        start_x = self.start_x / self.zoom_level
        start_y = self.start_y / self.zoom_level
        end_x = self.end_x / self.zoom_level
        end_y = self.end_y / self.zoom_level
        print(f"Region Co-ords: ({start_x}, {start_y}), ({end_x}, {end_y})")
        np_img = np.array(self.original_img)

        if len(np_img.shape) == 2:
            cv2_img = np_img
        elif np_img.shape[2] == 3:
            cv2_img = cv2.cvtColor(np_img, cv2.COLOR_BGR2GRAY)
        else:
            raise ValueError("Unexpected Image Shape")
        captured_text = capture_region(cv2_img[int(start_y):int(end_y), int(start_x):int(end_x)])
        self.regions_captured = len(captured_text)
        self.label_regions_captured()
        print(captured_text)
        print(f"You have {len(captured_text)} Text Regions")
    
    def label_regions_captured(self):
        text_frame = tk.Frame(self.app.main_frame, bg='#4e6096')
        # text_frame.pack(side=tk.RIGHT, fill=tk.Y)
        text_frame.grid(row=0, column=2, sticky='nsew')

        text_frame.grid_columnconfigure(0,weight=1)
        text_frame.grid_rowconfigure(0,weight=1)

        region_labels = [None] * self.regions_captured
        
        for text_box in range(len(region_labels)):
            region_labels[text_box] = tk.Text(text_frame, height=1, width=30)
            region_labels[text_box].grid(row=text_box, column=0, pady=10)
        pass

    def on_resize(self, event):
        if self.img is not None:
            self.config(scrollregion=self.bbox('all'))

    def on_mousewheel(self, event):
        print(f"Event delta: {event.delta}, Event num: {event.num}")
        factor = 1
        system = self.app.root.tk.call('tk', 'windowingsystem')

        if system == 'win32': #Windows system
            print('Windows works')
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

        print(f"System: {system}, Factor: {factor}, Zoom level before: {self.zoom_level}")
        self.zoom_level *= factor
        print(f"Zoom level after: {self.zoom_level}")
        new_width = int(self.original_img.width * self.zoom_level)
        new_height = int(self.original_img.height * self.zoom_level)

        self.img = self.original_img.resize((new_width,new_height), Image.LANCZOS)
        self.img_tk = ImageTk.PhotoImage(self.img)
        self.itemconfig(self.img_id, image = self.img_tk)
        self.config(scrollregion=(0, 0, self.img.width, self.img.height))

    def add_image(self, img, img_tk):
        self.delete('all')
        self.img = img
        self.img_tk = img_tk  
        self.img_id = self.create_image(0,0, image=self.img_tk, anchor='nw')
        if self.original_img is None:
            self.original_img = img.copy()
        self.config(scrollregion=(0,0, self.img.width, self.img.height))

app = App()
app.run()