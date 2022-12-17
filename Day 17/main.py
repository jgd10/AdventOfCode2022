from dataclasses import dataclass
from collections import namedtuple
import matplotlib.pyplot as plt


Cell = namedtuple('Cell', 'x, y')


# @dataclass
# class Cell:
#     x: int
#     y: int
#
#     @property
#     def neighbours(self):
#         neighbours = [
#             Cell(self.x + 1, self.y),
#             Cell(self.x - 1, self.y),
#             Cell(self.x, self.y + 1),
#             Cell(self.x, self.y - 1)
#             ]
#         return neighbours


SHAPES = [
    [Cell(i, 0) for i in range(4)],
    [Cell(1, 0), Cell(0, 1), Cell(1, 1), Cell(2, 1), Cell(1, 2)],
    [Cell(0, 0), Cell(1, 0), Cell(2, 0), Cell(2, 1), Cell(2, 2)],
    [Cell(0, i) for i in range(4)],
    [Cell(0, 0), Cell(0, 1), Cell(1, 1), Cell(1, 0)]
]


@dataclass
class Rock:
    origin: Cell
    _origin_cells: list[Cell]
    falling: bool = True
    last_move: tuple[int, int] = (0, 0)

    @classmethod
    def from_shape(cls, num):
        origin = Cell(0, 0)
        cells = SHAPES[num - 1]
        return cls(origin, cells)

    def move(self, dx, dy):
        self.last_move = (dx, dy)
        self.origin = Cell(self.origin.x + dx, self.origin.y + dy)

    def undo_last_move(self):
        dx, dy = self.last_move
        self.move(-1*dx, -1*dy)

    def jet_push(self, jet: str):
        if jet == '>':
            self.move(1, 0)
        else:
            self.move(-1, 0)

    def drop(self):
        self.move(0, -1)

    # def perimeter_cells(self):
    #     perimeter_cells = []
    #     for cell in self.cells:
    #         neighbours = [c for c in cell.neighbours
    #                       if c not in perimeter_cells
    #                       or c not in self.cells]
    #         perimeter_cells.extend(neighbours)
    #     return perimeter_cells

    @property
    def cells(self):
        return [Cell(self.origin.x + c.x, self.origin.y + c.y)
                for c in self._origin_cells]


@dataclass
class Chamber:
    fixed_cells: list[list[Cell]]
    _jets: str
    _current_jet: int = 0
    width: int = 7
    origin: Cell = Cell(0, 0)
    walls: tuple[int, int] = 0, 8
    _current_rock: int = 0

    @property
    def current_jet(self):
        jet = self._jets[self._current_jet]
        self._current_jet += 1
        if self._current_jet >= len(self._jets):
            self._current_jet = 0
        return jet

    @property
    def current_rock(self):
        self._current_rock += 1
        if self._current_rock > 5:
            self._current_rock = 1
        return self._current_rock

    def spawn_x_rocks(self, x: int):
        for i in range(x):
            self.spawn_rock()
        return self.max_height

    @property
    def max_height(self):
        height = len(self.fixed_cells)
        return height

    @property
    def spawn_height(self):
        return self.max_height + 3 + 1

    def spawn_rock(self):
        rock = Rock.from_shape(self.current_rock)
        rock.origin = Cell(1 + 2, self.spawn_height)
        # self.visualise(rock)
        while rock.falling:
            jet = self.current_jet
            rock.jet_push(jet)
            # self.visualise(rock)
            col = self.check_collisions(rock)
            if col:
                rock.undo_last_move()
            rock.drop()
            # self.visualise(rock)
            col = self.check_collisions(rock)
            if col:
                rock.undo_last_move()
                self.set_rock_resting_place(rock)
                #print(self.max_height)
                #self.visualise(rock)

    def check_collisions(self, rock: Rock):
        for cell in rock.cells:
            if cell.x <= 0:
                return True
            if cell.x > self.width:
                return True
            if cell.y <= 0:
                return True
            if any([cell in row for row in self.fixed_cells]):
                return True
        return False

    def set_rock_resting_place(self, rock: Rock):
        ys = list({c.y for c in rock.cells})
        ys.sort()
        for y in ys:
            new_cells = [c for c in rock.cells if c.y == y]
            if y <= self.max_height:
                self.fixed_cells[y-1].extend(new_cells)
            else:
                self.fixed_cells.append(new_cells)
        rock.falling = False

    def visualise(self, rock: Rock = None):
        fig = plt.figure()
        ax: plt.Axes = fig.add_subplot(111)
        ax.set_aspect(1.0)
        ax.axhline(y=0, color='k')
        ax.axvline(x=0, color='k')
        ax.axvline(x=8, color='k')
        x = [c.x for row in self.fixed_cells for c in row]
        y = [c.y for row in self.fixed_cells for c in row]
        ax.plot(x, y, linestyle=' ', marker='s', color='r')
        if rock is not None:
            xx = [c.x for c in rock.cells]
            yy = [c.y for c in rock.cells]
            ax.plot(xx, yy, linestyle=' ', marker='s', color='b')
        ax.set_xticks([0, 1, 2, 3, 4, 5, 6, 7, 8])
        ax.set_yticks([i for i in range(18)])
        ax.set_ylim(0, 17)
        ax.grid()
        plt.show()

    def visualise_top(self, rock: Rock = None):
        fig = plt.figure()
        ax: plt.Axes = fig.add_subplot(111)
        ax.set_aspect(1.0)
        ax.axhline(y=0, color='k')
        ax.axhline(y=8, color='k')
        x = [c.x for c in self.fixed_cells if c.y == self.max_height]
        y = [c.y for c in self.fixed_cells if c.y == self.max_height]
        ax.axhline(y=self.max_height, color='c')
        ax.set_ylim(self.max_height-2, self.max_height+2)
        ax.plot(x, y, linestyle=' ', marker='s', color='r')
        ax.set_xticks([0, 1, 2, 3, 4, 5, 6, 7, 8])
        ax.grid()
        plt.show()


def main():
    with open('test.txt') as f:
        jets = f.read().strip('\n')
    chamber = Chamber([], jets)
    height0 = chamber.spawn_x_rocks(2022)
    print(height0)


    # chamber.visualise_top()

    # chamber.visualise()

main()
