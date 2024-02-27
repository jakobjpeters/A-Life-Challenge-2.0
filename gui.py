import copy
import math
import pickle
import random
import tkinter as tk
import tkinter.filedialog
import time
from main import GRID_HEIGHT, GRID_WIDTH, World, EnergySource, Terrain
from enum import Enum, auto

WIDTH = 800
HEIGHT = 600
CELL_SIZE = 400 / GRID_WIDTH
FPS_REFRESH_RATE = 1 # second


EARTH_COLOR = '#556b2f' #dark olive green
SAND_COLOR = '#e9d66b' #dark aleride yellow
WATER_COLOR = '#00008b' # dark blue
ROCK_COLOR = '#808080' #grey

TERRAIN_DICTIONARY_str = {"Terrain.WATER": WATER_COLOR, "Terrain.ROCK":ROCK_COLOR, "Terrain.SAND":SAND_COLOR, "Terrain.EARTH":EARTH_COLOR}
TERRAIN_ARRAY = [[Terrain.EARTH for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]

class App:
    """
    Controls the GUI for the simulation.
    `self.root` is the `tk.Tk()` instance.
    """

    def __init__(self, root):
        self.root = root
        root.title("A-Life Challenge 2.0")
        self.world = None
        self.terrain_selected = False
        self.terrain_array = [[Terrain.EARTH for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
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
        new_button.place(relx=0.5, rely=0.05, anchor=tk.CENTER)

        customize_button = tk.Button(button_canvas, text="Customize Terrain", command=self.customize_terrain_command,
                                 width=30, height=2)
        customize_button.place(relx=0.5, rely=0.35, anchor=tk.CENTER)

        load_button = tk.Button(button_canvas, text="Load", command=self.load,
                                width=30, height=2)
        load_button.place(relx=0.5, rely=0.65, anchor=tk.CENTER)

        about_button = tk.Button(button_canvas, text="About", command=self.about_button_command,
                                 width=30, height=2)
        about_button.place(relx=0.5, rely=0.95, anchor=tk.CENTER)

        # label box
        self.label = tk.Label(self.main_frame, text="This is a little blurb about the simulation")
        self.label.place(anchor=tk.CENTER, relx=0.5, rely=0.1)

        self.main_frame.pack(fill=tk.BOTH, expand=True)
        self.button_frame.pack(fill=tk.BOTH, expand=True)

    def new_button_command(self):
        self.label.place_forget()
        self.button_frame.pack_forget()

        if self.terrain_selected == True:
            self.canvas.pack_forget()


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

        start_button = tk.Button(self.new_frame, text="Start", command=self.start_simulation,
                            width=30, height=2, bg="#5189f0", fg="#FFFFFF", activebackground="#5C89f0")
        start_button.pack()


    def customize_terrain_command(self):
        """
        Enables user to choose terrain features.
        """
        self.terrain_selected = True

        # Select terrain types.
        self.canvas = tk.Canvas(self.main_frame, width=800, height=600)
                           
        self.selected_option = tk.StringVar()
        self.terrain_button = tk.Radiobutton(self.canvas, text='Earth', variable=self.selected_option , value = "Terrain.EARTH")
        self.terrain_button.place(relx=0.65, rely=0.2, anchor=tk.W)

        self.terrain_button = tk.Radiobutton(self.canvas, text='Water', variable=self.selected_option , value = "Terrain.WATER")                
        self.terrain_button.place(relx=0.65, rely=0.3, anchor=tk.W)

        self.terrain_button = tk.Radiobutton(self.canvas, text='Rock', variable=self.selected_option , value = "Terrain.ROCK")           
        self.terrain_button.place(relx=0.65, rely=0.4, anchor=tk.W)

        self.terrain_button = tk.Radiobutton(self.canvas, text='Sand', variable=self.selected_option , value = "Terrain.SAND")                     
        self.terrain_button.place(relx=0.65, rely=0.5, anchor=tk.W)

        self.organism_info_area = tk.Label(self.main_frame, justify=tk.LEFT, anchor='w', font='TkFixedFont', text='Select Terrain Type')
        self.organism_info_area.place(anchor=tk.N, relx=0.9, rely=0.0, width=500, height=100)

        customize_button = tk.Button(self.canvas, text="Select Parameters", command=self.new_button_command,
                                 width=30, height=2)
        customize_button.place(relx=0.5, rely=0.8, anchor=tk.CENTER)

        self.canvas.pack()



        self.terrain_grid = []
        for y in range(GRID_HEIGHT):
            self.terrain_grid.append([]) 
            for x in range(GRID_WIDTH):
                _x, _y = CELL_SIZE * (x + 1), CELL_SIZE * (y + 1)
                rect = self.canvas.create_rectangle(
                    _x, _y, _x + CELL_SIZE,
                    _y + CELL_SIZE,
                    fill=EARTH_COLOR,
                    outline='',
                )
                self.terrain_grid[y].append(rect)
                self.canvas.tag_bind(rect, '<Button-1>', lambda _, x=x, y=y: self.terrain_selection(x, y, self.selected_option ,clicked=True))

        self.canvas.pack()

    def terrain_selection(self, x, y, selected_terrain, clicked=False):
        """
        Allows user to click on and select terrain.
        """
        if clicked:
            terrain_color = TERRAIN_DICTIONARY_str[selected_terrain.get()]
            self.canvas.itemconfigure(self.terrain_grid[y][x], fill=terrain_color, outline='')
            TERRAIN_ARRAY[y][x] = selected_terrain.get()


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
        bottom = tk.Label(subwindow, text="bottom pane")
        subwindow.add(bottom)

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

                # attach callback functions to cell when its clicked or hovered
                self.canvas.tag_bind(rect, '<Enter>', lambda _, x=x, y=y: self.view_organism_details(x, y))
                self.canvas.tag_bind(rect, '<Button-1>', lambda _, x=x, y=y: self.view_organism_details(x, y, clicked=True))
                self.canvas.tag_bind(rect, '<Leave>', lambda _: self.clear_organism_details())


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
                color = self.get_cell_color(x, y)         
                self.color_cell(x, y, color)

        species = self.world.species
        for organism in self.world.organisms:
            x, y = organism.get_location()
            self.shape_cell(x, y, organism.genome.phenotype[EnergySource], organism.energy_level)
            self.color_cell(x, y, "#%02x%02x%02x" % tuple([int(255 * color) for color in species.labels_colors[species.organisms_labels[organism]]]))
            if organism is self.tracked_organism:
                self.highlight_cell(x, y)


    def get_cell_color(self, x, y):
        terrain = TERRAIN_ARRAY[y][x]

        if terrain == "Terrain.WATER" or terrain == Terrain.WATER:
            return WATER_COLOR
        elif terrain == "Terrain.SAND" or terrain == Terrain.SAND:
            return SAND_COLOR
        elif terrain == "Terrain.ROCK" or terrain == Terrain.ROCK: 
            return ROCK_COLOR
        elif terrain == "Terrain.EARTH" or terrain == Terrain.EARTH:
            return EARTH_COLOR

        
        
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

