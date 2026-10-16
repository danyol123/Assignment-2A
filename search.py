"""
COS30019 - Introduction to AI
Assignment 2, Part A - Tree Based Search (Route Finding Problem)

Usage (Windows CMD):
    python search.py <filename> <method>

    <method> is one of: DFS, BFS, GBFS, AS, CUS1, CUS2   (case-insensitive)

Output when a goal is reached:
    <filename> <method>
    <goal> <number_of_nodes>
    <path>

Output when no goal can be reached:
    <filename> <method>
    No goal is reachable; <number_of_nodes>

--------------------------------------------------------------------------
FILE LAYOUT (for the team)
--------------------------------------------------------------------------
  1. Data structures    : Node (search-tree node), Problem (the parsed map)
  2. File parsing       : parse_problem()
  3. Search strategies  : dfs / bfs / gbfs / astar / cus1 / cus2   <-- TEAM FILLS IN
  4. Output + CLI       : format_result(), main()

HOW TO IMPLEMENT A STRATEGY
--------------------------------------------------------------------------
Each strategy is a function:   strategy(problem) -> Node | None

  * Return the goal Node that was reached, or None if no goal is reachable.
  * ALWAYS create nodes with  problem.make_node(...)  (or problem.root())
    and NEVER call Node(...) directly. make_node() hands out the creation
    order number (node.order) and counts every node created, which is the
    "number_of_nodes" in the required output. The root counts as 1.
  * Use problem.expand(node) to get the children of a node. Children come
    back already sorted in ASCENDING node-number order (assignment NOTE 2).
  * problem.is_goal(node) tells you if a node is a destination.
  * problem.heuristic(node) is the straight-line (Euclidean) distance from
    the node to its NEAREST destination, for the informed methods.
  * Tie-breaking (assignment NOTE 2): when priorities are equal, expand the
    smaller node number first; if still equal, expand the node created
    earlier first (smaller node.order). Using  (priority, state, order)  as
    a heap key, or just node.sort_key(priority), gives you exactly that.
  * This is TREE-based search: there is no global "explored" set. Because
    many edges go both ways, a strategy such as DFS may loop forever unless
    you stop it re-visiting a state already on its own path. Use
    node.on_path(state) for that. Decide as a team whether each method
    needs it and document the decision in the report.
"""

import math
import re
import sys
from typing import Dict, List, Optional, Tuple

# Names accepted on the command line -> function name defined further below.
METHODS = ("DFS", "BFS", "GBFS", "AS", "CUS1", "CUS2")


# ==========================================================================
# 1. DATA STRUCTURES
# ==========================================================================

class Node:
    """One node of the SEARCH TREE (not to be confused with a map node).

    state  : the map node number this tree node sits on
    parent : parent Node in the search tree (None for the root)
    cost   : g(n), total path cost from the origin to this node
    depth  : number of moves from the origin
    order  : creation order (0 = first node ever created); used for ties
    """

    __slots__ = ("state", "parent", "cost", "depth", "order")

    def __init__(self, state: int, parent: Optional["Node"], cost: float, order: int):
        self.state = state
        self.parent = parent
        self.cost = cost
        self.depth = 0 if parent is None else parent.depth + 1
        self.order = order

    def path(self) -> List[int]:
        """Map-node numbers from the origin down to this node."""
        states, node = [], self
        while node is not None:
            states.append(node.state)
            node = node.parent
        states.reverse()
        return states

    def on_path(self, state: int) -> bool:
        """True if `state` already appears on the path origin -> this node
        (handy for avoiding cycles inside a single branch)."""
        node = self
        while node is not None:
            if node.state == state:
                return True
            node = node.parent
        return False

    def sort_key(self, priority: float) -> Tuple[float, int, int]:
        """Heap/sort key that applies the assignment tie-break rules:
        lowest priority first, then smaller node number, then created earlier."""
        return (priority, self.state, self.order)

    def __repr__(self) -> str:
        return f"Node(state={self.state}, g={self.cost}, depth={self.depth}, order={self.order})"


