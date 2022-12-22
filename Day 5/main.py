STACK_INDEX_MAP = {k: s for k, s in zip(range(0, 10*4, 4), '123456789')}


def parse_move(move):
    entries = move.split(' ')
    start = entries[3]
    end = entries[5].strip('\n')
    amount = int(entries[1])
    return start, end, amount


def parse_crates(crates_input):
    numbers_row = [r for r in crates_input if r[:2] == ' 1'][0]
    stacks = {k: []
              for k in [s
                        for s in numbers_row.split(' ')
                        if s in '123456789' and s]}
    for row in crates_input:
        for i, char in enumerate((split_row := list(row))):
            if char == '[':
                stack_num = STACK_INDEX_MAP[i]
                crate = ''.join(split_row[i+1])
                stacks[stack_num].append(crate)
    for k, stack in stacks.items():
        stacks[k] = stack[::-1]
    return stacks


def move_crates(stacks, moves):
    for move in moves:
        start_stack = stacks[move[0]]
        moving_crates = start_stack[-move[2]:]
        remaining_crates = start_stack[:-move[2]]
        stacks[move[0]] = remaining_crates
        stacks[move[1]].extend(moving_crates)


with open('input.txt', 'r') as f:
    data = f.readlines()


crates = []
moves_ = []
for r in data:
    if r[:3] == 'mov':
        moves_.append(parse_move(r))
    else:
        crates.append(r)

s = parse_crates(crates)
move_crates(s, moves_)
final_crates = ''.join([v[-1] for v in s.values()])
print(final_crates)
