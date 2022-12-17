from enum import Enum


class Result(Enum):
    CORRECT = 1
    INCORRECT = 2
    INCONCLUSIVE = 3


def bubble_sort(items):
    sorted_items = []
    n = len(items)
    while len(sorted_items) < n:
        for i in range(len(items) - 1):
            item1 = items[i]
            item2 = items[i+1]
            result = check_line_pair(item1, item2)
            if not result:
                items[i], items[i+1] = item2, item1
        sorted_items.append(items.pop(-1))
    return sorted_items[::-1]


def check_line_pair(line1, line2):
    left = eval(line1)
    right = eval(line2)
    result = compare_elements(left, right)
    return result == Result.CORRECT


def compare_elements(val1, val2):
    if isinstance(val1, int) and isinstance(val2, int):
        result = compare_integers(val1, val2)
        return result

    if isinstance(val1, int):
        val1 = [val1]
    if isinstance(val2, int):
        val2 = [val2]

    if len(val1) < len(val2):
        correct_lengths = Result.CORRECT
    elif len(val1) == len(val2):
        correct_lengths = Result.INCONCLUSIVE
    else:
        correct_lengths = Result.INCORRECT

    # result = Result.INCONCLUSIVE
    for element1, element2 in zip(val1, val2):
        result = compare_elements(element1, element2)
        if result in [Result.CORRECT, result.INCORRECT]:
            return result
    return correct_lengths


def compare_integers(val1, val2):
    if val1 != val2:
        if val1 < val2:
            return Result.CORRECT
        else:
            return Result.INCORRECT
    else:
        return Result.INCONCLUSIVE


def main():
    with open('input.txt') as f:
        data = [s.strip('\n') for s in f.readlines()]
        lines = []
        index_sum = 0
        counter = 0
        all_lines = []
        for row in data:
            if row:
                lines.append(row.strip('\n'))
                all_lines.append(row.strip('\n'))
            if len(lines) == 2:
                counter += 1
                valid_input = check_line_pair(*lines)
                # print(counter, valid_input, lines)
                if valid_input:
                    index_sum += counter
                lines = []
        print(index_sum)
    items = bubble_sort(all_lines + ['[[2]]', '[[6]]'])
    indices = 1
    for i, item in enumerate(items):
        if item in ['[[2]]', '[[6]]']:
            indices *= i + 1
    print(indices)


main()
