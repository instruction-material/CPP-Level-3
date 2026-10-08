# Validation, Exceptions, and Resource Boundaries

Private lesson candidate. Native example execution and failure-path acceptance
remain pending.

**Concept focus:** Separate resource cleanup from the decision to accept a
changed result. Identify what remains valid when an operation stops.

A precondition describes what an operation requires, such as two different file
paths. An invariant describes what remains true for an accepted object, such
as every score being in the range 0 through 100. A postcondition describes the
result of a successful operation. State the failed-case outcome as well: which
old values or files survive, which partial work is discarded and which message
explains the stop.

Expected invalid input can be rejected with a normal return value or reported
through an exception at a documented boundary. An exception transfers control
to a matching handler; it does not automatically restore earlier mutations.
RAII releases resources during unwinding. Preserving application state requires
the operation's own design.

The basic exception guarantee keeps objects valid and avoids resource leaks,
but their values can differ after a failure. A strong guarantee preserves the
observable accepted state when the operation fails. Both descriptions need a
named scope. A failed file publication and a failed message after publication
are different operations with different outcomes.

This complete practice program validates a proposed batch in a temporary vector.
It commits that candidate with `swap` only after all new scores pass validation.
Save it as `boundary.cpp` in a separate practice folder.

```cpp
#include <iostream>
#include <stdexcept>
#include <string>
#include <vector>

void appendValidated(std::vector<int>& accepted,
                     const std::vector<int>& proposed) {
    auto candidate = accepted;
    for (const int score : proposed) {
        if (score < 0 || score > 100)
            throw std::invalid_argument("Score outside 0 through 100.");
        candidate.push_back(score);
    }
    accepted.swap(candidate);
}

void printAccepted(const std::vector<int>& accepted) {
    std::cout << "Accepted:";
    for (const int score : accepted) std::cout << ' ' << score;
    std::cout << '\n';
}

int main(const int argc, char* argv[]) {
    if (argc != 1 &&
        !(argc == 2 && std::string(argv[1]) == "reject")) {
        std::cerr << "Usage: boundary [reject]\n";
        return 2;
    }
    std::vector<int> accepted{84};
    try {
        appendValidated(accepted, {91, argc == 2 ? 101 : 76});
    } catch (const std::invalid_argument& error) {
        printAccepted(accepted);
        std::cerr << "Rejected: " << error.what() << '\n';
        return 1;
    }
    printAccepted(accepted);
    return 0;
}
```

Predict both runs before compiling:

```sh
c++ -std=c++20 -Wall -Wextra -Wpedantic -Wconversion -Wsign-conversion -Werror boundary.cpp -o boundary
./boundary
./boundary reject
```

The ordinary run prints `Accepted: 84 91 76` and returns 0. The rejected run
prints `Accepted: 84` to standard output, reports
`Rejected: Score outside 0 through 100.` to standard error and returns 1.
Capture the two streams separately rather than assuming their combined display
order. An unsupported argument prints usage to standard error and returns 2.

For the rejected run, the candidate briefly contains 84 and 91. It is destroyed
when validation throws; the original vector still contains 84. Moving the
append directly into `accepted` would leave 91 accepted before the late invalid
score was found. Try that change only in a separate practice copy, predict its
new rejected-state output and compare. Record the first prediction mismatch
with its cause. Change the proposed boundary scores to 0, 59, 60 and 100, then
predict each accepted result. The successful case alone cannot establish the
failed-case guarantee.

This small example catches only its expected validation exception. Allocation
failure can still propagate. Copying and appending operate on the candidate,
so the accepted vector remains unchanged if either allocation fails before the
swap. That statement does not promise successful diagnostic output when the
machine or output stream has failed. Do not add an empty `catch (...)` that
silently reports success.

Carry the same idea into the file processor. First validate the paths and read
all rows into a bounded vector. Reject a malformed late row before acquiring
output staging. Next acquire an exclusive staging directory beside the output,
write its temporary report and inspect the stream after writing, flushing and
closing. Streams do not throw for every failure by default; check their state
explicitly unless their exception masks are deliberately configured.

Only rename the completed temporary file after those checks. In this project's
local macOS/Linux, single-writer contract, a successful rename is the publication
boundary. A later failed success message does not restore the old report. This
is not a crash-recovery or durable-write guarantee, and it does not protect
against another process changing the paths concurrently.

The guard cleans up only the staging directory and temporary file it acquired.
Its destructor uses nonthrowing filesystem operations, because throwing during
exception unwinding can terminate the process. Cleanup can still fail when the
operating system refuses it. A collision with a pre-existing staging path must
leave that other path intact; it is not owned by this operation.

Before implementation, complete a failure table with these rows: missing input,
malformed late record, existing staging collision, failed partial write, failed
rename and failed acknowledgment after rename. For each, predict the exit code,
accepted output, owned temporary work and diagnostic. Test safe input and path
failures yourself; the native acceptance gate supplies controlled write and
rename faults. Retain actual evidence instead of a hand-written passing label.
An instructor can use each row as a pause point, while an independent learner
can complete the same predictions and observations in order.

Primary wording references: [exception unwinding](https://eel.is/c++draft/except.ctor)
and [filesystem rename](https://eel.is/c++draft/fs.op.rename).
