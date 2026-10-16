@echo off
rem Runs search.py on tests\test0.txt ... tests\test14.txt
rem Usage:  run_tests.bat DFS      (or BFS, GBFS, AS, CUS1, CUS2)
rem         run_tests.bat ALL      (every method, one after another)
rem Tip:    run_tests.bat DFS > dfs_results.txt   saves the output to a file

if "%~1"=="" goto usage
if /I "%~1"=="ALL" goto all
call :run %~1
goto end

:all
for %%M in (DFS BFS GBFS AS CUS1 CUS2) do call :run %%M
goto end

:run
for /L %%i in (0,1,14) do (
  python search.py tests\test%%i.txt %~1
  echo.
)
exit /b 0

:usage
echo Usage: run_tests.bat METHOD   (DFS, BFS, GBFS, AS, CUS1, CUS2 or ALL)

:end