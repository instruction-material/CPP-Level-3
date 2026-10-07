# Recursion Trace Drill: Worked Example

Staff comparison after a learner prediction and recorded attempt. Continue the
saved Recursive Maze Search source; this is a worked worksheet, not another
application or an automatic grade. The learner worksheet supplies the complete
preparation, input cases, records, native commands and review sequence.

These transcripts are checked against the unchanged six-file maze reference
introduced at source revision 3adb873179bd149b1f6ef9fddfec8557a6a71eb4. The
verify-recursion-trace.py gate compares all three complete outputs with an
independent iterative stack model, in ordinary and ASan/UBSan builds. The gate
also checks a completed learner fixture and the untouched learner's status 3.
This evidence describes those sources, not another saved learner attempt.

The command for each copied input is ./maze-search --trace < case-X.txt.
The completed reference and completed learner return status 0 with empty stderr
for all three inputs. The input files remain unchanged. Boundary, wall and
visited calls produce no trace event, although their short-lived frames exist.

## Case A

Input:

```text
1 2
SE
```

Actual trace and final result:

```text
Enter 0 0
Enter 0 1
Path 2
0 0
0 1
```

## Case B

Input:

```text
3 4
S..#
.###
...E
```

Actual trace and final result:

```text
Enter 0 0
Enter 0 1
Enter 0 2
Backtrack 0 2
Backtrack 0 1
Enter 1 0
Enter 2 0
Enter 2 1
Enter 2 2
Enter 2 3
Path 6
0 0
1 0
2 0
2 1
2 2
2 3
```

## Case C

Input:

```text
4 4
S..#
.#.#
...#
###E
```

Actual trace and final result:

```text
Enter 0 0
Enter 0 1
Enter 0 2
Enter 1 2
Enter 2 2
Enter 2 1
Enter 2 0
Enter 1 0
Backtrack 1 0
Backtrack 2 0
Backtrack 2 1
Backtrack 2 2
Backtrack 1 2
Backtrack 0 2
Backtrack 0 1
Backtrack 0 0
No path
```

## Interpret the frames and shared state

In A, the upward neighbor is out of bounds and returns false without an event.
The right child enters E and returns true. Both successful visit frames return
normally; their cells remain in the result vector. No Backtrack event is needed.

In B, cells (0,2) and (0,1) fail in that order and are removed from the candidate
path. Their visited marks remain. The (0,0) frame resumes after its right child
returns false, then tries down. Eight cells are entered, two are abandoned and
the final path contains six cells. The grid is never modified.

In C, the accessible region contains a cycle but the exit is separated by walls.
Eight distinct cells are entered once. Revisiting (0,0) from (1,0) is rejected by
the visited base case. All eight failed frames abandon their path entries in
reverse order, leaving an empty candidate path. Visited marks still describe the
explored region. No path is a completed reachability result with status 0.

An Enter/Backtrack sequence is an observable path trace, not a printout of every
function call. Successful returns do not print Backtrack, but the actual frames
still end. Shared result data can outlive these frames because the wrapper owns
it; it does not refer to destroyed frame-local objects.

Keeping visited marks prevents repeated work in a cyclic region. Removing failed
path entries restores the current route. Confusing these two roles can retain a
dead-end path or repeatedly explore a cycle. Each solve creates fresh search
state. A run of A after C must therefore reproduce A's output above.

The deterministic DFS path need not be shortest. A different neighbor order can
change a successful path without changing reachability. Custom-case explanations
require actual observations from the submitted source and independently checked
routes; this example does not pre-fill their answers.

## Completion and native workflow

Review the original prediction, the first mismatch, its call/return explanation,
two custom cases, compiler/platform and exact source or exported ZIP identity.
Compare the completed learner's ordinary and debug outputs. An untouched starter
has no successful or unreachable result: it emits the explicit unfinished error
on stderr and returns 3. Preserve that distinction in a teaching walkthrough.

The reference worksheet's main.cpp prints this document only. Compile it with
`c++ -std=c++17 -Wall -Wextra -Wpedantic -Werror main.cpp -o trace-notes`
and redirect stdout to a separate notes file if useful. Build the actual maze
with its C++20 Makefile and use the three inputs from the learner worksheet.
From the source root, run python3 verify-recursion-trace.py. Existing CMake
targets trace_drill_starter and trace_drill_solution remain worksheet printers.
