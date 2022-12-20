def find_new_index(value, index, size):
    new_index = index + value
    if 0 < new_index < size:
        return new_index
    if value < 0:
        if (new_index % size) == 0:
            return size
        return new_index % size
    else:
        return new_index % size


def insert_value_in_list(value, index, list_):
    if value[1] < 0 and index != 0:
        left = list_[:index]
        right = list_[index:]
    elif index == len(list_):
        left = list_[:]
        right = []
    else:
        left = list_[:index + 1]
        right = list_[index + 1:]
    if value in left:
        left.remove(value)
    else:
        right.remove(value)
    return left + [value] + right


def main():
    with open('input.txt') as f:
        data = [s.strip('\n') for s in f.readlines()]
    sequence = [[i, int(s)] for i, s in enumerate(data)]
    sequence2 = [[i, int(s)*811589153] for i, s in enumerate(data)]

    base_sequence = sequence2[:]
    length = len(sequence2)
    for ii in range(10):
        for j, s in enumerate(base_sequence):
            value = s[1]
            index = sequence2.index(s)
            new_index = find_new_index(value, index, length-1)
            sequence2.insert(new_index, sequence2.pop(index))

    # 1, 2, -3, 4, 0, 3, -2
    val = [k for k in sequence2 if k[1] == 0][0]
    j0 = sequence2.index(val)

    j1000 = (j0 + 1000) % length
    j2000 = (j0 + 2000) % length
    j3000 = (j0 + 3000) % length

    print([sequence2[j1000][1], sequence2[j2000][1], sequence2[j3000][1]])
    print(sum([sequence2[j1000][1], sequence2[j2000][1], sequence2[j3000][1]]))


main()
