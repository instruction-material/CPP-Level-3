# Course Source Manifest

Canonical source repository: `CPP-Level-3`

## Mapped Catalog Courses

- `cpp-level-3`: C++ Level 3

## Verification Gate

- Run `./verify-course-source.sh` from this repository root before treating the source pack as ready.
- The verification gate checks for this manifest, the source backlog ledger, source-like files, removed Replit metadata, and any repo-specific readiness files.
- Run `python3 verify-build-debug.py` for the required CPPI0 checkpoint's actual
  multi-file builds, intentional learner failure, corrected reference, input
  boundaries, trace, header dependencies, and ordinary/sanitized execution.
- Run `python3 verify-notebook.py` to check the optional worksheet printers and
  worked examples against actual ordinary and sanitized checkpoint output.
- Run `python3 verify-inventory.py` for actual reference views, distinct unfinished
  learner output and allocation-failure state preservation under ordinary and
  sanitized builds.
- Project-specific unit tests or build commands should still be run inside individual project folders when a project includes its own test harness.

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
- Source-like files: 63
