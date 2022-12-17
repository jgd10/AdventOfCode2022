from dataclasses import dataclass
from collections import namedtuple
import matplotlib.pyplot as plt


Cell = namedtuple('Cell', 'x, y')


def subtract_cells(cell1, cell2):
    return Cell(cell2.x - cell1.x, cell2.y - cell1.y)

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


L = 1000000000000

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
class Well:
    base: int
    cells: list[list[Cell]]

    def __repr__(self):
        return f'Well(base={self.base}, rows={len(self.cells)})'

    @property
    def top(self):
        maxy = max([c.y for row in self.cells for c in row])
        return self.base + maxy

    @classmethod
    def from_rows(cls, rows, origin):
        cells = [[Cell(c.x, c.y-origin) for c in row] for row in rows]
        return cls(origin, cells)

    def __eq__(self, other):
        return self.cells == other.cells

    def visualise(self):
        fig = plt.figure()
        ax: plt.Axes = fig.add_subplot(111)
        ax.set_aspect(1.0)
        ax.axhline(y=0, color='k')
        ax.axvline(x=0, color='k')
        ax.axvline(x=8, color='k')
        x = [c.x for row in self.cells for c in row]
        y = [c.y for row in self.cells for c in row]
        ax.plot(x, y, linestyle=' ', marker='s', color='r')
        ax.set_xticks([0, 1, 2, 3, 4, 5, 6, 7, 8])
        ax.set_yticks([i for i in range(max(y)+1)])
        ax.set_ylim(0, max(y))
        ax.grid()
        plt.show()


@dataclass
class GameState:
    well: Well
    rock: int
    jet: int
    rocks_spawned: int

    def __eq__(self, other):
        return self.well == other.well \
               and self.rock == other.rock \
               and self.jet == other.jet

    def visualise(self):
        self.well.visualise()


@dataclass
class Chamber:
    fixed_cells: list[list[Cell]]
    _jets: str
    _current_jet: int = 0
    _rocks_spawned: int = 0
    width: int = 7
    origin: Cell = Cell(0, 0)
    walls: tuple[int, int] = 0, 8
    _current_rock: int = 0
    game_states: list[GameState] = None
    baseline: int = 0
    extra_height: int = 0
    extra_cycles_initiated: bool = False

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
        while self.rocks_spawned < x:
            self.spawn_rock()
        return self.max_height_with_extra

    @property
    def max_height(self):
        height = len(self.fixed_cells)
        return height

    @property
    def max_height_with_extra(self):
        height = len(self.fixed_cells) + self.extra_height
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
                game_state = self.get_game_state()
                self.set_rock_resting_place(rock)
                self._rocks_spawned += 1
                new_state = self.get_game_state()
                if new_state.well.base > game_state.well.base:
                    # game_state.visualise()
                    self.store_state(game_state)
                # print(self.max_height)
                # self.visualise(rock)

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

    def get_game_state(self):
        if self.game_states is None:
            self.game_states = []
        return GameState(self.current_well,
                         self._current_rock,
                         self._current_jet,
                         self.rocks_spawned)

    @property
    def rocks_spawned(self):
        return self._rocks_spawned

    def store_state(self, state: GameState):
        if state in self.game_states and not self.extra_cycles_initiated:
            self.extra_cycles_initiated = True
            matched = [g for g in self.game_states if g == state][0]
            dy = state.well.top - matched.well.top
            dt = state.rocks_spawned - matched.rocks_spawned
            num_iterations = (L - state.rocks_spawned) // dt
            self.extra_height = num_iterations * dy
            self._rocks_spawned += num_iterations * dt
            print(self.extra_height, self.rocks_spawned)
        self.game_states.append(state)

    @property
    def current_well(self):
        start = self.get_well_start()
        rows = self.fixed_cells[start-1:]
        new = Well.from_rows(rows, start)
        return new

    def get_well_start(self):
        top_down_rows = self.fixed_cells[::-1]
        filled_cols = {i+1: 0 for i in range(self.width)}
        j = 1
        while not all([filled for filled in filled_cols.values()]):
            if j >= len(top_down_rows):
                break
            row = top_down_rows[j-1]
            for cell in row:
                filled_cols[cell.x] = j
            j += 1
        well_start = self.max_height - j
        return max(well_start, 0)

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
    with open('input.txt') as f:
        jets = f.read().strip('\n')
    chamber = Chamber([], jets)
    height0 = chamber.spawn_x_rocks(L)
    print(height0)


    # chamber.visualise_top()

    # chamber.visualise()

main()
