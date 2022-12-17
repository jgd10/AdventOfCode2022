from dataclasses import dataclass
from collections import namedtuple
from enum import Enum


Coord = namedtuple('Coord', 'x, y')


class Material(Enum):
    VOID = 0
    ROCK = 1
    SAND = 2


class Hole(Enum):
    NONE = 0
    ENTRY = 1
    EXIT = 2


class Status(Enum):
    FALLING = 0
    AT_REST = 1
    OUT_OF_SYSTEM = 2


@dataclass
class SandGrain:
    coord: Coord
    status: Status = Status.FALLING

    def move_to(self, cell: 'Cell'):
        self.coord = cell.coord
        if cell.hole == Hole.EXIT:
            self.status = Status.OUT_OF_SYSTEM


@dataclass
class Cell:
    coord: Coord
    material: Material
    hole: Hole = Hole.NONE

    @property
    def ascii(self):
        if self.material == Material.VOID:
            if self.hole == Hole.ENTRY:
                return '+'
            if self.hole == Hole.EXIT:
                return '-'
            return '.'
        if self.material == Material.ROCK:
            return '#'
        if self.material == Material.SAND:
            return 'o'
        return

    def create_sand_grain(self):
        # self.material = Material.SAND
        return SandGrain(self.coord)

    def set_as_sand(self, grain: SandGrain):
        if self.hole == Hole.NONE:
            self.material = Material.SAND
            grain.coord = self.coord
            grain.status = Status.AT_REST
        else:
            grain.status = Status.OUT_OF_SYSTEM


@dataclass
class Mesh:
    cells: dict[Coord, Cell]
    min_coord: Coord
    max_coord: Coord
    _sources: list[Cell] = None
    grains_present: list[SandGrain] = None

    @property
    def sources(self):
        if self._sources is None:
            self._sources = self.get_sources()
        return self._sources

    def visualise(self):
        rows = []
        for j in range(self.min_coord.y, self.max_coord.y+1):
            row = [self.cells[Coord(i, j)].ascii
                   for i in range(self.min_coord.x, self.max_coord.x)]
            string = ''.join(row) + '\n'
            rows.append(string)

        print(''.join(rows))

    def generate_sand(self):
        if self.grains_present is None:
            self.grains_present = []
        while not any([g.status == Status.OUT_OF_SYSTEM
                       for g in self.grains_present]):
            for source in self.sources:
                grain = source.create_sand_grain()
                self.grains_present.append(grain)
                while grain.status == Status.FALLING:
                    self.find_next_position(grain)
        return len(self.grains_present) - 1

    def find_next_position(self, grain: SandGrain):
        start_x, start_y = grain.coord.x, grain.coord.y
        new_coord = Coord(start_x, start_y + 1)
        if self.can_grain_move_to_coord(new_coord):
            grain.move_to(self.cells[new_coord])
        else:
            new_coord = Coord(start_x - 1, start_y + 1)
            if self.can_grain_move_to_coord(new_coord):
                grain.move_to(self.cells[new_coord])
            else:
                new_coord = Coord(start_x + 1, start_y + 1)
                if self.can_grain_move_to_coord(new_coord):
                    grain.move_to(self.cells[new_coord])
                else:
                    self.cells[grain.coord].set_as_sand(grain)

    def can_grain_move_to_coord(self, coord: Coord):
        if coord in self.cells:
            new_cell = self.cells[coord]
            return new_cell.material not in [Material.SAND, Material.ROCK]
        else:
            return False

    def set_sand_source(self, coord: Coord):
        self.cells[coord].hole = Hole.ENTRY

    def get_sources(self):
        return [cell for cell in self.cells.values() if cell.hole == Hole.ENTRY]

    def set_sand_exits(self):
        max_y = self.max_coord.y
        for cell in self.cells.values():
            if cell.coord.y == max_y and cell.material == Material.VOID:
                cell.hole = Hole.EXIT

    def apply_line_instruction(self, line: 'LineInstruction'):
        for i in range(len(line.coords)-1):
            start = line.coords[i]
            end = line.coords[i+1]
            xdiff = end.x - start.x
            ydiff = end.y - start.y
            if xdiff != 0:
                self.draw_horizontal_line(start, end)
            elif xdiff == 0 and ydiff != 0:
                self.draw_vertical_line(start, end)
            else:
                raise ValueError

    def draw_horizontal_line(self, start: Coord, end: Coord):
        xincrement = (end.x - start.x)/abs(end.x - start.x)
        start_x = start.x
        y = start.y
        while start_x != end.x + xincrement:
            coord = Coord(start_x, y)
            self.cells[coord].material = Material.ROCK
            start_x += xincrement

    def draw_vertical_line(self, start: Coord, end: Coord):
        yincrement = (end.y - start.y)/abs(end.y - start.y)
        start_y = start.y
        x = start.x
        while start_y != end.y + yincrement:
            coord = Coord(x, start_y)
            self.cells[coord].material = Material.ROCK
            start_y += yincrement


@dataclass
class LineInstruction:
    coords: list[Coord]

    @classmethod
    def from_string(cls, string):
        coords = []
        entries = string.split(' -> ')
        for e in entries:
            x, y = e.split(',')
            coords.append(Coord(int(x), int(y)))
        return cls(coords)

    @property
    def bounds(self):
        min_x = 99999
        max_x = 0
        min_y = 99999
        max_y = 0
        for c in self.coords:
            min_x = min(min_x, c.x)
            max_x = max(max_x, c.x)
            min_y = min(min_y, c.y)
            max_y = max(max_y, c.y)
        return (min_x, max_x), (min_y, max_y)


def parse_lines(lines):
    instructions = [LineInstruction.from_string(line)
                    for line in lines if line]
    return instructions


def build_mesh(instructions: list[LineInstruction]):
    min_x = 99999
    max_x = 0
    min_y = 0  # we know y starts at 0
    max_y = 0
    for i in instructions:
        (b0x, b1x), (b0y, b1y) = i.bounds
        min_x = min(min_x, b0x)
        max_x = max(max_x, b1x)
        min_y = min(min_y, b0y)
        max_y = max(max_y, b1y)
    mesh = {}
    for i in range(min_x, max_x+1):
        for j in range(min_y, max_y+1):
            cell = Cell(Coord(i, j), Material.VOID)
            mesh[(i, j)] = cell
    mesh = Mesh(mesh, Coord(min_x, min_y), Coord(max_x, max_y))
    for instruction in instructions:
        mesh.apply_line_instruction(instruction)
    return mesh


def main():
    with open('input.txt') as f:
        data = [s.strip('\n') for s in f.readlines()]

    data.append('1000, 166 -> 0, 166')
    instructions = parse_lines(data)
    mesh = build_mesh(instructions)
    mesh.set_sand_source(Coord(500, 0))
    mesh.set_sand_exits()
    mesh.visualise()

    print(mesh.generate_sand() + 1)
    mesh.visualise()


main()
