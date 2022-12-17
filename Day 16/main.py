from dataclasses import dataclass
from itertools import combinations
from more_itertools import set_partitions


def sorted_k_partitions(seq, k):
    """Returns a list of all unique k-partitions of `seq`.

    Each partition is a list of parts, and each part is a tuple.

    The parts in each individual partition will be sorted in shortlex
    order (i.e., by length first, then lexicographically).

    The overall list of partitions will then be sorted by the length
    of their first part, the length of their second part, ...,
    the length of their last part, and then lexicographically.
    from https://stackoverflow.com/questions/39192777/how-to-split-a-list-into-n-groups-in-all-possible-combinations-of-group-length-a
    """
    n = len(seq)
    groups = []  # a list of lists, currently empty

    def generate_partitions(i):
        if i >= n:
            yield list(map(tuple, groups))
        else:
            if n - i > k - len(groups):
                for group in groups:
                    group.append(seq[i])
                    yield from generate_partitions(i + 1)
                    group.pop()

            if len(groups) < k:
                groups.append([seq[i]])
                yield from generate_partitions(i + 1)
                groups.pop()

    result = generate_partitions(0)

    # Sort the parts in each partition in shortlex order
    result = [sorted(ps, key=lambda p: (len(p), p)) for ps in result]
    # Sort partitions by the length of each part, then lexicographically.
    result = sorted(result, key=lambda ps: (*map(len, ps), ps))

    return result


@dataclass
class Node:
    name: str
    edges: list['Edge']
    rate: int = 0

    @classmethod
    def init(cls, name, rate):
        return cls(name, [], rate)

    def __repr__(self):
        return f'Node({self.name}, {self.rate}, {len(self.edges)})'


@dataclass
class Edge:
    start: Node
    end: Node
    weight: int


