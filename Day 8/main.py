

def check_visibility_of_coord(coord, r, c):
    j0, i0 = coord
    tree_ = r[j0][i0]
    blocking_trees_east = [t for t in r[j0][:i0] if t >= tree_]
    visible_east = not bool(blocking_trees_east)
    blocking_trees_west = [t for t in r[j0][i0+1:] if t >= tree_]
    visible_west = not bool(blocking_trees_west)
    blocking_trees_north = [t for t in c[i0][:j0] if t >= tree_]
    visible_north = not bool(blocking_trees_north)
    blocking_trees_south = [t for t in c[i0][j0+1:] if t >= tree_]
    visible_south = not bool(blocking_trees_south)
    return any([visible_south, visible_north, visible_west, visible_east])


def find_number_blocked_at(host, channel):
    if channel:
        for k, t in enumerate(channel):
            if t >= host:
                return k+1
        return k + 1
    else:
        return 0


def find_max_scenic_score(all_coords, r, c):
    max_score = 0
    for coord in all_coords:
        score = find_scenic_score(coord, r, c)
        max_score = max(score, max_score)
    return max_score


def find_scenic_score(coord, r, c):
    j0, i0 = coord
    tree_ = r[j0][i0]
    scenic_num_east = find_number_blocked_at(tree_, r[j0][:i0][::-1])
    scenic_num_west = find_number_blocked_at(tree_, r[j0][i0+1:])
    scenic_num_north = find_number_blocked_at(tree_, c[i0][:j0][::-1])
    scenic_num_south = find_number_blocked_at(tree_, c[i0][j0+1:])
    return scenic_num_south*scenic_num_west*scenic_num_north*scenic_num_east


def find_visible_trees(rs, cs):
    all_coords = {(i, j) for i in range(len(rs)) for j in range(len(cs))}
    visible_coords = [c
                      for c in all_coords
                      if check_visibility_of_coord(c, rs, cs)]
    return visible_coords


with open('input.txt', 'r') as f:
    data = [line.strip('\n') for line in f.readlines()]

rows = [[int(c) for c in list(row)] for row in data]
cols = [[] for row in rows]
for row in rows:
    for ii, tree in enumerate(row):
        cols[ii].append(tree)


visible_coords = find_visible_trees(rows, cols)
print(find_max_scenic_score(visible_coords, rows, cols))

