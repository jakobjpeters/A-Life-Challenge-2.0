import os
import pickle
import tkinter as tk
import time
from main import World, GRID_HEIGHT, GRID_WIDTH, Body

WIDTH = 800
HEIGHT = 600
CELL_SIZE = 20
FPS_REFRESH_RATE = 1 # second
CELL_COLOR = '#2f2f2f'
BODY_COLORS = {body: color for body, color in zip(Body, (
    '#f5f5f5', '#00FFFF', '#0000FF', '#9b30ff', '#ffc0cb', '#ff0000', '#FFA500', '#FFF000', '#00FF00', '#000000'
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
        # root.resizable(width=False, height=False)

        # create frames for screens
        self.main_frame = tk.Frame(root, bg='#ffffff')
        self.button_frame = tk.Frame(
            self.main_frame)

        # dynamic coordinates
        canvas_center_x = WIDTH / 2
        canvas_center_y = HEIGHT / 2

        # canvas for buttons
        button_canvas = tk.Canvas(
            self.button_frame, width=250, height=200, bg='#00ff00', highlightthickness=0)
        button_canvas.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        # buttons on the button canvas
        start_button = tk.Button(button_canvas, text="Start", command=self.start_button_command,
                                 width=30, height=2)
        start_button.place(relx=0.5, rely=0.2, anchor=tk.CENTER)

        load_button = tk.Button(button_canvas, text="Load", command=self.load_button_command,
                                width=30, height=2)
        load_button.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        about_button = tk.Button(button_canvas, text="About", command=self.about_button_command,
                                 width=30, height=2)
        about_button.place(relx=0.5, rely=0.8, anchor=tk.CENTER)

        # label box
        self.label = tk.Label(self.main_frame, text="This is a little blurb about the simulation")
        self.label.place(anchor=tk.CENTER, relx=0.5, rely=0.1)

        # show the initial screen
        self.show_screen(self.button_frame)

        self.tracked_organism = None

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
        # FIXME: option to load / save worlds in GUI
        world_to_load = ''  # set None
        if world_to_load:
            with open('world.pkl', 'rb') as pkl:
                self.world = pickle.load(pkl)
        else:
            self.world = World()
            with open('world.pkl', 'wb') as pkl:
                pickle.dump(self.world, pkl)

        # new frame for after pushing the start button
        start_screen_frame = tk.Frame(
            self.main_frame, width=800, height=600, bg='#ffffff')
        self.canvas = tk.Canvas(start_screen_frame, width=800,
                           height=600)

        update_button = tk.Button(self.canvas, text="Update", command=self.update_button_command,
                        width=30, height=2)
        update_button.place(relx=0.8, rely=0.5, anchor=tk.CENTER)

        self.organism_info_area = tk.Label(self.main_frame, justify=tk.LEFT, anchor='w', font='TkFixedFont', text='Hover over organism to view details')
        self.organism_info_area.place(anchor=tk.N, relx=0.9, rely=0.0, width=500, height=200)
        self.canvas.pack()

        self.grid = []
        for y in range(GRID_HEIGHT):
            self.grid.append([])
            for x in range(GRID_WIDTH):
                _x, _y = CELL_SIZE * (x + 1), CELL_SIZE * (y + 1)
                rect = self.canvas.create_rectangle(
                    _x, _y, _x + CELL_SIZE,
                    _y + CELL_SIZE,
                    fill='',
                    outline='',                    
                )
                self.grid[y].append(rect)

                # attach callback functions to cell when its clicked or hovered
                self.canvas.tag_bind(rect, '<Enter>', lambda _, x=x, y=y: self.view_organism_details(x, y))
                self.canvas.tag_bind(rect, '<Button-1>', lambda _, x=x, y=y: self.view_organism_details(x, y, clicked=True))
                self.canvas.tag_bind(rect, '<Leave>', lambda _: self.clear_organism_details())

        self.show_screen(start_screen_frame)
        self.render()

    def update_button_command(self):
        """
        When the `update` button is clicked, simulate the next frame in the simulation.
        When the simulation changes between day and night, change the color of the GUI to reflect that.
        """
        self.world.update()
        if self.tracked_organism:
            self.organism_info_area.configure(text=str(self.tracked_organism))
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
        self.canvas.itemconfigure(self.grid[y][x], fill=color, outline='')

    def highlight_cell(self, x, y):
        """
        Give cell a cell at `x` and `y` a yellow outline.
        """
        self.canvas.itemconfigure(self.grid[y][x], outline='yellow', width=3)
        self.canvas.tag_raise(self.grid[x][y])

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
                    organism = cell[0]
                    color = BODY_COLORS[organism.genome.phenotype[Body]]
                    if organism.awake:
                        self.color_cell(x, y, color)
                    else:
                        self.color_cell(x, y, darken_color(color))
                    if organism is self.tracked_organism:
                        self.highlight_cell(x, y)
                else:
                    self.color_cell(x, y, CELL_COLOR)

    def view_organism_details(self, x, y, clicked=False):
        """
        Show details about an organism.

        When hovering over an organism, that organism's info is shown. If
        an organism is clicked, it will become "tracked" and its details
        will be shown at all times (except temporarily when hovering over
        another organism)
        """
        cell_content = self.world.cell_content(x, y)
        if cell_content:
            organism = cell_content[0]
            self.organism_info_area.configure(text=str(organism))
            if clicked:
                self.clear_tracked_organism()
                if organism is self.tracked_organism:
                    self.clear_organism_details()
                    return
                self.highlight_cell(x, y)
                self.tracked_organism = organism
        elif clicked:
            self.clear_tracked_organism()
            self.clear_organism_details()

    def clear_organism_details(self):
        """
        Clear text in `self.organism_info_area`, or show the currently
        tracked organism's info if there is one.
        """
        if self.tracked_organism:
            self.organism_info_area.configure(text=str(self.tracked_organism))
        else:
            self.organism_info_area.configure(text='')

    def clear_tracked_organism(self):
        """
        No longer track the currently tracked organism and remove its highlight.
        """
        if self.tracked_organism:
            old_loc = self.tracked_organism.get_location()
            self.canvas.itemconfigure(self.grid[old_loc[1]][old_loc[0]], outline='')
            self.tracked_organism = None

def darken_color(hex_color):
    """Darken hex color"""
    hex_color = hex_color.removeprefix('#')
    value = int(hex_color, 16)
    new_value = (value & 0x7e7e7e) >> 1 | (value & 0x808080)
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
