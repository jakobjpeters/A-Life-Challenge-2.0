from random import randint
from enum import Enum
from gui import *

N_ORGANISMS = 3
GRID_WIDTH = 10
GRID_HEIGHT = 10
STARTING_ENERGY_LEVEL = 5
GENES = Enum('Genes',[])

class Genome:
    # update traits here
    # naming convention is TRAIT_options and then update self.phenotype and self.genotype with TRAIT
    reproduction_options = ['sexual', 'asexual']
    energy_source_options = ['herbivore', 'carnivore', 'omnivore', 'photosynthesis']
    body_options = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    skin_options = ["fur", "shell", "camouflage", 'membrane', "quills"]
    movement_options = ["bipedal", "quadripedal", "stationary"]
    sleep_options = ['diurnal', 'nocturnal']
    GENE_LENGTH = 50 # increasing GENE_LENGTH will make the odds of a mutation decrease

    def __init__(self, reproduction=None, energy_source=None, body=None, skin=None, movement=None, sleep=None, genotype=None):
        # will randomly generate a phenotype/genotype if one is not given
        if genotype:
            self.genotype = offspring_genotype
            self.phenotype = self.calculate_phenotype_from_genotype()
        else:
            self.phenotype = {
                'reproduction': reproduction if reproduction else self.choose_reproduction(),
                'energy_source': energy_source if energy_source else self.choose_energy(),
                'body': body if body else self.choose_body(),
                'skin': skin if skin else self.choose_skin(),
                'movement': movement if movement else self.choose_movement(),
                'sleep': sleep if sleep else self.choose_sleep()
            }

            self.genotype = {
                'reproduction': self.get_genotype(self.reproduction_options, self.phenotype['reproduction']),
                'energy_source': self.get_genotype(self.energy_source_options, self.phenotype['energy_source']),
                'body': self.get_genotype(self.body_options, self.phenotype['body']),
                'skin': self.get_genotype(self.skin_options, self.phenotype['skin']),
                'movement': self.get_genotype(self.movement_options, self.phenotype['movement']),
                'sleep': self.get_genotype(self.sleep_options, self.phenotype['sleep'])
            }

    def calculate_phenotype_from_genotype(self):
        phenotype = {}
        for key in self.genotype:
            phenotype[key] = self.get_phenotype_from_genotype(key)
        return phenotype

    def get_phenotype_from_genotype(self, key):
        phen_list = getattr(self, f"{key}_options")
        divisions = self.GENE_LENGTH // len(phen_list)
        phen_index = int((self.genotype[key] - 1) // divisions)
        return phen_list[phen_index]

    # randomly selecting a phenotype
    def choose_reproduction(self):
        return random.choice(self.reproduction_options)

    def choose_energy(self):
        return random.choice(self.energy_source_options)

    def choose_body(self):
        return random.choice(self.body_options)

    def choose_skin(self):
        return random.choice(self.skin_options)

    def choose_movement(self):
        return random.choice(self.movement_options)

    def choose_sleep(self):
        return random.choice(self.sleep_options)

    # randomly selecting a genotype
    def random_gene(self):
        return random.randint(0, self.GENE_LENGTH)

    def get_genotype(self, phen_list, pheno):
        divisions = self.GENE_LENGTH // len(phen_list)
        phen_index = phen_list.index(pheno)
        base = divisions * phen_index
        max_ind = ((phen_index + 1) * divisions) - 1
        return random.randint(base, max_ind)

    def print_genotype(self):
        print("Genotype: ", self.genotype)

    def __str__(self):
        return str(self.phenotype)

class Organism():
    """
    A simulated entity that exists within a simulated environment.

    The `x` and `y` attributes indicate its position in the environment.
    An organism dies when its `energy_level` is less than or equal to `0`.
    """
    energy_level = STARTING_ENERGY_LEVEL
    photosynthesis_rate =  1.1 # energy_levels / frame during day
    metabolism_rate = 1 # make this a function of "size"?
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

    def photosynthesize(self):
        """Increase energy_level by an organisms photosynthesis_rate"""
        self.energy_level += self.photosynthesis_rate
    
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
    


class Sun():
    """
    Provide energy to photosynthesizing organisms during daytime.
    """
    is_day = True

    def __init__(self, day_length=5):
        self.day_length = day_length # currently implemented as days / frame
        self.time_to_twighlight = self.day_length

    def update(self):
        """
        Cycle between day or night if have reached twighlight.
        """
        self.time_to_twighlight -= 1
        if self.time_to_twighlight == 0:
            self.is_day = not self.is_day
            self.time_to_twighlight = self.day_length


class World():
    """
    A simulated environment containing simulated organisms.

    The `organisms` attribute is a list of `Organism`s.
    The `grid` is the environment, where `grid[y][x]` is a list of things in that cell.
    The `frame` is a counter which increases by `1` every time `update` is called.
    """
    organisms = [Organism(randint(0, GRID_WIDTH - 1), randint(0, GRID_HEIGHT - 1)) for _ in range(N_ORGANISMS)]
    grid = [[[] for __ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
    sun = Sun()
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
        self.move_organism(_organism, 0, 0)

    def update(self):
        """
        This method processes and executes one from of the simulation.

        The `self.frame` is incremented by `1` every time this method is called.
        The behavior of each organism in `self.organisms` is determined and enacted sequentially.
        """
        self.frame += 1
       
        organisms = self.organisms.copy()
        for _organism in organisms:
            if self.sun.is_day:
                _organism.photosynthesize()
            _organism.energy_level -= _organism.metabolism_rate
            if _organism.energy_level <= 0:
                self.kill(_organism)
            else:
                self.pathfind(_organism)

        self.sun.update()

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
        for organism in world.organisms:
            print(organism)
        world.update()
        while True:
            ans = input('Next frame? [y/n] ')
            if ans in ('Y', 'y', ''):
                break
            if ans == 'n' or ans == 'N':
                stop = True
                break
        if stop:
            break
