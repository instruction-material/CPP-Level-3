# Worked Warnings and Debugger Evidence Notebook

This separate reference illustrates the same saved Build and Debug Checkpoint.
Attempt and save the learner worksheet before comparing it. The exact output
below is checked against the paired checkpoint source by `verify-notebook.py`.
Compiler versions and debugger screens must be recorded from the actual
environment. These example results do not grade a student's saved source.

## Build and starting state

Use the CPPI0 learner pack's `main.cpp`, `score_ledger.cpp`, `score_tools.cpp`
and two headers. Build with C++20, `-Wall -Wextra -Wpedantic -Werror -g -O0`.
The supplied source builds without compiler warnings. The build's success
does not imply that the totals are correct.

With `--scores 85`, the hand-calculated total is 85. The untouched learner
prints `Scores: 85` followed by `Total: 0` and returns 0. Its `--check`
reports three passing and four failing comparisons and returns 1.

With `--trace --scores 40 60 80`, the learner output is:

```text
Scores: 40 60 80
trace index=1 score=60 running=60
trace index=2 score=80 running=140
Total: 140
```

The trace does not visit the first value. In `score_tools.cpp`, the sum loop
starts at index 1. A debugger at `sumScores` can inspect the vector size and
step through that initial condition; the loop body is skipped for one score.
The debugger commands in the worksheet are suggested observation steps,
not a fabricated debugger session or a claimed warning.

## Explanation and corrected behavior

Starting at index 0 includes every validated score. No parser, ledger or
public command change is needed. After rebuilding the saved learner with
that correction, `--scores 85` reports `Total: 85`. The corrected trace is:

```text
Scores: 40 60 80
trace index=0 score=40 running=40
trace index=1 score=60 running=100
trace index=2 score=80 running=180
Total: 180
```

The corrected reference's seven comparisons all pass and `--check` returns
0. Custom checks can include explicit `--scores` with no values (total 0)
and `--scores 60 0` (total 60). `--scores 50 -1` returns 2, writes an error
and prints no partial score output. These results test the input contract
as well as the changed calculation.

## Review boundary

Keep the recorded before/after output, source change, build command, checks
and two custom cases with the final saved checkpoint. Explain why a clean
compiler build did not catch this logic bug. A successful run of this
notebook's convenience generator only prints these notes; it does not check
or certify a student's work. Use the student's actual saved checkpoint
commands and outputs for review.

The original `main.cpp` in this reference pack prints this worked Markdown
example. The Markdown is the primary resource. The generator builds with
`c++ -std=c++17 -Wall -Wextra -Wpedantic -Werror main.cpp -o notebook`.
