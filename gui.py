import tkinter as tk
import time
from main import World, GRID_HEIGHT, GRID_WIDTH, Body

WIDTH = 800
HEIGHT = 600
CELL_SIZE = 20
FPS_REFRESH_RATE = 1 # second
CELL_COLOR = '#2f2f2f'
BODY_COLORS = {body: color for body, color in zip(Body, (
    '#f5f5f5', '#00FFFF', '#0000FF', '#9b30ff', '#ffc0cb', '#ff0000', '#FFA500', '#FFFF00', '#00FF00', '#000000'
))}

class App:
    """
    Controls the GUI for the simulation.
    `self.root` is the `tk.Tk()` instance.
    """

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
        """
        Starts the simulation by instantiating a new `World`.
        The left side of the simulation displays the simulated environment.
        The right side of the screen contains a button to calculate the next frame and
        will display other information about the simulation.
        """
        self.world = World()

        # new frame for after pushing the start button
        start_screen_frame = tk.Frame(
            self.main_frame, width=800, height=600, bg='#ffffff')
        self.canvas = tk.Canvas(start_screen_frame, width=800,
                           height=600, bg='gray')
        self.canvas.pack()

        update_button = tk.Button(self.canvas, text="Update", command=self.update_button_command,
                        width=30, height=2, bg="#5189f0", fg="#FFFFFF", activebackground="#5C89f0")
        update_button.place(relx=0.8, rely=0.5, anchor=tk.CENTER)

        for i, color in enumerate(("blue", "red", "orange", "green", "white")):
            self.canvas.create_text(550, 20 * i + 30, text="Live information will go here",
                font=('Times', 16), fill=color)

        self.grid = []
        for y in range(GRID_HEIGHT):
            self.grid.append([])
            for x in range(GRID_WIDTH):
                _x, _y = CELL_SIZE * (x + 1), CELL_SIZE * (y + 1)
                self.grid[y].append(self.canvas.create_rectangle(_x, _y, _x + CELL_SIZE, _y + CELL_SIZE))

        self.show_screen(start_screen_frame)
        self.render()

    def update_button_command(self):
        """
        When the `update` button is clicked, simulate the next frame in the simulation.
        When the simulation changes between day and night, change the color of the GUI to reflect that.
        """
        self.world.update()
        if self.world.sun.is_day:
            self.canvas.configure(bg='white')
        else:
            self.canvas.configure(bg='black')
        self.render()

    def load_button_command(self):
        print("Load button command")

    def about_button_command(self):
        print("About button command")

    def color_cell(self, x, y, color):
        """
        Changes the cell given by `x` and `y` to the given `color`.
        """
        self.canvas.itemconfigure(self.grid[y][x], fill = color)

    def render(self):
        """
        Changes the color of each cell to display that it's empty of contains an organism.
        The color of an organism is determined by its `body` trait.
        If the organism is asleep, its color appear darker.
        """
        for x in range(GRID_WIDTH):
            for y in range(GRID_HEIGHT):
                cell = self.world.grid[y][x]
                if cell:
                    color = BODY_COLORS[cell[0].genome.phenotype[Body]]
                    if cell[0].awake:
                        self.color_cell(x, y, color)
                    else:
                        self.color_cell(x, y, darken_color(color))
                else:
                    self.color_cell(x, y, CELL_COLOR)

def darken_color(hex_color):
    """Darken hex color"""
    hex_color = hex_color.removeprefix('#')
    value = int(hex_color, 16)
    new_value = (value & 0xfefefe) >> 1
    new_color = f"#{hex(new_value).removeprefix('0x').ljust(6, '0')}"
    return new_color

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    
    start, counter = time.time(), 0

    while True:
        root.update_idletasks()
        root.update()

        if False:
            counter += 1
            current = time.time()
            elapsed = current - start
            if elapsed > FPS_REFRESH_RATE:
                print("FPS: ", counter / elapsed)
                counter = 0
                start = current
