import textwrap

from random import randint, choice, gauss, sample
from math import ceil, copysign
from enum import Enum, auto
from species import Species
#from gui import Simulation

GRID_WIDTH = 50
GRID_HEIGHT = 50
STARTING_ENERGY_RATE = 10
GENE_LENGTH = 50  # increasing GENE_LENGTH increases rate of phenotype change
EAT_ENERGY_RATE = 2
VISIBLE_RANGE = 5
SIGMA = 1
MUTATION_RATE = 50  # range from 0 to 100%
PHOTOSYNTHESIS_RATE = 1.1
REPRODDUCTION_ENERGY_THRESHOLD = 2


class Relationships(Enum):
    NEUTRAL = auto()
    PREY = auto()
    CONSPECIFIC = auto()
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
    QUADRIPEDAL = auto()  # 2 chances at reproduction


class Sleep(Enum):
    DIURNAL = auto()
    NOCTURNAL = auto()


class Size(Enum):
    ONE = 1
    TWO = 2
    THREE = 3
    FOUR = 4 

PREDATOR_PREY_TYPES = {EnergySource[predator]: [EnergySource[x] for x in prey] for predator, prey in (
    ("HERBIVORE", ["PHOTOSYNTHESIS"]),
    ("CARNIVORE", ["OMNIVORE", "CARNIVORE", "HERBIVORE"]),
    ("OMNIVORE", ["OMNIVORE", "CARNIVORE", "HERBIVORE", "PHOTOSYNTHESIS"]),
    ("PHOTOSYNTHESIS", [])
)}


TRAITS = [Reproduction, EnergySource, Skin, Movement, Sleep, Size]


def distance(xy, _xy):
    """
    Calculate the manhatten distance between two pairs.

    TODO: write tests
    """
    return abs(xy[0] - xy[0]) + abs(_xy[1] - _xy[1])


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
        self.genotype, self.phenotype = genotype.copy(), phenotype.copy()

        for trait in TRAITS:
            if trait in genotype:
                self.genotype[trait] = genotype[trait]
                self.set_phenotype(trait)
            elif trait in phenotype:
                self.set_genotype(trait)
            else:
                self.genotype[trait] = randint(1, GENE_LENGTH)
                self.set_phenotype(trait)

    def set_phenotype(self, trait):
        """
        Determines and sets the `trait` `self.phenotype` according to the trait's value in `self.genotype`.
        """
        self.phenotype[trait] = trait(
            ceil(len(trait) * self.genotype[trait] / GENE_LENGTH))

    def set_genotype(self, trait):
        """
        Determines and sets the `trait` `self.genotype` according to the trait's value in `self.phenotype`.
        """
        self.genotype[trait] = ceil(
            GENE_LENGTH * self.phenotype[trait].value / len(trait))

    def print_genotype(self):
        print("Genotype: ", self.genotype)

    def __str__(self):
        string = ''
        for trait in TRAITS:
            string += f'{trait.__name__}: {self.phenotype[trait].name}\n'
        return string


