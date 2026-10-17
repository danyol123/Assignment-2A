"""
Builds a results table for any search method over every test file in a folder.

Usage (run from the folder that contains search.py):
    python results_table.py [folder] [method]

    folder : folder with test0.txt, test1.txt, ...   (default: tests)
    method : DFS, BFS, GBFS, AS, CUS1, CUS2 or ALL    (default: ALL)

Examples:
    python results_table.py tests CUS2
    python results_table.py tests ALL

Output (saved in the current folder, and printed):
    <METHOD>_results.txt   one table per method (e.g. BFS_results.txt)
    all_results.txt        one combined table (only when 2+ methods ran)
"""
import glob
import heapq
import math
import os
import re
import sys

from search import parse_problem, STRATEGIES, METHODS


def best_cost(problem):
    """Lowest possible total cost from the origin to any destination
    (Dijkstra). Used only for the 'Best cost' column."""
    goals = set(problem.destinations)
    dist = {problem.origin: 0}
    heap = [(0, problem.origin)]
    while heap:
        d, node = heapq.heappop(heap)
        if d > dist.get(node, math.inf):
            continue                       # outdated heap entry
        if node in goals:
            return d                       # first goal popped = cheapest
        for neighbour, step_cost in problem.edges.get(node, []):
            new_d = d + step_cost
            if new_d < dist.get(neighbour, math.inf):
                dist[neighbour] = new_d
                heapq.heappush(heap, (new_d, neighbour))
    return None                            # no destination reachable


def test_number(path):
    """Sort test0, test1, ..., test10 in numeric order (not 0, 1, 10, 2)."""
    return int(re.search(r"(\d+)", os.path.basename(path)).group(1))


def run_method(files, best_costs, method):
    """Run one method on every file. Returns a list of rows, or None if the
    method has not been implemented yet."""
    rows = []
    for file in files:
        name = os.path.splitext(os.path.basename(file))[0]
        problem = parse_problem(file)      # parse fresh: node counter starts at 0
        try:
            goal = STRATEGIES[method](problem)
        except NotImplementedError:
            return None                    # whole method is missing: skip it
        except Exception as err:           # one failing test must not stop the rest
            print(f"{method} failed on {name}: {err!r}", file=sys.stderr)
            rows.append([name, best_costs[file], f"ERROR: {err}", "-", "-", "-"])
            continue

        if goal is None:
            rows.append([name, "-", "no goal", "-", "-", problem.nodes_created])
        else:
            rows.append([name, best_costs[file], " ".join(map(str, goal.path())),
                         goal.depth, goal.cost, problem.nodes_created])
    return rows


def save_table(base_name, header, rows):
    """Print a table and save it as <base_name>.txt (columns aligned)."""
    table = [header] + [[str(x) for x in r] for r in rows]
    widths = [max(len(r[c]) for r in table) for c in range(len(header))]
    lines = [" | ".join(cell.ljust(widths[c]) for c, cell in enumerate(r)).rstrip()
             for r in table]
    text = "\n".join(lines)
    with open(base_name + ".txt", "w") as f:
        f.write(text + "\n")
    print(text)
    print(f"(saved {base_name}.txt)\n", file=sys.stderr)


def main():
    folder = sys.argv[1] if len(sys.argv) > 1 else "tests"
    choice = sys.argv[2].upper() if len(sys.argv) > 2 else "ALL"

    if choice == "ALL":
        methods = list(METHODS)
    elif choice in STRATEGIES:
        methods = [choice]
    else:
        print(f"Unknown method '{choice}'. Use one of: {', '.join(METHODS)} or ALL",
              file=sys.stderr)
        return 1

    files = sorted(glob.glob(os.path.join(folder, "test*.txt")), key=test_number)
    if not files:
        print(f"No test*.txt files found in '{folder}'", file=sys.stderr)
        return 1

    best_costs = {f: best_cost(parse_problem(f)) for f in files}
    header = ["Test", "Best cost", "Path", "Moves", "Cost", "Nodes"]
    done = {}                              # method -> rows

    for method in methods:
        rows = run_method(files, best_costs, method)
        if rows is None:
            print(f"[{method}] not implemented yet, skipped\n", file=sys.stderr)
            continue
        print(f"=== {method} ===")
        save_table(f"{method}_results", header, rows)
        done[method] = rows

    # Combined table, one "path" and one "cost / nodes" column per method
    if len(done) > 1:
        combined_header = ["Test", "Best cost"]
        for method in done:
            combined_header += [f"{method} path", f"{method} cost / nodes"]
        combined = []
        for i, file in enumerate(files):
            row = [done[next(iter(done))][i][0], done[next(iter(done))][i][1]]
            for method in done:
                _, _, path, _, cost, nodes = done[method][i]
                row += [path, f"{cost} / {nodes}"]
            combined.append(row)
        print("=== ALL METHODS ===")
        save_table("all_results", combined_header, combined)
    return 0


if __name__ == "__main__":
    sys.exit(main())