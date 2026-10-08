# Saveable Command-Driven Rover Simulation

This required capstone combines the course's command parsing, containers,
recursion, value validation, file handling and ownership. Build a small C++20
console rover, not a full game framework. One `Rover` owns the graph and current
state. A temporary `unique_ptr<Command>` supplies a narrow runtime interface.
The four phases remain an enum. Runtime command dispatch and phase selection
solve different problems; the optional State Review explores that distinction.

## Prerequisites and setup

Complete the Task Manager, maze search, container audit and resource/value-type
lessons first. Read a map/set traversal, a constructor invariant, a temporary
candidate and a `unique_ptr` before implementing this capstone. Supported native
validation uses GCC/Clang on Linux with C++20. The standard source also targets
macOS with a C++20 compiler. Windows replacement-rename behavior is not certified.
The browser edits source; export its ZIP and extract it before native execution.

Each role pack contains eight files: `main.cpp`, `rover.cpp`, `storage.cpp`,
`command.cpp`, `rover.h`, `command.h`, `Makefile` and this `README.md`.
From an extracted pack:

```sh
make CXX=c++ main
./main
```

Equivalent single-line build:

```sh
c++ -std=c++20 -Wall -Wextra -Wpedantic -Wconversion -Wsign-conversion -Werror main.cpp rover.cpp command.cpp storage.cpp -o main
```

From the repository root, configure with `cmake -S . -B build` and build
`command_sim_starter` or `command_sim_solution`. The starter compiles cleanly;
its five marked functions explicitly report unfinished work. Empty input and
`quit` differ: empty input exits normally, while the untouched parser rejects
any nonempty command, including `quit`. The driver is supplied, not a TODO.

## State and ownership

```text
input loop owns Rover
  Rover owns Snapshot
    map owns each zone and its ordered set of directed neighbors
    Snapshot owns position, phase and movement count
  unique_ptr<Command> owns one actual derived command
    execute(Rover&) borrows the candidate; no shared owner is introduced
    virtual destruction destroys the actual derived object
```

The initial graph is `entry -> lab -> dock`, with three zones. Position is
`entry`, phase is `ready`, and moves is `0`. Edges are directed. Adding
`dock -> entry` creates a cycle; it does not turn every edge into a two-way link.
Identifiers are one through 24 ASCII bytes, start with a letter, and contain
only letters, digits or underscores. The graph holds one through 64 zones and
at most 1024 distinct edges. Self-links are allowed. Position names an existing
zone. Moves is from 0 through 1,000,000; ready state has zero moves.

A graph copy and a completed `Result` are prepared before the driver's no-throw
state swap. Expected command rejection leaves the accepted state unchanged.
This bounded copy makes the boundary explicit; it is not an efficiency claim
for a large real-time engine. File publication and bytes already written to
stdout cannot be rolled back by this in-memory boundary.

## Command contract

Commands are lowercase and have exact argument counts. Tokens need whitespace
separators. Quotes can group a file path with spaces; inside quotes, backslash
escapes the next character. Paths contain one through 512 printable ASCII bytes.
Commands contain at most 1024 bytes before newline. Empty/whitespace lines are
skipped. Unknown commands, malformed quoting, extra/missing arguments and
invalid IDs are rejected before the `Parsed` result changes.

| Command | Behavior |
| --- | --- |
| `help` | Print the supported commands; change no state. |
| `show` | Print phase, position, moves and every sorted zone/neighbor list. |
| `link FROM TO` | In ready phase, create missing valid zones and add one new directed edge. Reject duplicates or bounds violations. |
| `start` | Only ready becomes running. |
| `pause` | Only running becomes paused. |
| `resume` | Only paused becomes running. |
| `finish` | Running or paused becomes finished. |
| `move TO` | In running phase, follow one direct outgoing edge and increment moves once. |
| `route TO` | Read-only recursive DFS from current position to a registered target. Print one path or `route unavailable`. |
| `save PATH` | In any phase, publish a deterministic snapshot through a new staging directory. |
| `load PATH` | In any phase, parse/validate a snapshot candidate and replace accepted state only on success. |
| `quit` | End input processing from any phase without changing the phase. |

Route search marks each entered zone once and backtracks failed path entries.
Ordered `set` neighbors give deterministic traversal. The path is simple and
bounded by 64 zones. It need not be the shortest path. If the current zone is
the target, the one-zone path is the base case. A known but unreachable target
is a successful query with `route unavailable`; an absent target is rejected.

Successful results use stdout. Rejections use `Rejected: ...` on stderr and
continue to the next command. EOF and handled rejections return status 0.
Unexpected input/output failure returns 1; extra program arguments produce
`Usage: rover` on stderr and status 2. Overlong lines are drained with bounded
storage and rejected once. Output is checked before normal exit; earlier bytes
may already have reached a reader. There is no implicit save at EOF or quit.

