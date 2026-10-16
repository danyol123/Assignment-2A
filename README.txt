How to run it

In Command Prompt, go to the folder that holds search.py, run_tests.bat and tests\:

cd C:\path\to\your\folder
python search.py tests\test0.txt DFS
python search.py tests\test0.txt BFS
run_tests.bat DFS
run_tests.bat BFS
run_tests.bat DFS > dfs_results.txt

The first two lines run one file with one method.
run_tests.bat DFS and run_tests.bat BFS run all 15 files for that method.
The last line saves the output to a text file you can paste from.
run_tests.bat ALL runs every method, and the ones nobody has finished yet just print “not implemented”.