"""
results.py - runs search methods on every test file and prints a results table.

Usage (from the repo folder, next to search.py):
    python results.py                 -> GBFS and AS on every tests\test*.txt
    python results.py GBFS AS BFS     -> choose which methods to run

It imports search.py, so it does NOT change the required program output.
It also writes results.csv (open it in Excel for the report tables).

Columns: path cost, nodes created, and the true cheapest cost (found with
Dijkstra) so you can see whether a method returned the optimal path.
"""
import csv
import glob
import heapq
import os
import re
import sys

import search


def cheapest_cost(problem):
    """True lowest path cost origin -> nearest destination (Dijkstra).
    Only used to check optimality; not one of the assignment methods."""
    best = {problem.origin: 0}
    heap = [(0, problem.origin)]
    while heap:
        cost, state = heapq.heappop(heap)
        if state in problem.destinations:
            return cost
        if cost > best.get(state, float("inf")):
            continue
        for nxt, step in problem.edges.get(state, []):
            new = cost + step
            if new < best.get(nxt, float("inf")):
                best[nxt] = new
                heapq.heappush(heap, (new, nxt))
    return None


def test_number(path):
    m = re.search(r"(\d+)", os.path.basename(path))
    return int(m.group(1)) if m else 0


def main():
    methods = [m.upper() for m in sys.argv[1:]] or ["GBFS", "AS"]
    files = sorted(glob.glob(os.path.join("tests", "test*.txt")), key=test_number)
    if not files:
        print("No test files found in tests\\ (run this from the repo folder).")
        return

    rows = []
    for f in files:
        name = os.path.splitext(os.path.basename(f))[0]
        for method in methods:
            try:
                problem = search.parse_problem(f)          # fresh problem = fresh node count
                goal = search.STRATEGIES[method](problem)
                best = cheapest_cost(problem)
            except NotImplementedError:
                rows.append([name, method, "-", "-", "-", "-", "not implemented"])
                continue
            except Exception as err:                       # bad file etc.
                rows.append([name, method, "-", "-", "-", "-", f"error: {err}"])
                continue
            if goal is None:
                rows.append([name, method, "none", "-", problem.nodes_created,
                             best if best is not None else "-", "no goal reachable"])
                continue
            optimal = "yes" if best is not None and abs(goal.cost - best) < 1e-9 else "NO"
            rows.append([name, method, goal.state, round(goal.cost, 2),
                         problem.nodes_created, best,
                         "path " + search.format_path(goal.path()) + f" | optimal: {optimal}"])

    header = ["test", "method", "goal", "path_cost", "nodes", "cheapest", "notes"]
    widths = [max(len(str(r[i])) for r in rows + [header]) for i in range(6)]
    line = lambda r: "  ".join(str(r[i]).ljust(widths[i]) for i in range(6)) + "  " + str(r[6])
    print(line(header))
    for r in rows:
        print(line(r))

    with open("results.csv", "w", newline="", encoding="utf-8") as out:
        w = csv.writer(out)
        w.writerow(header)
        w.writerows(rows)
    print("\nSaved results.csv")


if __name__ == "__main__":
    main()