## Five implementation tasks

1. `parseCommand` in `command.cpp`: build a temporary parsed command, enforce
   the token/ID/path contract, and assign only after validation.
2. `nextPhase` in `rover.cpp`: implement the five legal table entries. Return
   false without changing `after` for every other phase/event pair.
3. `Rover::move` in `rover.cpp`: check running phase, direct edge and count
   before changing either position or moves.
4. `visitRoute` in `rover.cpp`: implement visited-state cycle prevention,
   current-target base case, ordered recursion and failed-path backtracking.
5. `decodeSnapshot` in `storage.cpp`: decode into a temporary snapshot, enforce
   every bound/order/invariant, and assign only after the entire file is valid.

The `BEGIN TASK`/`END TASK` regions locate the exact bodies. Supplied graph
linking, command ownership, checked save wrapper, driver and formatting remain
complete. Work in vertical slices: parser and show; transitions; movement;
route; then load/restart. Record a prediction before each slice. Compare the
reference only after writing the reason for a correction.

## Snapshot schema and failure policy

A snapshot has a final newline, exact version/header fields, sorted unique
zones and sorted unique `FROM TO` edge rows. No blank, duplicate, out-of-order
or trailing records are accepted. Numeric fields contain decimal digits only.
The declared counts must match all rows. Maximum size is 65,536 bytes.
The 1024-edge bound ensures every valid graph fits that byte envelope.
An initial snapshot is exactly:

```text
ROVER 1
phase ready
position entry
moves 0
zones 3
dock
entry
lab
edges 2
entry lab
lab dock
end
```

The decoder also checks that edges and position name declared zones, phase is
known, and ready state has zero moves. A snapshot is a state record, not proof
that its past commands were actually executed. Loading does not infer a
student identity or replay history.

Save exclusively acquires the sibling directory `PATH.rover-stage`, writes
`snapshot` inside it, checks close, and renames the completed file to `PATH`.
An existing stage causes rejection and remains untouched. Owned staging files
are cleaned on normal C++ unwinding. A failed open/write/close/rename leaves a
pre-existing valid target unchanged. Supported POSIX replacement is atomic;
crash durability, hostile concurrent directory replacement, network filesystems
and automatic recovery of abandoned stages are outside this course contract.
Load reads only a regular file, bounds its bytes, validates a candidate and
performs a no-throw swap. Missing/malformed files leave the prior state intact.

## Worked trace

Predict stdout, stderr and state after each command:

```text
show
route dock
start
move lab
pause
move dock
resume
move dock
finish
show
quit
```

Expected stdout:

```text
phase ready position entry moves 0
dock:
entry: lab
lab: dock
route entry -> lab -> dock
phase running
position lab moves 1
phase paused
phase running
position dock moves 2
phase finished
phase finished position dock moves 2
dock:
entry: lab
lab: dock
```

Expected stderr contains one line: `Rejected: Move requires running phase.`
The paused move changes neither position nor moves. The process returns 0.

For an actual restart, run `start`, `move lab`, `save "rover state.txt"`, then
`quit`. In a fresh process, `load "rover state.txt"` and `show` restore running,
lab and one move with the same graph. `save` does not change a phase or count.

## Independent study and walkthrough evidence

- Add `link entry archive` and `link archive dock` while ready. Predict which
  sorted branch `route dock` follows, then compare the actual path. Explain why
  DFS does not promise the fewest moves. Add a cycle and repeat the query twice.
- Try every event from each phase, including a second finish after finished.
  Write the complete four-by-four accepted/rejected transition table.
- Try `move dock` directly from entry while running. Preserve entry/zero moves.
  Then take both valid moves and distinguish reachability from one direct edge.
- Save accepted state, alter position/count and load it back. Compare complete
  graph/position/phase/count equality, not just one printed label.
- In a separate file copy, change one zone count, one edge target, the version,
  phase, numeric field, row order or final newline. Each failed load preserves
  the previous accepted state. Keep the valid snapshot for a later successful
  load. Also test an absent path and an already occupied staging directory.
- Draw the ownership diagram and explain the virtual destructor and `override`.
  Do not copy a derived command into a base object; the interface is abstract.
  Explain why the graph belongs to Rover rather than each command object.

Record compiler/version, clean build, a successful and rejected command trace,
route base/cycle/unreachable cases, actual save/restart, malformed-file rollback,
and one limitation. In a walkthrough, pause before mutation/commit and predict
state first. For independent study, write the prediction and explanation first.
The regression verifier checks behavior; it does not grade an unseen explanation.
