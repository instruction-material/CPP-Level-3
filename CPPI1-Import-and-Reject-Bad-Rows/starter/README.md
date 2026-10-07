# Import and Reject Bad Rows

This optional CPPI1 challenge extends the completed Saveable Task Manager. It
practices a selective import policy: append valid records, explain each rejected
record, and continue checking later rows. The required Task Manager still rejects
an entire invalid saved file during startup or `reload`. Import and reload have
different purposes and must keep their different failure rules.

## Preparation and files

Complete the required Task Manager first, including explicit save and restart
checks. Review whole-token integer parsing, `string_view` lifetime, stream state,
vectors, temporary state and `TaskLedger::replace`. Use C++20 and only the C++
standard library. No packages, database or network service are needed.

The 11-file pack supplies a completed base Task Manager and its command loop.
Keep the file names and public interfaces. The learner's two TODOs are in
`task_import.cpp`; the supplied base is preparation for this extension rather
than another assignment to implement the required project again.

| Files | Responsibility |
| --- | --- |
| `main.cpp` | Command loop and import report formatting |
| `command_parser.h`, `command_parser.cpp` | Existing commands and quoted import paths |
| `task_manager.h`, `task_manager.cpp` | Task invariants, IDs and filtered views |
| `task_storage.h`, `task_storage.cpp` | Complete-file reload and explicit save |
| `task_import.h`, `task_import.cpp` | Row parsing, selective import and fatal-error preservation |
| `Makefile`, `README.md` | Native build and this contract |

The untouched learner compiles and runs the supplied base commands. Import
reports `Error: UNFINISHED: implement selective import.` and keeps current state.
That is an expected starting condition, not evidence that import works. Record
an attempt and predicted results before comparing with the reference.

## Command and file contract

Run `task-import` with the same `--file PATH` option as the required Task Manager;
the default saved path is `tasks.tsv`. `--help` opens no files. Startup, `add`,
`done`, `list [all|open|done]`, `save`, `reload`, `help`, `quit` and their exit
statuses retain the required project's rules. This program adds one command:

```text
import "incoming tasks.tsv"
```

The command is lowercase and the path is enclosed in one pair of double quotes.
The path contains 1 to 1024 printable ASCII bytes, with at least one non-space
byte, and no double quote. There is no escape syntax. Boundary spaces, tabs and
carriage return outside the quoted argument are ignored. Reject missing quotes,
extra arguments, empty/all-space paths and control or non-ASCII bytes. A failed
command parse leaves its output unchanged. This path bound is a parser exercise,
not a guarantee that every operating system accepts every such path.

The import file is a readable regular file, at most 64 KiB (65536 bytes). Reject
directories and symlinks, including dangling symlinks. Its first physical line is
exactly `CLASSES_TASKS_V1`. A header-only file imports zero rows successfully.
Accept LF or CRLF endings and an optional final newline. Do not trim data fields,
accept a byte-order mark, create directories or rewrite the input file.

Each data row is `ID<TAB>status<TAB>text`, with exactly two tab bytes. ID is a whole
ASCII decimal number from 1 to 999999; leading zeros are allowed. Status is
exactly `0` for open or `1` for done. Text contains 1 to 80 printable ASCII bytes
other than double quote and at least one non-space byte. Retain spaces in text.
These are the same bounds used by the required Task Manager.

## Selective acceptance and reports

Process data rows in file order, beginning at physical line 2. Keep the current
tasks, their status and their order. Accept a valid row only when its ID exceeds
the largest current or already accepted ID and fewer than 100 tasks would be
stored. Gaps are allowed. Keep imported IDs and status; do not renumber, sort,
overwrite, complete or deduplicate existing tasks. A rejected row does not
advance the last ID or consume capacity. Later valid rows can still be accepted.
After a successful import, the next `add` uses one greater than the final largest
ID. Importing ID 999999 therefore exhausts new IDs without integer overflow.

Report one rejection per bad row, using this first-failure order:

| Check | Exact reason |
| --- | --- |
| Exactly three tab-delimited fields | `expected ID<TAB>status<TAB>text` |
| Whole ID in range | `invalid ID` |
| Status exactly 0 or 1 | `invalid status` |
| Task text within its bounds | `invalid text` |
| ID greater than the current last ID | `ID must increase beyond the current last ID` |
| Space in the 100-task ledger | `task limit reached` |

