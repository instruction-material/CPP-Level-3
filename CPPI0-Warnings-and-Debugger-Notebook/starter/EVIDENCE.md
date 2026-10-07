# Warnings and Debugger Evidence Notebook

This optional worksheet records evidence from the saved Build and Debug
Checkpoint. Continue that same project; no second application is required.
Preserve the original learner attempt before a correction.
The checkpoint brief supplies the input rules, expected totals, source map,
build commands and completion criteria.

## Preparation

1. Save the current checkpoint in the site IDE and download its ZIP, or use
   the existing local learner pack. Extract the ZIP before compiling C++.
2. Copy this worksheet to a notes file. Keep it alongside the checkpoint
   source, separate from the source file being edited.
3. Record the compiler version, platform, source role and starting revision
   or ZIP filename. Include the names of all five `.cpp`/`.h` files.

## Build evidence

Run inside the extracted checkpoint folder:

```sh
c++ --version
c++ -std=c++20 -Wall -Wextra -Wpedantic -Werror -g -O0 main.cpp score_ledger.cpp score_tools.cpp -o checkpoint-debug
./checkpoint-debug --check
./checkpoint-debug --trace --scores 40 60 80
```

Record the exact command and actual compiler output. A successful build with
no warnings is a valid observation. Do not invent a warning or mistake a
linker error for a warning. If the compiler reports an error, fix the build
first and preserve the diagnostic with the change that resolved it.

- Compiler version and platform: [record]
- Starting source or ZIP: [record]
- Exact build command: [record]
- Compiler output and exit status: [record]

## Prediction and trace

Before running, predict the total for one score and for the default three
scores by hand. Then run the same arguments with `--trace`, and record the
actual output and exit status. Use the visited indices and running totals to
locate a mismatch. The untouched learner has one intentional logic bug.

- Input and predicted result: [record]
- Actual output and exit status: [record]
- Trace observations and source location: [record]
- Hypothesis and smallest proposed change: [record]

## Optional debugger observation

The debug build contains symbols. With GDB, run `gdb --args
./checkpoint-debug --scores 85`; use `break sumScores`, `run`, `next`, and
`info locals`. With LLDB, use `lldb -- ./checkpoint-debug --scores 85`,
`breakpoint set --name sumScores`, `run`, `next`, and `frame variable`.
Stop before and after the loop condition. Record what was actually observed
about the vector size, loop index and whether the loop body was entered.
Availability and displays differ across platforms. If no debugger is
available, retain the trace instead and state that limitation.

- Debugger version or trace-only reason: [record]
- Breakpoint and command sequence: [record]
- Observed variable values and step: [record]
- How the observation supports or rejects the hypothesis: [record]

## Correction and verification

Save the attempted explanation before consulting the staff reference.
Make the smallest justified change in the checkpoint, rebuild, and run the
same input. Record before and after output. Run `--check` and two additional
hand-calculated cases, including a boundary or a rejected input. Rejection
cases have no partial score output and return status 2. A completed learner
must produce seven actual passing checks and return status 0 for `--check`.
An untouched learner's known failure is evidence of reproduction only.

- Changed file and precise edit: [record]
- Rebuild command and result: [record]
- Same input, corrected output and exit status: [record]
- Seven-check output and exit status: [record]
- Custom case 1, prediction and actual result: [record]
- Custom case 2, prediction and actual result: [record]
- Explanation of why the change fixes the cause: [record]

## Review

Compare the saved evidence with the worked example after attempting the
repair. A reference transcript is an example from a particular source
revision, not proof that another student's source passed. Keep the notebook
and final exported source together. Pause at each prediction, build, trace and correction to discuss
the recorded reasoning.

The original `main.cpp` in this notebook pack only prints this worksheet
for convenience. It does not implement a second project, run the checkpoint,
grade evidence or certify completion. The Markdown file is the primary
resource. Optionally compile the generator with
`c++ -std=c++17 -Wall -Wextra -Wpedantic -Werror main.cpp -o notebook`
and run `./notebook > evidence.md`. Edit the generated notes separately.
