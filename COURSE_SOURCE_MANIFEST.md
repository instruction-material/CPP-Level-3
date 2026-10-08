# Course Source Manifest

Canonical source repository: `CPP-Level-3`

## Mapped Catalog Courses

- `cpp-level-3`: C++ Level 3

## Verification Gate

- Run `./verify-course-source.sh` for source presence and catalog bookkeeping.
  It checks this manifest, the backlog ledger, source-like files and removed
  Replit metadata. Presence alone does not establish working starter/reference
  behavior or complete teaching material.
- The behavioral gates below cover only their named projects. Other active
  folders require their own content, source and workflow audit.
- Run `python3 verify-build-debug.py` for the required CPPI0 checkpoint's actual
  multi-file builds, intentional learner failure, corrected reference, input
  boundaries, trace, header dependencies, and ordinary/sanitized execution.
- Run `python3 verify-notebook.py` to check the optional worksheet printers and
  worked examples against actual ordinary and sanitized checkpoint output.
- Run `python3 verify-inventory.py` for actual reference views, distinct unfinished
  learner output and allocation-failure state preservation under ordinary and
  sanitized builds.
- Run `python3 verify-task-manager.py` for command grammar, ledger boundaries,
  save/restart, late-row rejection, a real write failure with retry, distinct
  unfinished learner and completed learner/reference behavior, strict C++20
  ordinary/sanitized builds, Make and the existing CMake target names.
- Run `python3 verify-row-import.py` for selective valid-row imports, rejected
  physical-line reports, fatal-read rollback, save/restart and ordinary/sanitized
  learner/reference builds with Make and CMake.
- Run `python3 verify-maze-search.py` for bounded input, recursive search, valid
  paths, trace/backtracking, repeated calls and independent reachability checks.
- Run `python3 verify-recursion-trace.py` for the optional saved-maze worksheet's
  three full worked traces, independent stack/reachability models, ordinary and
  sanitizer execution, blank learner records, printers and CMake targets.
- Run `python3 verify-container-audit.py` for three optional inventory probes,
  copied-view and ordering boundaries, completed/unfinished learner distinctions,
  independent row models, ordinary/sanitizer execution and worksheet printers.
- Run project-specific acceptance checks for every other folder before claiming
  readiness; the catalog mapping does not certify those implementations.

## Active Catalog Targets

| Folder |
| --- |
| `CPPI0-Build-and-Debug-Checkpoint` |
| `CPPI0-Warnings-and-Debugger-Notebook` |
| `CPPI1-Import-and-Reject-Bad-Rows` |
| `CPPI1-Mini-Command-Scanner` |
| `CPPI1-Saveable-Task-Manager` |
| `CPPI2-Recursion-Trace-Drill` |
| `CPPI2-Recursive-Maze-Search` |
| `CPPI3-Container-Tradeoff-Audit` |
| `CPPI3-Inventory-Indexer` |
| `CPPI4-Ownership-Rewrite-Reflection` |
| `CPPI4-Resource-Safe-File-Processor` |
| `CPPI5-Fraction-Toolkit` |
| `CPPI5-Template-Error-Reading-Drill` |
| `CPPI6-Enum-vs-Polymorphic-State-Review` |
| `CPPI6-Saveable-Command-Simulation` |

## Source Inventory

- Top-level folders: 15
- Active linked folders: 15
- Ledgered inactive/support folders: 0
