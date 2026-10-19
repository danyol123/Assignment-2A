"""
COS30019 - Assignment 2A - Research: visit ALL destinations by the shortest path.

Usage (Windows CMD), from the folder that contains search.py:
    python research_all.py <filename>

Uses only CUS1 (Uniform-Cost Search). The search state is extended from
"map node" to "(map node, set of destinations already visited)", and the goal
is reached when every destination has been visited.
"""

import sys

from search import Problem, ProblemFormatError, cus1, format_result, parse_problem


class VisitAll(Problem):
    """Route-finding problem whose goal is to visit every destination."""

    def __init__(self, base):
        super().__init__(base.nodes, base.edges, base.origin, base.destinations)
        self.all = frozenset(base.destinations)
        self.seen = {}

    def root(self):
        node = super().root()
        self.seen[node.order] = frozenset([node.state]) & self.all
        return node

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
        while node is not None:
            if node.state == state and self.seen[node.order] == visited:
                return True
            node = node.parent
        return False

    def is_goal(self, node):
        return self.seen[node.order] == self.all


def main(argv):
    if len(argv) != 2:
        print("Usage: python research_all.py <filename>", file=sys.stderr)
        return 1
    try:
        problem = VisitAll(parse_problem(argv[1]))
    except (FileNotFoundError, ProblemFormatError) as err:
        print(f"Cannot read '{argv[1]}': {err}", file=sys.stderr)
        return 1
    goal = cus1(problem)
    print(format_result(argv[1], "VISITALL-CUS1", goal, problem.nodes_created))
    if goal:
        print(f"Total cost: {goal.cost}, moves: {goal.depth}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))