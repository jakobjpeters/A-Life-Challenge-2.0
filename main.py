
from random import randint, choice, uniform
from math import ceil
from enum import Enum
from gui import *

N_ORGANISMS = 3
GRID_WIDTH = 5
GRID_HEIGHT = 5
STARTING_ENERGY_LEVEL = 5
GENE_LENGTH = 50 # increasing GENE_LENGTH will make the odds of a mutation decrease
EAT_ENERGY_RATE = 0.5

REPRODUCTION = Enum('Reproduction', ['sexual', 'asexual'])
ENERGY_SOURCE = Enum('EnergySource', ['photosynthesis', 'herbivore', 'carnivore', 'omnivore'])
SKIN = Enum('Skin', ['fur', 'shell', 'camouflage', 'membrane', 'quills'])
MOVEMENT = Enum('Movement', ['bipedal', 'quadripedal', 'stationary'])
SLEEP = Enum('Sleep', ['diurnal', 'nocturnal'])
BODY = Enum('Body', ['one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten'])
TRAITS = [REPRODUCTION, ENERGY_SOURCE, SKIN, MOVEMENT, SLEEP, BODY]

PREDATOR_PREY_TYPES = {ENERGY_SOURCE[predator]: [ENERGY_SOURCE[x] for x in prey] for predator, prey in (
    ("herbivore", ["photosynthesis"]),
    ("carnivore", ["omnivore", "carnivore", "herbivore"]),
    ("omnivore", ["omnivore", "carnivore", "herbivore", "photosynthesis"]),
    ("photosynthesis", [])
)}

class Genome:
    def __init__(self, phenotype={}, genotype={}):
        self.genotype, self.phenotype = {}, {}

        for trait in TRAITS:
            if trait in genotype:
                self.set_phenotype(trait)
            elif trait in phenotype:
                self.set_genotype(trait)
            else:
                self.genotype[trait] = randint(1, GENE_LENGTH)
                self.set_phenotype(trait)

    def set_phenotype(self, trait):
        """
        Assumes `trait in self.genotype`.
        """
        self.phenotype[trait] = trait(ceil(len(trait) * self.genotype[trait] / GENE_LENGTH))

    def set_genotype(self, trait):
        """
        Assumes `trait in self.phenotype`
        """
        self.genotype[trait] = ceil(GENE_LENGTH * self.phenotype[trait].value / len(trait))

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
    photosynthesis_rate =  1.1 # energy_levels / frame during day
    metabolism_rate = 1 # make this a function of "size"?
    troph_type = 'p' #h, c, o
    movement = 0
    vision = 0

    def __init__(self, x, y):
        """
        Instantiate an organism at the given `x` and `y` coordinates.
        """
        self.genome = Genome()
        self.energy_level = choice((4, 5, 6))
        self.update_location(x, y)

    def update_location(self, x, y):
        """
        Move an organism to the given `x` and `y` coordinates.
        """
        self.x, self.y = x, y

    def photosynthesize(self):
        """
        Increase energy_level by an organisms photosynthesis_rate if self
        has the photosynthesis phenotype
        """
        if self.genome.phenotype[ENERGY_SOURCE] == ENERGY_SOURCE.photosynthesis:
            self.energy_level += self.photosynthesis_rate

    def eat(self, other):
        """
        Increase energy_level by fractional amount
        """
        self.energy_level += EAT_ENERGY_RATE * other.energy_level

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
        return str(id(self))[-5:]

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
        """
        Determine whether eating, reproduction, or neither occurs when
        organisms collide.
        """
        organisms = self.grid[y][x]
        organism_1 = organisms[0]
        organism_2 = organisms[1]

        prey = resolve_feeding(organism_1, organism_2)
        predator = organism_1 if organism_2 is prey else organism_2
        if prey:
            predator.eat(prey)
            self.kill(prey)
        else:
            # TODO: reproduce if same species
            ...

    def move_organism(self, _organism, dx, dy):
        """
        Move the given `_organism` to its current location plus `dx, dy`.
        This new location must be within bounds of `self.grid`.
        If its new cell is non-empty, handle collision.
        """
        self.remove_from_cell(_organism)
        new_x = _organism.x + dx if _organism.x + dx < GRID_WIDTH else _organism.x
        new_y = _organism.y + dy if _organism.y + dy < GRID_HEIGHT else _organism.y
        x, y = new_x, new_y
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

            # FIXME: currently just moving randomly
            self.move_organism(_organism, choice((-1, 0, 1)), choice((-1, 0, 1)))
            if self.sun.is_day:
                _organism.photosynthesize()
            _organism.energy_level -= _organism.metabolism_rate
            if _organism.energy_level <= 0:
                self.kill(_organism)

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
        rand_gen = uniform(0, 1)
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
                    grid_str += '[     ]'
                elif len(cell) > 1:
                    grid_str += '[Coll.]'
                else:
                    grid_str += str(cell)
            grid_str += '\n'
        return grid_str


def resolve_feeding(organism_1, organism_2):
    """
    Return Organism that will be eaten or None.

    Organisms that are the same phenotype never eat each other. In other cases,
    use `PREDATOR_PREY_TYPES` dict to determine wether one organism can
    eat another organism based on its energy_source phenotype. In order to eat
    another organism, one organism must not only be able to eat it based on its
    energy_source phenotype, but it must also have more energy. If two organisms
    could possibly eat each other, then the organism with more energy eats the
    one with less energy.
    """
    phenotype_1 = organism_1.genome.phenotype
    phenotype_2 = organism_2.genome.phenotype

    # No cannibalism.
    if phenotype_1 == phenotype_2:
        return None

    organism_1_type = phenotype_1[ENERGY_SOURCE]
    organism_2_type = phenotype_2[ENERGY_SOURCE]
    organism_1_prey_types = PREDATOR_PREY_TYPES[organism_1_type]
    organism_2_prey_types = PREDATOR_PREY_TYPES[organism_2_type]
    organism_1_can_eat_organism_2 = organism_2_type in organism_1_prey_types
    organism_2_can_eat_organism_1 = organism_1_type in organism_2_prey_types

    prey = None
    if organism_1_can_eat_organism_2 and not organism_2_can_eat_organism_1:
        if organism_1.energy_level > organism_2.energy_level:
            prey = organism_2
    elif organism_2_can_eat_organism_1 and not organism_1_can_eat_organism_2:
        if organism_2.energy_level > organism_1.energy_level:
            prey = organism_1
    elif organism_1_can_eat_organism_2 and organism_2_can_eat_organism_1:
        if organism_1.energy_level > organism_2.energy_level:
            prey = organism_2
        elif organism_2.energy_level > organism_1.energy_level:
            prey = organism_1
    return prey


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