class Problem:
    """A parsed Route Finding problem plus helpers used by every strategy."""

    def __init__(
        self,
        nodes: Dict[int, Tuple[float, float]],
        edges: Dict[int, List[Tuple[int, float]]],
        origin: int,
        destinations: List[int],
    ):
        self.nodes = nodes                  # {node_id: (x, y)}
        self.edges = edges                  # {from_id: [(to_id, cost), ...]} sorted by to_id
        self.origin = origin
        self.destinations = destinations    # list of destination node ids
        self._dest_set = set(destinations)
        self.nodes_created = 0              # the "number_of_nodes" for the output

    # ---- node creation (keeps the counter + creation order consistent) ----
    def make_node(self, state: int, parent: Optional[Node], step_cost: float = 0) -> Node:
        """Create a search-tree node. Always use this instead of Node(...)."""
        cost = step_cost if parent is None else parent.cost + step_cost
        node = Node(state, parent, cost, self.nodes_created)
        self.nodes_created += 1
        return node

    def root(self) -> Node:
        """Create the root node (the origin)."""
        return self.make_node(self.origin, None, 0)

    # ---- expansion ----
    def expand(self, node: Node) -> List[Node]:
        """Create and return the children of `node`, in ascending node-number
        order. Every child returned counts as a created node."""
        children = []
        for neighbour, step_cost in self.edges.get(node.state, []):
            children.append(self.make_node(neighbour, node, step_cost))
        return children

    # ---- goal test + heuristic ----
    def is_goal(self, node: Node) -> bool:
        return node.state in self._dest_set

    def heuristic(self, node: Node) -> float:
        """Euclidean distance from this node to the NEAREST destination."""
        x, y = self.nodes[node.state]
        return min(
            math.hypot(x - self.nodes[d][0], y - self.nodes[d][1])
            for d in self.destinations
        )


# ==========================================================================
# 2. FILE PARSING
# ==========================================================================

class ProblemFormatError(Exception):
    """Raised when the problem file is malformed."""


_NUM = r"-?\d+(?:\.\d+)?"
_NODE_RE = re.compile(rf"^(\d+)\s*:\s*\(\s*({_NUM})\s*,\s*({_NUM})\s*\)$")
_EDGE_RE = re.compile(rf"^\(\s*(\d+)\s*,\s*(\d+)\s*\)\s*:\s*({_NUM})$")


def _number(text: str):
    """int if the text is a whole number, otherwise float."""
    value = float(text)
    return int(value) if value.is_integer() else value


def parse_problem(filename: str) -> Problem:
    """Read a problem file and return a Problem.

    Expected sections (keywords are case-insensitive, blank lines ignored):
        Nodes:        lines like   1: (4,1)
        Edges:        lines like   (2,1): 4       (from 2 to 1, cost 4)
        Origin:       a single node number
        Destinations: node numbers separated by semi-colons, e.g.  5; 4
    """
    with open(filename, "r", encoding="utf-8-sig") as f:
        lines = f.read().splitlines()

    nodes: Dict[int, Tuple[float, float]] = {}
    edge_list: List[Tuple[int, int, float]] = []
    origin: Optional[int] = None
    destinations: List[int] = []
    section: Optional[str] = None

    keywords = {"nodes:": "nodes", "edges:": "edges",
                "origin:": "origin", "destinations:": "destinations"}

    for line_no, raw in enumerate(lines, start=1):
        line = raw.strip()
        if not line:
            continue

        # A section keyword (the rest of the line, if any, is handled as content).
        lowered = line.lower()
        keyword = next((k for k in keywords if lowered.startswith(k)), None)
        if keyword:
            section = keywords[keyword]
            line = line[len(keyword):].strip()
            if not line:
                continue

        try:
            if section == "nodes":
                m = _NODE_RE.match(line)
                if not m:
                    raise ValueError
                nodes[int(m.group(1))] = (_number(m.group(2)), _number(m.group(3)))
            elif section == "edges":
                m = _EDGE_RE.match(line)
                if not m:
                    raise ValueError
                edge_list.append((int(m.group(1)), int(m.group(2)), _number(m.group(3))))
            elif section == "origin":
                origin = int(line)
            elif section == "destinations":
                destinations.extend(int(p) for p in line.split(";") if p.strip())
            else:
                raise ValueError
        except ValueError:
            raise ProblemFormatError(f"line {line_no}: cannot understand '{raw.strip()}'")

    # ---- validation ----
    if not nodes:
        raise ProblemFormatError("no nodes were found")
    if origin is None:
        raise ProblemFormatError("no origin was found")
    if not destinations:
        raise ProblemFormatError("no destinations were found")
    for n in [origin] + destinations:
        if n not in nodes:
            raise ProblemFormatError(f"node {n} is used but was never defined under Nodes:")

    edges: Dict[int, List[Tuple[int, float]]] = {n: [] for n in nodes}
    for a, b, cost in edge_list:
        if a not in nodes or b not in nodes:
            raise ProblemFormatError(f"edge ({a},{b}) uses an undefined node")
        edges[a].append((b, cost))
    for n in edges:
        edges[n].sort(key=lambda e: e[0])   # ascending order of destination node (NOTE 2)

    return Problem(nodes, edges, origin, destinations)


