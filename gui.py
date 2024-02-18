from random import seed
import pickle
import tkinter as tk
import time
from main import GRID_HEIGHT, GRID_WIDTH, World

WIDTH = 800
HEIGHT = 600
CELL_SIZE = 8
FPS_REFRESH_RATE = 1 # second
CELL_COLOR = '#2f2f2f'

class App:
    """
    Controls the GUI for the simulation.
    `self.root` is the `tk.Tk()` instance.
    """

    def __init__(self, root):
        self.root = root
        root.title("A-Life Challenge 2.0")

        # window size
        screenwidth = root.winfo_screenwidth()
        screenheight = root.winfo_screenheight()
        alignstr = '%dx%d+%d+%d' % (WIDTH, HEIGHT,
                                    (screenwidth - WIDTH) / 2, (screenheight - HEIGHT) / 2)
        root.geometry(alignstr)

        # create frames for screens
        self.main_frame = tk.Frame(root, bg='#ffffff')
        self.button_frame = tk.Frame(
            self.main_frame)

        # canvas for buttons
        button_canvas = tk.Canvas(
            self.button_frame, width=250, height=200, bg='#00ff00', highlightthickness=0)
        button_canvas.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        # buttons on the button canvas
        new_button = tk.Button(button_canvas, text="Start", command=self.new_button_command,
                                 width=30, height=2)
        new_button.place(relx=0.5, rely=0.2, anchor=tk.CENTER)

        load_button = tk.Button(button_canvas, text="Load", command=self.load_button_command,
                                width=30, height=2)
        load_button.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        about_button = tk.Button(button_canvas, text="About", command=self.about_button_command,
                                 width=30, height=2)
        about_button.place(relx=0.5, rely=0.8, anchor=tk.CENTER)

        # label box
        self.label = tk.Label(self.main_frame, text="This is a little blurb about the simulation")
        self.label.place(anchor=tk.CENTER, relx=0.5, rely=0.1)

        self.tracked_organism = None
        self.paused = False
        self.speed = 1.0

        self.main_frame.pack(fill=tk.BOTH, expand=True)
        self.button_frame.pack(fill=tk.BOTH, expand=True)

    def new_button_command(self):
        self.label.place_forget()
        self.button_frame.pack_forget()

        self.new_frame = tk.Frame(self.main_frame, bg='#3E3E3E')
        self.new_frame.pack(fill=tk.BOTH, expand=True)

        seed_label = tk.Label(self.new_frame, text="\nRandom seed", font=('Times', 14), fg="#000000")
        seed_label.pack()

        self.seed_entry = tk.Entry(self.new_frame, validate='all', validatecommand=(self.new_frame.register(lambda s: str.isdigit(s) or s == ''), '%P'))
        self.seed_entry.insert(0, 0)
        self.seed_entry.pack()

        species_label = tk.Label(self.new_frame, text="\nNumber of species", font=('Times', 14), fg="#000000")
        species_label.pack()

        self.species_slider = tk.Scale(self.new_frame, from_=0, to=20, orient='horizontal')
        self.species_slider.set(10)
        self.species_slider.pack()

        organisms_label = tk.Label(self.new_frame, text="\nNumber of organisms", font=('Times', 14), fg="#000000")
        organisms_label.pack()

        self.organisms_slider = tk.Scale(self.new_frame, from_=0, to=400, orient='horizontal')
        self.organisms_slider.set(200)
        self.organisms_slider.pack()

        start_button = tk.Button(self.new_frame, text="Start", command=self.start_button_command,
                            width=30, height=2, bg="#5189f0", fg="#FFFFFF", activebackground="#5C89f0")
        start_button.pack()



    def start_button_command(self):
        """
        Starts the simulation by instantiating a new `World`.
        The left side of the simulation displays the simulated environment.
        The right side of the screen contains a button to calculate the next frame and
        will display other information about the simulation.
        """
        seed(self.seed_entry.get())

        # FIXME: option to load / save worlds in GUI
        world_to_load = ''  # set None
        if world_to_load:
            with open('world.pkl', 'rb') as pkl:
                self.world = pickle.load(pkl)
        else:
            self.world = World(n_organisms=self.organisms_slider.get(), n_species=self.species_slider.get())
            with open('world.pkl', 'wb') as pkl:
                pickle.dump(self.world, pkl)

        # new frame for after pushing the start button
        self.canvas = tk.Canvas(self.main_frame, width=800,
                           height=600)

        self.pause_button = tk.Button(self.canvas, text='Pause', command=self.toggle_pause,
                        width=30, height=2)
        self.pause_button.place(relx=0.8, rely=0.5, anchor=tk.CENTER)

        self.faster_button = tk.Button(self.canvas, text='Faster', command=self.faster,
                                       width=5, height=2)
        self.faster_button.place(relx=0.7, rely=0.6, anchor=tk.CENTER)

        self.slower_button = tk.Button(self.canvas, text='Slower', command=self.slower,
                                       width=5, height=2)
        self.slower_button.place(relx=0.8, rely=0.6, anchor=tk.CENTER)

        self.slower_button = tk.Button(self.canvas, text='Reset', command=self.reset_speed,
                                       width=5, height=2)
        self.slower_button.place(relx=0.9, rely=0.6, anchor=tk.CENTER)

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


        self.new_frame.pack_forget()
        self.canvas.pack()
        self.render()
        self.run_after_delay()

    def run_after_delay(self):
        self.root.after(int(1000 * self.speed), self.run)

    def run(self):
        """
        When the `update` button is clicked, simulate the next frame in the simulation.
        When the simulation changes between day and night, change the color of the GUI to reflect that.
        """
        if not self.paused:
            self.world.update()
            if self.tracked_organism:
                self.organism_info_area.configure(text=str(self.tracked_organism))
            if self.world.sun.is_day:
                self.canvas.configure(bg='white')
            else:
                self.canvas.configure(bg='black')
            self.render()

        self.run_after_delay()

    def faster(self):
        """Double simulation speed."""
        self.speed *= 0.5

    def slower(self):
        """Halve simulation speed."""
        self.speed *= 2

    def reset_speed(self):
        """Set simulation speed back to default."""
        self.speed = 1.0

    def toggle_pause(self):
        """Pause/resume simulation."""
        self.paused = not self.paused
        if self.paused:
            self.pause_button.config(text='Resume')
        else:
            self.pause_button.config(text='Pause')

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
                self.color_cell(x, y, CELL_COLOR)

        species = self.world.species
        for organism, label in zip(self.world.organisms, species.labels):
            x, y = organism.get_location()
            self.color_cell(x, y, "#%02x%02x%02x" % tuple([int(255 * color) for color in species.labels_colors[label]]))
            if organism is self.tracked_organism:
                self.highlight_cell(x, y)

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