class Organism():
    """
    A simulated entity that exists within a simulated environment.

    The `x` and `y` attributes indicate its position in the environment.
    An organism dies when its `energy_level` is less than or equal to `0`.
    """

    def __init__(self, x, y, starting_energy_rate, generation, is_day=True, genotype={}):
        """
        Instantiate an organism at the given `x` and `y` coordinates.
        """
        self.genome = Genome(genotype=genotype)
        self.energy_level = starting_energy_rate * self.size()
        self.update_location(x, y)
        self.awake = (self.genome.phenotype[Sleep] == Sleep.DIURNAL) == is_day
        self.alive = True
        self.can_reproduce = False
        self.generation = generation
  
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
            self.energy_level += PHOTOSYNTHESIS_RATE

    def size(self):
        """
        Return the value of the organism's size phenotype.
        """
        return self.genome.phenotype[Size].value

    def metabolize(self):
        """
        Adjust organism's energy level by a baseline metabolism rate. Metabolism
        is reduced by half when an organism is asleep.
        """
        if self.awake:
            self.energy_level -= self.size()

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

    def meet(self, other, organisms_labels):
        """
        Return the relationship that `self` has to `other`.

        If two organisms have the same phenotype, the relationship is `friendly`.
        If `self` has more energy than and can eat `other` (as determined by `PREDATOR_PREY_TYPES`),
        then then the relationship is `prey`.
        If `other` has more energy than and can eat `self` (as determined by `PREDATOR_PREY_TYPES`),
        then then the relationship is `predator`.
        Otherwise, the relationship is `friendly`.
        """
        organism_1_type = self.genome.phenotype[EnergySource]
        organism_2_type = other.genome.phenotype[EnergySource]
        organism_1_prey_types = PREDATOR_PREY_TYPES[organism_1_type]
        organism_2_prey_types = PREDATOR_PREY_TYPES[organism_2_type]
        organism_1_can_eat_organism_2 = organism_2_type in organism_1_prey_types
        organism_2_can_eat_organism_1 = organism_1_type in organism_2_prey_types
        organism_1_size = self.size()
        organism_2_size = other.size()

        relationship = Relationships.NEUTRAL
        if self in organisms_labels and other in organisms_labels and organisms_labels[self] == organisms_labels[other]:
            if all(_organism.energy_level > REPRODDUCTION_ENERGY_THRESHOLD * _organism.size() for _organism in (self, other)):
                relationship = Relationships.CONSPECIFIC
        elif organism_1_can_eat_organism_2 and not organism_2_can_eat_organism_1:
            if organism_1_size > organism_2_size:
                relationship = Relationships.PREY
        elif organism_2_can_eat_organism_1 and not organism_1_can_eat_organism_2:
            if organism_2_size > organism_1_size:
                relationship = Relationships.PREDATOR
        elif organism_1_can_eat_organism_2 and organism_2_can_eat_organism_1:
            if organism_1_size > organism_2_size:
                relationship = Relationships.PREY
            elif organism_2_size > organism_1_size:
                relationship = Relationships.PREDATOR
        return relationship

    def get_genotype_values(self):
        """
        returns a list of values for the Organisms genotype
        """
        return [self.genome.genotype[trait] for trait in TRAITS]
    
    def get_terrain_restriction(self):
        '''
        Returns terrain that organism cannot cross
        '''
        movment_method = self.genome.phenotype[Movement]
        if movment_method == Movement.BIPEDAL:
            return "Terrain.WATER"
        elif movment_method == Movement.STATIONARY:
            return "Terrain.ROCK"
        return "Terrain.SAND"

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
        attributes += f'Organism {self.__repr__()}{" (dead)" if not self.alive else ""}:\n'
        attributes += f'  awake:         {self.awake}\n'
        attributes += f'  position:      x: {self.x}, y: {self.y}\n'
        attributes += f'  energy_level:  {self.energy_level:.1f}\n'
        attributes += f'  generation:  {self.generation}\n'
        attributes += f'  genome:\n'
        attributes += f'{textwrap.indent(str(self.genome), "    ")}'
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
        self.day_length = day_length  # currently implemented as days / frame
        self.time_to_twighlight = self.day_length
        self.day_night_cycles = 0

    def update(self):
        """
        Cycle between day or night if have reached twighlight.
        """
        self.time_to_twighlight -= 1
        if self.time_to_twighlight == 0:
            self.is_day = not self.is_day
            self.time_to_twighlight = self.day_length
        self.day_night_cycles += 1


