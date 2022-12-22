from typing import List, Dict
from dataclasses import dataclass
import numpy as np


@dataclass
class Item:
    value: int
    remainders: Dict[int, int] = None
    denoms: Dict[int, int] = None


@dataclass
class Monkey:
    id: int
    items: List[Item]
    test_denominator: int
    operation_const: int
    operator: str
    true_id: int
    false_id: int
    true_monkey: 'Monkey' = None
    false_monkey: 'Monkey' = None
    inspection_counter: int = 0
    result_last_time: bool = None

    def operation(self, item):
        vals = []
        for remainder, denom in zip(item.remainders, item.denoms):
            if self.operator == '*':
                vals.append(remainder * (self.operation_const % denom) % denom)
            elif self.operator == '+':
                vals.append((remainder + self.operation_const) % denom)
            elif self.operator == '**':
                vals.append((remainder*remainder) % denom)
        return vals

    def test(self, item):
        return item.remainders[self.id] == 0

    def inspect_items(self):
        #print()
        while len(self.items) > 0:
            item = self.items.pop(0)
            item.remainders = self.operation(item)
            self.inspection_counter += 1
            result = self.test(item)
            if result:
                self.true_monkey.pass_item(item)
            else:
                self.false_monkey.pass_item(item)

    def pass_item(self, item: Item):
        self.items.append(item)


def params_filled(*args):
    return all([a is not None for a in args])


def parse_input(lines):
    monkey_lines = [line for line in lines if 'Monkey' in line]
    monkeys = {}
    monkey_num = None
    items = None
    operation = None
    const = None
    denominator = None
    true_monkey = None
    false_monkey = None
    for line in lines:
        if line in monkey_lines:
            _, monkey_num = [s.strip(':') for s in line.split('Monkey')]
            monkey_num = int(monkey_num)
            items = None
            operation = None
            const = None
            denominator = None
            true_monkey = None
            false_monkey = None
        if 'Starting items' in line:
            _, item_strings = line.split(':')
            items = [Item(int(s.strip(' ')))
                     for s in item_strings.split(',')]
        if 'Operation' in line:
            if '+' in line:
                operation = '+'
                _, const = [s.strip(' ') for s in line.split('+')]
                const = int(const)
            elif '*' in line:
                if line.count('old') == 2:
                    operation = '**'
                    const = 0
                else:
                    operation = '*'
                    _, const = [s.strip(' ') for s in line.split('*')]
                    const = int(const)
        if 'Test' in line:
            _, denominator = line.split('by')
            denominator = int(denominator)

        if 'true' in line:
            _, true_monkey = line.split('monkey')
            true_monkey = int(true_monkey)
        if 'false' in line:
            _, false_monkey = line.split('monkey')
            false_monkey = int(false_monkey)
        if params_filled(monkey_num, items, operation, const,
                         denominator, true_monkey, false_monkey):
            new = Monkey(monkey_num, items, denominator, const,
                         operation, true_monkey, false_monkey)
            monkeys[monkey_num] = new
    if params_filled(monkey_num, items, operation, const,
                     denominator, true_monkey, false_monkey):
        new = Monkey(monkey_num, items, denominator,
                     const,
                     operation, true_monkey, false_monkey)
        monkeys[monkey_num] = new

    for monkey in monkeys.values():
        for item in monkey.items:
            item.remainders = [item.value for i in monkeys]
            item.denoms = [m.test_denominator for m in monkeys.values()]
            for monkey2 in monkeys.values():
                item.remainders[monkey2.id] = item.remainders[monkey2.id] % monkey2.test_denominator
        monkey.true_monkey = monkeys[monkey.true_id]
        monkey.false_monkey = monkeys[monkey.false_id]
    return monkeys


def main():
    with open('input.txt') as f:
        data = [s.strip('\n') for s in f.readlines()]
    monkeys = parse_input(data)
    for i in range(10000):
        for monkey in monkeys.values():
            monkey.inspect_items()
    inspections = [m.inspection_counter for m in monkeys.values()]
    inspections = sorted(inspections)
    print(inspections)
    two_largest = inspections[-2:]
    monkey_business = two_largest[0] * two_largest[1]
    print(monkey_business)


main()
