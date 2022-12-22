from dataclasses import dataclass
from collections import namedtuple
from enum import Enum
from itertools import groupby
import numpy as np


Coord = namedtuple('Coord', 'x, y')


class TileType(Enum):
    VOID = 0
    OPEN = 1
    WALL = 2


TYPE_MAP = {'#': TileType.WALL, '.': TileType.OPEN, ' ': TileType.VOID}


class Direction(Enum):
    NORTH = 3
    EAST = 0
    WEST = 2
    SOUTH = 1


class Side(Enum):
    NONE = 0
    LEFT = 1
    RIGHT = 2


SIDE_MAP = {'L': Side.LEFT, 'R': Side.RIGHT}


class Face(Enum):
     ONE = 1
     TWO = 2
     THREE = 3
     FOUR = 4
     FIVE = 5
     SIX = 6


DIRECTION_MAP = {0: Direction.EAST, 1: Direction.SOUTH,
                 2: Direction.WEST, 3: Direction.NORTH}


@dataclass
class Command:
    steps: int
    direction: Direction
    change: Side


@dataclass
class Player:
    tile: 'Tile'
    direction: Direction


@dataclass
class Tile:
    coord: Coord
    type: int
    char: str = None


@dataclass
class Connection:
    origin: Face
    destination: Face
    origin_direction: Direction
    destination_direction: Direction


@dataclass
class Region:
    face: int
    tiles: dict[Coord, Tile]
    connections: dict[Face, Connection] = None
    _imin: int = None
    _imax: int = None
    _jmin: int = None
    _jmax: int = None

    @property
    def imin(self):
        if self._imin is None:
            self._imin = min([c.x for c in self.tiles])
        return self._imin

    @property
    def jmin(self):
        if self._jmin is None:
            self._jmin = min([c.y for c in self.tiles])
        return self._jmin

    @property
    def imax(self):
        if self._imax is None:
            self._imax = max([c.x for c in self.tiles])
        return self._imax

    @property
    def jmax(self):
        if self._jmax is None:
            self._jmax = max([c.y for c in self.tiles])
        return self._jmax


