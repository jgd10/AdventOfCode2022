import math
from dataclasses import dataclass
from enum import Enum
import random
from typing import Tuple, List, Dict

height_map = {k: i for i, k in enumerate('abcdefghijklmnopqrstuvwxyz')}
HEIGHT_MAP = {**height_map, 'E': 25, 'S': 0}


class Ends:
    START = 0
    MIDPOINT = 1
    END = 2


@dataclass
class Square:
    coordinate: Tuple[int, int]
    height: int
    letter: str
    paths: Dict[str, Tuple[Tuple[int, int], bool]]
    position: int
    visited: int = 0

    @classmethod
    def from_coord(cls, coord, grid: List[List[int]]):
        n = len(grid[0])
        m = len(grid)
        i, j = coord
        letter = grid[j][i]
        value = HEIGHT_MAP[letter]
        if grid[j][i] == 'E':
            end_ = Ends.END
        elif grid[j][i] == 'S':
            end_ = Ends.START
        else:
            end_ = Ends.MIDPOINT
        north, south, east, west = True, True, True, True
        n_coord, s_coord, e_coord, w_coord = (i, j-1), (i, j+1),\
                                             (i+1, j), (i-1, j)
        if i-1 < 0:
            west = False
        else:
            west_val = HEIGHT_MAP[grid[j][i-1]]

        if i+1 >= n:
            east = False
        else:
            east_val = HEIGHT_MAP[grid[j][i+1]]

        if j-1 < 0:
            north = False
        else:
            north_val = HEIGHT_MAP[grid[j-1][i]]

        if j+1 >= m:
            south = False
        else:
            south_val = HEIGHT_MAP[grid[j+1][i]]

        if north and (north_val - value) > 1:
            north = False
        if south and (south_val - value) > 1:
            south = False
        if east and (east_val - value) > 1:
            east = False
        if west and (west_val - value) > 1:
            west = False
        paths = {'N': (n_coord, north), 'S': (s_coord, south),
                 'E': (e_coord, east), 'W': (w_coord, west)}

        return cls(coord, value, letter, paths, end_)

    @staticmethod
    def separation_between_coords(start, end):
        xdiff = end[0] - start[0]
        ydiff = end[1] - start[1]
        return math.sqrt(xdiff**2 + ydiff**2)

    def decide_next(self, destination, grid):
        available_paths = {}
        for direction, path in self.paths.items():
            coord, available = path
            if available:
                available_paths[direction] = coord

        height_changes = {k: self.height-grid[c].height
                          for k, c in available_paths.items()}

        net_increase = []
        net_nochange = []
        net_decrease = []
        for direction, change in height_changes.items():
            if change < 0:
                net_increase.append(direction)
            elif change == 0:
                net_nochange.append(direction)
            else:
                net_decrease.append(direction)
        if len(net_increase) == 1:
            return available_paths[net_increase[0]]
        elif len(net_increase) > 1:
            available_paths = {k: available_paths[k] for k in net_increase}

        if not net_increase and len(net_nochange) == 1:
            return available_paths[net_nochange[0]]
        elif not net_increase and len(net_nochange) > 1:
            available_paths = {k: available_paths[k] for k in net_nochange}

        least_visited = {}
        num_visits = 999
        for direction in available_paths:
            square = grid[available_paths[direction]]
            num_visits = min(num_visits, square.visited)
            least_visited[direction] = square.visited

        least_visited = [k for k, v in least_visited.items() if
                         v == num_visits]
        if len(least_visited) == 1:
            return available_paths[least_visited[0]]

        distance = 999
        path_distances = {}
        for direction, coord in available_paths.items():
            new = self.separation_between_coords(coord, destination.coordinate)
            path_distances[direction] = new
            distance = min(distance, new)

        closest_paths = [k for k, v in path_distances.items() if v == distance]
        if len(closest_paths) == 1:
            return available_paths[closest_paths[0]]
        else:
            possible_paths = [available_paths[k] for k in closest_paths]
            return random.choice(possible_paths)


def main():
    with open('input.txt') as f:
        data = [s.strip('\n') for s in f.readlines()]

    grid = [list(row) for row in data]
    squares = {}
    for j, row in enumerate(grid):
        for i, val in enumerate(row):
            squares[(i, j)] = Square.from_coord((i, j), grid)
            assert squares[(i, j)].letter == val

    start = [s for s in squares.values() if s.position == Ends.START][0]
    end = [s for s in squares.values() if s.position == Ends.END][0]
    my_square = start
    counter = 0
    while my_square.position != Ends.END:
        my_square.visited += 1
        my_coord = my_square.decide_next(end, squares)
        my_square = squares[my_coord]
        print(my_coord, my_square.letter)
        counter += 1
    return counter


print(main())
