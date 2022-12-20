import math
from dataclasses import dataclass
from enum import Enum


class Material:
    ORE = 1
    CLAY = 2
    OBSIDIAN = 3
    GEODE = 4


MATERIALS = [Material.ORE, Material.CLAY, Material.OBSIDIAN, Material.GEODE]


@dataclass
class Robot:
    material: int

    @staticmethod
    def collect():
        return 1


@dataclass
class Factory:
    robots: list
    time: int
    materials: dict[int, int]
    blueprint: 'Blueprint'

    @classmethod
    def begin_part_1(cls, blueprint: 'Blueprint'):
        robots = [Robot(Material.ORE)]
        return cls(robots, 24, {t: 0 for t in MATERIALS}, blueprint)

    def loop(self):
        while self.time > 0:
            self.build_robots()
            for robot in self.robots:
                self.materials[robot.material] += robot.collect()
            self.time -= 1
        return self.materials

    def explore_path(self, time, robots, materials):
        robots = self.build_robots()
        for robot in robots:
            materials[robot.material] += 1

    @property
    def quality_level(self):
        if self.time > 0:
            self.loop()
        return self.materials[Material.GEODE] * self.blueprint.id

    def build_robot(self, type_: int):
        required_materials = self.blueprint.robot_costs[type_]
        if self.build_decision(type_):
            for mat, val in required_materials.items():
                self.materials[mat] -= val
            self.robots.append(Robot(type_))

    def build_robots(self):
        raise NotImplementedError
        new_bots = [self.build_robot(material, materials)
                    for material in [Material.GEODE, Material.OBSIDIAN,
                                     Material.CLAY, Material.ORE]]
        return new_bots, materials

    def build_decision(self, type_: int):
        required_materials = self.blueprint.robot_costs[type_]
        viability = [self.materials[mat] >= val
                     for mat, val in required_materials.items()]
        if not all(viability):
            return False
        return all(viability)


@dataclass
class Blueprint:
    name: str
    robot_costs: dict[int, 'Materials']
    id: int
    _possible_end_geodes: set[int] = None
    _robot_increases: dict[int, 'Robots'] = None
    _const: int = None

    def find_quality_level(self):
        initial_state = (Robots(1, 0, 0, 0), Materials(0, 0, 0, 0), 32)
        self.cycle(initial_state)
        return max(self.end_geodes), self.id, self.id*max(self.end_geodes)

    @property
    def end_geodes(self):
        if self._possible_end_geodes is None:
            self._possible_end_geodes = {0}
        return self._possible_end_geodes

    @property
    def robot_increases(self):
        if self._robot_increases is None:
            self._robot_increases = {Material.ORE: Robots(1, 0, 0, 0),
                                     Material.CLAY: Robots(0, 1, 0, 0),
                                     Material.OBSIDIAN: Robots(0, 0, 1, 0),
                                     Material.GEODE: Robots(0, 0, 0, 1)}
        return self._robot_increases

    @classmethod
    def from_string(cls, string):
        name, string = string.split(':')
        ore_string, clay_string, obs_string, geo_string, _ = string.split('.')
        _, ore_price = ore_string.split('costs ')
        _, clay_price = clay_string.split('costs ')
        orebot_price = int(ore_price.replace('ore', ''))
        claybot_price = int(clay_price.replace('ore', ''))

        _, obsbot_price = obs_string.split('costs ')
        _, geobot_price = geo_string.split('costs ')
        obsbot_price = obsbot_price.replace('ore', '')
        obsbot_price = obsbot_price.replace('clay', '')
        geobot_price = geobot_price.replace('ore', '')
        geobot_price = geobot_price.replace('obsidian', '')
        obsbot_prices = obsbot_price.split('and')
        geobot_prices = geobot_price.split('and')

        costs = {Material.ORE: Materials(orebot_price, 0, 0, 0),
                 Material.CLAY: Materials(claybot_price, 0, 0, 0),
                 Material.OBSIDIAN: Materials(int(obsbot_prices[0]),
                                              int(obsbot_prices[1]),
                                              0, 0),
                 Material.GEODE: Materials(int(geobot_prices[0]),
                                           0,
                                           int(geobot_prices[1]),
                                           0)}
        _, id_ = name.split(' ')
        return cls(name, costs, int(id_))

    def find_possible_states(self, materials: 'Materials',
                             robots: 'Robots', time_: int):
        # can only make one robit per cycle, or do nothing
        # Order important
        # 1) Make the NEW robits
        # 2) Then old robits bring stuff in and materials updated
        states = [(robots.copy(), materials.copy() + robots, time_)]

        for name, criteria in self.robot_costs.items():
            if materials >= criteria:
                if name == Material.ORE \
                        and robots.ore >= max(self.robot_costs[Material.GEODE].ore,
                                              self.robot_costs[Material.CLAY].ore,
                                              self.robot_costs[Material.OBSIDIAN].ore):
                    pass
                elif name == Material.CLAY \
                        and robots.clay >= self.robot_costs[Material.OBSIDIAN].clay:
                    pass
                elif name == Material.OBSIDIAN \
                        and robots.obsidian >= self.robot_costs[Material.GEODE].obsidian:
                    pass
                else:
                    increase = self.robot_increases[name]
                    states.append((robots + increase, materials - criteria + robots, time_))
        return states[::-1]

    @staticmethod
    def max_possible_geodes_in_remaining_time(time_, geodes, geode_bots):
        for i in range(time_):
            geodes += geode_bots
            geode_bots += 1
        return geodes

    def can_prune(self, state):
        robots, materials, remaining_time = state
        gamma = self.robot_costs[Material.CLAY].ore
        beta = self.robot_costs[Material.GEODE].obsidian
        epsilon = self.robot_costs[Material.OBSIDIAN].clay
        if remaining_time == 0:
            return True
        if robots.geode == 0 \
                and robots.obsidian == 0 \
                and materials.geode == 0 \
                and materials.obsidian == 0 \
                and remaining_time < self.min_turns_to_create(beta):
            return True
        if robots.geode == 0 \
                and robots.clay == 0 \
                and robots.obsidian == 0 \
                and materials.clay == 0 \
                and materials.obsidian == 0 \
                and materials.geode == 0 \
                and remaining_time < self.min_turns_to_create(gamma):
            return True
        if robots.geode == 0 \
                and robots.clay == 0 \
                and robots.obsidian == 0 \
                and materials.obsidian == 0 \
                and materials.geode == 0 \
                and remaining_time < self.min_turns_to_create(epsilon):
            return True
        if self.max_possible_geodes_in_remaining_time(remaining_time,
                                                      materials.geode,
                                                      robots.geode) \
                <= max(self.end_geodes):
            return True

    def min_turns_to_create(self, n):
        return math.ceil((-1 + math.sqrt(1+4*n))/2)

    @property
    def minimum_turns_to_make_one_geode(self):
        if self._const is None:
            alpha = self.robot_costs[Material.GEODE].ore
            beta = self.robot_costs[Material.GEODE].obsidian
            gamma = self.robot_costs[Material.CLAY].ore
            delta = self.robot_costs[Material.OBSIDIAN].ore
            epsilon = self.robot_costs[Material.OBSIDIAN].clay
            const = alpha + beta * delta + gamma * epsilon
            turns = -.5 + math.sqrt(1 + 4*const)/2
            self._const = int(math.ceil(turns))
        return self._const

    def cycle(self, state):
        robots, materials, remaining_time = state
        if self.can_prune(state):
            self.end_geodes.add(materials.geode)
            return
        remaining_time -= 1
        possible_states = self.find_possible_states(materials, robots,
                                                    remaining_time)
        for new_state in possible_states:
            self.cycle(new_state)