@dataclass
class Mesh:
    tiles: list[list[Tile]]
    directions: list[Command]
    region_size: int
    _tiles_by_coord: dict[Coord, Tile] = None
    player: Player = None
    _open_tiles: set[Coord] = None
    _wall_tiles: set[Coord] = None
    _void_tiles: set[Coord] = None
    _imax: int = None
    _jmax: int = None
    _regions: dict[int, Region] = None

    @property
    def regions(self):
        if self._regions is None:
            n = self.region_size
            array = np.array(self.tiles)
            region1 = array[:n, n:n*2]
            region2 = array[:n, n*2:n*3]
            region3 = array[n:n*2, n:n*2]
            region4 = array[n*2:n*3, :n]
            region5 = array[n*2:n*3, n:n*2]
            region6 = array[n*3:n*4, :n]
            regions = {}
            for i, r in enumerate([region1, region2, region3,
                                   region4, region5, region6]):
                tiles = {t.coord: t for t in r.flatten()}
                face = i + 1
                regions[i+1] = Region(face, tiles)
            regions[1].connections = {Face.FOUR: Connection(Face.ONE, Face.FOUR, Direction.WEST, Direction.EAST),
                                      Face.THREE: Connection(Face.ONE, Face.THREE, Direction.SOUTH, Direction.SOUTH),
                                      Face.SIX: Connection(Face.ONE, Face.SIX, Direction.NORTH, Direction.EAST),
                                      Face.TWO: Connection(Face.ONE, Face.TWO, Direction.EAST, Direction.EAST)}

            regions[2].connections = {Face.ONE: Connection(Face.TWO, Face.ONE, Direction.WEST, Direction.WEST),
                                      Face.THREE: Connection(Face.TWO, Face.THREE, Direction.SOUTH, Direction.WEST),
                                      Face.SIX: Connection(Face.TWO, Face.SIX, Direction.NORTH, Direction.NORTH),
                                      Face.FIVE: Connection(Face.TWO, Face.FIVE, Direction.EAST, Direction.WEST)}

            regions[3].connections = {Face.FOUR: Connection(Face.THREE, Face.FOUR, Direction.WEST, Direction.SOUTH),
                                      Face.TWO: Connection(Face.THREE, Face.TWO, Direction.EAST, Direction.NORTH),
                                      Face.FIVE: Connection(Face.THREE, Face.FIVE, Direction.SOUTH, Direction.SOUTH),
                                      Face.ONE: Connection(Face.THREE, Face.ONE, Direction.NORTH, Direction.NORTH)}

            regions[4].connections = {Face.ONE: Connection(Face.FOUR, Face.ONE, Direction.WEST, Direction.EAST),
                                      Face.THREE: Connection(Face.FOUR, Face.THREE, Direction.NORTH, Direction.EAST),
                                      Face.FIVE: Connection(Face.FOUR, Face.FIVE, Direction.EAST, Direction.EAST),
                                      Face.SIX: Connection(Face.FOUR, Face.SIX, Direction.SOUTH, Direction.SOUTH)}

            regions[5].connections = {Face.FOUR: Connection(Face.FIVE, Face.FOUR, Direction.WEST, Direction.WEST),
                                      Face.THREE: Connection(Face.FIVE, Face.THREE, Direction.NORTH, Direction.NORTH),
                                      Face.SIX: Connection(Face.FIVE, Face.SIX, Direction.SOUTH, Direction.WEST),
                                      Face.TWO: Connection(Face.FIVE, Face.TWO, Direction.EAST, Direction.WEST)}

            regions[6].connections = {Face.FOUR: Connection(Face.SIX, Face.FOUR, Direction.NORTH, Direction.NORTH),
                                      Face.FIVE: Connection(Face.SIX, Face.FIVE, Direction.EAST, Direction.NORTH),
                                      Face.ONE: Connection(Face.SIX, Face.ONE, Direction.WEST, Direction.SOUTH),
                                      Face.TWO: Connection(Face.SIX, Face.TWO, Direction.SOUTH, Direction.SOUTH)}
            self._regions = regions

        return self._regions

    @property
    def tiles_by_coord(self):
        if self._tiles_by_coord is None:
            self._tiles_by_coord = {t.coord: t for row in self.tiles
                                    for t in row}
        return self._tiles_by_coord

    @property
    def imax(self):
        if self._imax is None:
            self._imax = len(self.tiles[0])
        return self._imax

    @property
    def jmax(self):
        if self._jmax is None:
            self._jmax = len(self.tiles)
        return self._jmax

    @property
    def open_tiles(self):
        if self._open_tiles is None:
            self._open_tiles = {t.coord for row in self.tiles
                                for t in row if t.type == TileType.OPEN}
        return self._open_tiles

    @property
    def wall_tiles(self):
        if self._wall_tiles is None:
            self._wall_tiles = {t.coord for row in self.tiles
                                for t in row if t.type == TileType.WALL}
        return self._wall_tiles

    @property
    def void_tiles(self):
        if self._void_tiles is None:
            self._void_tiles = {t.coord for row in self.tiles
                                for t in row if t.type == TileType.VOID}
            # rows
            voids = set()
            for n in range(self.imax+1):
                voids.update({Coord(n, -1), Coord(n, self.jmax)})
            # cols
            for n in range(self.jmax+1):
                voids.update({Coord(-1, n), Coord(self.imax, n)})
            self._void_tiles.update(voids)
        return self._void_tiles

    @classmethod
    def from_file(cls, file_name, region_size: int = 50):
        with open(file_name) as f:
            data = [s.strip('\n') for s in f.readlines()]
        map_ = [s for s in data if '.' in s]

        directions = [s for s in data if 'R' in s][0]
        tiles = []
        longest_row = max([len(row) for row in map_])
        for i, row in enumerate(map_):
            tile_row = []
            for j in range(longest_row):
                if j < len(row):
                    cell = row[j]
                else:
                    cell = ' '
                tile_row.append(Tile(Coord(j, i), type=TYPE_MAP[cell]))
            tiles.append(tile_row)

        commands = []
        counter = 0
        for _, d in groupby(directions, str.isalpha):
            element = ''.join(d)
            if counter == 0:
                new_direct = Direction.EAST
                change = Side.NONE
                counter += 1
                steps = int(element)
                commands.append(Command(steps, new_direct, change))
            elif element in ['R']:
                change = Side.RIGHT
                new_direct_val = new_direct.value + 1
                if new_direct_val > 3:
                    new_direct_val = 0
                new_direct = DIRECTION_MAP[new_direct_val]
            elif element in ['L']:
                change = Side.LEFT
                new_direct_val = new_direct.value - 1
                if new_direct_val < 0:
                    new_direct_val = 3
                new_direct = DIRECTION_MAP[new_direct_val]
            else:
                steps = int(element)
                commands.append(Command(steps, new_direct, change))

        return cls(tiles, commands, region_size)

    def initialise_player(self):
        start = [t for t in self.tiles[0] if t.type == TileType.OPEN][0]
        self.player = Player(start, direction=Direction.EAST)
        return self.player

    def apply_command_to_player(self, command: Command):
        # Need to change direction based on Side and NOT the direction
        # stored in the command. Won't work with cube.
        steps = command.steps
        player_x = self.player.tile.coord.x
        player_y = self.player.tile.coord.y
        final = Coord(player_x, player_y)
        initial_direction = self.player.direction
        if command.change == Side.RIGHT:
            direction_val = initial_direction.value + 1
            if direction_val > 3:
                direction_val = 0
            direction = DIRECTION_MAP[direction_val]
        elif command.change == Side.LEFT:
            direction_val = initial_direction.value - 1
            if direction_val < 0:
                direction_val = 3
            direction = DIRECTION_MAP[direction_val]
        elif command.change == Side.NONE:
            direction = initial_direction
        else:
            raise TypeError
        for k in range(steps):
            if direction == Direction.NORTH:
                yk = -1
                xk = 0
            elif direction == Direction.EAST:
                yk = 0
                xk = 1
            elif direction == Direction.WEST:
                yk = 0
                xk = -1
            elif direction == Direction.SOUTH:
                yk = 1
                xk = 0
            else:
                raise TypeError
            player_x += xk
            player_y += yk
            new = Coord(player_x, player_y)
            if new in self.void_tiles:
                pre_wrap_x = player_x - xk
                pre_wrap_y = player_y - yk
                old_direction = direction
                player_x, player_y, direction = self.wraparound2(pre_wrap_x, pre_wrap_y,
                                                                 direction)
                new = Coord(player_x, player_y)
                if new in self.wall_tiles:
                    final = Coord(pre_wrap_x,
                                  pre_wrap_y)
                    direction = old_direction
                    break
            if new in self.wall_tiles:
                final = Coord(player_x - xk,
                              player_y - yk)
                break
            else:
                final = Coord(player_x,
                              player_y)
        self.player = Player(self.tiles_by_coord[final], direction)

    def wraparound(self, player_x, player_y, pre_wrap_x, pre_wrap_y, xk, yk):
        new = Coord(pre_wrap_x, pre_wrap_y)
        while new not in self.void_tiles:
            player_x -= xk
            player_y -= yk
            new = Coord(player_x, player_y)
        player_x += xk
        player_y += yk
        return player_x, player_y

    def wraparound2(self, player_x, player_y, direction):
        new = Coord(player_x, player_y)
        region = [r for r in self.regions.values() if new in r.tiles][0]
        connection = [c for c in region.connections.values() if c.origin_direction == direction][0]
        new_face = connection.destination
        new_dir = connection.destination_direction
        new_region = [r for r in self.regions.values() if r.face == new_face.value][0]
        match direction:
            case Direction.NORTH:
                disp = player_x - region.imin
            case Direction.EAST:
                disp = player_y - region.jmin
            case Direction.WEST:
                disp = region.jmax - player_y
            case Direction.SOUTH:
                disp = region.imax - player_x
        match new_dir:
            case Direction.NORTH:
                player_x = disp + new_region.imin
                player_y = new_region.jmax
            case Direction.EAST:
                player_y = disp + new_region.jmin
                player_x = new_region.imin
            case Direction.WEST:
                player_y = new_region.jmax - disp
                player_x = new_region.imax
            case Direction.SOUTH:
                player_x = new_region.imax - disp
                player_y = new_region.jmin
        return player_x, player_y, new_dir

    def execute_commands(self):
        for command in self.directions:
            self.apply_command_to_player(command)


def main():
    m = Mesh.from_file('input.txt')
    m.initialise_player()
    m.execute_commands()
    pwd = (m.player.tile.coord.x + 1) * 4 + \
          (m.player.tile.coord.y + 1) * 1000 + \
          m.player.direction.value
    print(pwd)


if __name__ == '__main__':
    main()


