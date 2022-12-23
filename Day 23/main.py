from dataclasses import dataclass
from collections import namedtuple
from enum import Enum
from matplotlib import pyplot as plt


class Direction(Enum):
    NORTH = 3
    WEST = 2
    SOUTH = 1
    EAST = 0


Coord = namedtuple('Coord', 'x, y')


@dataclass
class Elf:
    coord: Coord
    _directions_for_consideration: list[Direction] = None

    @property
    def directions(self):
        if self._directions_for_consideration is None:
            self._directions_for_consideration = [Direction.NORTH,
                                                  Direction.SOUTH,
                                                  Direction.WEST,
                                                  Direction.EAST]
        return self._directions_for_consideration

    def rotate_directions(self):
        if self._directions_for_consideration is None:
            self._directions_for_consideration = [Direction.NORTH,
                                                  Direction.SOUTH,
                                                  Direction.WEST,
                                                  Direction.EAST]
        else:
            next_dir = self._directions_for_consideration.pop(0)
            self._directions_for_consideration.append(next_dir)

    def get_direction(self):
        if self._directions_for_consideration is None:
            self._directions_for_consideration = [Direction.NORTH,
                                                  Direction.SOUTH,
                                                  Direction.WEST,
                                                  Direction.EAST]

        next_dir = self._directions_for_consideration.pop(0)
        self._directions_for_consideration.append(next_dir)
        return next_dir

    def proposed_step(self, direction: Direction):
        match direction:
            case Direction.NORTH:
                newx, newy = self.coord.x, self.coord.y - 1
            case Direction.SOUTH:
                newx, newy = self.coord.x, self.coord.y + 1
            case Direction.WEST:
                newx, newy = self.coord.x - 1, self.coord.y
            case Direction.EAST:
                newx, newy = self.coord.x + 1, self.coord.y
        return Coord(newx, newy)

    def step(self, direction: Direction):
        new = self.proposed_step(direction)
        self.coord = new

    def get_neighbour_points(self):
        newx, newy = self.coord.x, self.coord.y - 1
        coord1 = Coord(newx, newy)
        newx, newy = self.coord.x, self.coord.y + 1
        coord2 = Coord(newx, newy)
        newx, newy = self.coord.x - 1, self.coord.y
        coord3 = Coord(newx, newy)
        newx, newy = self.coord.x + 1, self.coord.y
        coord4 = Coord(newx, newy)

        newx, newy = self.coord.x - 1, self.coord.y - 1
        coord5 = Coord(newx, newy)
        newx, newy = self.coord.x - 1, self.coord.y + 1
        coord6 = Coord(newx, newy)
        newx, newy = self.coord.x + 1, self.coord.y - 1
        coord7 = Coord(newx, newy)
        newx, newy = self.coord.x + 1, self.coord.y + 1
        coord8 = Coord(newx, newy)
        return {Direction.NORTH: {coord1, coord5, coord7},
                Direction.SOUTH: {coord2, coord6, coord8},
                Direction.EAST: {coord4, coord7, coord8},
                Direction.WEST: {coord3, coord5, coord6}}, \
               {coord1, coord2, coord3, coord4, coord5, coord6, coord7, coord8}


@dataclass
class Mesh:
    elves: list[Elf]
    proposed: dict[Coord, list[Elf]] = None
    _directions_for_consideration: list[Direction] = None

    @property
    def area(self):
        imin = min([e.coord.x for e in self.elves])
        jmin = min([e.coord.y for e in self.elves])
        imax = max([e.coord.x for e in self.elves])
        jmax = max([e.coord.y for e in self.elves])
        return (jmax+1-jmin) * (imax+1-imin)

    def visualise(self):
        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.set_aspect('equal')
        elves_x = [e.coord.x for e in self.elves]
        elves_y = [e.coord.y for e in self.elves]
        ax.plot(elves_x, elves_y, linestyle=' ', marker='s', ms=8)
        ax.grid()
        plt.show()

    @property
    def directions(self):
        if self._directions_for_consideration is None:
            self._directions_for_consideration = [Direction.NORTH,
                                                  Direction.SOUTH,
                                                  Direction.WEST,
                                                  Direction.EAST]
        return self._directions_for_consideration

    def rotate_directions(self):
        if self._directions_for_consideration is None:
            self._directions_for_consideration = [Direction.NORTH,
                                                  Direction.SOUTH,
                                                  Direction.WEST,
                                                  Direction.EAST]
        else:
            next_dir = self._directions_for_consideration.pop(0)
            self._directions_for_consideration.append(next_dir)

    @property
    def coordinates(self):
        return {e.coord for e in self.elves}

    def rotate_elf_directions(self):
        for elf in self.elves:
            elf.rotate_directions()

    def get_proposed_coords2(self):
        self.proposed = {}
        start_coords = self.coordinates
        for elf in self.elves:
            surrounding_points, all_pts = elf.get_neighbour_points()
            proposed_step = None
            empty_quadrants = 0
            if any(k in start_coords for k in all_pts):
                for d in self.directions:
                    quadrant = surrounding_points[d]
                    if not any(k in start_coords for k in quadrant):
                        if empty_quadrants == 0:
                            proposed_step = elf.proposed_step(d)
                        empty_quadrants += 1
                if empty_quadrants == 4:
                    proposed_step = None
                if proposed_step is not None and proposed_step not in self.proposed:
                    self.proposed[proposed_step] = [elf]
                elif proposed_step is not None and proposed_step in self.proposed:
                    self.proposed[proposed_step].append(elf)
                else:
                    # Do nothing!
                    pass
            else:
                proposed_step = None

    def get_proposed_coords(self):
        self.proposed = {}
        for elf in self.elves:
            surrounding_points, all_pts = elf.get_neighbour_points()
            proposed_step = None
            empty_quadrants = 0
            for d in elf.directions:
                quadrant = surrounding_points[d]
                if not any(k in self.coordinates for k in quadrant):
                    if empty_quadrants == 0:
                        proposed_step = elf.proposed_step(d)
                    empty_quadrants += 1
            if empty_quadrants == 4:
                proposed_step = None
            if proposed_step is not None and proposed_step not in self.proposed:
                self.proposed[proposed_step] = [elf]
            elif proposed_step is not None and proposed_step in self.proposed:
                self.proposed[proposed_step].append(elf)
            else:
                # Do nothing!
                pass

    def move_proposed_steps(self):
        moved_elves = 0
        for coord, elves in self.proposed.items():
            if len(elves) == 1:
                elf = elves[0]
                elf.coord = coord
                moved_elves += 1
        return moved_elves


def parse_file(file_name: str):
    with open(file_name) as f:
        data = [s.strip('\n') for s in f.readlines()]
    padding = len(data) * 5
    elves = []
    for j, row in enumerate(data):
        for i, c in enumerate(row):
            if c == '#':
                coord = Coord(padding + i, padding + j)
                elves.append(Elf(coord))
    mesh = Mesh(elves)
    counter = 0
    moved_elves = len(mesh.elves)
    while moved_elves > 0:
        mesh.get_proposed_coords2()
        moved_elves = mesh.move_proposed_steps()
        mesh.rotate_directions()
        counter += 1
        if counter % 10 == 0:
            print('Part 1: ', mesh.area - len(mesh.elves), 'Part 2:', counter)
    print(counter)


def main():
    parse_file('input.txt')


if __name__ == '__main__':
    main()
