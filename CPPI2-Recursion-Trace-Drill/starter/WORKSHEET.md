# Recursion Trace Drill

This optional worksheet extends the saved Recursive Maze Search project. Keep
the same maze source and saved attempt. Predict three recursive searches before
running them, then compare observations and explain one corrected misconception.
The worksheet is a notes resource; its optional main.cpp only prints these notes.
It does not implement another maze application or grade an explanation.

## Preparation and trace rules

Review the complete CPPI2 stack-frame and backtracking lessons and the maze brief.
Save the current source and download its ZIP from the site IDE, then extract it.
Record the source role, revision or ZIP filename, compiler version and platform.
Complete the maze's visit function first. The untouched learner reports
`Error: UNFINISHED: implement recursive search.` with status 3. That outcome is
unfinished work, not evidence that an exit cannot be reached.

The supplied parser accepts a row/column header followed by exactly that many
grid lines. Coordinates are zero-based. S is the start, E is the exit, . is open,
and # is a wall. The grid is at most 20 by 20 and input is at most 16384 bytes.
The maze brief gives the complete input and rejection contract. All three cases
below are valid and can be copied exactly to separate text files.

Search tries neighbors in the fixed order up, right, down, left. Each visit frame
has its own cell value and next neighbor. The constant grid is borrowed; visited
marks, the candidate path and trace are shared within one search. Out-of-bounds,
wall and visited calls return false before entering a cell. Reaching E returns
true. An unsuccessful branch removes its cell from the candidate path and
records Backtrack; its visited mark stays set.

`--trace` records Enter only for a first visit to a passable cell and Backtrack
only when abandoning that cell. Rejected recursive calls still happen but have
no event. A successful frame returns normally without a Backtrack event. The
final saved path is a vector of cells, not a live stack of function frames.
Depth-first search returns the first path in the stated order; it need not be
shortest. Each separate solve starts with fresh search state.

## Predict before running

For each case, draw the grid with coordinates. Start a stack drawing at S and
write the neighbor order beside it. Trace calls and returns until the search
finishes. Include at least one rejected neighbor in the stack drawing even
though it has no printed event. Keep the predicted transcript separate from
the observed transcript; preserve the original prediction after a correction.

Record this table separately for each case and add rows as needed:

| Step | Active cell and next neighbor | Call or return | Visited marks | Candidate path | Printed event |
| --- | --- | --- | --- | --- | --- |
| 1 | [record] | [record] | [record] | [record] | [record] |

- Predicted full Enter/Backtrack sequence: [record]
- Predicted final Path line and coordinates, or No path: [record]
- Reason the search terminates: [record]
- Frame that resumes after a false child return: [record]
- Difference between the saved path and returned function frames: [record]

## Case A: Adjacent cells

Save as case-a.txt:

```text
1 2
SE
```

Track the boundary call made before moving right. Which calls print no event?
Explain how a true result passes back through its parent.

## Case B: Branch choices

Save as case-b.txt:

```text
3 4
S..#
.###
...E
```

Track where an attempted route ends and which older frame resumes. Compare
visited marks with the candidate path after that return. Keep the grid unchanged.

## Case C: A loop and a separated exit

Save as case-c.txt:

```text
4 4
S..#
.#.#
...#
###E
```

Track an attempted revisit. Explain which base case stops it and why removing a
path entry does not remove its visited mark. Predict the final candidate path.

## Run the saved maze and record evidence

Inside the extracted, completed six-file maze pack:

```sh
c++ --version
make maze-search maze-search-debug
./maze-search --trace < case-a.txt
./maze-search --trace < case-b.txt
./maze-search --trace < case-c.txt
ASAN_OPTIONS=detect_leaks=0 ./maze-search-debug --trace < case-b.txt
```

Record each command's actual stdout, stderr and exit status. A complete valid
search returns status 0 for either outcome. The debug build checks address and
undefined-behavior errors; disabling leak detection for platform compatibility
does not prove leak freedom. A compiler error must be resolved before comparing
runtime output. The program reads input and does not modify the case files.

- Source role, revision or ZIP and compiler/platform: [record]
- Exact command and actual stdout, stderr and exit status for A: [record]
- Exact command and actual stdout, stderr and exit status for B: [record]
- Exact command and actual stdout, stderr and exit status for C: [record]
- Debug observation and status, or tool availability limitation: [record]
- Earliest difference from a prediction and its source location: [record]
- Corrected explanation connecting that difference to a call or return: [record]

If output differs, locate the first event mismatch before changing code. Check
neighbor order, base-case order, visited marks and path removal. Save the attempted
explanation before consulting the separate staff worked example. An instructor
can pause at each prediction, execution and explanation using these same records.

## Extend and review

Change one wall in case B and predict the effect before running again. Draw a
second grid with two possible routes and explain how neighbor order can affect
the returned path. Distinguish a reachability result from a shortest-path claim.
Run A again after C and explain why an earlier search must not retain visited
marks. Keep both custom inputs and predictions with the saved source.

Submit the three predictions, stack drawings, actual transcripts with statuses,
one corrected misconception, two custom cases and the saved source identity.
The staff example describes one verified source; it does not certify another
saved attempt or replace its actual output.

Optionally compile the preserved worksheet printer separately with
`c++ -std=c++17 -Wall -Wextra -Wpedantic -Werror main.cpp -o trace-notes`
and run `./trace-notes > notes.md`. Edit notes.md separately. Native compilation
and execution of the maze use C++20, not this C++17 convenience printer.
