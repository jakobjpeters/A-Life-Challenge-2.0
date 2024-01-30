
from random import randint
from enum import Enum

N_ORGANISMS = 10
GRID_WIDTH = 10
GRID_HEIGHT = 10
GENES = Enum('Genes',[])

class Organism():
    """
    A simulated entity that exists within a simulated environment.

    The `x` and `y` attributes indicate its position in the environment.
    An organism dies when its `energy_level` is less than or equal to `0`.
    """
    energy_level = 0
    genome = []
    troph_type = 'p' #h, c, o
    movement = 0
    vision = 0

    def __init__(self, x, y):
        """
        Instantiate an organism at the given `x` and `y` coordinates.
        """
        self.update_location(x, y)

    def update_location(self, x, y):
        """
        Move an organism to the given `x` and `y` coordinates.
        """
        self.x, self.y = x, y
    
    def get_location(self):
        """
        Return a tuple of the organism's `x` and `y` coordinates.
        """
        return self.x, self.y

    def __repr__(self) -> str:
        """
        Return the last four digits of an organism's unique identifier as a string.
        This is used to display the organism in the REPL.
        """
        return str(id(self))[-4:]

    def __str__(self):
        """
        Return a string containing details about the organism's attributes.
        This is used to display the organism when calling `print`.
        """
        attributes = ''
        attributes += f'Organism {self.__repr__()}:\n'
        attributes += f'  position:      x: {self.x}, y: {self.y}\n'
        attributes += f'  energy_level:  {self.energy_level}\n'
        attributes += f'  genome:        {self.genome}\n'
        return attributes

class World():
    """
    A simulated environment containing simulated organisms.

    The `organisms` attribute is a list of `Organism`s.
    The `grid` is the environment, where `grid[y][x]` is a list of things in that cell.
    The `frame` is a counter which increases by `1` every time `update` is called.
    """
    organisms = [Organism(randint(0, GRID_WIDTH - 1), randint(0, GRID_HEIGHT - 1)) for _ in range(N_ORGANISMS)]
    grid = [[[] for __ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
    frame = 0

    def __init__(self):
        """
        Instantiate a simulated environment and append each organism to its respective cell.
        """
        for _organism in self.organisms:
            self.insert_to_cell(_organism)

    def get_cell(self, _organism):
        """
        Return the cell corresponding to an organism's `x` and `y` coordinates.
        """
        return self.grid[_organism.y][_organism.x]

    def insert_to_cell(self, _organism):
        """
        Insert an organism in the cell at its `x` and `y` coordinates.
        """
        self.get_cell(_organism).append(_organism)

    def remove_from_cell(self, _organism):
        """
        Remove an organism from the cell at its `x` and `y` coordinates.
        """
        self.get_cell(_organism).remove(_organism)

    def kill(self, _organism):
        """
        Remove an organism from `self.organisms` and from its cell.
        """
        self.organisms.remove(_organism)
        self.remove_from_cell(_organism)

    def collide(self, x, y):
        pass

    def move_organism(self, _organism, dx, dy):
        """
        Move the given `_organism` to its current location plus `dx, dy`.
        This new location must be within bounds of `self.grid`.
        If its new cell is non-empty, handle collision.
        """
        self.remove_from_cell(_organism)
        x, y = _organism.x + dx, _organism.y + dy
        _organism.update_location(x, y)
        self.insert_to_cell(_organism)

        if len(self.grid[y][x]) > 1:
            self.collide(x, y)

    def pathfind(self, _organism):
        # dx = randint(0, _organism.movement)
        # dy = _organism.movement - dx
        # min(GRID_WIDTH, dx), min(GRID_HEIGHT, dy)
        move_organism(_organism, 0, 0)


    def update(self):
        """
        This method processes and executes one from of the simulation.

        The `self.frame` is incremented by `1` every time this method is called.
        The behavior of each organism in `self.organisms` is determined and enacted sequentially.
        """
        self.frame += 1

        for _organism in self.organisms:
            _organism.energy_level -= 1
            if _organism.energy_level <= 0:
                self.kill(_organism)
            else:
                self.pathfind(_organism)

    def save(self):
        """
        Write the state of the simulation to a file, so that it can be resumed later.
        """
        pass

    def cell_content(self, x, y):
        "Accepts tuple integers x and y where y is the yth list and x is the xth position in the yth list."
        return grid[y][x]

    def see(self, _organism):
        vision = _organism.vision
        start_point_x, start_point_y = _organism.x - vision, _organism.y - vision
        field_of_view = {}
        for x in range(vision):
            for y in range(vision):
                if start_point_x + x >= 0 and vision + y >= 0 and vision + x < GRID_WIDTH and y < GRID_HEIGHT:
                    field_of_view[(start_point_x + x, start_point_y + y)] = self.cell_content(start_point_x + x, start_point_y + y)
        return field_of_view

    def decision_model(self, choices):
        rand_gen = random.uniform(0, 1)
        cummulative_prob = 0
        for choice in choices.keys:
            if cummulative_prob < rand_gen and rand_gen <= cummulative_prob + choices[choice]:
                return rand_gen
            cummulative_prob += choices[choice]
            
    def __str__(self):
        """
        Return a string that shows the simulated environment and the entities within it.
        This is used to display the world when calling `print`.
        """
        grid_str = ''
        for row in self.grid:
            for cell in row:
                if not cell:
                    grid_str += '[    ]'
                elif len(cell) > 1:
                    grid_str += '[Coll]'
                else:
                    grid_str += str(cell)
            grid_str += '\n'
        return grid_str

if __name__ == '__main__':
    SHOW_GUI = False
    world = World()
    stop = False

    if SHOW_GUI is True:
        root = tk.Tk()
        app = App(root, world)
        root.mainloop()
            
    while True:
        print(world)
        while True:
            ans = input('Next frame? [y/n] ')
            if ans in ('Y', 'y', ''):
                break
            if ans == 'n' or ans == 'N':
                stop = True
                break
        if stop:
            break
