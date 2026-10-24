COS30019 Assignment 2A - Tree Based Search (Route Finding) - Team Swim & Burn

REQUIREMENTS
- Windows 11, Command Prompt (cmd)
- Python 3 (tested with 3.13.5). Only the standard library is used.

FILES (keep them in the same folder)
- search.py         the six search methods and the command-line program
- results_table.py  runs the methods on every test map and saves results tables
- visit_all.py      research extension: visit ALL destinations by the shortest path
- tests\            test0.txt to test14.txt, plus tests\README.txt (what each map tests)

HOW TO RUN
Open Command Prompt and go to the folder that holds the files above:

    cd C:\path\to\your\folder

1) Run one method on one map:

    python search.py <filename> <method>

   Example:  python search.py tests\test0.txt BFS

   <method> is DFS, BFS, GBFS, AS, CUS1 or CUS2 (not case-sensitive).
   Output when a destination is reached (3 lines):
       <filename> <method>
       <goal> <number_of_nodes>
       <path>
   Output when no destination can be reached (2 lines):
       <filename> <method>
       No goal is reachable; <number_of_nodes>

2) Run one method on all 15 maps and save a table:

    python results_table.py tests <method>

   Saves <METHOD>_results.txt (columns: Test, Best cost, Path, Moves, Cost, Nodes).

3) Run all six methods on all 15 maps:

    python results_table.py tests ALL

   Saves one <METHOD>_results.txt per method and all_results.txt (one combined table).
   "Best cost" is the lowest possible cost found independently with Dijkstra's algorithm.

4) Research extension - visit every destination with the lowest total cost:

    python visit_all.py <filename> <method>

   Example:  python visit_all.py tests\test5.txt AS

   Prints the usual three lines (method name shown as VISITALL-<METHOD>), then the total
   cost and number of moves. Destinations with no path from the origin, or that cannot be
   visited in the same walk as the others, are listed as skipped.
   A search stops after 2,000,000 nodes and prints
   "Stopped after 2000000 nodes without reaching a goal" (this happens for GBFS on test11).
   AS, CUS1 and CUS2 give the lowest total cost; DFS, BFS and GBFS only give a valid walk.

NOTES
- Run every command from the folder that holds search.py, because the programs find
  search.py and the test files through relative paths.
- Ties: the smaller node number is expanded first, then the node created earlier.
- Cycles are avoided along each branch only (the search is tree-based, no shared explored set).
- number_of_nodes counts every node created, including the root. CUS2 (IDA*) counts nodes
  again in every round.
- The full explanation of the methods, tests and results is in the report.