from dataclasses import dataclass
from typing import Callable
from sympy import simplify, solve, Eq, symbols


def monkey_func(lhs, rhs, operator):
    if operator == '+':
        return lambda d: d[lhs](d) + d[rhs](d)
    if operator == '-':
        return lambda d: d[lhs](d) - d[rhs](d)
    if operator == '/':
        return lambda d: d[lhs](d) // d[rhs](d)
    if operator == '*':
        return lambda d: d[lhs](d) * d[rhs](d)
    if operator == '=':
        return lambda d: d[lhs](d) == d[rhs](d)
    if operator is None and rhs is None and lhs is not None:
        return lambda d: int(lhs)


def parse_expression(string):
    if '+' in string:
        a, b = string.split('+')
        new_func = monkey_func(a, b, '+')
    elif '-' in string:
        a, b = string.split('-')
        new_func = monkey_func(a, b, '-')
    elif '/' in string:
        a, b = string.split('/')
        new_func = monkey_func(a, b, '/')
    elif '*' in string:
        a, b = string.split('*')
        new_func = monkey_func(a, b, '*')
    elif '=' in string:
        a, b = string.split('=')
        new_func = monkey_func(a, b, '=')
    else:
        new_func = monkey_func(string, None, None)
    return new_func


@dataclass
class Monkey:
    name: str
    string: str
    children: 'list[Monkey, Monkey]' = None
    operator: str = None
    function: Callable = None

    def populate(self, monkey_yellow_pages):
        if '+' in self.string:
            self.operator = '+'
            child1, child2 = self.string.split(self.operator)
            self.children = [monkey_yellow_pages[child1],
                             monkey_yellow_pages[child2]]
        elif '-' in self.string:
            self.operator = '-'
            child1, child2 = self.string.split(self.operator)
            self.children = [monkey_yellow_pages[child1],
                             monkey_yellow_pages[child2]]
        elif '/' in self.string:
            self.operator = '/'
            child1, child2 = self.string.split(self.operator)
            self.children = [monkey_yellow_pages[child1],
                             monkey_yellow_pages[child2]]
        elif '*' in self.string:
            self.operator = '*'
            child1, child2 = self.string.split(self.operator)
            self.children = [monkey_yellow_pages[child1],
                             monkey_yellow_pages[child2]]
        elif '=' in self.string:
            self.operator = '='
            child1, child2 = self.string.split(self.operator)
            self.children = [monkey_yellow_pages[child1],
                             monkey_yellow_pages[child2]]
        else:
            self.children = []
            val = int(self.string)
            self.function = lambda d: val

    @property
    def dependents(self):
        if self.children:
            child1, child2 = self.children
            return f'({child1.dependents}{self.operator}{child2.dependents})'
        else:
            return self.string


@dataclass
class Monkeys:
    functions: dict[str, Callable]
    lines: dict[str, str]
    all: dict[str, Monkey]

    @classmethod
    def from_text(cls, file_name: str):
        with open(file_name) as f:
            data = [s.strip('\n').replace(' ', '').split(':')
                    for s in f.readlines()]
        funcs = {}
        lines = {}
        monks = {}
        for name, value in data:
            lines[name] = value
            funcs[name] = parse_expression(value)
            monks[name] = Monkey(name, value)
        for name, monkey in monks.items():
            monkey.populate(monks)
        return cls(funcs, lines, monks)


def main():
    monkeys = Monkeys.from_text('input.txt')
    # part 1
    print(monkeys.functions['root'](monkeys.functions))
    # part 2
    monkeys.functions['root'] = parse_expression(
        monkeys.lines['root'].replace('+', '=')
    )
    monkeys.all['humn'].string = 'x'
    root = monkeys.all['root']
    lhs, rhs = root.children
    x = symbols('x')
    if 'x' not in lhs.dependents:
        value = monkeys.functions[lhs.name](monkeys.functions)
        eqn = simplify(rhs.dependents)
    else:
        value = monkeys.functions[rhs.name](monkeys.functions)
        eqn = simplify(lhs.dependents)
    print(solve(Eq(eqn, value), x))


if __name__ == '__main__':
    main()