@dataclass
class Network:
    nodes: dict[str, Node]
    start: Node
    _shortest_paths: dict[str, 'Path'] = None
    _valves: list[Node] = None
    _valve_names: set[str] = None
    _path_flow_pressures: dict[str, int] = None
    _visited_valves_with_elephant: set[str] = None

    def __repr__(self):
        return f'Network({[n.__repr__() for n in self.nodes.values()]}'

    def shortest_path_between(self, node1, node2):
        """Breadth-first algorithm used"""
        visited_nodes = {k: False for k in self.nodes}
        parents = {k: None for k in self.nodes}
        nodes = [node1]
        visited_nodes[node1.name] = True
        while len(nodes) > 0:
            node = nodes.pop(0)
            if node is node2:
                break
            for edge in node.edges:
                if not visited_nodes[edge.end.name]:
                    visited_nodes[edge.end.name] = True
                    parents[edge.end.name] = node.name
                    nodes.append(edge.end)
        node_path = []
        name = node2.name
        while name != node1.name:
            node_path.append(self.nodes[name])
            name = parents[name]
        node_path.append(node1)
        return Path(node_path[::-1])

    def highest_rank_path(self, node1, node2):
        visited_nodes = {k: False for k in self.nodes}
        visited_nodes[node1.name] = True
        chosen_path = Path([node1])
        while True:
            possible_paths = [chosen_path + Path([node1, edge.end]) for edge in node1.edges]
            possible_paths.sort(key=lambda x: x.rank, reverse=True)
            chosen_path = chosen_path + possible_paths.pop(0)
            visited_nodes[chosen_path.nodes[-1].name] = True
            if chosen_path.nodes[-1] is node2:
                return chosen_path
            else:
                node1 = chosen_path.nodes[-1]

    @property
    def shortest_paths_between_valves(self):
        if self._shortest_paths is None:
            paths_between_non_zero_nodes = {}
            for n1, n2 in combinations([self.start] + self.valves, 2):
                shortest_path = self.shortest_path_between(n1, n2)
                paths_between_non_zero_nodes[n1.name + n2.name]\
                    = shortest_path.start_at(n1)
                paths_between_non_zero_nodes[n2.name + n1.name] \
                    = shortest_path.start_at(n2)
            self._shortest_paths = paths_between_non_zero_nodes
        return self._shortest_paths

    @property
    def combined_visited_valves(self):
        if self._visited_valves_with_elephant is None:
            self._visited_valves_with_elephant = set()
        return self._visited_valves_with_elephant

    @property
    def valves(self):
        if self._valves is None:
            self._valves = [n for name, n in self.nodes.items() if n.rate > 0]
        return self._valves

    @property
    def valve_names(self):
        if self._valve_names is None:
            self._valve_names = {n.name for n in self.valves}
        return self._valve_names

    def maximum_pressure_release_paths(self):
        paths = []
        results = set()
        self.all_paths2(paths, 0, 30, results)
        results = list(results)
        results.sort(reverse=True)
        return results.pop(0)

    def possible_valve_combinations(self):
        possible_combinations = sorted_k_partitions(list(self.valve_names), 2)
        reduced_combos = {}
        for pc in possible_combinations:
            group1, group2 = pc
            reduced_combos


    def maximum_pressure_release_with_elephant(self):
        scores = []
        possible_combinations = sorted_k_partitions(list(self.valve_names), 2)
        print(len(possible_combinations))
        for combo in possible_combinations:
            ellie, me = combo
            elephant_valves = {v for v in ellie}
            my_valves = {v for v in me}
            ellie_paths = []
            ellie_results = set()
            self.all_paths3(ellie_paths, 0, 26, ellie_results, elephant_valves)
            ellie_results = list(ellie_results)
            ellie_results.sort(reverse=True)
            ellie_max = ellie_results.pop(0)
            my_paths = []
            my_results = set()
            self.all_paths3(my_paths, 0, 26, my_results, my_valves)
            my_results = list(my_results)
            my_results.sort(reverse=True)
            my_max = my_results.pop(0)
            scores.append(ellie_max + my_max)

        scores.sort(reverse=True)
        return scores.pop(0)

    def calculate_flow_pressure(self, paths):
        if self._path_flow_pressures is None:
            self._path_flow_pressures = {}
        key = ''.join([f'{p.start.name}{p.end.name}' for p in paths])
        if key in self._path_flow_pressures:
            return self._path_flow_pressures[key]
        remaining_time = 30
        net_change = 0
        for path in paths:
            time_taken = path.tunnels + 1
            remaining_time -= time_taken
            remaining_time = max(remaining_time, 0)
            net_change += path.end.rate * remaining_time
            if remaining_time == 0:
                break
        self._path_flow_pressures[key] = net_change
        return net_change

    def calculate_path_flow_pressure(self, path, remaining_time):
        time_taken = path.tunnels + 1
        remaining_time -= time_taken
        remaining_time = max(remaining_time, 0)
        return path.end.rate * remaining_time, remaining_time

    def all_paths2(self, paths, score, remaining_time, scores):
        if not paths:
            start = 'AA'
            visited_valves = {'AA'}
        else:
            start = paths[-1].end.name
            visited_valves = {p.end.name for p in paths}
            visited_valves.add('AA')
        paths_from_start = [n.start_at(self.nodes[start])
                            for k, n in self.shortest_paths_between_valves.items()
                            if start in k and n.end.name not in visited_valves]
        if len(paths_from_start) > 0:
            largest_path_score = 0
            for path_from_start in paths_from_start:
                path_score, time = self.calculate_path_flow_pressure(
                    path_from_start, remaining_time
                )
                if path_score > 0:
                    largest_path_score = max(path_score, largest_path_score)
                    self.all_paths2(paths + [path_from_start],
                                    score + path_score,
                                    time, scores)
            score += largest_path_score
        scores.add(score)

    def all_paths3(self, paths, score, remaining_time, scores, target_valves):
        if not paths:
            start = 'AA'
            visited_valves = {'AA'}
        else:
            start = paths[-1].end.name
            visited_valves = {p.end.name for p in paths}
            visited_valves.add('AA')
        paths_from_start = [n.start_at(self.nodes[start])
                            for k, n in self.shortest_paths_between_valves.items()
                            if start in k and n.end.name not in visited_valves
                            and n.end.name in target_valves]
        if len(paths_from_start) > 0:
            largest_path_score = 0
            for path_from_start in paths_from_start:
                path_score, time = self.calculate_path_flow_pressure(
                    path_from_start, remaining_time
                )
                if path_score > 0:
                    largest_path_score = max(path_score, largest_path_score)
                    self.all_paths3(paths + [path_from_start],
                                    score + path_score,
                                    time, scores, target_valves)
            score += largest_path_score
        scores.add(score)