# ==========================================================================
# 3. SEARCH STRATEGIES  -- TO BE IMPLEMENTED BY THE TEAM
# ==========================================================================
# Each function takes a Problem and returns the goal Node reached, or None.
# See the "HOW TO IMPLEMENT A STRATEGY" notes at the top of this file.

def dfs(problem: Problem) -> Optional[Node]:
    """Depth-First Search (uninformed)."""
    raise NotImplementedError("DFS has not been implemented yet")


def bfs(problem: Problem) -> Optional[Node]:
    """Breadth-First Search (uninformed)."""
    raise NotImplementedError("BFS has not been implemented yet")


def gbfs(problem: Problem) -> Optional[Node]:
    """Greedy Best-First Search (informed): orders the frontier by h(n) only."""
    raise NotImplementedError("GBFS has not been implemented yet")


def astar(problem: Problem) -> Optional[Node]:
    """A* Search (informed): orders the frontier by f(n) = g(n) + h(n)."""
    raise NotImplementedError("AS has not been implemented yet")


def cus1(problem: Problem) -> Optional[Node]:
    """Custom strategy 1 (uninformed): an uninformed method to find a path to a goal."""
    raise NotImplementedError("CUS1 has not been implemented yet")


def cus2(problem: Problem) -> Optional[Node]:
    """Custom strategy 2 (informed): Depth-First Branch and Bound, fewest moves.

    g(n) = node.depth (number of moves), h(n) = 0 for a goal, otherwise 1
    (a non-goal needs at least one more move, so h is admissible).
    A branch is pruned when f = g + h >= the best number of moves found so far.
    """
    sys.setrecursionlimit(10000)
    best: Optional[Node] = None          # best goal Node that found so far

    def h(node: Node) -> int:
        return 0 if problem.is_goal(node) else 1

    def visit(node: Node) -> None:
        nonlocal best
        if problem.is_goal(node):
            if best is None or node.depth < best.depth:
                best = node              # strictly better; ties keep the earlier one
            return
        for child in problem.expand(node):           # ascending node order
            if node.on_path(child.state):            # avoid loops within a branch
                continue
            bound = best.depth if best is not None else math.inf
            if child.depth + h(child) >= bound:      # prune
                continue
            visit(child)

    visit(problem.root())
    return best


# Method name used on the command line -> strategy function.
STRATEGIES = {
    "DFS": dfs,
    "BFS": bfs,
    "GBFS": gbfs,
    "AS": astar,
    "CUS1": cus1,
    "CUS2": cus2,
}


# ==========================================================================
# 4. OUTPUT + COMMAND LINE
# ==========================================================================

def format_path(path: List[int]) -> str:
    """How the path is printed. Change here if the marker wants another style
    (e.g. ' -> ' or one move per line)."""
    return " ".join(str(n) for n in path)


def format_result(filename: str, method: str, goal: Optional[Node], nodes_created: int) -> str:
    """Build the required standard output text."""
    header = f"{filename} {method}"
    if goal is None:
        return f"{header}\nNo goal is reachable; {nodes_created}"
    return f"{header}\n{goal.state} {nodes_created}\n{format_path(goal.path())}"


def main(argv: List[str]) -> int:
    if len(argv) != 3:
        print("Usage: python search.py <filename> <method>", file=sys.stderr)
        print("Methods: " + ", ".join(METHODS), file=sys.stderr)
        return 1

    filename, method = argv[1], argv[2].upper()

    if method not in STRATEGIES:
        print(f"Unknown method '{argv[2]}'. Choose one of: {', '.join(METHODS)}", file=sys.stderr)
        return 1

    try:
        problem = parse_problem(filename)
    except FileNotFoundError:
        print(f"Cannot open file '{filename}'", file=sys.stderr)
        return 1
    except ProblemFormatError as err:
        print(f"Problem file error in '{filename}': {err}", file=sys.stderr)
        return 1

    try:
        goal = STRATEGIES[method](problem)
    except NotImplementedError as err:
        print(f"{err}", file=sys.stderr)
        return 2

    print(format_result(filename, method, goal, problem.nodes_created))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))