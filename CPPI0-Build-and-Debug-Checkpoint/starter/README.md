# Build and Debug Checkpoint

This required checkpoint establishes a repeatable C++20 build and debug workflow
before the larger command and persistence projects. The program records at most
20 scores, each from 0 through 100, and reports their total. It has a class in one
module, parsing and calculation helpers in another, and a command-line entry
point. The learner pack has one deliberate logic bug. The reference demonstrates
the corrected calculation after the attempted fix and evidence have been saved.

## Prerequisites and source map

The starting skills are functions, loops, vectors, classes, const accessors,
header declarations, and compiling a C++ program. No GUI, database, network,
external library, or manual resource owner is needed.

- `main.cpp`: command interpretation, demonstration, and seven actual checks.
- `score_ledger.h` / `score_ledger.cpp`: a class that stores validated scores.
- `score_tools.h` / `score_tools.cpp`: decimal parsing and traced calculation.
- `Makefile`: release-style and debug builds with header dependencies.

Each `starter/` and `solution/` folder is independently buildable and includes
the listed filenames and a copy of this brief. Complete the learner pack;
the reference is for comparison after recording the attempted explanation.

## Build and run

With a C++20 compiler and Make, run these commands inside either pack:

```sh
make checkpoint checkpoint-debug
./checkpoint
./checkpoint --check
./checkpoint-debug --trace
./checkpoint --scores 85
./checkpoint --scores
```

The direct compiler equivalent, including every implementation file, is:

```sh
c++ -std=c++20 -Wall -Wextra -Wpedantic -Werror -g -O0 main.cpp score_ledger.cpp score_tools.cpp -o checkpoint-debug
```

Compiling only `main.cpp` is incomplete because the other modules supply the
class and helper definitions. The `.h` files are included declarations, not
additional implementation files passed to the compiler. Rebuild after an edit.

From the repository root, the CMake 3.20+ alternative is:

```sh
cmake -S . -B build -DCMAKE_BUILD_TYPE=Debug
cmake --build build --config Debug --target build_debug_starter build_debug_solution
ctest --test-dir build -C Debug -R build_debug_ --output-on-failure
```

The targets are `build/build_debug_starter` and `build/build_debug_solution` for
single-configuration generators. Multi-configuration generators place the
executables under `build/Debug/` and use the platform's executable suffix. These
two targets use C++20; unrelated repository targets retain their own settings.
CTest expects the untouched learner's deliberate failed check. That expectation
proves reproduction and does not declare the learner's repair complete. After a
fix, `--check` must return 0 in the saved learner pack.

For a site IDE workspace, confirm the course import, inspect all five `.cpp`/`.h`
files, save the attempt, and export the ZIP. C++ execution uses a local native
compiler after extraction. It is not a Python or JavaScript run. The extracted
source can be built with the direct compiler command above even if build-only
files are omitted by a download tool.

## Observable contract

The default demonstration uses `40 60 80`. Its correct output is:

```text
Scores: 40 60 80
Total: 180
```

`--scores` supplies an explicit list. An empty list has total 0; `85` alone has
total 85; `0 60` and `60 0` both have total 60; twenty values of 100 total 2000.
The input order is preserved. `--trace` precedes `--scores` when combined and
prints one index, score, and running total for each value actually visited.
Without an explicit list, `--trace` uses the default demonstration.

Tokens accept ASCII decimal digits only. Leading zeros are permitted. Reject
negative or plus signs, empty tokens, surrounding spaces, decimal points,
trailing text, values over 100, a 21st score, and unknown options. Rejection
reports an error without printing a partial score list or total and returns 2.
The class rejects invalid additions before changing its existing scores.

`--check` compares seven observed totals with known results. A correct program
prints seven `PASS` lines and returns 0; a mismatch prints `FAIL` and returns 1.
Other runtime or output failures return 1. `--help` prints the supported forms.
The total is an `int`: validated capacity and ranges bound it to 0 through 2000.
The calculation helper's precondition is the same validated score domain.

## Attempt, trace, and debug

1. Save a baseline copy and the exact compiler command. Predict the totals of
   the empty, single-score, default, and zero-prefix cases before running them.
2. Run `--check`. Record one failure and one case that passes despite the bug.
   A passing example alone cannot prove the calculation is correct.
3. Run the failing example with `--trace`. Compare the visited indices and
   running totals with the prediction. Identify the module responsible.
4. Explain a proposed correction, then make one focused code change. Rebuild
   with warnings enabled and repeat the original failing and passing cases.
5. Add two custom score sequences with hand-calculated totals and repeat the
   seven checks. Test at least one rejected token and the capacity boundary.

Trace output is sufficient evidence; a debugger is an alternative. For GDB:

```sh
gdb --args ./checkpoint-debug --scores 85
```

At the debugger prompt, use `break sumScores`, `run`, `next`, and `print total`.
For LLDB, use `lldb -- ./checkpoint-debug --scores 85`, then
`breakpoint set --name sumScores`, `run`, `next`, and `frame variable`.
Capture the relevant observation before and after the edit. Debug information
comes from `-g`; `-O0` keeps stepping close to the source. If a tool is unavailable,
use the documented trace path rather than inventing an observation.

## Completion and instructor checkpoints

Completion requires the saved learner source, a warning-clean C++20 build,
the reproduced failure, a reasoned correction, seven passing checks, two custom
cases, one rejected-input result, and a short evidence note containing the exact
commands, expected and actual results, changed file, and why the fix works.
Reopen or rebuild the saved files to confirm the evidence belongs to that attempt.

A walkthrough can pause after the file map, predictions, first failing trace,
proposed edit, and regression checks. Ask for a prediction and explanation at each
pause before consulting the reference. The optional Warnings and Debugger Evidence
Notebook develops this same evidence; it does not require a second application.

## Extensions

Keep the checkpoint small. Optional extensions include another hand-calculated
case, comparing Make and CMake build commands, or recording debugger evidence
in addition to a trace. Saving tasks, importing rows, scanners, and command
architectures belong to later modules.

## Learner status

The supplied program compiles cleanly. Its wrong total is intentional, and four
of the seven checks initially fail. Record the failure before changing code.
Keep the checks and public API intact; repair the calculation rather than
changing expected totals or suppressing failed checks.
