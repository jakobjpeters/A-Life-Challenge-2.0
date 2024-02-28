import copy
import math
import pickle
import random
import tkinter as tk
import tkinter.filedialog
import time
from main import GRID_HEIGHT, GRID_WIDTH, World, EnergySource
from enum import Enum, auto
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import numpy as np

WIDTH = 800
HEIGHT = 600
CELL_SIZE = 400 / GRID_WIDTH
FPS_REFRESH_RATE = 1 # second


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
        self.button_frame = tk.Frame(self.main_frame)

        # canvas for buttons
        button_canvas = tk.Canvas(
            self.button_frame, width=250, height=200, bg='#00ff00', highlightthickness=0)
        button_canvas.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        # buttons on the button canvas
        new_button = tk.Button(button_canvas, text="Start", command=self.new_button_command,
                                 width=30, height=2)
        new_button.place(relx=0.5, rely=0.2, anchor=tk.CENTER)

        load_button = tk.Button(button_canvas, text="Load", command=self.load,
                                width=30, height=2)
        load_button.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        about_button = tk.Button(button_canvas, text="About", command=self.about_button_command,
                                 width=30, height=2)
        about_button.place(relx=0.5, rely=0.8, anchor=tk.CENTER)

        # label box
        self.label = tk.Label(self.main_frame, text="This is a little blurb about the simulation")
        self.label.place(anchor=tk.CENTER, relx=0.5, rely=0.1)

        self.main_frame.pack(fill=tk.BOTH, expand=True)
        self.button_frame.pack(fill=tk.BOTH, expand=True)

    def new_button_command(self):
        self.label.place_forget()
        self.button_frame.pack_forget()

        self.new_frame = tk.Frame(self.main_frame, bg='#3E3E3E')
        self.new_frame.pack(fill=tk.BOTH, expand=True)

        button_canvas = tk.Canvas(
            self.new_frame, width=250, height=500, bg='SystemButtonFace', highlightthickness=0)
        button_canvas.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        seed_label = tk.Label(button_canvas, text="\nRandom seed", font=('Times', 14), bg='SystemButtonFace')
        seed_label.place(relx=0.5, rely=0.1, anchor=tk.CENTER)

        self.seed_entry = tk.Entry(button_canvas, validate='all', validatecommand=(self.new_frame.register(lambda s: str.isdigit(s) or s == ''), '%P'))
        self.seed_entry.insert(0, 0)
        self.seed_entry.place(relx=0.5, rely=0.2, anchor=tk.CENTER)

        species_label = tk.Label(button_canvas, text="\nSpecies variability", font=('Times', 14), bg='SystemButtonFace')
        species_label.place(relx=0.5, rely=0.35, anchor=tk.CENTER)

        self.species_slider = tk.Scale(button_canvas, from_=1, to=20, orient='horizontal')
        self.species_slider.set(10)
        self.species_slider.place(relx=0.5, rely=0.45, anchor=tk.CENTER)

        organisms_label = tk.Label(button_canvas, text="\nNumber of organisms", font=('Times', 14), bg='SystemButtonFace')
        organisms_label.place(relx=0.5, rely=0.6, anchor=tk.CENTER)

        self.organisms_slider = tk.Scale(button_canvas, from_=0, to=400, orient='horizontal')
        self.organisms_slider.set(200)
        self.organisms_slider.place(relx=0.5, rely=0.7, anchor=tk.CENTER)

        start_button = tk.Button(button_canvas, text="Start", command=self.start_simulation,
                            width=30, height=2, bg="#5189f0", fg="#FFFFFF", activebackground="#5C89f0")
        start_button.place(relx=0.5, rely=0.9, anchor=tk.CENTER)

    def load(self):
        """Load .world file and launch simulation."""
        file = tkinter.filedialog.askopenfilename()
        with open(file, 'rb') as f:
            # FIXME: handle invalid files
            world = pickle.load(f)
        simulation = Simulation(self.main_frame, self.root, world=world)
        simulation.start()

    def start_simulation(self):
        n_organisms = self.organisms_slider.get()
        n_species = self.species_slider.get()
        seed = int(self.seed_entry.get())
        simulation = Simulation(
            self.main_frame,
            self.root,
            n_organisms=n_organisms,
            n_species=n_species,
            seed=seed
        )
        simulation.start()

    def about_button_command(self):
        print("About button command")


