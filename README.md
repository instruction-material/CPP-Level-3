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

## CPPI2 recursive maze search

`CPPI2-Recursive-Maze-Search` supplies a six-file C++20 pack with complete bounded
input validation and one focused recursive learner function. Search keeps the
input immutable, marks entered cells once, backtracks failed path entries and
returns the first path in up/right/down/left order. It does not promise a shortest
path. The untouched learner explicitly reports unfinished search.

Build `maze_search_starter` and `maze_search_solution` with CMake and run
`python3 verify-maze-search.py`. The independent breadth-first oracle checks
reachability and valid returned paths on 480 deterministic graph comparisons,
alongside recursion traces, repeated calls, parser rollback, strict byte/grid
bounds, ordinary/sanitizer builds and Make/CMake workflows. This project does not
certify unrelated course packs.

## Optional CPPI2 recursion worksheet

`CPPI2-Recursion-Trace-Drill/starter/WORKSHEET.md` continues the saved, completed
maze project. Predict three valid inputs, draw call/return state, then record
actual traces and a corrected explanation. Blank learner records remain separate
from the staff `solution/WORKED-TRACE.md`. The preserved C++17 main.cpp files and
CMake trace_drill targets only print their respective worksheets.

Run `python3 verify-recursion-trace.py` to compare the complete worked outputs
with an independent iterative frame-stack model and breadth-first reachability.
It runs ordinary and sanitizer maze references and completed learner fixtures,
distinguishes untouched status 3, checks input preservation and repeated solves
in one process, and verifies both worksheet printers and CMake targets.

## Optional CPPI3 container audit

`CPPI3-Container-Tradeoff-Audit/starter/WORKSHEET.md` continues the saved Inventory
Indexer. Predict three probes, record actual view and mutation results, then
justify one container choice. The worksheet distinguishes insertion, key and
sorted-name order, copies from live references, and complexity bounds from actual
measurements. The separate `solution/WORKED-AUDIT.md` contains the checked staff
example. Both original C++17 main.cpp files and CMake container_audit targets
only print their corresponding documents.

Run `python3 verify-container-audit.py` for actual ordinary/sanitizer calls on the
reference, a completed learner fixture and the distinct untouched learner. An
independent plain-row model checks all outputs, duplicate rejection, copied-view
boundaries and fresh repeated cases. Both worksheet printers and CMake targets
must reproduce their complete documents. The primary inventory source is
unchanged; its separate verifier still checks allocation-failure rollback.

## CPPI4 resource-safe publication and optional ownership reflection

`CPPI4-Resource-Safe-File-Processor` reads bounded tab-separated score records,
validates every row before preparing output, and publishes a checked report by
renaming a staged file. Its learner has four explicit unfinished tasks; its
reference performs the actual operation. Both include `scores.tsv`, a strict
C++20 Makefile and the full neutral brief. The accompanying ownership and error
boundary lessons contain complete small programs with prediction exercises.

The optional `CPPI4-Ownership-Rewrite-Reflection/starter/NOTES.md` continues the
saved completed file processor. Read a concrete Level 2 manual allocation, make
a separate automatic-ownership comparison, and explain the saved application's
resource lifetimes and publication boundary. The worked staff record remains
separate. Reading the worksheet imports no second application. The preserved
CMake targets and main.cpp wrappers print their respective documents exactly.

Run `python3 verify-file-processor.py`, `python3 verify-ownership-worksheet.py`,
`python3 verify-cppi4-lessons.py` and `python3 verify-cppi4-builds.py` on Linux.
These gates test reference and completed-learner report bytes against an
independent model, distinguish untouched learner failure, exercise actual
partial writes and failed rename with prior output preservation, inspect
ownership exceptions, and check normal/changed lesson examples. Native checks
use strict C++17/20 ordinary and sanitizer builds; all four Make packs and
preserved CMake targets are checked separately. Each subprocess has a bounded
lifetime and cleanup. These checks cover their executed cases; they do not
certify unrelated course packs, crash durability or concurrent path changes.

## CPPI5 values, templates and optional diagnostic practice

`CPPI5-Fraction-Toolkit` provides five genuine learner implementation tasks and
a bounded exact Fraction reference. Both three-file packs carry their complete
neutral brief and strict C++20 Makefile. The two complete teaching documents
explain invariants, const copies, nonmutating named operations, conventional
operators, ordering laws, template requirements and diagnostic reading.

`CPPI5-Template-Error-Reading-Drill/WORKSHEET.md` is optional separate practice.
Its ordinary learner supplies integer/string calls. A documented macro triggers
a missing Score comparison; the worked copy supplies only that comparison.
Save and preserve the primary project before starting the drill. Its worksheet
and worked record replace generic notes and fixed grading output.

Run `python3 verify-fraction-toolkit.py`, `python3 verify-template-drill.py`,
`python3 verify-cppi5-lessons.py` and `python3 verify-cppi5-builds.py` on the hosted
Linux toolchain. They compare completed and reference results with Python's
independent exact arithmetic model, inspect actual GCC/Clang diagnostics, probe
copy/const/order laws and unchanged operands after rejection, execute the
complete/changed teaching programs, and check all four Make packs and preserved
CMake names. Ordinary/sanitizer C++17/20 acceptance is separate from the
documented C++20 learner build path. These gates cover executed cases; source
publication does not validate unseen learner work or establish site deployment.

## CPPI6 rover capstone and optional state review

The required Saveable Command-Driven Simulation is an eight-file C++20 rover
pack with five marked implementation tasks: parsing, transitions, movement,
bounded recursive routes and transactional snapshot decoding. Complete input,
command ownership, graph linking, safe-save infrastructure and full neutral
teaching are supplied. The separate optional State Review has a five-file
learner pack and six-file reference with a worked record. It compares the same
four-phase table through an enum and actual derived State objects.

Use `verify-rover-simulation.py`, `verify-state-review.py`,
`verify-cppi6-lessons.py` and `verify-cppi6-builds.py` for actual native behavioral,
independent model, lifetime, changed-example and Make/CMake checks. The complete
source workflow preserves the earlier sixteen native groups and runs the four
capstone groups in a separate bounded job. Site import/catalog acceptance and
production activation are separate from source verification.
