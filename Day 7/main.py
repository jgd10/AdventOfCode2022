from enum import Enum


class CommandNotFound(Exception):
    pass


class Record:
    def __init__(self, name, is_dir, size, children=[]):
        self.name: str = name
        self.is_directory: bool = is_dir
        self._size: int = 0
        self.parent: 'Record' = None
        self._children: 'list[Record]' = None

    @property
    def size(self):
        if self.is_directory:
            size = sum([r.size for r in self.children])
            self._size = size
        return self._size

    @property
    def children(self):
        if self._children is None:
            self._children = []
        return self._children


class Commands(Enum):
    CD = 'cd'
    LS = 'ls'


def parse_command(line_, dir_: Record):
    line_ = line_.replace('\n', '')
    items = line_.split(' ')
    if items[1] == Commands.CD.name.lower():
        command = Commands.CD.name
        if items[2] == '..':
            new_dir = dir_.parent
        else:
            new_dir = identify_or_create_dir(dir_, items[2])
    elif items[1] == Commands.LS.name.lower():
        command = Commands.LS.name
        new_dir = dir_
    else:
        raise CommandNotFound(line_)
    return command, new_dir


def parse_output(line_, dir_):
    items = line_.split(' ')
    if items[0] == 'dir':
        new_rec = identify_or_create_dir(dir_, items[1])
    else:
        new_rec = identify_or_create_file(dir_, items[1], int(items[0]))
    return new_rec


def identify_or_create_dir(dir_, name):
    if dir_ is None:
        new_dir = Record(name, True, parent=None)
    elif name in [d.name for d in dir_.children]:
        new_dir = [d for d in dir_.children if d.name == name][0]
    else:
        new_dir = Record(name, True, parent=dir_)
        dir_.children.append(new_dir)
    return new_dir


def identify_or_create_file(dir_: Record, name: str, size: int = 0):
    if dir_ is None:
        new_file = Record(name, False, size, parent=None)
    elif name in [d.name for d in dir_.children]:
        new_file = [d for d in dir_.children if d.name == name][0]
    else:
        new_file = Record(name, False, size, parent=dir_)
        dir_.children.append(new_file)
    return new_file


def parse_terminal_line(line, current_dir: Record | None, current_cmd):
    if line[0] == '$':
        current_cmd, current_dir = parse_command(line, current_dir)
    else:
        parse_output(line, current_dir)
    return current_dir, current_cmd


def find_root(record: Record):
    parent = record.parent
    if parent is not None:
        return find_root(parent)
    else:
        return record


def collect_all_dirs(parent: Record, all_recs):
    for child in parent.children:
        if child.is_directory:
            all_recs.append(child)
            collect_all_dirs(child, all_recs)


def calc_part1(root_: Record):
    all_recs_ = []
    collect_all_dirs(root_, all_recs_)
    results = [r.size
               for r in all_recs_
               if r.size <= 100000 and r.is_directory]
    return sum(results)


def calc_part2(root_: Record):
    all_recs_ = []
    collect_all_dirs(root_, all_recs_)
    used_size = root_.size
    unused_size = 70000000 - used_size
    needed_size = 30000000
    target_dir_size = needed_size - unused_size
    potential_dirs = [r for r in all_recs_ if r.size > target_dir_size]
    delete_rec = Record('Dummy', False, unused_size)
    for rec in potential_dirs:
        if rec.size < delete_rec.size:
            delete_rec = rec
    return delete_rec.size


with open('input.txt', 'r') as f:
    terminal = f.readlines()
    directory, cmd = parse_terminal_line(terminal[0].replace('\n', ''),
                                         None,
                                         '')
    for entry in terminal[1:]:
        entry = entry.replace('\n', '')
        directory, cmd = parse_terminal_line(entry, directory, cmd)


root = find_root(directory)

print(calc_part1(root))
print(calc_part2(root))

