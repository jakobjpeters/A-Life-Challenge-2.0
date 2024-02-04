
import unittest
from main import *

X, Y = 1, 2

class TestOrganism(unittest.TestCase):
    organism = Organism(X, Y)

    def test_init(self):
        organism = Organism(X, Y)
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
    world = World()

    def test_init(self):
        self.assertEqual(self.world.frame, 0)
        self.assertEqual(len(self.world.organisms), N_ORGANISMS)
        self.assertEqual(len(self.world.grid), GRID_HEIGHT)
        for row in self.world.grid:
            self.assertTrue(len(row) == GRID_WIDTH)

    def test_get_cell(self):
        for organism in self.world.organisms:
            self.assertIn(organism, self.world.get_cell(organism))

    def test_insert_to_cell(self):
        organism = Organism(X, Y)
        cell = self.world.get_cell(organism)
        self.assertNotIn(organism, cell)
        self.world.insert_to_cell(organism)
        self.assertIn(organism, cell)

    def test_remove_from_cell(self):
        organism = self.world.organisms[0]
        self.world.remove_from_cell(organism)
        self.assertNotIn(organism, self.world.get_cell(organism))
        self.world.insert_to_cell(organism)

    def test_kill(self):
        organism = self.world.organisms[0]
        self.world.kill(organism)
        self.assertNotIn(organism, self.world.organisms)
        self.assertNotIn(organism, self.world.get_cell(organism))

    def test_update(self):
        frame = self.world.frame
        self.world.update()
        self.assertEqual(self.world.frame, frame + 1)

class TestResolveFeeding(unittest.TestCase):
    def setUp(self):
        self.organism_1 = Organism(0, 0)
        self.organism_2 = Organism(0, 0)

        # Different skin options to make different 'species' by default
        self.organism_1.genome.phenotype[SKIN] = SKIN.fur
        self.organism_2.genome.phenotype[SKIN] = SKIN.shell

    def test_herbivore_eats_smaller_plant(self):
        self.organism_1.genome.phenotype[ENERGY_SOURCE] = ENERGY_SOURCE.herbivore
        self.organism_1.energy_level = 2
        self.organism_2.genome.phenotype[ENERGY_SOURCE] = ENERGY_SOURCE.photosynthesis
        self.organism_2.energy_level = 1
        prey = resolve_feeding(self.organism_1, self.organism_2)
        self.assertEqual(prey, self.organism_2)

    def test_smaller_plant_eaten_by_herbivore(self):
        self.organism_1.genome.phenotype[ENERGY_SOURCE] = ENERGY_SOURCE.photosynthesis
        self.organism_2.genome.phenotype[ENERGY_SOURCE] = ENERGY_SOURCE.herbivore
        self.organism_1.energy_level = 1
        self.organism_2.energy_level = 2
        prey = resolve_feeding(self.organism_1, self.organism_2)
        self.assertEqual(prey, self.organism_1)

    def test_herbivore_cannot_eat_larger_plant(self):
        self.organism_1.genome.phenotype[ENERGY_SOURCE] = ENERGY_SOURCE.herbivore
        self.organism_2.genome.phenotype[ENERGY_SOURCE] = ENERGY_SOURCE.photosynthesis
        self.organism_1.energy_level = 1
        self.organism_2.energy_level = 2
        prey = resolve_feeding(self.organism_1, self.organism_2)
        self.assertEqual(prey, None)

    def test_omnivore_eats_smaller_carnivore(self):
        self.organism_1.genome.phenotype[ENERGY_SOURCE] = ENERGY_SOURCE.omnivore
        self.organism_2.genome.phenotype[ENERGY_SOURCE] = ENERGY_SOURCE.carnivore
        self.organism_1.energy_level = 2
        self.organism_2.energy_level = 1
        prey = resolve_feeding(self.organism_1, self.organism_2)
        self.assertEqual(prey, self.organism_2)

    def test_equal_omnivore_carnivore_do_not_eat(self):
        self.organism_1.genome.phenotype[ENERGY_SOURCE] = ENERGY_SOURCE.omnivore
        self.organism_2.genome.phenotype[ENERGY_SOURCE] = ENERGY_SOURCE.carnivore
        self.organism_1.energy_level = 2
        self.organism_2.energy_level = 2
        prey = resolve_feeding(self.organism_1, self.organism_2)
        self.assertEqual(prey, None)

    def test_larger_omnivore_eats_smaller_omnivore(self):
        self.organism_1.genome.phenotype[ENERGY_SOURCE] = ENERGY_SOURCE.omnivore
        self.organism_2.genome.phenotype[ENERGY_SOURCE] = ENERGY_SOURCE.omnivore
        self.organism_1.energy_level = 2
        self.organism_2.energy_level = 1
        prey = resolve_feeding(self.organism_1, self.organism_2)
        self.assertEqual(prey, self.organism_2)

    def test_no_cannibalism(self):
        self.organism_1.genome.phenotype[ENERGY_SOURCE] = ENERGY_SOURCE.omnivore
        self.organism_1.genome.phenotype = self.organism_2.genome.phenotype
        self.organism_1.energy_level = 2
        self.organism_2.energy_level = 1
        prey = resolve_feeding(self.organism_1, self.organism_2)
        self.assertEqual(prey, None)


if __name__ == '__main__':
    unittest.main()