class World():
    """
    A simulated environment containing simulated organisms.

    The `organisms` attribute is a list of `Organism`s.
    The `grid` is the environment, where `grid[y][x]` is a list of things in that cell.
    The `frame` is a counter which increases by `1` every time `update` is called.
    """
    sun = Sun()
    frame = 0

    def __init__(self, n_organisms, n_species, terrain=None, seed=0):
        """
        Instantiate a simulated environment and append each organism to its respective cell.
        """
        self.seed = seed
        self.grid = [[None for __ in range(GRID_WIDTH)]
                     for _ in range(GRID_HEIGHT)]
        self.organisms = []
        self.terrain = terrain

        species = [{trait: randint(1, GENE_LENGTH)
                    for trait in TRAITS} for _ in range(n_species)]
        for _ in range(n_organisms):
            genotype = choice(species).copy()
            for key in genotype:
                genotype[key] = (
                    (genotype[key] + round(gauss(sigma=SIGMA))) % GENE_LENGTH) + 1
            while True:
                x, y = randint(0, GRID_WIDTH - 1), randint(0, GRID_HEIGHT - 1)
                if not self.grid[y][x]: 
                    self.spawn_organism(x, y, STARTING_ENERGY_RATE, 1, genotype)
                    break

        self.species = Species(self.organisms)

    def spawn_organism(self, x, y, starting_energy_rate, generation, genotype):
        _organism = Organism(x, y, starting_energy_rate, generation, 
                             self.sun.is_day, genotype)
        self.organisms.append(_organism)
        self.insert_to_cell(_organism)

    def insert_to_cell(self, _organism):
        """
        Insert an organism in the cell at its `x` and `y` coordinates.
        """
        x, y = _organism.get_location()
        self.grid[y][x] = _organism

    def remove_from_cell(self, _organism):
        """
        Remove an organism from the cell at its `x` and `y` coordinates.
        """
        x, y = _organism.get_location()
        self.grid[y][x] = None

    def matching_traits(self, organism_1, organism_2, trait, value):
        """
        returns a boolean for if two organims have the same matching phenotype

        if organism_1.genome.phenotype[EnergySource] != EnergySource.PHOTOSYNTHESIS and organism_2.genome.phenotype[EnergySource] != EnergySource.PHOTOSYNTHESIS:
        is now self.matching_traits(organism_1, organism_2, EnergySource, EnergySource.PHOTOSYNTHESIS)
        """
        if organism_1.genome.phenotype[trait] == organism_2.genome.phenotype[trait]:
            if organism_1.genome.phenotype[trait] == value:
                return True
        return False

    def collide(self, organism_1, organism_2):
        """
        Handle the collision of two organisms by them reproducing,
        one eating the other, or nothing.
        """
        relationship = organism_1.meet(organism_2, self.species.organisms_labels)

        if relationship == Relationships.CONSPECIFIC:
            # both organisms have sexual reproduction and are not photosynthesizer
            if self.matching_traits(organism_1, organism_2, Reproduction, Reproduction.SEXUAL):
                if self.matching_traits(organism_1, organism_2, Movement, Movement.QUADRIPEDAL):
                    # quadripeds reproduce twice
                    self.sexual_reproduce(organism_1, organism_2)
                self.sexual_reproduce(organism_1, organism_2)
        elif relationship == Relationships.PREY:
            if self.defense_mechanism(organism_1, organism_2):
                organism_1.eat(organism_2)
                self.remove_from_cell(organism_2)
        elif relationship == Relationships.PREDATOR:  # IS THIS EVER BEING CALLED??????? no, not rn
            if self.defense_mechanism(organism_2, organism_1):
                organism_2.eat(organism_1)
                self.remove_from_cell(organism_1)

    def defense_mechanism(self, predator, prey):
        """
        SHELL has 10% chance of surviving
        QUILLS has 5% chance of surviving
        """
        prey_skin = prey.genome.phenotype[Skin]
        if prey_skin == Skin.SHELL:
            if randint(1, 100) < 10:
                predator.energy_level /= 1.01
                return False
        if prey_skin == Skin.QUILLS:
            if randint(1, 100) < 5:
                return False
        return True

    def reachable_cells(self, _organism, n):
        """
        Yield each coordinate pair reachable from `(x, y)` in `n` moves
        if that pair is within the bounds `(range(0, GRID_WIDTH), range(0, GRID_HEIGHT))`.

        TODO: write tests
        """
        x, y = _organism.get_location()
        terrain_restriction = _organism.get_terrain_restriction()
        for _x in range(max(x - n, 0), min(1 + x + n, GRID_WIDTH)):
            for _y in range(max(y - n + abs(x - _x), 0), min(y + n + 1 - abs(x - _x), GRID_HEIGHT)):
                if self.terrain_path((x, y), (_x, _y), terrain_restriction, n):                
                    yield _x, _y                                                                    
    
    def terrain_path(self, origin, destination, terrain_restriction, n = 5):
        """
        Determens if there is a path to a certain place given terrain restrictions.
        """
        
        if origin == destination:
            return True
        
        current_neighbours = []
        visited = [origin]
        adjacents = self.adjacent_move(origin, visited, terrain_restriction)


        while n > 0 and adjacents != []:
            for adjacent in adjacents:
                if adjacent == destination:
                    return True
                adj = self.adjacent_move(adjacent, visited, terrain_restriction)
                for position in adj:                                             
                    visited.append(position)
                    current_neighbours.append(position)
            adjacents = current_neighbours                      
            current_neighbours = []                                         
            n -= 1                                                     
        return False                                                        

    def get_terrain(self, square):                      
        return self.terrain[square[1]][square[0]]       

    def adjacent_move(self, position, visited, terrain_restriction):
        """
        Get adjacent legal moves.                                                                                                                        
        """
        x = position[0]
        y = position[1] 

        adjactent_places = []
        for i in [-1, 1]:     
            if y + i >= 0 and y + i < 50 and (x, y + i) not in visited and self.get_terrain((x, y + i)) not in terrain_restriction:      #     (adj_x, position[1]) not in pathed and (adj_x, position[1]) not in current_path:
                adjactent_places.append((x, y + i))

            if x + i >= 0 and x + i < 50 and (x + i, y) not in visited and self.get_terrain((x + i, y)) not in terrain_restriction: #(position[0], adj_y) not in pathed and (position[0], adj_y) not in current_path:
                adjactent_places.append((x + i, y))    

        return adjactent_places  

    def empty_cells(self, _organism, n):
        """
        Equivalent to `reachable_cells`, but only yields cells that are not occupied.
        """
        for x, y in self.reachable_cells(_organism, n):
            if not self.grid[y][x]:
                yield x, y

    def sexual_reproduce(self, organism_1, organism_2):
        """
        generates an offspring using the genotype from both parents
        new offspring is placed in an unoccupied space in the vicinity of parents
        if there is no nearby empty cell, offspring is not created
        """
        if any(not _organism.can_reproduce or _organism.energy_level < _organism.size() for _organism in (organism_1, organism_2)):
            return

        cells = list(self.empty_cells(organism_1, 1)) + \
            list(self.empty_cells(organism_2, 1))
        if not cells:
            return

        x, y = choice(cells)

        for _organism in (organism_1, organism_2):
            _organism.can_reproduce = False
            _organism.metabolize()

        # randomly select a gene from each parent
        genotype_1 = organism_1.get_genotype_values()
        genotype_2 = organism_2.get_genotype_values()
        combined_genotype = list(zip(genotype_1, genotype_2))
        child_genotype = [choice(_) for _ in combined_genotype]

        # chance for a mutation to occur
        if randint(0, 100) < MUTATION_RATE:
            target_gene = choice(range(len(child_genotype)))
            child_genotype[target_gene] = (
                (child_genotype[target_gene] + randint(-10, 10)) % MUTATION_RATE) + 1
        new_genotype = {trait: value for trait,
                        value in zip(TRAITS, child_genotype)}
        
        generation = max(organism_1.generation, organism_2.generation) + 1
        self.spawn_organism(x, y, STARTING_ENERGY_RATE, generation, new_genotype)

    def scatter_seeds(self, org):
        """
        method for photosynthesis organisms to reproduce
        excludes organisms that reproduce asexually
        """
        stationary = org.genome.phenotype[Movement] == Movement.STATIONARY

        if stationary:  # plant fills all empty cells in range with offpsring
            cells = list(self.empty_cells(org, 2))
            if not (cells and org.can_reproduce):
                return

            for x, y in cells:
                child_genotype = org.get_genotype_values()
                target_gene = choice(range(len(child_genotype)))
                child_genotype[target_gene] = min(max(
                    (child_genotype[target_gene] + randint(-10, 10)) % MUTATION_RATE, 1), GENE_LENGTH)
                new_genotype = {trait: value for trait,
                                value in zip(TRAITS, child_genotype)}
                self.spawn_organism(x, y, 1, org.generation + 1, new_genotype)
                org.metabolize()
            for cell in cells:                                                                      
                if self.grid[cell[0]][cell[1]] is None:
                    child_genotype = org.get_genotype_values()
                    target_gene = choice(range(len(child_genotype)))
                    child_genotype[target_gene] = min(max(
                        (child_genotype[target_gene] + randint(-10, 10)) % MUTATION_RATE, 1), GENE_LENGTH)
                    new_genotype = {trait: value for trait,              
                                    value in zip(TRAITS, child_genotype)} 
                    self.spawn_organism(cell[0], cell[1], 1, org.generation + 1, new_genotype)
                    org.metabolize()

        else:  # non-stationary photosynthesizer searches nearby cells for photosynthesizer, reproduces if found
            cells = list(self.reachable_cells(org, 1))
            empty_cells = list(self.empty_cells(org, 1))
            if not (cells and empty_cells and org.can_reproduce):
                return
            # location of current organisms appears in reachable_cells
            cells.remove((org.x, org.y))

            for x, y in cells:
                org_2 = self.grid[y][x]
                photosynthesizer = org_2 and org_2.genome.phenotype[EnergySource] == EnergySource.PHOTOSYNTHESIS
                same_species = org_2 and org.meet(org_2, self.species.organisms_labels) == Relationships.CONSPECIFIC
                if photosynthesizer and same_species:
                    genotype_1 = org.get_genotype_values()
                    genotype_2 = org_2.get_genotype_values()
                    combined_genotype = list(zip(genotype_1, genotype_2))
                    child_genotype = [choice(_) for _ in combined_genotype]                                                                                         
                        
                    # chance for a mutation to occur
                    if randint(0, 100) < MUTATION_RATE:                                         
                        target_gene = choice(range(len(child_genotype)))                           
                        child_genotype[target_gene] = (                                            
                            (child_genotype[target_gene] + randint(-10, 10)) % MUTATION_RATE) + 1   
                    new_genotype = {trait: value for trait,                                         
                                    value in zip(TRAITS, child_genotype)}                       

                    x, y = choice(empty_cells)

                    generation = max(org.generation, org_2.generation) + 1
                    self.spawn_organism(x, y, 2, generation, new_genotype)
                    org.metabolize()
                    break

    def asexual_reproduction(self, org):
        """
        only takes an organsim with asexual reproduction
        searches empty cells and splits the organism evenly among the cells by size and energy_level
        """
        cells = list(self.empty_cells(org, 1))
        if not (cells and org.can_reproduce):
            return

        # limited to splitting in up to 3 offspring
        parent_size = org.genome.genotype[Size]
        max_offspring = min(len(cells), 3)
        cells = sample(cells, max_offspring)
        new_sizes = (parent_size // max_offspring) % GENE_LENGTH
        new_sizes += 1 if new_sizes == 0 else 0
        new_energies = org.energy_level / (max_offspring + 1)

        # offspring will populate empty cells
        for x, y in cells:
            if self.grid[y][x] is None:
                child_genotype = org.get_genotype_values()
                child_genotype[5] = new_sizes
                target_gene = choice(range(len(child_genotype) - 1)) # asexual size wont mutate
                mutation_value = (child_genotype[target_gene] + randint(-20, 20)) % GENE_LENGTH
                mutation_value += 1 if mutation_value == 0 else 0
                child_genotype[target_gene] = mutation_value
                new_genotype = {trait: value for trait,
                                value in zip(TRAITS, child_genotype)}
                self.spawn_organism(x, y, new_energies, org.generation + 1, new_genotype)
                # temporary, need a better way to split parent energy
                org.energy_level = new_energies
        # TODO: UPDATE PARENT SIZE AND ENERGY

    def move_organism(self, _organism, dx, dy):
        """
        Move the given `_organism` to its current location plus `dx, dy`.
        This new location must be within bounds of `self.grid`.
        The organism `metabolize`s by the number of cells moved.
        If its new cell is non-empty, handle collision.
        """                                                                 
        x, y = _organism.x + dx, _organism.y + dy
        cell = self.grid[y][x]

        if cell and not cell.genome.phenotype[EnergySource] == EnergySource.PHOTOSYNTHESIS:
            self.collide(_organism, cell)
        else:
            if cell:
                cell.alive = False
                self.remove_from_cell(cell)
            self.remove_from_cell(_organism)
            _organism.metabolize()
            _organism.update_location(x, y)
            self.insert_to_cell(_organism)                      

    def pathfind(self, _organism):
        """
        Search all cells within `VISIBLE_RANGE` for other organisms, choose an action, and then execute the action.

        Actions are determined by the relationship between organisms.
        The organism will move toward a `friendly` or `prey` organism and move away from a `predator` organism.
        The organism will prioritize the response to a `predator`, followed by `prey, and finally `friendly`.
        The organism will prioritize the response to an organism with the same relationship but is closer in `distance`.
        If no organism is found, the organism will wander `0` or `1` cells.

        TODO: separate relationships and actions
        TODO: write tests
        """
        x, y = _organism.get_location()
        _distance = 0
        action = Relationships.NEUTRAL
        _reachable_cells = self.reachable_cells(_organism, VISIBLE_RANGE)

        for _x, _y in _reachable_cells:
            cell = self.cell_content(_x, _y)
            if cell:
                _action = _organism.meet(cell, self.species.organisms_labels)
                __distance = distance((x, y), (_x, _y))
                if action.value < _action.value or (action.value == _action.value and __distance < _distance):
                    x, y = _x, _y
                    _distance = __distance
                    action = _action

        if (x, y) == _organism.get_location():
            wander = list(self.reachable_cells(_organism, 1))
            if wander:
                (x, y) = choice(wander)

        if action == Relationships.PREDATOR:
            dx, dy = 0, 0
            for _x, _y in _reachable_cells:
                __distance = distance((x, y), (_x, _y))
                if __distance > _distance:
                    _distance = __distance
                    dx, dy = _x - _organism.x, _y - _organism.y
        else:
            dx, dy = x - _organism.x, y - _organism.y

        if dx and abs(dx) > abs(dy):
            dx, dy = int(copysign(1, dx)), 0
        elif dy:
            dx, dy = 0, int(copysign(1, dy))

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
                if _organism.awake and _organism.genome.phenotype[Size] is not Movement.STATIONARY:
                    self.pathfind(_organism)
                if self.sun.is_day:
                    _organism.photosynthesize()
                _organism.metabolize()
                if _organism.alive and _organism.energy_level <= 0:
                    _organism.alive = False
                    self.remove_from_cell(_organism)
                if self.frame % 3 == 0:  # added non-sexual reproduction here since self.organisms is being iterated through
                    if _organism.genome.phenotype[Reproduction] == Reproduction.ASEXUAL:
                        self.asexual_reproduction(_organism)
                    elif _organism.genome.phenotype[EnergySource] == EnergySource.PHOTOSYNTHESIS:
                        self.scatter_seeds(_organism)

        organisms = self.organisms.copy()
        self.organisms = []
        for _organism in organisms:
            if _organism.alive:
            # if _organism.alive and any(_organism in ls for ls in self.grid):
                _organism.can_reproduce = True
                self.organisms.append(_organism)

        if self.organisms:
            self.species.cluster(self.organisms)

    def cell_content(self, x, y):
        "Accepts tuple integers x and y where y is the yth list and x is the xth position in the yth list."
        return self.grid[y][x]

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
                else:
                    grid_str += f'[{str(id(cell))[-5:]}]'
            grid_str += '\n'
        print("Number of organisms", len(self.organisms))   
        return grid_str


if __name__ == '__main__':
    world = World()
    stop = False

    while True:
        print(world)
        # for organism in world.organisms:
        #    print(organism)
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
