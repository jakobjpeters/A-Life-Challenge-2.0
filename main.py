
from random import randint
from enum import Enum

N_ORGANISMS = 10
GRID_WIDTH = 10
GRID_HEIGHT = 10
GENES = Enum('Genes',[])

class Organism():
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.energy_level = 0
        self.genome = []
        self.troph_type = 'p' #h, c, o
        self.movement = 0
        self.vision = 0

    def update_location(self, new_x, new_y):
        self.x = new_x
        self.y = new_y

    def get_location(self):
        return self.x, self.y


    def __repr__(self) -> str:
        return str(id(self))[-4:]

    def __str__(self):
        attributes = ''
        attributes += f'Organism {self.__repr__()}:\n'
        attributes += f'  position:      x: {self.x}, y: {self.y}\n'
        attributes += f'  energy_level:  {self.energy_level}\n'
        attributes += f'  genome:        {self.genome}\n'
        return attributes

class World():
    organisms = [Organism(randint(0, GRID_WIDTH - 1), randint(0, GRID_HEIGHT - 1)) for _ in range(N_ORGANISMS)]
    grid = [[[] for __ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
    frame = 0

    def __init__(self):
        for _organism in self.organisms:
            self.insert_to_cell(_organism)

    def get_cell(self, _organism):
        return self.grid[_organism.y][_organism.x]

    def insert_to_cell(self, _organism):
        self.get_cell(_organism).append(_organism)

    def remove_from_cell(self, _organism):
        self.get_cell(_organism).remove(_organism)

    def kill(self, _organism):
        self.organisms.remove(_organism)
        self.remove_from_cell(_organism)

    def get_movement(self, _organism):
        # dx = randint(0, _organism.movement)
        # dy = _organism.movement - dx
        # return min(GRID_WIDTH, dx), min(GRID_HEIGHT, dy)
        pass

    def collide(self, x, y):
        pass

    def move_organism(self, _organism):
        dx, dy = self.get_movement(_organism)
        self.remove_from_cell(_organism)
        x, y = _organism.x + dx, _organism.y + dy
        _organism.x, _organism.y = x, y
        self.insert_to_cell(_organism)

        if len(self.grid[y][x]) > 1:
            self.collide(x, y)


    def update(self):
        self.frame += 1

        for _organism in self.organisms:
            _organism.energy_level -= 1
            if _organism.energy_level <= 0:
                self.kill(_organism)
            else:
                self.move_organism(_organism)

    def save(self):
        pass

    def __str__(self):
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
    world = World()
    stop = False
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
