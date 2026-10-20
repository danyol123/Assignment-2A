How to run it

In Command Prompt, go to the folder that holds search.py, results_table.py, visit_all.py and tests\:

cd C:\path\to\your\folder

python search.py <filename> <method>
python results_table.py tests <method>
python results_table.py tests ALL
python visit_all.py <filename> <method>

<filename> is the test map file: tests/test0.txt, tests/test1.txt, etc..
<method> is one of: DFS, BFS, GBFS, AS, CUS1, CUS2

The search.py line runs one file with one method.
The first results_table.py line runs all 15 files for that method and saves it in a txt file.
The second results_table.py line runs all 15 files for that all methods and saves it in a txt file.
The visit_all.py line runs one file with one method to visit ALL destinations by the shortest path.