class Simulation:
    """
    Contains the interface for a running simulation.
    """
    def __init__(
        self,
        main_frame,
        root,
        world=None,
        n_organisms=None, 
        n_species=None,
        seed=None
    ):
        self.main_frame = main_frame
        self.root = root
        self.n_organisms = n_organisms
        self.n_species = n_species
        self.seed = seed
        self.tracked_organism = None
        self.paused = False
        self.speed = 1.0
        self.world = world
        self.initial_world = None
        self.canvas = None

    def start(self):
        """
        Starts the simulation by instantiating a new `World`.

        The left side of the window displays simulation controls and information
        about individual organisms. The right side of the window shows a visual
        representation of the simulation and general information about the
        current state.
        """

        if self.world is None:
            self.world = World(
                n_organisms=self.n_organisms,
                n_species=self.n_species,
                seed=self.seed
            )
            random.seed(self.seed)
            self.initial_world = copy.deepcopy(self.world)
        else:
            # use seed from saved simulation
            random.seed(self.world.seed)

    
        # Set up simulation windows
        self.main_frame.pack_forget()
        window = self.set_up_left_panel()
        window.pack(fill=tk.BOTH, expand=1)
        subwindow = tk.PanedWindow(window, orient=tk.VERTICAL, bg='slategray')
        window.add(subwindow)
        self.canvas = tk.Canvas(subwindow, width=400, height=400)
        self.set_up_canvas()
        subwindow.add(self.canvas)

        # bottom pane containing the graph
        self.paned_window = tk.PanedWindow(root, orient=tk.HORIZONTAL)
        self.paned_window.pack(fill=tk.BOTH, expand=True)
        self.subpane = tk.PanedWindow(self.paned_window, orient=tk.VERTICAL)
        self.paned_window.add(self.subpane)
        self.create_graph_subpane(self.world.species.seeds)

        # Display and run simulation
        self.render()
        self.run_after_delay()

    def run_after_delay(self):
        self.root.after(int(1000 * self.speed), self.run)

    def set_up_canvas(self):
        """
        Set up self.canvas creating a view of the World and its Organisms.
        """
        self.original_scale_factor = 1.0
        self.canvas.bind('<ButtonPress-1>', lambda event: self.canvas.scan_mark(event.x, event.y))
        self.canvas.bind("<B1-Motion>", lambda event: self.canvas.scan_dragto(event.x, event.y, gain=1))
        self.canvas_original_x = self.canvas.xview()[0]
        self.canvas_original_y = self.canvas.yview()[0]

        self.grid = []
        for y in range(GRID_HEIGHT):
            self.grid.append([])
            for x in range(GRID_WIDTH):
                _x, _y = CELL_SIZE * (x + 1), CELL_SIZE * (y + 1)
                rect = self.canvas.create_rectangle(
                    _x,
                    _y,
                    _x + CELL_SIZE,
                    _y + CELL_SIZE,
                    fill='',
                    outline='',
                )
                self.grid[y].append(rect)
                self.attach_callbacks(x, y)

    def create_graph_subpane(self, graph_data):
        """
        creates and updates the bottom graph showing the values of genotypes for each species
        currently works by creating a new graph and clearing the old graph each time it is called
        """
        x_labels = ["Reproduction", "EnergySource", "Skin", "Movement", "Sleep", "Size"]
        species_index = 0

        if not hasattr(self, 'ax'):
            # sets the axes on the first call
            self.ax = plt.figure(figsize=(10, 6)).add_subplot(111)
            self.lines = []

            self.ax.set_xticks(range(len(x_labels)))
            self.ax.set_xticklabels(x_labels)
            y_ticks = list(range(0, 51, 10))
            self.ax.set_yticks(y_ticks)

            for widget in self.subpane.winfo_children():
                widget.destroy()

            canvas = FigureCanvasTkAgg(plt.gcf(), master=self.subpane)
            canvas_widget = canvas.get_tk_widget()
            canvas_widget.pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        # redraw the lines after each frame
        for line in self.lines:
            line.remove()
        self.lines.clear()
        for _ in graph_data:
            line, = self.ax.plot([], [], color='red')
            self.lines.append(line)
            
        for species, line in zip(graph_data, self.lines):
            # add data to the lines based on species genotype and color
            _colors = self.world.species.labels_colors[species_index]
            species_color = "#%02x%02x%02x" % tuple([int(255 * color) for color in _colors])
            line.set_data(range(len(species)), species)
            line.set_color(species_color)
            species_index += 1

        plt.gcf().canvas.draw()

    def set_up_left_panel(self):
        """
        Setup left panel containing control buttons and Organism info.
        """
        window = tk.PanedWindow(bg='slategray', relief='raised')
        left_frame = tk.Frame(window)

        save_button = tk.Button(
            left_frame,
            text='Save',
            command=self.save,
            width=30,
            height=2
        )
        save_button.pack()

        self.pause_button = tk.Button(
            left_frame,
            text='Pause',
            command=self.toggle_pause,
            width=30,
            height=2
        )
        self.pause_button.pack()

        window.add(left_frame)

        zoom_button_row = tk.Frame(left_frame, width=5, height=2)
        tk.Label(zoom_button_row, text='Zoom:', width=5).pack(side=tk.LEFT)

        zoom_in_button = tk.Button(
            zoom_button_row,
            text="Zoom in",
            command=lambda: self.zoom_canvas(1.2),
            width=5,
            height=2
        )
        zoom_in_button.pack(side=tk.LEFT)
        zoom_out_button = tk.Button(
            zoom_button_row,
            text="Zoom out",
            command=lambda: self.zoom_canvas(0.8),
            width=5,
            height=2
        )
        zoom_out_button.pack(side=tk.LEFT)
        reset_view_button = tk.Button(
            zoom_button_row,
            text='Reset',
            command=self.reset_view,
            width=5,
            height=2
        )
        reset_view_button.pack(side=tk.LEFT)
        zoom_button_row.pack()

        speed_button_row = tk.Frame(left_frame, width=5, height=2)
        tk.Label(speed_button_row, text='Speed:', width=5).pack(side=tk.LEFT)

        faster_button = tk.Button(
            speed_button_row,
            text='Faster',
            command=self.faster,
            width=5,
            height=2
        )
        faster_button.pack(side=tk.LEFT)
        slower_button = tk.Button(
            speed_button_row,
            text='Slower',
            command=self.slower,
            width=5,
            height=2
        )
        slower_button.pack(side=tk.LEFT)
        reset_button = tk.Button(speed_button_row,
            text='Reset',
            command=self.reset_speed,
            width=5,
            height=2
        )
        reset_button.pack(side=tk.LEFT)
        speed_button_row.pack()

        self.organism_info_area = tk.Label(
            left_frame,
            justify=tk.LEFT,
            anchor='e',
            font='TkFixedFont',
            text='Hover over organism to view details'
        )
        self.organism_info_area.pack()
        return window
    
    def zoom_canvas(self, factor):
        """
        Scale the canvas view by the given `factor`
        """
        self.canvas.scale(tk.ALL, 0, 0, factor, factor)
        self.original_scale_factor *= 1.0 / factor

    def reset_view(self):
        """
        Reset self.canvas Zoom and position.
        """
        self.canvas.scale(tk.ALL, 0, 0, self.original_scale_factor, self.original_scale_factor)
        self.original_scale_factor = 1.0
        self.canvas.xview_moveto(self.canvas_original_x)
        self.canvas.yview_moveto(self.canvas_original_y)

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
            self.create_graph_subpane(self.world.species.seeds)
            self.render()

        self.run_after_delay()

    def save(self):
        """Save simulation as a .world file."""
        fname = tkinter.filedialog.asksaveasfilename(defaultextension='.world')
        with open(fname, 'wb') as f:
            pickle.dump(self.initial_world, f)

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

    def shape_cell(self, x, y, energy_source, energy_level):
        """
        Set the cell's shape at x and y based on the energy_source.

        Photosynthesizers: circle
        Herbivore: triangle
        Carnivore: rectangle
        Omnivore: hexagon
        """
        cell = self.grid[y][x]
        _x, _y = CELL_SIZE * (x + 1), CELL_SIZE * (y + 1)
        match energy_source:
            case EnergySource.PHOTOSYNTHESIS:
                cell = self.canvas.create_oval(_x, _y, _x+CELL_SIZE, _y+CELL_SIZE)
            case EnergySource.HERBIVORE:
                # triangle
                cell = self.canvas.create_polygon(_x, _y, _x+CELL_SIZE, _y, _x+(CELL_SIZE/2), _y+CELL_SIZE)
            case EnergySource.CARNIVORE:
                cell = self.canvas.create_rectangle(_x, _y, _x+CELL_SIZE, _y+CELL_SIZE)
            case EnergySource.OMNIVORE:
                # hexagon (used ChatGPT and trial and error -- math is hard)
                angle = 360 / 6
                vertices = []
                for i in range(6):
                    angle_rad = math.radians(angle * i)
                    vertex_x = _x + CELL_SIZE * 0.577 * math.cos(angle_rad)
                    vertex_y = _y + CELL_SIZE * 0.577 * math.sin(angle_rad)
                    vertices.extend([vertex_x + (0.5*CELL_SIZE), vertex_y + (0.5)*CELL_SIZE])
                cell = self.canvas.create_polygon(vertices)
    
        x1, y1, x2, y2 = self.canvas.bbox(cell)
        center_x = (x1 + x2) / 2
        center_y = (y1 + y2) / 2
        scale_factor = 1.0 if energy_level > 30 else 0.7 + energy_level * 0.01
        self.canvas.scale(cell, center_x, center_y, scale_factor, scale_factor)
        self.grid[y][x] = cell
        self.attach_callbacks(x, y)

    def render(self):
        """
        Changes the color of each cell to display that it's empty of contains an organism.
        The color of an organism is determined by its `body` trait.
        If the organism is asleep, its color appear darker.
        """
        for x in range(GRID_WIDTH):
            for y in range(GRID_HEIGHT):
                self.color_cell(x, y, '')  # by default cell is transparent

        species = self.world.species
        for organism in self.world.organisms:
            x, y = organism.get_location()
            self.shape_cell(x, y, organism.genome.phenotype[EnergySource], organism.energy_level)
            self.color_cell(x, y, "#%02x%02x%02x" % tuple([int(255 * color) for color in species.labels_colors[species.organisms_labels[organism]]]))
            if organism is self.tracked_organism:
                self.highlight_cell(x, y)

    def attach_callbacks(self, x, y):
        cell = self.grid[y][x]
        # attach callback functions to cell when its clicked or hovered
        self.canvas.tag_bind(cell, '<Enter>', lambda _, x=x, y=y: self.view_organism_details(x, y))
        self.canvas.tag_bind(cell, '<Button-1>', lambda _, x=x, y=y: self.view_organism_details(x, y, clicked=True))
        self.canvas.tag_bind(cell, '<Leave>', lambda _: self.clear_organism_details())

    def view_organism_details(self, x, y, clicked=False):
        """
        Show details about an organism.

        When hovering over an organism, that organism's info is shown. If
        an organism is clicked, it will become "tracked" and its details
        will be shown at all times (except temporarily when hovering over
        another organism)
        """
        organism = self.world.cell_content(x, y)
        if organism:
            self.organism_info_area.configure(text=str(organism))
            if clicked:
                self.clear_tracked_organism()
                if organism is self.tracked_organism:
                    self.clear_organism_details()
                    return
                self.highlight_cell(x, y)
                self.tracked_organism = organism

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
