import tkinter as tk
import time
from main import World

WIDTH = 800
HEIGHT = 600
FPS_REFRESH_RATE = 1 # second

class App:
    def __init__(self, root):
        self.root = root
        root.title("A-Life Challenge")

        # window size
        screenwidth = root.winfo_screenwidth()
        screenheight = root.winfo_screenheight()
        alignstr = '%dx%d+%d+%d' % (WIDTH, HEIGHT,
                                    (screenwidth - WIDTH) / 2, (screenheight - HEIGHT) / 2)
        root.geometry(alignstr)
        root.resizable(width=False, height=False)

        # create frames for screens
        self.main_frame = tk.Frame(root, width=800, height=600, bg='#ffffff')
        self.button_frame = tk.Frame(
            self.main_frame, width=250, height=200, bg='#3E3E3E')

        # dynamic coordinates
        canvas_center_x = WIDTH / 2
        canvas_center_y = HEIGHT / 2

        # canvas for buttons
        button_canvas = tk.Canvas(
            self.button_frame, width=250, height=200, bg='#00ff00', highlightthickness=0)
        button_canvas.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        # buttons on the button canvas
        start_button = tk.Button(button_canvas, text="Start", command=self.start_button_command,
                                 width=30, height=2, bg="#5189f0", fg="#FFFFFF", activebackground="#5C89f0")
        start_button.place(relx=0.5, rely=0.2, anchor=tk.CENTER)

        load_button = tk.Button(button_canvas, text="Load", command=self.load_button_command,
                                width=30, height=2, bg="#5189f0", fg="#FFFFFF", activebackground="#5C89f0")
        load_button.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        about_button = tk.Button(button_canvas, text="About", command=self.about_button_command,
                                 width=30, height=2, bg="#5189f0", fg="#FFFFFF", activebackground="#5C89f0")
        about_button.place(relx=0.5, rely=0.8, anchor=tk.CENTER)

        # label box
        self.label = tk.Label(self.main_frame, text="This is a little blurb about the simulation", font=('Times', 14),
                              fg="#000000")
        self.label.place(x=canvas_center_x - 167, y=20, width=335, height=93)

        # show the initial screen
        self.show_screen(self.button_frame)

    def show_screen(self, screen_frame):
        # hide other screen and display selected one
        self.button_frame.pack_forget()
        self.main_frame.pack_forget()
        screen_frame.pack(fill=tk.BOTH, expand=True)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

    def start_button_command(self):
        self.world = World()

        # new frame for after pushing the start button
        start_screen_frame = tk.Frame(
            self.main_frame, width=800, height=600, bg='#ffffff')
        canvas = tk.Canvas(start_screen_frame, width=800,
                           height=600, bg='#2f2f2f')
        canvas.pack()

        update_button = tk.Button(canvas, text="Update", command=self.update_button_command,
                        width=30, height=2, bg="#5189f0", fg="#FFFFFF", activebackground="#5C89f0")
        update_button.place(relx=0.8, rely=0.5, anchor=tk.CENTER)

        for i, color in enumerate(("blue", "red", "orange", "green", "white")):
            canvas.create_text(550, 20 * i + 30, text="Live information will go here",
                font=('Times', 16), fill=color)

        # text display for the world state
        self.output_box = tk.Text(self.main_frame, wrap=tk.WORD, width=50,
                                  height=30, bg='#3E3E3E', fg='#FFFFFF', font=('Times', 12))
        self.output_box.place(relx=0.01, rely=0.01, anchor=tk.NW)

        # update text and show new frame
        self.update_output_box()
        self.show_screen(start_screen_frame)

    def update_button_command(self):
        print("update")
        self.world.update()
        self.render()

    def load_button_command(self):
        print("Load button command")

    def about_button_command(self):
        print("About button command")

    def update_output_box(self):
        # clear the output box
        self.output_box.delete(1.0, tk.END)
        self.render()

    def render(self):
        self.output_box.delete(1.0, tk.END)
        self.output_box.insert(tk.END, str(self.world))

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    
    start, counter = time.time(), 0

    while True:
        root.update_idletasks()
        root.update()

        counter += 1
        current = time.time()
        elapsed = current - start
        if elapsed > FPS_REFRESH_RATE:
            print("FPS: ", counter / elapsed)
            counter = 0
            start = current

