
from random import randint, choice, uniform
from math import ceil
from enum import Enum, auto

N_ORGANISMS = 100
GRID_WIDTH = 20
GRID_HEIGHT = 20
STARTING_ENERGY_LEVEL = 10
GENE_LENGTH = 50 # increasing GENE_LENGTH will make the odds of a mutation decrease
EAT_ENERGY_RATE = 0.5
VISIBLE_RANGE = 2
# RELATIONSHIPS = Enum('Relationships', ['friendly', 'prey', 'predator'])

# REPRODUCTION = Enum('Reproduction', ['sexual', 'asexual'])
# EnergySource = Enum('EnergySource', ['photosynthesis', 'herbivore', 'carnivore', 'omnivore'])
# SKIN = Enum('Skin', ['fur', 'shell', 'camouflage', 'membrane', 'quills'])
# MOVEMENT = Enum('Movement', ['stationary', 'bipedal', 'quadripedal'])
# SLEEP = Enum('Sleep', ['diurnal', 'nocturnal'])
# BODY = Enum('Body', ['one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten'])
# TRAITS = [REPRODUCTION, EnergySource, SKIN, MOVEMENT, SLEEP, BODY]


class Relationships(Enum):
    FRIENDLY = auto()
    PREY = auto()
    PREDATOR = auto()

class Reproduction(Enum):
    SEXUAL = auto()
    ASEXUAL = auto()


class EnergySource(Enum):
    PHOTOSYNTHESIS = auto()
    HERBIVORE = auto()
    CARNIVORE = auto()
    OMNIVORE = auto()


class Skin(Enum):
    FUR = auto()
    SHELL = auto()
    CAMOFLAUGE = auto()
    MEMBRANE = auto()
    QUILLS = auto()


class Movement(Enum):
    STATIONARY = auto()
    BIPEDAL = auto()
    QUADRIPEDAL = auto()


class Sleep(Enum):
    DIURNAL = auto()
    NOCTURNAL = auto()


class Body(Enum):
    ONE = 1
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    SIX = 6
    SEVEN = 7
    EIGHT = 8
    NINE = 9
    TEN = 10


PREDATOR_PREY_TYPES = {EnergySource[predator]: [EnergySource[x] for x in prey] for predator, prey in (
    ("HERBIVORE", ["PHOTOSYNTHESIS"]),
    ("CARNIVORE", ["OMNIVORE", "CARNIVORE", "HERBIVORE"]),
    ("OMNIVORE", ["OMNIVORE", "CARNIVORE", "HERBIVORE", "PHOTOSYNTHESIS"]),
    ("PHOTOSYNTHESIS", [])
)}


TRAITS = [Relationships, Reproduction, EnergySource, Skin, Movement, Sleep, Body]

def distance(xy, _xy):
    """
    Calculate the manhatten distance between two pairs.

    TODO: write tests
    """
    return abs(xy[0] - xy[0]) + abs(_xy[1] - _xy[1])

def reachable_cells(x, y, n):
    """
    Yield each coordinate pair reachable from `(x, y)` in `n` moves
    if that pair is within the bounds `(range(0, GRID_WIDTH), range(0, GRID_HEIGHT))`.

    TODO: write tests
    """
    for _x in range(max(x - n, 0), min(1 + x + n, GRID_WIDTH)):
        for _y in range(max(y - n + abs(x - _x), 0), min(y + n + 1 - abs(x - _x), GRID_HEIGHT)):
            yield _x, _y

