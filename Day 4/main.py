import csv


def range_to_set(string):
    start, end = string.split('-')
    start, end = int(start), int(end)
    diff = end - start
    new = {start, end}
    for i in range(diff):
        new.add(start+i)
    return new


def ranges_from_string(row):
    ranges = [range_to_set(s) for s in row]
    return ranges


with open('input.txt', 'r') as f:
    reader = csv.reader(f)
    data = [ranges_from_string(row) for row in reader]


complete_overlaps = [pair for pair in data
                     if pair[0].issubset(pair[1])
                     or pair[1].issubset(pair[0])]
any_overlaps = [pair for pair in data if any(i in pair[0] for i in pair[1])]
print(len(any_overlaps))

