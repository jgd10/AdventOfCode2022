from dataclasses import dataclass
from typing import List


@dataclass
class Task:
    duration: int
    command: str
    value: int
    cycles_experienced: int = 0
    completed: bool = False

    def increment_cycle(self):
        self.cycles_experienced += 1

    def execute(self, x: int):
        if self.cycles_experienced == self.duration \
                and not self.completed:
            self.completed = True
            return x + self.value
        else:
            return x


class NOOP(Task):
    def __init__(self):
        super().__init__(1, 'noop', 0)


class AddXTask(Task):
    def __init__(self, value: int):
        super().__init__(2, 'addx', value, 0)


def parse_commands(strings):
    commands = []
    for string in strings:
        entries = string.split(' ')
        if entries[0].lower() == 'noop':
            commands.append(NOOP())
        elif entries[0].lower() == 'addx':
            val = int(entries[1])
            commands.append(AddXTask(val))
    return commands


def execute_commands(commands: List[Task], cycle_limit: int = 240):
    results = []
    command = None
    x = 1
    execution_occurring = False
    for i in range(cycle_limit):
        results.append((i+1, x))
        if not execution_occurring:
            command = commands.pop(0)
            execution_occurring = True
        if not command.completed:
            command.increment_cycle()
            x = command.execute(x)
        if command.completed:
            execution_occurring = False

    return results


def part1(results):
    total = 0
    for cycle in [20, 60, 100, 140, 180, 220]:
        result = results[cycle-1]
        assert result[0] == cycle, result
        total += result[1]*result[0]
    return total


def part2(results):
    pixels = ['.']*240
    k = 0
    for i in range(6):
        for j in range(40):
            cycle = results[k]
            k += 1
            num, x = cycle
            if x <= j+1 < x+3:
                pixels[num-1] = '#'

    for i in range(6):
        row = ''.join(pixels[i*40:(i+1)*40])
        print(row)


def main():
    with open('input.txt') as f:
        data = [s.strip('\n') for s in f.readlines()]
    commands = parse_commands(data)
    results = execute_commands(commands)
    print(part1(results))
    part2(results)


main()

