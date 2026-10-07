# Recursive Maze Search

Implement a recursive depth-first search through a small grid. This required
CPPI2 project makes stack frames, base cases, visited state and backtracking
observable. Read the contract and predict a trace before writing the recursive
function. Independent study and an instructor walkthrough use the same steps.

## Preparation and files

Use C++20 and the standard library. Review vectors, references, function returns
and the CPPI1 multi-file build. The six-file pack contains `main.cpp` (commands
and output), `maze.h` (types and public interfaces), `maze.cpp` (complete bounded
input validation), `maze_search.cpp` (search), `Makefile` and this brief. Keep
these names and interfaces. The learner implements only `visit` in
`maze_search.cpp`; input validation and a fresh search-state wrapper are supplied.

The untouched learner builds and accepts valid input, then reports
`Error: UNFINISHED: implement recursive search.` on standard error with exit
status 3. It must not claim that an unfinished search found no path. Record an
attempt before consulting the reference.

## Input and output

Run `maze-search` with input on standard input. Its first line contains the row
and column counts as two whole ASCII decimal numbers from 1 through 20. Leading
zeros are allowed. Spaces and tabs may separate the numbers or surround the
header; signs, extra tokens and partial numbers are rejected. Then supply exactly
the declared number of grid lines, each exactly the declared width. Grid bytes
are `S` (one start), `E` (one exit), `.` (open) and `#` (wall). Do not trim grid
lines. Accept LF or CRLF and an optional final newline. An additional blank line
is extra input and is rejected. The complete input is at most 16384 bytes.

Reject malformed dimensions, missing or extra lines, ragged rows, invalid
characters, duplicate/missing endpoints, oversized input and stream read errors.
Print `Error: message` to standard error and return status 2 without a search
result. `readMaze` preserves its earlier output object on failure and clears the
error on success. Input validation is supplied so the assignment can focus on
recursion. Files are never created or modified by this program.

For valid input, search uses four neighbors in this exact order: **up, right,
down, left**. Coordinates are zero-based. A successful search prints `Path N`
followed by one `row column` line per cell, including the start and exit. The
path has no repeated cell and moves one orthogonal step at a time. An unreachable
exit prints `No path`. Both valid outcomes return status 0. Depth-first search
finds the first path in this traversal order; it does not promise a shortest path.

`--trace` prints `Enter row column` when first entering a passable cell and
`Backtrack row column` when abandoning that cell, before the final result.
Rejected neighbors produce no event. Successful frames remain on the path and
do not print backtrack events. `--help` alone prints usage without reading input.
Unknown, repeated or extra arguments return status 2.

## What each call owns

Each `visit` frame owns its `cell` value and the next neighbor being tried.
The maze is borrowed as a constant reference. The visited grid, current path,
entered-cell record and trace are shared by reference within one search. The
wrapper creates all of that state afresh on every `solveMaze` call.

Use base cases before indexing: out of bounds, wall and already visited return
false. For a new open cell, mark it visited, append it to the path and entered
record, and record `Enter`. Reaching the exit returns true. Otherwise recurse
through the four neighbors in order. A true child returns true through each
parent without removing the successful path. If all children fail, record
`Backtrack`, remove this cell from the path and return false.

The visited set grows and remains marked even when the current path backtracks.
That prevents cycles and repeated exploration. The path is the current candidate
route, so it shrinks when a branch fails. These two structures answer different
questions. Unmarking visited cells is unnecessary for reachability and can cause
repeated work; a word-search assignment with path-specific constraints would
need a different contract. Do not alter the input grid to store visited marks.

At most 400 passable cells can be entered. Every successful recursive expansion
marks a previously unvisited cell; invalid neighbors stop immediately. This
finite progress argument explains termination. Time and stored search state are
O(rows × columns). This small bound also limits recursion depth. Large graphs
would require an explicit stack or a different resource policy.

## Prediction and implementation checkpoints

1. Draw a two-cell `SE` maze. Predict the enter events, path length and returns.
2. Trace a dead end. Identify which frame resumes when a child returns false and
   which path entry must be removed.
3. Draw a loop. Explain why a visited check must precede another recursive call.
4. Implement the base cases, then choosing a cell and the exit case. Test these
   before adding all four recursive calls.
5. Add failure backtracking. Keep visited marks while removing failed path cells.
6. Run an unreachable maze and confirm the final path is empty. Search the same
   object again, then a different maze, and confirm there is no retained state.
7. Explain why a returned path may be longer than a shortest path. Predict how
   changing neighbor order would change the returned route.

An instructor can pause after each prediction to inspect the stack drawing,
shared state and observed output. A walkthrough does not change the contract.

## Small example

```text
2 3
S#E
...
```

The completed program prints:

```text
Path 5
0 0
1 0
1 1
1 2
0 2
```

Predict the `--trace` events first, then compare. Add a wall at row 1, column 1
and predict the changed outcome. Construct another maze that makes the search
backtrack before finding its exit.

## Build and hand-in evidence

From either pack:

```sh
make
./maze-search --help
./maze-search --trace < maze.txt
make maze-search-debug
./maze-search-debug < maze.txt
```

Without Make, keep the header beside all three source files:

```sh
c++ -std=c++20 -Wall -Wextra -Wpedantic -Wconversion -Wsign-conversion -Werror main.cpp maze.cpp maze_search.cpp -o maze-search
```

`make clean` removes only the two executables and preserves input files. From
the source repository root, build `maze_search_starter` and
`maze_search_solution` with CMake and run `python3 verify-maze-search.py`.
The site IDE edits, saves and exports the pack; native compilation executes it.

Submit the six files, an initial prediction, a corrected stack trace, and
predicted/observed cases for adjacent endpoints, walls, cycles, a dead end before
success, an unreachable exit, a one-row maze, the 20×20 bound, malformed input
and repeated searches. Explain visited state versus the current path and why
the algorithm terminates. A fixed pass counter is not evidence of search.
