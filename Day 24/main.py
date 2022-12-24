import math
from dataclasses import dataclass
from collections import namedtuple
from enum import Enum


Coord = namedtuple('Coord', 'x, y')


class VerticalDirection(Enum):
    NORTH = -1
    SOUTH = 1


class HorizontalDirection(Enum):
    WEST = -1
    EAST = 1


class Status(Enum):
    FIRST = 1
    SECOND = 2
    THIRD = 3


CHEVRON_MAP = {'>': HorizontalDirection.EAST, '^': VerticalDirection.NORTH,
               '<': HorizontalDirection.WEST, 'v': VerticalDirection.SOUTH}


@dataclass
class Blizzard:
    origin: Coord
    min: int
    max: int
    direction: VerticalDirection | HorizontalDirection
    _p: dict[int, int] = None
    _chevron: str = None

    def __repr__(self):
        return f'Blizzard({self.chevron} origin={self.origin})'

    def get_position(self, time_: int):
        if self._p is None:
            if self.chevron == '>':
                x = self.origin.x
                self._p = {}
                t = 0
                while x <= self.max:
                    self._p[t] = x
                    t += 1
                    x += self.direction.value
                x = self.min
                while x < self.origin.x:
                    self._p[t] = x
                    t += 1
                    x += self.direction.value
            if self.chevron == '<':
                x = self.origin.x
                self._p = {}
                t = 0
                while x >= self.min:
                    self._p[t] = x
                    t += 1
                    x += self.direction.value
                x = self.max
                while x > self.origin.x:
                    self._p[t] = x
                    t += 1
                    x += self.direction.value
            if self.chevron == 'v':
                y = self.origin.y
                self._p = {}
                t = 0
                while y <= self.max:
                    self._p[t] = y
                    t += 1
                    y += self.direction.value
                y = self.min
                while y < self.origin.y:
                    self._p[t] = y
                    t += 1
                    y += self.direction.value
            if self.chevron == '^':
                y = self.origin.y
                self._p = {}
                t = 0
                while y >= self.min:
                    self._p[t] = y
                    t += 1
                    y += self.direction.value
                y = self.max
                while y > self.origin.y:
                    self._p[t] = y
                    t += 1
                    y += self.direction.value
        time_ = time_ % (self.max - self.min + 1)
        if self.chevron in '<>':
            coord = Coord(self._p[time_], self.origin.y)
        elif self.chevron in '^v':
            coord = Coord(self.origin.x, self._p[time_])
        else:
            raise TypeError
        return coord

    @property
    def chevron(self):
        if self._chevron is None:
            if self.direction == VerticalDirection.SOUTH:
                self._chevron = 'v'
            if self.direction == VerticalDirection.NORTH:
                self._chevron = '^'
            if self.direction == HorizontalDirection.WEST:
                self._chevron = '<'
            if self.direction == HorizontalDirection.EAST:
                self._chevron = '>'
        return self._chevron


@dataclass
class Valley:
    start: Coord
    imin: int
    jmin: int
    imax: int
    jmax: int
    end: Coord
    blizzards: list[Blizzard]
    _blizzard_positions: dict[int, set[Coord]] = None
    _all_positions: set[Coord] = None

    @property
    def cycle_time(self):
        return math.lcm((self.imax-self.imin+1), (self.jmax-self.jmin+1))

    @property
    def blizzard_positions(self):
        if self._blizzard_positions is None:
            self._blizzard_positions = {i: self.get_blizzard_positions(i)
                                        for i in range(self.cycle_time)}
        return self._blizzard_positions

    @classmethod
    def from_file(cls, file_name: str):
        with open(file_name) as f:
            data = [s.strip('\n') for s in f.readlines()]
        imin, jmin = 1, 1
        imax = len(data[0]) - 2
        jmax = len(data) - 2
        origin = Coord(1, 0)
        target = Coord(imax, jmax + 1)
        blizzards = []
        for j, row in enumerate(data):
            if jmin <= j <= jmax:
                for i, c in enumerate(row):
                    if c in '><v^':
                        direction = CHEVRON_MAP[c]
                        min_, max_ = (imin, imax) if c in '><' else (jmin, jmax)
                        b = Blizzard(Coord(i, j), min_, max_, direction)
                        blizzards.append(b)
        return cls(origin, imin, jmin, imax, jmax, target, blizzards)

    def get_blizzard_positions(self, time_: int):
        return {b.get_position(time_) for b in self.blizzards}

    @property
    def all_positions(self):
        if self._all_positions is None:
            self._all_positions = {Coord(i, j)
                                   for i in range(self.imin, self.imax+1)
                                   for j in range(self.jmin, self.jmax+1)}
            self.all_positions.add(self.end)
            self.all_positions.add(self.start)
        return self._all_positions


@dataclass
class Node:
    position: Coord
    time: int
    relative_time: int
    children: 'list[Node]' = None
    _unique: hash = None

    @property
    def hash(self):
        if self._unique is None:
            string = f'{self.position}' \
                     f'{self.relative_time}'
            self._unique = hash(string)
        return self._unique


@dataclass
class Expedition:
    valley: Valley
    min_time: int = 999999

    def get_child_nodes(self, start: Coord, time_: int):
        new_coords = {Coord(start.x + 1, start.y),
                      Coord(start.x - 1, start.y),
                      Coord(start.x, start.y + 1),
                      Coord(start.x, start.y - 1),
                      start}
        new_coords = self.valley.all_positions.intersection(new_coords)
        relative_time = time_ % self.valley.cycle_time
        blizzards = self.valley.blizzard_positions[relative_time]
        new_coords = new_coords - blizzards
        return [Node(n, time_, relative_time) for n in new_coords]

    def breadth_first(self, destination: Coord):
        """Breadth-first algorithm used"""
        node1 = Node(self.valley.start, 0, 0)
        visited_nodes = {node1.hash}
        nodes = [node1]
        journey = Status.FIRST
        while len(nodes) > 0:
            node = nodes.pop(0)
            if node.position == destination:
                match journey:
                    case Status.FIRST:
                        print(f'First journey done in {node.time} mins')
                        nodes = [node]
                        visited_nodes = {node.hash}
                        destination = self.valley.start
                        journey = Status.SECOND
                    case Status.SECOND:
                        print(f'Second journey done in {node.time} mins')
                        nodes = [node]
                        visited_nodes = {node.hash}
                        destination = self.valley.end
                        journey = Status.THIRD
                    case Status.THIRD:
                        print(f'Final journey done in {node.time} mins')
                        break
            node.children = self.get_child_nodes(node.position, node.time+1)
            for child in node.children:
                if child.hash not in visited_nodes:
                    visited_nodes.add(child.hash)
                    nodes.append(child)
        return node.time


def main():
    valley = Valley.from_file('input.txt')
    expedition = Expedition(valley)
    time = expedition.breadth_first(valley.end)
    # expedition.depth_first(valley.start, 0)
    print(time)


if __name__ == '__main__':
    main()
