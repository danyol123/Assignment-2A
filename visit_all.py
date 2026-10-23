"""
COS30019 - Assignment 2A - Research: visit ALL destinations by the shortest path.

Usage (Windows CMD), from the folder that contains search.py:
    python visit_all.py <filename> <method>
    <method> is one of: DFS, BFS, GBFS, AS, CUS1, CUS2

If destination is unreachable:
  1. Destinations that cannot be reached from the origin at all are dropped first (simple graph reachability) and reported at the end.
  2. If the remaining ones still cannot all be visited in one walk (for example because of one-way edges), the program tries smaller groups, largest first, and reports the best walk it can find.
  3. If nothing can be visited, it prints "No goal is reachable; <nodes>".
"""

import math
import sys
from collections import deque
from itertools import combinations

from search import Problem, ProblemFormatError, STRATEGIES, format_result, parse_problem

LIMIT = 2_000_000

class NodeLimit(Exception):
    pass

class VisitAll(Problem):
    """Route-finding problem whose goal is to visit every target destination."""

    def __init__(self, base, targets):
        super().__init__(base.nodes, base.edges, base.origin, base.destinations)
        self.all = frozenset(targets)
        self.seen = {}
        self.scale = min([1.0] + [c / self.dist(a, b)
                                  for a, nbrs in self.edges.items()
                                  for b, c in nbrs if self.dist(a, b) > 0])

    def dist(self, a, b):
        return math.hypot(self.nodes[a][0] - self.nodes[b][0],
                          self.nodes[a][1] - self.nodes[b][1])

    def root(self):
        node = super().root()
        self.seen[node.order] = frozenset([node.state]) & self.all
        return node

    def make_node(self, state, parent, step_cost=0):
        if self.nodes_created >= LIMIT:
            raise NodeLimit
        return super().make_node(state, parent, step_cost)

    def expand(self, node, avoid_cycles=False):
        children = []
        for nbr, cost in self.edges.get(node.state, []):
            visited = self.seen[node.order] | ({nbr} & self.all)
            if avoid_cycles and self.repeats(node, nbr, visited):
                continue
            child = self.make_node(nbr, node, cost)
            self.seen[child.order] = visited
            children.append(child)
        return children

    def repeats(self, node, state, visited):
        """True if the same (map node, visited set) is already on this branch."""
        while node is not None:
            if node.state == state and self.seen[node.order] == visited:
                return True
            node = node.parent
        return False

    def is_goal(self, node):
        return self.seen[node.order] == self.all

    def heuristic(self, node):
        """Distance to the FARTHEST unvisited target, times scale (admissible)."""
        left = self.all - self.seen[node.order]
        return self.scale * max((self.dist(node.state, d) for d in left), default=0)


def reachable_from_origin(base):
    """Map nodes that can be reached from the origin (ignores edge costs)."""
    found, queue = {base.origin}, deque([base.origin])
    while queue:
        for nbr, _cost in base.edges.get(queue.popleft(), []):
            if nbr not in found:
                found.add(nbr)
                queue.append(nbr)
    return found


def solve(base, strategy):
    """Returns (goal node or None, nodes created in total, targets visited,
    destinations with no path from the origin)."""
    reachable = reachable_from_origin(base)
    unreachable = sorted(set(base.destinations) - reachable)
    targets = sorted(set(base.destinations) & reachable)
    total_nodes = 0
    for size in range(len(targets), 0, -1):
        wins = []
        for group in combinations(targets, size):
            problem = VisitAll(base, group)
            goal = strategy(problem)
            total_nodes += problem.nodes_created
            if goal is not None:
                wins.append((goal.cost, goal, group))
        if wins:
            _cost, goal, group = min(wins, key=lambda w: w[0])
            return goal, total_nodes, set(group), unreachable
    return None, total_nodes, set(), unreachable


def main(argv):
    if len(argv) != 3 or argv[2].upper() not in STRATEGIES:
        print("Usage: python visit_all.py <filename> <method>", file=sys.stderr)
        print("Methods: " + ", ".join(STRATEGIES), file=sys.stderr)
        return 1
    method = argv[2].upper()
    try:
        base = parse_problem(argv[1])
    except (FileNotFoundError, ProblemFormatError) as err:
        print(f"Cannot read '{argv[1]}': {err}", file=sys.stderr)
        return 1

    try:
        goal, nodes, visited, unreachable = solve(base, STRATEGIES[method])
    except NodeLimit:
        print(f"{argv[1]} VISITALL-{method}")
        print(f"Stopped after {LIMIT} nodes without reaching a goal")
        return 0
    
    print(format_result(argv[1], "VISITALL-" + method, goal, nodes))
    if goal:
        print(f"Total cost: {goal.cost}, moves: {goal.depth}")
        if unreachable:
            print(f"Skipped, no path from the origin: {unreachable}")
        clash = sorted(set(base.destinations) - visited - set(unreachable))
        if clash:
            print(f"Skipped, cannot be visited in the same walk as the others: {clash}")
    elif unreachable:
        print(f"Skipped, no path from the origin: {unreachable}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))