Blank data rows are rejected by the field check. Rejected rows retain their
physical line numbers, including intervening blanks. A final newline ends the
last row; a second newline creates an additional blank row. On success, write
`Imported A rejected R` to standard output, then `Rejected line N: reason` for
each rejection in file order. Row rejections are ordinary import results and
do not write to standard error or stop the command loop.

## Fatal errors and saved state

A missing, unreadable, non-regular, oversized or incompletely read input, or a
bad header, fails the whole operation. Write `Error: message` to standard error
and continue the command loop. Preserve both the ledger and the caller's earlier
`ImportReport`; do not publish a partial report. A fatal error after valid input
bytes must still preserve state. Read the bounded input completely, then build
temporary tasks and a temporary report, and commit only after every fatal check
has succeeded. `parseImportRow` independently leaves its `Task` output unchanged
on failure. Successful functions clear their error output.

Import changes only current memory. The input file and saved task file remain
unchanged until an explicit `save`. `quit` and end-of-input never save. `reload`
discards unsaved imports only if the entire saved file is valid. A malformed
late saved row still rejects the whole reload and keeps current memory intact.
Importing the current saved file is permitted but normally rejects its existing
IDs; use a separate input file when practicing new records. Use a trusted working
folder and one running writer, as in the required project.

## Guided implementation and prediction

1. Trace a ledger containing ID 3 and the sequence of incoming IDs 4, 4, 2, 8.
   Predict each acceptance or rejection, the final order and the next new ID.
2. Implement `parseImportRow`. Find separator positions before taking views.
   Keep borrowed views within the input string's lifetime and copy accepted
   text into a temporary `Task`. Check the documented reason order.
3. Implement the bounded read and header check in `importTaskRows`. Distinguish
   clean EOF from a read error. Predict whether any task/report changes after a
   valid row followed by a read failure or byte 65537.
4. Copy existing tasks into a candidate. Track physical line numbers and a
   pending report. Parse each row, then check ID order and capacity before append.
   A rejected row affects only the pending rejection list.
5. Commit through `TaskLedger::replace` once. Publish the pending report only
   after the ledger replacement succeeds. Verify no success counter is printed
   for unfinished or fatal behavior.
6. Run the same mixed file through import and complete-file reload. Explain why
   one operation accepts a subset while the other preserves the whole old state.
   Save, exit and start a fresh process to prove persistence separately.

An instructor can pause at each checkpoint to inspect predicted output and the
invariant before implementation. Independent study uses the same predictions,
small tests and explanations; a walkthrough does not change the contract.

## Worked input and observable result

With an empty ledger, this example shows tab separators as `<TAB>` for readability:

```text
CLASSES_TASKS_V1
2<TAB>0<TAB>first
broken
5<TAB>1<TAB>finished
```

Create actual tab bytes, not the characters `<TAB>`. Import produces:

```text
Imported 2 rejected 1
Rejected line 3: expected ID<TAB>status<TAB>text
```

`list` then shows IDs 2 and 5 in that order; the next `add` uses ID 6. Before
running a changed example, predict the effect of a duplicate ID, invalid status,
blank data row and a valid row after those failures.

## Build and hand-in evidence

From either pack:

```sh
make
./task-import --help
./task-import --file practice.tsv
make task-import-debug
```

`make clean` removes only the two executable files, preserving saved/imported
data. Without Make, keep all four headers beside the five translation units:

```sh
c++ -std=c++20 -Wall -Wextra -Wpedantic -Werror main.cpp task_manager.cpp command_parser.cpp task_storage.cpp task_import.cpp -o task-import
```

From the course source repository root:

```sh
cmake -S . -B build
cmake --build build --target bad_rows_starter bad_rows_solution
python3 verify-row-import.py
```

The site IDE edits, saves and exports the complete pack. Export it for native
C++20 compilation and real file checks. Submit the 11 files, the implemented
TODOs, predicted/observed results, rejection reasons and an explanation of the
import/reload distinction. Check an empty file versus a header-only file; mixed
and all-rejected rows; duplicate/decreasing IDs; 80/81-byte text; 100/101-task
capacity; 65536/65537 bytes; CRLF and missing final newline; missing input; a bad
header after an earlier import; save/restart; and unchanged saved/input bytes
before save. Add at least two boundary cases and retain an initial attempt.
Fixed pass counters do not demonstrate parsing, state changes or persistence.
