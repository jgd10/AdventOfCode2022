import math
from dataclasses import dataclass


class CommandNotFound(Exception):
    pass


def distance_between_positions(position1, position2):
    dx = abs(position1[0] - position2[0])
    dy = abs(position1[1] - position2[1])
    return math.sqrt(dx**2. + dy**2.)


@dataclass
class Tile:
    position: tuple[int, int]
    has_head: bool
    has_tail: bool
    tail_waz_ere: bool = False


@dataclass
class Rope:
    head_position: tuple[int, int]
    tail_position: tuple[int, int]
    head_positions: set[tuple[int, int]]
    tail_positions: set[tuple[int, int]]

    @property
    def in_tension(self):
        sep = distance_between_positions(self.tail_position,
                                         self.head_position)
        return sep >= 2

    def move_head(self, movement: str):
        self.tail_positions.add(self.tail_position)
        self.head_positions.add(self.head_position)
        command, amount = movement.split(' ')
        amount = int(amount)
        match command:
            case 'U':
                dx, dy = 0, 1
            case 'D':
                dx, dy = 0, -1
            case 'L':
                dx, dy = -1, 0
            case 'R':
                dx, dy = 1, 0
            case _:
                raise CommandNotFound

        for i in range(amount):
            self.head_position = (self.head_position[0] + dx,
                                  self.head_position[1] + dy)
            new_tail = self.release_tension()
            self.tail_positions.add(new_tail)

    def release_tension(self):
        if not self.in_tension:
            return self.tail_position
        ydiff = self.head_position[1] - self.tail_position[1]
        xdiff = self.head_position[0] - self.tail_position[0]
        if self.tail_position[0] == self.head_position[0]:

            self.tail_position = (self.tail_position[0],
                                  self.tail_position[1] + ydiff//abs(ydiff))
        elif self.tail_position[1] == self.head_position[1]:

            self.tail_position = (self.tail_position[0] + xdiff//abs(xdiff),
                                  self.tail_position[1])
        else:
            self.tail_position = (self.tail_position[0] + xdiff//abs(xdiff),
                                  self.tail_position[1] + ydiff//abs(ydiff))
        return self.tail_position


@dataclass
class LongRope:
    knots: dict[str, tuple[int, int]]
    knot_positions: dict[str, set[tuple[int, int]]]

    @classmethod
    def ten_knot_rope(cls):
        knots = {k: (0, 0) for k in 'H123456789'}
        knot_pos = {k: {(0, 0)} for k in 'H123456789'}
        return cls(knots, knot_pos)

    def check_tensions(self):
        for h, t in zip('H12345678', '123456789'):
            sep = distance_between_positions(self.knots[t],
                                             self.knots[h])
            if sep >= 2:
                self.release_tension(h, t)

    def move_head(self, movement: str):
        for k in 'H123456789':
            self.knot_positions[k].add(self.knots[k])
        command, amount = movement.split(' ')
        amount = int(amount)
        match command:
            case 'U':
                dx, dy = 0, 1
            case 'D':
                dx, dy = 0, -1
            case 'L':
                dx, dy = -1, 0
            case 'R':
                dx, dy = 1, 0
            case _:
                raise CommandNotFound

        for i in range(amount):
            self.knots['H'] = (self.knots['H'][0] + dx,
                               self.knots['H'][1] + dy)
            self.check_tensions()

    def release_tension(self, h, t):
        ydiff = self.knots[h][1] - self.knots[t][1]
        xdiff = self.knots[h][0] - self.knots[t][0]
        if xdiff == 0 and ydiff == 0:
            return
        if xdiff == 0:

            self.knots[t] = (self.knots[t][0],
                             self.knots[t][1] + ydiff // abs(ydiff))
        elif ydiff == 0:
            self.knots[t] = (self.knots[t][0] + xdiff // abs(xdiff),
                             self.knots[t][1])
        else:
            self.knots[t] = (self.knots[t][0] + xdiff // abs(xdiff),
                             self.knots[t][1] + ydiff // abs(ydiff))
        self.knot_positions[t].add(self.knots[t])


def execute_moves_2knot(moves):
    rope = Rope((0, 0), (0, 0), {(0, 0)}, {(0, 0)})
    for move in moves:
        rope.move_head(move)
    return rope


def execute_moves_10knot(moves):
    rope = LongRope.ten_knot_rope()
    for move in moves:
        rope.move_head(move)
    return rope


with open('input.txt') as f:
    moves_ = [s.strip('\n') for s in f.readlines()]

rope_ = execute_moves_10knot(moves_)
print(len(rope_.knot_positions['9']))
