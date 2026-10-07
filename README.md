# C++ Level 3

Starter and solution material for the C++ Level 3 bridge course.

This course sits between C++ Level 2 and the downstream Data Structures / Design Patterns tracks. It focuses on medium-size command-line programs, file-backed state, recursion, STL fluency, RAII, value types, templates, and introductory polymorphism.

Each project directory contains a student-facing `starter/` implementation and an instructor `solution/` implementation.

## Projects

- `CPPI0-Build-and-Debug-Checkpoint`: Build and Debug Checkpoint
- `CPPI0-Warnings-and-Debugger-Notebook`: Warnings and Debugger Notebook
- `CPPI1-Saveable-Task-Manager`: Saveable Task Manager
- `CPPI1-Import-and-Reject-Bad-Rows`: Import and Reject Bad Rows
- `CPPI1-Mini-Command-Scanner`: Mini Command Scanner
- `CPPI2-Recursive-Maze-Search`: Recursive Maze Search
- `CPPI2-Recursion-Trace-Drill`: Recursion Trace Drill
- `CPPI3-Inventory-Indexer`: Inventory Indexer
- `CPPI3-Container-Tradeoff-Audit`: Container Tradeoff Audit
- `CPPI4-Resource-Safe-File-Processor`: Resource-Safe File Processor
- `CPPI4-Ownership-Rewrite-Reflection`: Ownership Rewrite Reflection
- `CPPI5-Fraction-Toolkit`: Fraction Toolkit
- `CPPI5-Template-Error-Reading-Drill`: Template Error Reading Drill
- `CPPI6-Saveable-Command-Simulation`: Saveable Command-Driven Simulation
- `CPPI6-Enum-vs-Polymorphic-State-Review`: Enum vs Polymorphic State Review

## Optional CPPI1 selective-import extension

`CPPI1-Import-and-Reject-Bad-Rows` extends the completed Task Manager with
an `import "PATH"` command. Its learner/reference packs contain five C++20
translation units, four headers, a Makefile and the full neutral brief. The
supplied base remains complete; only two importer functions are unfinished.
Import accepts valid increasing-ID rows and reports rejected physical lines,
while fatal file/header/read failures preserve both state and the earlier report.
The required project's full-file reload policy remains separate.

```sh
cmake -S . -B build
cmake --build build --target bad_rows_starter bad_rows_solution
python3 verify-row-import.py
```

The verifier distinguishes the untouched learner from the reference and a
completed learner fixture; it checks mixed imports, explicit save/restart,
fatal read failures, strict bounds, Make and CMake in ordinary and sanitizer
builds. This scope does not certify unrelated C++3 projects.
