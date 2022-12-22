from dataclasses import dataclass


@dataclass
class Elf:
    total_calories: int


with open('input.txt', 'r') as f:
    data = f.read().split('\n')

new_elf = []
elves = []
max_cals = 0
for entry in data:
    if not entry:
        elves.append(sum(new_elf))
        max_cals = max(max_cals, sum(new_elf))
        new_elf = []
    else:
        new_elf.append(int(entry))

top_3_elves = sorted(elves)[-3:]
print(top_3_elves)
print(sum(top_3_elves))