@dataclass
class Materials:
    ore: int = 0
    clay: int = 0
    obsidian: int = 0
    geode: int = 0

    def __iadd__(self, other: 'Materials | Robots | int'):
        if isinstance(other, int):
            return Materials(self.ore + other,
                             self.clay + other,
                             self.obsidian + other,
                             self.geode + other)
        else:
            return Materials(self.ore+other.ore,
                             self.clay+other.clay,
                             self.obsidian+other.obsidian,
                             self.geode+other.geode)

    def __add__(self, other: 'Materials | Robots | int'):
        return Materials(self.ore+other.ore,
                         self.clay+other.clay,
                         self.obsidian+other.obsidian,
                         self.geode+other.geode)

    def __sub__(self, other: 'Materials | Robots | int'):
        return Materials(self.ore - other.ore,
                         self.clay - other.clay,
                         self.obsidian - other.obsidian,
                         self.geode - other.geode)

    def __isub__(self, other: 'Materials | Robots | int'):
        if isinstance(other, int):
            return Materials(self.ore - other,
                             self.clay - other,
                             self.obsidian - other,
                             self.geode - other)
        else:
            return Materials(self.ore-other.ore,
                             self.clay-other.clay,
                             self.obsidian-other.obsidian,
                             self.geode-other.geode)

    def __ge__(self, other: 'Materials | Robots'):
        return other.ore <= self.ore \
               and other.clay <= self.clay \
               and other.obsidian <= self.obsidian \
               and other.geode <= self.geode

    def __le__(self, other: 'Materials | Robots'):
        return self.ore <= other.ore \
               and self.clay <= other.clay \
               and self.obsidian <= other.obsidian \
               and self.geode <= other.geode

    def copy(self):
        return Materials(self.ore, self.clay, self.obsidian, self.geode)


class Robots(Materials):
    def __init__(self, ore: int, clay: int, obsidian: int, geode: int):
        super().__init__(ore, clay, obsidian, geode)

    def __add__(self, other: 'Materials | Robots | int'):
        return Robots(self.ore+other.ore,
                      self.clay+other.clay,
                      self.obsidian+other.obsidian,
                      self.geode+other.geode)

    def copy(self):
        return Robots(self.ore, self.clay, self.obsidian, self.geode)


def main():
    with open('input.txt') as f:
        data = [s.strip('\n') for s in f.readlines()]
    total = 1
    for i, row in enumerate(data[:3]):
        blueprint = Blueprint.from_string(row)
        amt, id_, val = blueprint.find_quality_level()
        total *= amt
        print(amt)
    print(total)


main()