class Genome:
    """
    This class will belong to a simulated organism.
    The genotype encodes a specific (integer) value for each trait.
    The phenotype maps from the values of the genotype to categorical traits.
    """
    def __init__(self, genotype={}, phenotype={}):
        """
        The `genotype` is a dictionary mapping from traits to an integer.
        The `phenotype` is a dictionary mapping from traits to a category.
        
        Traits given in the `genotype` parameter will be used to determine that trait in the  phenotype.
        Traits given in the `phenotype` but not in the `genotype` will be used to determine that trait in the `genotype`.
        Traits not in either parameter will generate a random value for its value in the `genotype`,
        which will determine its value in the `phenotype`.
        """
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
        Determines and sets the `trait` `self.phenotype` according to the traits value in `self.genotype`.
        """
        self.phenotype[trait] = trait(ceil(len(trait) * self.genotype[trait] / GENE_LENGTH))

    def set_genotype(self, trait):
        """
        Determines and sets the `trait` `self.genotype` according to the traits value in `self.phenotype`.
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
        self.awake = True
        self.alive = True

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
        if self.genome.phenotype[EnergySource] == EnergySource.PHOTOSYNTHESIS:
            self.energy_level += self.photosynthesis_rate

    def metabolize(self, x = 1):
        """
        Adjust organism's energy level by a baseline metabolism rate. Metabolism
        is reduced by half when an organism is asleep.
        """
        if self.awake:
            self.energy_level -= x * self.metabolism_rate
        else:
            self.energy_level -= 0.5 * self.metabolism_rate

    def eat(self, other):
        """
        Increase the `energy_level` of `self` by the energy of the `other` scaled by `EAT_ENERGY_RATE`.
        Update `other.alive` to `False`.
        """
        self.energy_level += EAT_ENERGY_RATE * other.energy_level
        other.alive = False

    def get_location(self):
        """
        Return a tuple of the organism's `x` and `y` coordinates.
        """
        return self.x, self.y

    def meet(self, other):
        """
        Return the relationship that `self` has to `other`.

        If two organisms have the same phenotype, the relationship is `friendly`.
        If `self` has more energy than and can eat `other` (as determined by `PREDATOR_PREY_TYPES`),
        then then the relationship is `prey`.
        If `other` has more energy than and can eat `self` (as determined by `PREDATOR_PREY_TYPES`),
        then then the relationship is `predator`.
        Otherwise, the relationship is `friendly`.
        """
        phenotype_1 = self.genome.phenotype
        phenotype_2 = other.genome.phenotype

        # No cannibalism.
        if phenotype_1 == phenotype_2:
            return Relationships.FRIENDLY

        organism_1_type = phenotype_1[EnergySource]
        organism_2_type = phenotype_2[EnergySource]
        organism_1_prey_types = PREDATOR_PREY_TYPES[organism_1_type]
        organism_2_prey_types = PREDATOR_PREY_TYPES[organism_2_type]
        organism_1_can_eat_organism_2 = organism_2_type in organism_1_prey_types
        organism_2_can_eat_organism_1 = organism_1_type in organism_2_prey_types

        relationship = Relationships.FRIENDLY
        if organism_1_can_eat_organism_2 and not organism_2_can_eat_organism_1:
            if self.energy_level > other.energy_level:
                relationship = Relationships.PREY
        elif organism_2_can_eat_organism_1 and not organism_1_can_eat_organism_2:
            if other.energy_level > self.energy_level:
                relationship = Relationships.PREDATOR
        elif organism_1_can_eat_organism_2 and organism_2_can_eat_organism_1:
            if self.energy_level > other.energy_level:
                relationship = Relationships.PREY
            elif other.energy_level > self.energy_level:
                relationship = Relationships.PREDATOR
        return relationship

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
        attributes += f'  awake:         {self.awake}'
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
        """
        Initializes `self.day_length` (default is 5 frames) and a counter to determine when day switches to night.
        """
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
    grid = [[[] for __ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
    sun = Sun()
    frame = 0

    def __init__(self):
        """
        Instantiate a simulated environment and append each organism to its respective cell.
        """
        self.organisms = [self.spawn_organism(randint(0, GRID_WIDTH - 1), randint(0, GRID_HEIGHT - 1)) for _ in range(N_ORGANISMS)]

    def spawn_organism(self, x, y):
        _organism = Organism(x, y)
        self.insert_to_cell(_organism)
        _organism.awake = (_organism.genome.phenotype[Sleep] == Sleep.DIURNAL) == self.sun.is_day
        return _organism

    def get_cell(self, _organism):
        """
        Return the cell corresponding to an organism's `x` and `y` coordinates.
        """
        x, y = _organism.get_location()
        return self.grid[y][x]

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

    def collide(self, x, y):
        """
        Handle the collision of two organisms by them reproducing,
        one eating the other, or nothing.
        """
        organisms = self.grid[y][x]
        organism_1 = organisms[0]
        organism_2 = organisms[1]

        relationship = organism_1.meet(organism_2)

        if relationship == Relationships.FRIENDLY:
            # maybe reproduce
            pass
        elif relationship == Relationships.PREY:
            organism_1.eat(organism_2)
            self.remove_from_cell(organism_2)
        elif relationship == Relationships.PREDATOR:
            organism_2.eat(organism_1)
            self.remove_from_cell(organism_1)

    def move_organism(self, _organism, dx, dy):
        """
        Move the given `_organism` to its current location plus `dx, dy`.
        This new location must be within bounds of `self.grid`.
        The organism `metabolize`s by the number of cells moved.
        If its new cell is non-empty, handle collision.
        """
        x, y = _organism.x + dx, _organism.y + dy

        self.remove_from_cell(_organism)
        _organism.metabolize(dx + dy)
        _organism.update_location(x, y)
        self.insert_to_cell(_organism)

        if len(self.grid[y][x]) > 1:
            self.collide(x, y)

    def pathfind(self, _organism):
        """
        Search all cells within `VISIBLE_RANGE` for other organisms, choose an action, and then execute the action.

        Actions are determined by the relationship between organisms.
        The organism will move toward a `friendly` or `prey` organism and move away from a `predator` organism.
        The organism will prioritize the response to a `predator`, followed by `prey, and finally `friendly`.
        The organism will prioritize the response to an organism with the same relationship but is closer in `distance`.
        If no organism is found, the organism will wander `0` or `1` cells.

        TODO: separate relationships and actions
        TODO: separate vision and distance moved
        TODO: write tests
        """
        x, y = _organism.get_location()
        _distance = 0
        action = Relationships.FRIENDLY
        _reachable_cells = reachable_cells(x, y, VISIBLE_RANGE)

        for _x, _y in _reachable_cells:
            cell = self.cell_content(_x, _y)
            if cell:
                _action = _organism.meet(cell[0])
                __distance = distance((x, y), (_x, _y))
                if action.value < _action.value or (action.value == _action.value and __distance < _distance):
                    x, y = _x, _y
                    _distance = __distance
                    action = _action

        if (x, y) == _organism.get_location():
            (x, y) = choice(list(reachable_cells(x, y, 1)))

        if action == Relationships.PREDATOR:
            dx, dy = 0, 0
            for _x, _y in _reachable_cells:
                __distance = distance((x, y), (_x, _y))
                if __distance > _distance:
                    _distance = __distance
                    dx, dy = _x - _organism.x, _y - _organism.y
        else:
            dx, dy = x - _organism.x, y - _organism.y

        self.move_organism(_organism, dx, dy)

    def update(self):
        """
        This method processes and executes one from of the simulation.

        The `self.frame` is incremented by `1` every time this method is called.
        The behavior of each organism in `self.organisms` is determined and enacted sequentially.

        While iterating over the organisms, an organism that dies
        must have its `alive` attribute set to `False` and be removed from its cell.
        The organism will be removed from `self.organisms` after the loop is complete,
        so that it does not mutate the collection being iterated over.
        """
        self.frame += 1
        is_twighlight = self.sun.time_to_twighlight == 1
        self.sun.update()

        for _organism in self.organisms:
            if _organism.alive:
                if is_twighlight:
                    _organism.awake = not _organism.awake
                if _organism.awake:
                    self.pathfind(_organism)
                if self.sun.is_day:
                    _organism.photosynthesize()
                _organism.metabolize()
                if _organism.alive and _organism.energy_level <= 0:
                    _organism.alive = False
                    self.remove_from_cell(_organism)

        self.organisms = [_organism for _organism in self.organisms if _organism.alive]

    def save(self):
        """
        Write the state of the simulation to a file, so that it can be resumed later.
        """
        pass

    def cell_content(self, x, y):
        "Accepts tuple integers x and y where y is the yth list and x is the xth position in the yth list."
        return self.grid[y][x]

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

if __name__ == '__main__':
    world = World()
    stop = False

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
