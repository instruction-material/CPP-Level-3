#include <iostream>

int main(const int argc, char*[]) {
    if (argc != 1) { std::cerr << "Usage: main\n"; return 2; }
    std::cout << R"OWNERSHIP_MD(# Ownership Rewrite Reflection

This optional worksheet continues the completed Resource-Safe File Processor.
Keep its saved IDE attempt and report files. Reading this worksheet imports no
second application. Make a separate scratch file for the short comparison below;
do not overwrite the completed file processor to run a teaching experiment.

## Read and trace one concrete manual owner

The supplied `manual-ownership.cpp` retains `printScores` and `manualArrayDemo`
exactly from the verified Level 2 ownership comparison. The wrapper runs only
the manual example, keeping the rewrite separate from the initial reading.
Its fictional scores are 84, 91, 76 and 88. Native compilation requires C++17
or C++20 on macOS or Linux, after downloading and extracting the file.

```sh
c++ -std=c++20 -Wall -Wextra -Wpedantic -Wconversion -Wsign-conversion -Werror manual-ownership.cpp -o ownership
./ownership
```

The visible output text is:

```text
Manual array: 84 91 76 88
Manual responsibility: delete[] must run exactly once.
```

The actual program prints one space after 88 before the newline. A correct normal output alone
does not establish correct cleanup on a throwing path.

Read the complete supplied program, then draw three snapshots: before `new[]`,
while `printScores` reads the array, and after cleanup. Label the variable that
is responsible for `delete[]`, the array allocation, and the borrowed pointer
parameter. `printScores` observes the values; it neither takes ownership nor
deletes them. Its pointer and length remain valid only while their owner lives.

## Attempt a rewrite before comparing

1. In a separate `ownership-attempt.cpp`, replace the manual allocation with
   either `std::vector<int>` or `std::unique_ptr<int[]>`. Keep all four scores
   and their display order. Explain which line acquires storage and which
   object's destruction releases it.
2. Keep the printing function as a borrowed view. For vector storage, use
   `data()` and `size()`; for unique array ownership, use `get()` and a separate
   length. Remove every manual `delete[]` for the automatically owned storage.
3. Write predictions for normal return, allocation failure before ownership is
   acquired, and an exception after acquisition. Explain why the cleanup
   obligation must be fulfilled in both normal and exceptional exits.
4. Change the scores and add one record in the vector version. Compare exact
   output with a handwritten prediction. In the fixed array version, change
   the allocation, initializer and supplied length consistently. Never read
   past the allocation merely to test a failure case.

`unique_ptr<int[]>` uses the array form of destruction. A plain `unique_ptr<int>`
does not own an array allocated by `new int[n]`. Copying a unique owner is
forbidden; moving it transfers ownership and leaves the source without the
allocation. A raw pointer obtained with `get()` still observes the same
allocation and is not a second owner. Do not delete it or keep using it after
the owning object releases the allocation.

Compile the rewrite under the same strict warnings. On a supported native
compiler, also run AddressSanitizer and UndefinedBehaviorSanitizer:

```sh
c++ -std=c++20 -Wall -Wextra -Wpedantic -Wconversion -Wsign-conversion -Werror -g -O0 -fsanitize=address,undefined -fno-sanitize-recover=all ownership-attempt.cpp -o ownership-sanitized
./ownership-sanitized
```

A silent sanitizer run covers the executed cases, not every possible lifetime
or exceptional path. Normal `std::cout` failures normally set stream state;
throwing output requires a deliberately configured stream or a controlled test
stream. Do not report an exception-cleanup test from an ordinary print alone.

## Connect ownership to the saved file processor

Write answers in a separate `ownership-notes.md`, or in a new notes file in the
existing saved attempt. Leave `main.cpp`, `scores.tsv` and the accepted report
unchanged while answering.

| Resource or observation | Owner and lifetime to identify | Application duty that remains |
| --- | --- | --- |
| Input file handle | The local `ifstream`, from successful open through function exit | Detect open/read failure and enforce input limits |
| Parsed records | The local vector, through processing | Validate fields, order and record count |
| Temporary report handle | The local `ofstream`, through explicit close | Check writing, flushing and closing before publication |
| Acquired staging directory | The noncopyable staging guard, only after successful acquisition | Remove only owned temporary paths; preserve a pre-existing collision |
| Borrowed record reference | The enclosing vector owns its storage | Avoid retaining references across invalidating changes |
| Published report | The output file persists after the processing scope | Define rename as the publication boundary and report later acknowledgment failure accurately |

For malformed input, a partial temporary write, failed publication, and failed
success output after publication, record: which owners exist, which destructors
run, whether the previous report is preserved, and whether a new report is
already committed. Automatic destruction cannot choose a validation rule, check
a stream error that was ignored, or undo an already successful publication.

Finish with one owner/observer diagram, both output predictions, the changed
input results, and the four failure-path explanations. In a paired walkthrough,
one reader predicts the state and the other follows the actual scope and
cleanup path; swap roles before the changed case. Consult the separate worked
reference after recording the attempt.
)OWNERSHIP_MD";
    std::cout.flush();
    return std::cout ? 0 : 1;
}
