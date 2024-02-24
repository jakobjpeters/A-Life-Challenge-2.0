
import unittest
from main import *

X, Y = 1, 2
N_ORGANISMS = 100
N_SPECIES = 10

class TestOrganism(unittest.TestCase):
    organism = Organism(X, Y, STARTING_ENERGY_RATE)

    def test_init(self):
        organism = Organism(X, Y, STARTING_ENERGY_RATE)
        self.assertEqual(organism.x, X)
        self.assertEqual(organism.y, Y)

    def test_update_location(self):
        self.organism.update_location(3, 4)
        self.assertEqual(self.organism.x, 3)
        self.assertEqual(self.organism.y, 4)

    def test_get_location(self):
        x, y = self.organism.get_location()
        self.assertEqual(self.organism.x, x)
        self.assertEqual(self.organism.y, y)

class TestWorld(unittest.TestCase):
    world = World(N_ORGANISMS, N_SPECIES)

    def test_init(self):
        self.assertEqual(self.world.frame, 0)
        self.assertEqual(len(self.world.organisms), N_ORGANISMS)
        self.assertEqual(len(self.world.grid), GRID_HEIGHT)
        for row in self.world.grid:
            self.assertTrue(len(row) == GRID_WIDTH)

    def test_insert_to_cell(self):
        organism = Organism(X, Y, STARTING_ENERGY_RATE)
        self.assertNotEqual(organism, self.world.cell_content(X, Y))
        self.world.insert_to_cell(organism)
        self.assertEqual(organism, self.world.cell_content(X, Y))

    def test_remove_from_cell(self):
        organism = self.world.organisms[0]
        self.world.remove_from_cell(organism)
        self.assertNotEqual(organism, self.world.cell_content(X, Y))
        self.world.insert_to_cell(organism)

    def test_update(self):
        frame = self.world.frame
        self.world.update()
        self.assertEqual(self.world.frame, frame + 1)

class TestMeet(unittest.TestCase):
    def setUp(self):
        self.organism_1 = Organism(0, 0, STARTING_ENERGY_RATE)
        self.organism_2 = Organism(0, 0, STARTING_ENERGY_RATE)

        # Different skin options to make different 'species' by default
        self.organism_1.genome.phenotype[Skin] = Skin.FUR
        self.organism_2.genome.phenotype[Skin] = Skin.SHELL

    def test_herbivore_eats_smaller_plant(self):
        self.organism_1.genome.phenotype[EnergySource] = EnergySource.HERBIVORE
        self.organism_1.genome.phenotype[Size] = Size.TWO
        self.organism_2.genome.phenotype[EnergySource] = EnergySource.PHOTOSYNTHESIS
        self.organism_2.genome.phenotype[Size] = Size.ONE
        relationship = self.organism_1.meet(self.organism_2, {self.organism_1: 1, self.organism_2: 2})
        self.assertEqual(relationship, Relationships.PREY)

    def test_smaller_plant_eaten_by_herbivore(self):
        self.organism_1.genome.phenotype[EnergySource] = EnergySource.PHOTOSYNTHESIS
        self.organism_2.genome.phenotype[EnergySource] = EnergySource.HERBIVORE
        self.organism_1.genome.phenotype[Size] = Size.ONE
        self.organism_2.genome.phenotype[Size] = Size.TWO
        relationship = self.organism_1.meet(self.organism_2, {self.organism_1: 1, self.organism_2: 2})
        self.assertEqual(relationship, Relationships.PREDATOR)

    def test_herbivore_cannot_eat_larger_plant(self):
        self.organism_1.genome.phenotype[EnergySource] = EnergySource.HERBIVORE
        self.organism_2.genome.phenotype[EnergySource] = EnergySource.PHOTOSYNTHESIS
        self.organism_1.genome.phenotype[Size] = Size.ONE
        self.organism_2.genome.phenotype[Size] = Size.TWO
        relationship = self.organism_1.meet(self.organism_2, {self.organism_1: 1, self.organism_2: 2})
        self.assertEqual(relationship, Relationships.NEUTRAL)

    def test_omnivore_eats_smaller_carnivore(self):
        self.organism_1.genome.phenotype[EnergySource] = EnergySource.OMNIVORE
        self.organism_2.genome.phenotype[EnergySource] = EnergySource.CARNIVORE
        self.organism_1.genome.phenotype[Size] = Size.TWO
        self.organism_2.genome.phenotype[Size] = Size.ONE
        relationship = self.organism_1.meet(self.organism_2, {self.organism_1: 1, self.organism_2: 2})
        self.assertEqual(relationship, Relationships.PREY)

    def test_equal_omnivore_carnivore_do_not_eat(self):
        self.organism_1.genome.phenotype[EnergySource] = EnergySource.OMNIVORE
        self.organism_2.genome.phenotype[EnergySource] = EnergySource.CARNIVORE
        self.organism_1.genome.phenotype[Size] = Size.ONE
        self.organism_2.genome.phenotype[Size] = Size.ONE
        relationship = self.organism_1.meet(self.organism_2, {self.organism_1: 1, self.organism_2: 2})
        self.assertEqual(relationship, Relationships.NEUTRAL)

    def test_larger_omnivore_eats_smaller_omnivore(self):
        self.organism_1.genome.phenotype[EnergySource] = EnergySource.OMNIVORE
        self.organism_2.genome.phenotype[EnergySource] = EnergySource.OMNIVORE
        self.organism_1.genome.phenotype[Size] = Size.TWO
        self.organism_2.genome.phenotype[Size] = Size.ONE
        relationship = self.organism_1.meet(self.organism_2, {self.organism_1: 1, self.organism_2: 2})
        self.assertEqual(relationship, Relationships.PREY)

    def test_no_cannibalism(self):
        self.organism_1.genome.phenotype[EnergySource] = EnergySource.OMNIVORE
        self.organism_1.genome.phenotype = self.organism_2.genome.phenotype
        self.organism_1.genome.phenotype[Size] = Size.TWO
        self.organism_2.genome.phenotype[Size] = Size.ONE
        relationship = self.organism_1.meet(self.organism_2, {self.organism_1: 1, self.organism_2: 1})
        self.assertEqual(relationship, Relationships.CONSPECIFIC)


if __name__ == '__main__':
    unittest.main()
