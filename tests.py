
import unittest
import main

X, Y = 1, 2

class TestOrganism(unittest.TestCase):
    organism = main.Organism(X, Y)

    def test_init(self):
        organism = main.Organism(X, Y)
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
    world = main.World()

    def test_init(self):
        self.assertEqual(self.world.frame, 0)
        self.assertEqual(len(self.world.organisms), main.N_ORGANISMS)
        self.assertEqual(len(self.world.grid), main.GRID_HEIGHT)
        for row in self.world.grid:
            self.assertTrue(len(row) == main.GRID_WIDTH)

    def test_get_cell(self):
        for organism in self.world.organisms:
            self.assertIn(organism, self.world.get_cell(organism))

    def test_insert_to_cell(self):
        organism = main.Organism(X, Y)
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

if __name__ == '__main__':
    unittest.main()
