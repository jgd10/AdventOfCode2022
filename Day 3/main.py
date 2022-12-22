import csv


all_items = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'

PRIORITIES = {item: i+1 for i, item in enumerate(all_items)}


def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def find_dupe_item_priority(string):
    n = len(string)//2
    first, second = string[:n], string[n:]
    assert len(string[:n]) == len(string[n:])
    repeat_item = [c for c in first if c in second][0]
    return PRIORITIES[repeat_item]


def find_badges(rows):
    total_ = 0
    for chunk in chunks(rows, 3):
        all_chars = {c for elf in chunk for c in elf[0]}
        for c in all_chars:
            if c in chunk[0][0] and c in chunk[1][0] and c in chunk[2][0]:
                total_ += PRIORITIES[c]
    return total_


with open('input.txt', 'r') as f:
    reader = csv.reader(f)
    data = [row for row in reader]

total = 0
for row in data:
    total += find_dupe_item_priority(row[0])

print(total)

badge_total = find_badges(data)
print(badge_total)
