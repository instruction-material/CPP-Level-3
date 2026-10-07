Reference pack: compare actual behavior after retaining a learner attempt.

# Saveable Task Manager

This required CPPI1 project practices a small command parser, validated state
changes and text-file persistence. It follows the C++20 build/debug checkpoint.
The completed program manages one task list. It keeps command syntax, task
rules and disk storage in separate translation units so each can be checked
without an interactive session. The optional Import and Reject Bad Rows project
extends this saved list with an import policy; it is not required here. The
Mini Command Scanner studies scanning positions and token kinds separately.

## Preparation and files

Use a C++20 compiler and the C++ standard library. No external packages, database
or service are needed. Review functions, vectors, structs, string views, stream
state, `std::from_chars` and `std::filesystem`. A string view borrows existing
text; keep it only while the original string remains alive. Copy task text into
the command or ledger when it must outlive the input line.

Start with the nine files in `starter/`. Keep their names and public interfaces.

| File | Responsibility |
| --- | --- |
| `main.cpp` | Supplied command loop, messages and explicit save/quit policy |
| `command_parser.h`, `command_parser.cpp` | Command grammar and integer parsing |
| `task_manager.h`, `task_manager.cpp` | Task state, validation and filtered views |
| `task_storage.h`, `task_storage.cpp` | Full-file load and temporary-file save |
| `README.md`, `Makefile` | This brief and a reproducible local build |

The learner pack compiles but its project functions are unfinished. Startup
reports an `UNFINISHED` load error and exits with status 1 until loading is
implemented. This is an expected starting condition, not a passed acceptance
check. `--help` is already supplied. The reference is a functioning application
for comparison after recording an attempt and predicted results.

## Command contract

Commands are lowercase and occupy one input line. Space, tab and carriage return
at line boundaries are ignored. Blank lines do nothing. Task text must be
enclosed in one pair of double quotes. This exercise has no escape syntax.

| Command | Behavior |
| --- | --- |
| `add "text"` | Append an open task; print `Added ID` |
| `done ID` | Mark an existing task complete; print `Completed ID` |
| `list` or `list all` | Print all tasks in insertion order |
| `list open` or `list done` | Print only the requested status in insertion order |
| `save` | Save the current list; print `Saved N` on success |
| `reload` | Replace the current list from a fully valid saved file; print `Loaded N` |
| `help` | Print the supplied usage and command list |
| `quit` | Print `Bye.` and stop processing input |

Each list begins with `Tasks N`, then one line per selected task in the form
`ID [open] text` or `ID [done] text`. No tasks means just `Tasks 0`.
An invalid command or failed operation writes `Error: message` to standard error
and the loop continues. It must not change the task list, the next ID or the
saved file. Successful parser/model/storage functions clear their error output.
Failed parsing must leave the caller's `Command` or integer output unchanged.

IDs are whole ASCII decimal numbers from 1 to 999999. Leading zeros are accepted;
signs, fractions, spaces inside an ID, overflow and extra arguments are rejected.
New IDs increase by one from the largest loaded ID, or start at 1 for an empty
list. There is no delete command and completing a task does not reuse its ID.
Completing an already completed task succeeds. An unknown ID fails.

Keep at most 100 tasks. Text contains 1 to 80 bytes, at least one non-space byte,
and only printable ASCII characters (32 through 126) other than double quote.
Tabs, newlines, control bytes, non-ASCII text and an all-space text are rejected.
Spaces inside quotes are retained exactly. These bounds deliberately keep this
parser exercise small; Unicode and quote escaping are later extensions.

## File contract and recovery

`task-manager` uses `tasks.tsv` in its working directory. `task-manager --file
PATH` selects another file; quote a path containing spaces in the shell.
`task-manager --help` alone prints help without opening a file. Other option
shapes print usage to standard error and exit with status 2. Normal startup
loads the file and prints `Loaded N`. A missing startup file begins an empty
list. An existing unreadable or invalid file reports an error and exits with
status 1 before processing commands.

The first file line is exactly `CLASSES_TASKS_V1`. Each later line contains an
ID, a tab, exactly `0` for open or `1` for done, a tab, then the task text.
For example, these lines show the separators as `<TAB>` for readability:

