from dataclasses import dataclass
from itertools import zip_longest


CONVERTER = {'=': -2, '-': -1, '0': 0, '1': 1, '2': 2}

ADDITION_TABLE = {('=', '='): ('-', '1'),
                  ('=', '-'): ('-', '2'),
                  ('=', '0'): ('0', '='),
                  ('=', '1'): ('0', '-'),
                  ('=', '2'): ('0', '0'),
                  ('-', '-'): ('0', '='),
                  ('-', '0'): ('0', '-'),
                  ('-', '1'): ('0', '0'),
                  ('-', '2'): ('0', '1'),
                  ('0', '0'): ('0', '0'),
                  ('0', '1'): ('0', '1'),
                  ('0', '2'): ('0', '2'),
                  ('1', '1'): ('0', '2'),
                  ('1', '2'): ('1', '='),
                  ('2', '2'): ('1', '-')}


@dataclass
class SNAFU:
    string: str
    _rep: list[str] = None
    _converter: dict[str, int] = None

    @property
    def decimal(self):
        return sum(self.converter[k]*(5**i) for i, k in enumerate(self.string[::-1]))

    @property
    def converter(self):
        if self._converter is None:
            self._converter = {'=': -2, '-': -1, '0': 0, '1': 1, '2': 2}
        return self._converter

    def __add__(self, other):
        new = {i: '0' for i in range(100)}
        i = 0
        for v1, v2 in zip_longest(self.string[::-1], other.string[::-1], fillvalue='0'):
            carry1, val = self.sum_singles(v1, v2)
            carry2, new[i] = self.sum_singles(val, new[i])
            _, carry = self.sum_singles(carry1, carry2)
            j = i
            while carry != '0':
                carry, new[j+1] = self.sum_singles(carry, new[j+1])
                j += 1
            i += 1
        result = SNAFU(''.join([v for v in new.values()][::-1]).lstrip('0'))
        return result

    @staticmethod
    def sum_singles(v1, v2):
        sum_ = (v1, v2)
        if sum_ not in ADDITION_TABLE:
            sum_ = sum_[::-1]
        return ADDITION_TABLE[sum_]


def main():
    with open('input.txt') as f:
        data = [s.strip('\n') for s in f.readlines()]
    snafus = [SNAFU(s) for s in data]
    total = SNAFU('0')
    for sn in snafus:
        total = total + sn
    print(total)


def my_test():
    with open('my_test.txt') as f:
        data = [s.strip('\n') for s in f.readlines()]
    for row in data:
        num1, num2, result = row.split(' ')
        result2 = SNAFU(num1) + SNAFU(num2)
        print(result, result2)


if __name__ == '__main__':
    main()
