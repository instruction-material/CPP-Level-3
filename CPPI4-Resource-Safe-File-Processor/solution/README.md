# Resource-Safe File Processor

## Purpose and starting point

Build a file-processing program that validates every input record before
publishing a replacement report. Practice automatic resource cleanup and name
the exact point at which temporary work becomes the accepted result. Use the
parsing and saved-state ideas from CPPI1, and vector ownership from CPPI3.

Confirm the starter import in the site IDE. Keep any earlier saved attempt
separate, then edit the four marked task bodies in `main.cpp`. The untouched
starter reports `Unfinished task: processFile.` and returns 1. That message
identifies unfinished work; it is not a passing project result.

The site IDE edits and saves C++ projects. Download and extract the ZIP before
running it with a native C++20 compiler on macOS or Linux. From the directory
containing `main.cpp` and `scores.tsv`, use:

```sh
c++ -std=c++20 -Wall -Wextra -Wpedantic -Wconversion -Wsign-conversion -Werror -g -O0 main.cpp -o project
./project
```

The included Makefile also supports `make main` and `./main`. Its `main-debug`
target enables AddressSanitizer and UndefinedBehaviorSanitizer. Retain the actual
compiler version, commands, outputs and exit statuses. A sanitizer result covers
the executed cases; it does not prove every input or resource lifetime correct.

## Input and report contract

`./project` reads `scores.tsv` and publishes `report.tsv` in its working directory.
`./project INPUT OUTPUT` chooses different paths. Other argument counts print
usage and return 2. Successful processing returns 0; unfinished tasks, invalid
records and resource failures return 1 with a diagnostic.

The first input line is exactly `CPPI4_SCORES_V1`. Every following physical line
contains exactly two fields separated by one tab: a name and a score.

Names contain 1 through 40 printable ASCII bytes and at least one non-space
byte. Tabs, carriage returns and other control bytes are invalid inside a name.
Preserve accepted leading and trailing spaces. Duplicate names are allowed and
stay in their original order. A score contains only ASCII decimal digits and
has a value from 0 through 100. Leading zeroes are accepted; signs, fractions,
spaces, trailing text and integer overflow are rejected.

Accept LF and CRLF line endings and a final line without a newline. Reject a
missing or incorrect header, blank record lines, extra columns and embedded NUL
bytes. Accept zero through 100 records. Enforce a physical-line limit of 128
bytes before removing the CR from CRLF, and a total-file limit of 16,384 bytes
including line endings. Use the supplied bounded reader before storing an
unbounded line or file.

The supplied fictional sample has Ada with score 84 and Lin with score 59. Its
report is:

```text
CPPI4_REPORT_V1
Ada\t84\tpass
Lin\t59\treview
TOTAL\t2\t143
```

Here `\t` denotes one actual tab. End every report line with a newline. Scores
at least 60 receive `pass`; lower scores receive `review`. Preserve accepted
name spaces and record order. The footer gives the integer record count and
score total. Header-only input produces the report header and a `TOTAL` row
with count and total zero. Do not substitute a floating-point average.

## Four tasks

1. `parseScoreRow`: split exactly two fields, validate both completely and
   return one `Record`. Predict empty, signed, boundary and trailing-text scores
   before implementing the function.
2. `readScores`: open the input, check its header and use the bounded reader to
   validate every row. Enforce the record limit before accepting another row.
   Observe read and close failures. Return a vector only after the entire input
   is accepted, including any late record.
3. `writeReport`: validate the in-memory records before emitting anything, then
   render the deterministic rows and integer footer. Check the output stream.
   Rendering a report is separate from publishing the output file.
4. `processFile`: validate the paths and finish reading before acquiring output
   staging. Write the temporary report, explicitly flush, close and check the
   stream, then rename only after the report is complete. Let the supplied
   guard clean up its owned temporary work on early return or unwinding.

Keep the supplied signatures, driver and file interface. For each task, write
its precondition, successful result and failed-case result; predict one changed
case, implement it and retain the actual observation. An instructor can pause
at those same predictions. Compare with staff reference material only after
saving and testing a learner attempt.

## Owners and publication boundary

The input stream owns its file handle. The vector owns its record values. The
noncopyable `StagingDirectory` guard exclusively acquires `OUTPUT.stage` beside
the output and owns only the directory it created. The output stream owns the
temporary report handle. The reference returned by `temporaryFile()` borrows
the guard's path and cannot outlive it.

If `OUTPUT.stage` already exists as a file, directory or dangling symlink,
report the collision and leave it intact. Write `report.tmp` inside the newly
acquired directory. Reject equal input/output paths, hard-link aliases and an
existing output that is not a regular file, including a symlink.

The successful rename is the publication boundary. A failed parse, read,
staging acquisition, write, flush, close or rename preserves previous output
bytes. The guard attempts nonthrowing cleanup of its own temporary file and
empty directory on exit. Operating-system refusal can prevent cleanup. A
failed success message after rename leaves the new report committed and returns
1 with that distinction in the diagnostic.

This contract assumes ordinary files on a local macOS/Linux filesystem and one
writer per output. It does not promise recovery after a crash, durable writes
during power loss, protection from concurrent path changes or identical
replacement semantics on every operating system.

## Evidence and completion

Save the old report bytes before each failed-case test. Run the sample, an empty
valid input, scores 59 and 60, changed records, duplicate names and names with
accepted spaces. Check the exact report, both output streams and exit code.
Then try a missing input, malformed late row, excessive rows, invalid name or
score, missing output parent and existing staging collision. Keep collision
paths intact and inspect whether the old report survived.

Record predictions for controlled partial-write and rename failures, plus a
failed acknowledgment after publication. The native acceptance checks exercise
those faults directly; an ordinary successful print does not establish them.
Do not create an unsafe race or deliberately exhaust the machine to simulate
a failure.

Finish with the saved completed attempt, input/report evidence, an owner/observer
diagram, the first prediction mismatch and its cause, and one guarantee outside
this program's contract. The optional Ownership Rewrite Reflection continues
this saved project through notes and a short separate comparison. It is not a
second required file-processing application.