@dataclass
class Path:
    nodes: list[Node]

    def __repr__(self):
        return f'Path({self.nodes[0].name}-{self.nodes[-1].name}-{len(self.nodes)})'

    def start_at(self, start: Node):
        if self.nodes[0] is start:
            return self
        else:
            return Path(self.nodes[::-1])

    def flow_pressure_rank(self, remaining_time: int = 30):
        length = len(self.nodes)
        net_change = 0
        time = remaining_time
        for n in self.nodes:
            if time == 0:
                break
            if n is self.nodes[-1]:
                net_change += time * n.rate
            time -= 1
        return net_change / length

    def flow_pressure_rank2(self, remaining_time: int = 30):
        time_taken = self.tunnels + 1
        # remaining_time -= time_taken
        # remaining_time = max(remaining_time, 0)
        return self.end.rate / time_taken

    @property
    def tunnels(self):
        return len(self.nodes) - 1

    def copy(self):
        return Path(self.nodes[:])

    @property
    def ends(self):
        return [self.nodes[0], self.nodes[-1]]

    @property
    def start(self):
        return self.nodes[0]

    @property
    def end(self):
        return self.nodes[-1]

    @property
    def rank(self):
        length = len(self.nodes)
        net_change = 0
        time = 30
        for n in self.nodes:
            if n is self.nodes[-1]:
                net_change += time * n.rate
            time -= 1
        return net_change / length

    @property
    def length(self):
        return len(self.nodes)


def maximise_flow(network):
    start = network.nodes['AA']
    # goals: open pressure ASAP
    #        open the biggest valves ASAP
    remaining_non_zero_nodes = [v for v in network.nodes.values() if v.rate > 0]
    paths = network.shortest_path_visiting_these_nodes(
        remaining_non_zero_nodes
    )
    paths_list = [p for p in paths.values()]
    paths_list.sort(key=lambda x: x.rank, reverse=True)
    optimal_path = paths_list.pop(0)
    remaining_nonzero_nodes = [n
                               for n in remaining_non_zero_nodes
                               if n not in optimal_path.nodes]

    while True:
        paths_to_next_node = []
        for node in optimal_path.nodes:
            paths = [network.shortest_path_between(node, nz)
                     for nz in remaining_nonzero_nodes]
            paths_to_next_node.extend(paths)
        paths_to_next_node.sort(key=lambda x: x.rank, reverse=True)
        path = paths_to_next_node.pop(0)
        optimal_path = optimal_path + path
        remaining_nonzero_nodes = [n for n in remaining_non_zero_nodes
                                   if n not in optimal_path.nodes]
        if len(remaining_non_zero_nodes) == 0:
            break
    return optimal_path


def parse_line(line: str):
    name_and_rate, tunnels = line.split(';')
    name = name_and_rate[6:8]
    _, rate = name_and_rate.split('=')
    rate = int(rate)
    _, tunnels = tunnels.split('to valve')
    if 's' in tunnels:
        tunnels = tunnels.replace('s ', '')
    tunnels = tunnels.split(', ')
    return name, rate, [t.strip(' ') for t in tunnels]


def build_network(rows):
    nodes = {}
    tunnels = {}
    for row in rows:
        name, rate, links = parse_line(row)
        if name not in nodes:
            nodes[name] = Node.init(name, rate)
            tunnels[name] = links
    for name, valves in tunnels.items():
        nodes[name].edges = [Edge(nodes[name], nodes[k], 1) for k in valves]
    return Network(nodes, nodes['AA'])


def main():
    with open('input.txt') as f:
        data = [s.strip('\n') for s in f.readlines()]

    network = build_network(data)
    max_pressure = network.maximum_pressure_release_paths()
    print(max_pressure)
    max_pressure2 = network.maximum_pressure_release_with_elephant()
    print(max_pressure2)


main()