```text
CLASSES_TASKS_V1
1<TAB>0<TAB>Read parser contract
2<TAB>1<TAB>Check an empty list
```

Actual saved files contain tab bytes, not the characters `<TAB>`. Load accepts
LF or CRLF endings and an optional final newline. Blank data rows, extra tabs,
duplicate or decreasing IDs, invalid status/text, more than 100 rows, a different
header and files larger than 64 KiB are invalid. Gaps between increasing IDs are
allowed. Load must validate the entire file into temporary state before calling
`TaskLedger::replace`; a bad last row must leave the current list intact.
`replace` independently validates count, IDs and text before replacing state.

An explicit `reload` rejects a missing file and keeps the current list. A
successful reload discards unsaved edits, so save first when those edits matter.
Neither `quit` nor end of input automatically saves. This makes the difference
between current state and saved state visible and testable.

Save writes a new `PATH.tmp`, checks the write, flush and close, and then renames
it over `PATH`. If any step fails, preserve the old saved bytes and remove only
the new temporary file. Refuse a pre-existing temporary entry; do not erase it.
The destination must be a regular file or absent; destination symlinks and
directories are rejected. Do not create missing directories automatically.
Use this exercise with one running writer in a trusted working folder. It does
not implement concurrent writers, power-loss durability or recovery by guessing
which abandoned temporary file to use. Inspect an abandoned temporary file
before choosing to remove it and retry.

## Implementation path and guided checkpoints

1. Read the supplied headers and predict output for an empty list, two additions,
   one completion and each status filter. Trace which function owns each rule.
2. Implement `TaskLedger::add`, `complete`, `select` and `replace`. Check bounds
   before mutation. Filtered views are copies and must preserve stored order.
   For replacement, validate a candidate list before swapping it into place.
3. Implement `parseCommand` using the supplied boundary-trimming and integer
   helpers. Build a temporary command and assign it only after full validation.
   Test syntax independently of the ledger: parsing a valid command does not
   mean its ID exists.
4. Implement load. Separate header/row parsing from committing state. Check
   stream failure as well as syntax. Test a malformed row after several valid
   rows, not just at the beginning.
5. Implement save. Keep the old file until the new file is fully written. Check
   failures explicitly and make a second attempt after correcting a blocked
   path. A printed success message alone is not proof of saved contents.
6. Run the command loop, save, exit and start a new process on the same file.
   Record predicted and observed outputs before comparing with the reference.

At each checkpoint, explain the invariant that should remain true, the smallest
case that could break it, and where a debugger or output check would reveal the
problem. An instructor can use the same checkpoints for a walkthrough without
changing the assignment or providing a completed implementation first.

## Build and run

From either the learner or reference pack:

```sh
make
./task-manager --help
./task-manager --file practice.tsv
```

For a debug build, use `make task-manager-debug`. `make clean` removes only the
two executable files and leaves saved task files alone. Without Make, compile
all four translation units, keeping the headers beside them:

```sh
c++ -std=c++20 -Wall -Wextra -Wpedantic -Werror main.cpp task_manager.cpp command_parser.cpp task_storage.cpp -o task-manager
```

From the repository root, CMake can build only these targets:

```sh
cmake -S . -B build
cmake --build build --target task_manager_starter task_manager_solution
python3 verify-task-manager.py
```

The repository verifier checks the unfinished learner separately from the
working reference and a completed learner fixture. The site IDE can edit, save
and export these files. File persistence and native filesystem behavior need a
native C++20 environment; export the whole pack for those checks.

## Acceptance and hand-in evidence

Use at least these checks: empty list; quoted text with retained spaces; two
tasks and all three filters; repeated completion; unknown ID; rejected syntax
with no state change; 80/81-byte text; the 100/101-task boundary; ID exhaustion;
save and restart; an empty saved list; CRLF and missing final newline; malformed
late row preserving current state; missing reload; a blocked temporary path
preserving old bytes; and a successful retry after the obstruction is removed.
Keep scratch files separate from anything valuable.

Submit the nine pack files, the implemented TODOs, and a short record containing
predicted/observed output, a saved-file sample, at least two additional boundary
checks, and an explanation of why load and save cannot partially replace good
state on an ordinary validation or I/O failure. Keep an initial attempt before
using the reference. Do not substitute fixed pass counters for behavioral checks.
