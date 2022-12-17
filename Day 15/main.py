import math
from collections import namedtuple
from dataclasses import dataclass
import itertools


Coord = namedtuple('Coord', 'x, y')


def taxicab_distance(c1: Coord, c2: Coord):
    xdiff = abs(c1.x - c2.x)
    ydiff = abs(c1.y - c2.y)
    return xdiff + ydiff


@dataclass
class Sensor:
    coord: Coord
    beacon: Coord
    _range: int = None

    @property
    def range(self):
        if self._range is None:
            self._range = taxicab_distance(self.coord, self.beacon)
        return self._range

    def is_coord_in_range(self, test: Coord):
        distance = taxicab_distance(self.coord, test)
        return distance <= self.range

    def is_sensor_in_range(self, sensor2: 'Sensor'):
        distance = taxicab_distance(self.coord, sensor2.coord)
        return distance <= (self.range + sensor2.range)

    def bounds_at_row(self, y):
        ydiff = abs(y - self.coord.y)
        if ydiff > self.range:
            return None, None
        else:
            xdiff = abs(self.range - ydiff)
            return self.coord.x - xdiff, self.coord.x + xdiff


@dataclass
class Range1D:
    min: int
    max: int

    def overlap(self, range2: 'Range1D'):
        return self.min <= range2.max and self.max >= range2.min

    def combine(self, range2: 'Range1D'):
        return Range1D(min(self.min, range2.min), max(self.max, range2.max))

    @property
    def valid(self):
        return self.min < self.max

    @property
    def exclusive_length(self):
        return self.max - self.min - 1

    @property
    def inclusive_length(self):
        return self.max - self.min + 2


def parse_equivalence(string: str) -> int:
    _, value = string.split('=')
    return int(value)


def parse_coord(string: str):
    _, coord = string.split('at ')
    xst, yst = coord.split(', ')
    return Coord(parse_equivalence(xst), parse_equivalence(yst))


def parse_line(string: str) -> Sensor:
    sensor, beacon = string.split(':')
    sensor_coord = parse_coord(sensor)
    beacon_coord = parse_coord(beacon)
    return Sensor(sensor_coord, beacon_coord)


def empty_coords_in_row(index, sensors: list[Sensor]):
    max_x, min_x, overlapping_sensors = combined_sensor_range_at_row(index,
                                                                     sensors)
    unique_beacons_on_row = set()
    for os in overlapping_sensors:
        if os.beacon.y == index:
            unique_beacons_on_row.add(os.beacon)
    return max_x - min_x + 1 - len(unique_beacons_on_row)


def combined_sensor_range_at_row(index, sensors):
    min_x, max_x = 999999999, -999999999
    overlapping_sensors = []
    for s in sensors:
        minx, maxx = s.bounds_at_row(index)
        if minx is not None and maxx is not None:
            overlapping_sensors.append(s)
            min_x = min(min_x, minx)
            max_x = max(max_x, maxx)
    return max_x, min_x, overlapping_sensors


def sensor_ranges_at_row(index, sensors):
    ranges = []
    for s in sensors:
        min_, max_ = s.bounds_at_row(index)
        if min_ is not None and max_ is not None:
            range_ = Range1D(min_, max_)
            ranges.append(range_)
    return ranges


def overlap(bound1, bound2):
    return bound1[0] <= bound2[1] and bound2[0] >= bound1[1]


def find_unoverlapped_points(bounds: list[tuple[int, int]], range_):
    sections = []
    while len(bounds) > 0:
        new_bound = bounds.pop(0)
        for i in range(len(sections)):
            if overlap(new_bound, sections[i]):
                sections[i] = (min(sections[i][0], new_bound[0]),
                               max(sections[i][1], new_bound[1]))
            else:
                sections.append(new_bound)
        if not sections:
            sections.append(new_bound)
    return []


def find_sensors_that_do_not_overlap(sensors: list[Sensor]):
    non_overlapping_sensors = []
    for s1, s2 in itertools.combinations(sensors, 2):
        if not s1.is_sensor_in_range(s2):
            non_overlapping_sensors.append((s1, s2))
    return non_overlapping_sensors


def combine_ranges(ranges: list[Range1D]):
    if not ranges:
        return ranges
    ranges.sort(key=lambda x: x.min, reverse=False)
    new_ranges = []
    first_r = ranges.pop(0)
    while len(ranges) > 0:
        r = ranges.pop(0)
        if r.min <= first_r.max:
            first_r = first_r.combine(r)
        else:
            new_ranges.append(first_r)
            first_r = r
    if first_r not in new_ranges:
        new_ranges.append(first_r)
    return new_ranges


def invert_ranges(ranges: list[Range1D], coverage: Range1D):
    if len(ranges) == 0:
        return []
    elif len(ranges) == 1:
        r = ranges[0]
        inverted = [Range1D(coverage.min, r.min), Range1D(r.max, coverage.max)]
    else:
        lhs_range = ranges[0]
        inverted = [Range1D(coverage.min, lhs_range.min)]
        rhs_range = ranges[1]
        inverted.extend([Range1D(rhs_range.max, coverage.max)])
        for i in range(len(ranges)-1):
            inverted.append(Range1D(ranges[i].max, ranges[i+1].min))
    return [r for r in inverted if r.valid]


def search_for_beacon(sensors, min_coord: Coord, max_coord: Coord):
    base_range = Range1D(min_coord.x, max_coord.x)
    for j in range(min_coord.y, max_coord.y+1):
        ranges = sensor_ranges_at_row(j, sensors)
        combined_ranges = combine_ranges(ranges)
        inverted_ranges = invert_ranges(combined_ranges, base_range)
        possible_regions = [r
                            for r in inverted_ranges if r.exclusive_length > 0]
        if possible_regions:
            return j, possible_regions
    return []


def parse_input():
    with open('input.txt') as f:
        data = [s.strip('\n') for s in f.readlines()]
    sensors = [parse_line(row) for row in data]

    j, range_ = search_for_beacon(sensors, Coord(0, 0), Coord(4000000, 4000000))
    y = j
    x = range_[0].min+1
    print(x*4000000+y)


parse_input()
