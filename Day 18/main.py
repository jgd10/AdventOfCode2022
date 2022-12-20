from dataclasses import dataclass
from collections import namedtuple
import matplotlib.pyplot as plt


Point = namedtuple('Point', 'x, y, z')


@dataclass
class Cell:
    coord: Point
    uncovered_surface_area: int = 6
    visited: bool = False
    connected_cells: set['Cell'] = None

    @property
    def neighbouring_points(self):
        neighbours = {
            Point(self.coord.x + 1, self.coord.y, self.coord.z),
            Point(self.coord.x - 1, self.coord.y, self.coord.z),
            Point(self.coord.x, self.coord.y + 1, self.coord.z),
            Point(self.coord.x, self.coord.y - 1, self.coord.z),
            Point(self.coord.x, self.coord.y, self.coord.z + 1),
            Point(self.coord.x, self.coord.y, self.coord.z - 1)
        }
        return neighbours

    @property
    def vertices(self):
        vertices = {
            Point(self.coord.x + .5, self.coord.y + .5, self.coord.z + .5),
            Point(self.coord.x + .5, self.coord.y - .5, self.coord.z + .5),
            Point(self.coord.x - .5, self.coord.y + .5, self.coord.z + .5),
            Point(self.coord.x - .5, self.coord.y - .5, self.coord.z + .5),
            Point(self.coord.x + .5, self.coord.y + .5, self.coord.z - .5),
            Point(self.coord.x + .5, self.coord.y - .5, self.coord.z - .5),
            Point(self.coord.x - .5, self.coord.y + .5, self.coord.z - .5),
            Point(self.coord.x - .5, self.coord.y - .5, self.coord.z - .5)
        }
        return vertices


@dataclass
class Droplet:
    cubes: list[Cell]
    _all_cells: dict[Point, Cell] = None
    _centroid: Point = None
    air_cubes: list[Cell] = None
    _boundaries: tuple[Cell, Cell] = None

    @classmethod
    def from_file(cls, fname: str):
        with open(fname) as f:
            data = [s.strip('\n') for s in f.readlines()]
        cells = []
        for row in data:
            if row:
                xstr, ystr, zstr = row.split(',')
                coord = Point(int(xstr), int(ystr), int(zstr))
                cells.append(Cell(coord))
        return cls(cells)

    @property
    def boundaries(self):
        if self._boundaries is None:
            all_x = {c.coord.x for c in self.cubes}
            all_y = {c.coord.y for c in self.cubes}
            all_z = {c.coord.z for c in self.cubes}
            min_point = Point(min(all_x), min(all_y), min(all_z))
            max_point = Point(max(all_x), max(all_y), max(all_z))
            self._boundaries = (Cell(min_point), Cell(max_point))
        return self._boundaries

    @property
    def vertices(self):
        vertices = set()
        for c in self.cubes:
            vertices.update(c.vertices)
        return vertices

    @property
    def total_surface_area(self):
        all_points = {c.coord for c in self.cubes}
        for cube in self.cubes:
            neighbours = cube.neighbouring_points
            cube.uncovered_surface_area -= len(all_points.intersection(neighbours))

        return sum([c.uncovered_surface_area for c in self.cubes])

    def visualise_centres(self):
        fig = plt.figure()
        ax = fig.add_subplot(projection='3d')
        x = [c.coord.x for c in self.cubes]
        y = [c.coord.y for c in self.cubes]
        z = [c.coord.z for c in self.cubes]
        ax.plot(x, y, z, zdir='z', c='k', linestyle=' ', marker='s', ms=10)
        plt.show()

    def visualise_vertices(self):
        fig = plt.figure()
        ax = fig.add_subplot(projection='3d')
        vertices = self.vertices
        x = [c.x for c in vertices]
        y = [c.y for c in vertices]
        z = [c.z for c in vertices]
        ax.plot(x, y, z, zdir='z', c='k', linestyle=' ', marker='s', ms=10)
        plt.show()

    def visualise_cubes(self):
        fig = plt.figure()
        ax = fig.add_subplot(projection='3d')
        ax.set_aspect('equal')
        ax.set_xlim(0, 20)
        ax.set_ylim(0, 20)
        ax.set_zlim(0, 20)
        for c in self.cubes:
            self.visualise_cube(ax, c)
        plt.show()

    def visualise_cube(self, ax, cube):
        x = [c.x for c in cube.vertices]
        y = [c.y for c in cube.vertices]
        z = [c.z for c in cube.vertices]
        ax.plot(x, y, z, zdir='z', linestyle=' ', marker='o', ms=2)

    def point_in_bounds(self, cell: Point):
        return self.boundaries[0].coord.x-1 <= cell.x <= self.boundaries[1].coord.x + 1 \
               and self.boundaries[0].coord.y-1 <= cell.y <= self.boundaries[1].coord.y + 1 \
               and self.boundaries[0].coord.z-1 <= cell.z <= self.boundaries[1].coord.z + 1

    def expand_air(self, air: Cell):
        neighbours = {n for n in air.neighbouring_points
                      if self.point_in_bounds(n)}
        return neighbours

    def area_exposed_to_air(self):
        all_points = {c.coord for c in self.cubes}
        start = self.boundaries[0]
        air_points = {Point(start.coord.x - 1,
                            start.coord.y - 1,
                            start.coord.z - 1)}
        visited_points = {start.coord}
        exposed_faces = 0
        while len(air_points) > 0:
            next_air = air_points.pop()
            visited_points.add(next_air)
            neighbours = self.expand_air(Cell(next_air))
            lava_points = neighbours.intersection(all_points)

            exposed_faces += len(lava_points)
            new_air = {s for s in neighbours - all_points
                       if s not in visited_points}
            air_points.update(new_air)
        return exposed_faces


def main():
    droplet = Droplet.from_file('input.txt')
    total_area = droplet.total_surface_area
    print(f'Part1: {total_area}, Part2: {droplet.area_exposed_to_air()}')


main()
