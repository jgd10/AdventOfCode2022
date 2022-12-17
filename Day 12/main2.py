import numpy as np
from dataclasses import dataclass


height_map = {k: i for i, k in enumerate('abcdefghijklmnopqrstuvwxyz')}
HEIGHT_MAP = {**height_map, 'E': 25, 'S': 0}


class Ends:
    START = 0
    MIDPOINT = 1
    END = 2


class Cell:
    def __init__(self, coord, letter, height, end, visited, tentative_distance):
        self.coord: tuple[int, int] = coord
        self.letter: str = letter
        self.height: int = height
        self.end: int = end
        self.visited: bool = visited
        self.tentative_distance: int = tentative_distance
        self.north: 'Cell' = None
        self.south: 'Cell' = None
        self.east: 'Cell' = None
        self.west: 'Cell' = None

    def set_as_start(self):
        self.height = 0
        self.end = Ends.START
        self.visited = True
        self.tentative_distance = 0

    def set_as_mid(self):
        self.height = HEIGHT_MAP[self.letter]
        self.end = Ends.MIDPOINT
        self.visited = False
        self.tentative_distance = 999999

    def __repr__(self):
        return f'Cell({self.coord}, {self.letter}, ' \
               f'{self.height}, {self.visited}, {self.tentative_distance})'

    @property
    def neighbours(self):
        neighbours = []
        for neighbour in [self.north, self.south, self.east, self.west]:
            if neighbour is not None and not neighbour.visited:
                height_diff = neighbour.height - self.height
                if height_diff <= 1:
                    neighbours.append(neighbour)
        return neighbours

    @property
    def all_neighbours(self):
        neighbours = []
        for neighbour in [self.north, self.south, self.east, self.west]:
            if neighbour is not None:
                neighbours.append(neighbour)
        return neighbours


def calc_distance(height0, height1):
    diff = height1 - height0
    if diff > 1:
        return 999999
    else:
        return 1


def smallest_distance(neighbours: list[Cell]):
    neighbours.sort(key=lambda x: x.tentative_distance, reverse=False)
    return neighbours[0]


def calc_largest_distance_to_a(cells: list[Cell]):
    cells = [c for c in cells if c.letter == 'a' and 'b' in [n.letter for n in c.all_neighbours]]
    cells.sort(key=lambda x: x.tentative_distance, reverse=True)
    return cells


def main():
    cells = setup_graph()
    current = [c for c in cells.values() if c.end == Ends.START][0]
    cells = [c for c in cells.values()]
    part1, sorted_cells = dijkstra(cells, current)

    largest_as = calc_largest_distance_to_a(sorted_cells)

    part2s = []
    print(len(largest_as))
    for c in largest_as:
        cells = setup_graph()
        start = [c for c in cells.values() if c.end == Ends.START][0]
        start.set_as_mid()
        start = cells[c.coord]
        start.set_as_start()
        cells = [c for c in cells.values()]
        part2, _ = dijkstra(cells, start)
        part2s.append(part2)
    min_val = 999999
    for val in part2s:
        min_val = min(min_val, val)
    print(min_val)


def setup_graph():
    with open('input.txt') as f:
        data = [s.strip('\n') for s in f.readlines()]
        data = [[c for c in row] for row in data]
    data = np.array(data)
    cells = {}
    n, m = data.shape
    for i in range(n):
        for j in range(m):
            tentative = 999999
            if data[i, j] == 'E':
                visited = False
                end = Ends.END
            elif data[i, j] == 'S':
                visited = True
                end = Ends.START
                tentative = 0
            else:
                visited = False
                end = Ends.MIDPOINT
            cells[(i, j)] = Cell((i, j),
                                 data[i, j],
                                 HEIGHT_MAP[data[i, j]],
                                 end,
                                 visited,
                                 tentative)
    for coord, cell in cells.items():
        i, j = coord[0], coord[1]
        cell.north = cells[(i, j - 1)] if (i, j - 1) in cells else None
        cell.south = cells[(i, j + 1)] if (i, j + 1) in cells else None
        cell.east = cells[(i + 1, j)] if (i + 1, j) in cells else None
        cell.west = cells[(i - 1, j)] if (i - 1, j) in cells else None
    return cells


def dijkstra(cells, current):
    sorted_cells = []
    while True:
        for cell in current.neighbours:
            tent_dist = calc_distance(current.height,
                                      cell.height) + current.tentative_distance
            cell.tentative_distance = tent_dist \
                if tent_dist < cell.tentative_distance \
                else cell.tentative_distance

        current.visited = True
        cells.remove(current)
        sorted_cells.append(current)
        next_cell = smallest_distance(cells)
        if next_cell.end == Ends.END:
            end_not_found = False
            break
        current = next_cell
    return next_cell.tentative_distance, sorted_cells


main()
