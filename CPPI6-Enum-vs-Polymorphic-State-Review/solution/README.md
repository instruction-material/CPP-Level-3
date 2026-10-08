# Enum State versus Polymorphic State Review

This optional exercise compares two representations of the rover's same four
phases and five legal transitions. It does not require replacing the core
capstone enum with a State pattern. Complete the primary rover first. The
comparison concerns phase/event behavior; command dispatch remains a different
polymorphic role.

## Build and files

The five-file learner pack contains `main.cpp`, `state_review.cpp`,
`state_review.h`, `Makefile` and `README.md`. The six-file reference also contains
`WORKED.md`. Read this worksheet before importing the separate practice pack.
Keep the completed rover and its saved identity unchanged.

From an extracted C++20 pack, run `make CXX=c++ main`, then `./main` and type
one event per line. The equivalent build is:

```sh
c++ -std=c++20 -Wall -Wextra -Wpedantic -Wconversion -Wsign-conversion -Werror main.cpp state_review.cpp -o main
```

Repository CMake targets are `state_review_starter` and `state_review_solution`.
The learner compiles but explicitly fails at its unfinished factory; status is
1 with `Failed: Unfinished state factory.` on stderr. Completing three marked
bodies restores the actual paired driver. Empty input does not bypass factory
construction. The reference exits 0 and reports balanced lifetime on empty input.

## One transition table, two mechanisms

| Current phase | start | pause | resume | finish |
| --- | --- | --- | --- | --- |
| ready | running | reject | reject | reject |
| running | reject | paused | reject | finished |
| paused | reject | reject | running | finished |
| finished | reject | reject | reject | reject |

An enum is a value. `enumNext` selects the next value with ordinary conditions
and returns `nullopt` for rejection. A `State` object supplies virtual behavior
through a base interface. Each actual derived type has one phase and decides
which events it accepts. Both mechanisms must implement the table, rather than
agreeing only on the one sample trace.

The supplied `Machine` owns one `unique_ptr<State>`. `Ready`, `Running`, `Paused`
and `Finished` override `phase` and `next`. The base destructor is virtual; no
base-value copy or object slicing is possible because the interface is abstract
and copy operations are deleted. The factory constructs the actual derived type.
The machine allocates a candidate before swapping ownership, so a failed
allocation leaves its prior state alive. Rejection allocates nothing and retains
the current object. Destruction releases the old actual derived state.

The `Lifetime` counters measure constructed/destroyed State objects. They are
instrumentation for this small single-process driver, not a thread-safe allocator
or proof about all program resources. Balanced counts alone do not establish
correct transitions. The independent table and behavior checks serve that role.

## Three narrow tasks

1. Complete `enumNext`: implement all five legal table entries and reject the
   other eleven pairs. Do not change another table cell to hide a mismatch.
2. Complete `Paused::next`: resume becomes running, finish becomes finished,
   and start/pause reject without a phase change.
3. Complete `makeState`: return a `unique_ptr<State>` owning the correct actual
   derived object for each phase. Preserve the supplied virtual destructor,
   `override` declarations and candidate-before-swap boundary.

Only the `BEGIN TASK`/`END TASK` bodies are missing. Record the table and a
prediction before filling them. Trace a pointer's owner and actual type through
one transition before consulting the separate worked record.

## Driver and expected trace

Input lines are exactly `start`, `pause`, `resume`, `finish`, `show` or `quit`.
Empty lines are skipped. Unknown input produces a stderr rejection and retains
both states. Each line is bounded to 24 bytes; overlong input is drained and
rejected once. EOF/quit end the loop. Extra program arguments return status 2
with `Usage: state-review`; read/output failures return status 1. Earlier output
cannot be rolled back. Normal completion reports actual lifetime balance.

Predict this trace:

```text
show
pause
start
pause
resume
finish
finish
quit
```

Expected stdout:

```text
enum ready poly ready
pause rejected enum ready poly ready
start accepted enum running poly running
pause accepted enum paused poly paused
resume accepted enum running poly running
finish accepted enum finished poly finished
finish rejected enum finished poly finished
lifetime balanced true
```

No stderr is expected, because a recognized but illegal event is a table
rejection printed in the paired result. An unrecognized event such as `restart`
uses `Rejected: unknown event.` on stderr and changes neither state.

## Changed cases and design decision

- From a fresh process, compare `start`, `pause`, `finish`. Explain the direct
  paused-to-finished path and why no resume is necessary before finish.
- Test all four events after finished and from ready. Record accepted/rejected
  behavior, resulting phases and constructor/destructor counts.
- Insert `show` and an unknown event between legal events. Explain why either
  leaves state and ownership unchanged.
- Predict actual object lifetimes in the worked trace. Count initial creation,
  accepted replacements and final destruction. An illegal event creates no state.
- Explain which design fits the four-phase rover. An enum is compact, explicit
  and easy to inspect for this closed table. Runtime State types become useful
  when phases own substantial distinct behavior or independently supplied roles;
  they add types, ownership and dispatch costs here. More classes do not by
  themselves improve a design.

For a walkthrough, pause at the candidate allocation and ownership swap, then
trace actual destruction through the virtual interface. For independent study,
write the transition/lifetime prediction before running the changed case. Submit
one trace, the full table, an ownership sketch and a reasoned design choice.
The exercise remains optional practice and does not alter the rover's core
completion contract. Source regression checks test actual behavior, not an
unseen architectural explanation.
