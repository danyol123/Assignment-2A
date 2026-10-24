# Test maps for COS30019 A2A (search.py)

Run any of them with:  `python search.py tests\testN.txt <METHOD>`
(Test files are kept as pure problem files, so the notes live here, not inside them.)

"Reference answer" = lowest-cost path from an independent Dijkstra check, plus the fewest-hops path
(what BFS should return). Use these to sanity-check each strategy.

| File | What it tests | Reference answer |
|------|---------------|------------------|
| test0.txt | General example: one-way edges, 2 destinations (6 & 7) | Cheapest: goal 7, path 1 4 7, cost 8. |
| test1.txt | Origin is also a destination (zero moves) | Goal 1, path "1", cost 0 |
| test2.txt | Straight one-way chain, only one possible path; all methods must agree | Goal 5, path 1 2 3 4 5, cost 4 |
| test3.txt | **No solution**: destinations are in a disconnected part of the map. Contains two-way edges (1<->2), so a tree search with no cycle check will loop forever. Every method must terminate and print `No goal is reachable; N` | No goal reachable |
| test4.txt | One-way edges force a detour: the direct route 1->2->3 is blocked because edge 3->2 only goes the other way | Goal 3, path 1 2 4 5 3, cost 10 |
| test5.txt | Several destinations where the fewest-hops goal is NOT the cheapest goal | Cheapest: goal 5, path 1 4 6 5, cost 9. BFS: goal 3, path 1 2 3 (cost 10) |
| test6.txt | Tie-breaking rules (NOTE 2): two equal-cost routes to goal 4 (via 2 or via 3), and symmetric heuristics, so the smaller node number must be expanded first | Goal 4, path 1 2 4, cost 6 |
| test7.txt | Cycles: ring of two-way edges, two equal-cost routes to goal 4 (cost 7); DFS can loop without a cycle check | Tie at cost 7: 1 2 3 4 (ascending-order rule) or 1 5 4 |
| test8.txt | Fewest moves vs lowest cost: one direct edge costing 20 versus a 5-move path costing 10. Separates BFS from A* | Cheapest: 1 3 4 5 6 2, cost 10. BFS: 1 2 (cost 20) |
| test9.txt | Greedy trap: GBFS follows the straight line to the goal and ends up on the expensive route; A* should avoid it | A*/optimal: 1 4 5 6, cost 12. GBFS typically: 1 2 3 6, cost 26 |
| test10.txt | Dead-end branch: DFS (smaller node first) goes into 2->3->4, which dead-ends, and must backtrack | Goal 7, path 1 5 6 7, cost 8 |
| test11.txt | 5x5 grid (25 nodes), origin in the centre (13), four equidistant corner destinations (1; 5; 21; 25). Larger tree plus 4-way ties | Goal 1, path 13 8 3 2 1 or 13 8 7 2 1, cost 4 (all corners cost 4; smallest number first) |
| test12.txt | Non-consecutive node IDs (1, 2, 10, 20) and numeric (not text) ordering: 2 must come before 10 | Goal 20, path 1 2 20, cost 6 |
| test13.txt | Heuristic that overestimates: edge 3->4 is cheaper than the straight-line distance, so A* with plain Euclidean h can return a non-optimal path. Good material for the Insights section | Optimal: 1 3 4, cost 6. A* with Euclidean h likely gives 1 2 4, cost 8 |
| test14.txt | Messy file formatting: Windows CRLF line endings, blank lines, tabs, extra spaces inside brackets and around `;` | Goal 3, path 1 3, cost 5 |

## Things worth knowing
- Tree-based search has no explored set. On any map with two-way edges, strategies need some form of cycle handling
  (e.g. `node.on_path(state)` in search.py) or they will not terminate on test3. Decide per method and document it in the report.
- Reference answers for GBFS/DFS/CUS1 are expectations, not the "optimal" path: those methods do not guarantee lowest cost.
- The brief asks for at least 15 test cases; this folder has exactly 15 (test0 to test14).