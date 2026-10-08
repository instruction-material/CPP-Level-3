# Ownership Rewrite Reflection: Worked Reference

Staff comparison follows the learner attempt. The complete published Level 2
program is supplied as `ownership-reference.cpp`, byte-identical to the source
reviewed for this worksheet. It includes the raw-array, vector and unique-array
demonstrations rather than synthetic checklist counts.

The manual allocation makes `scores` responsible for `delete[]` in both its
normal path and its catch path. `printScores` only observes the array. If
`new[]` throws, the assignment never completes, so no returned allocation exists
for that function to release. If output throws after allocation, the catch
deletes the array before propagating the exception. The catch and normal cleanup
are mutually exclusive. This example is correct but requires duplicated cleanup
paths and careful maintenance when another exit is introduced.

The vector version owns its storage through the vector object. The unique array
version owns through `unique_ptr<int[]>` and lends `get()` to `printScores`.
Their destructors release owned storage on both return and stack unwinding. A
borrowed pointer is not a separate owner. Moving a unique owner transfers its
resource; copying it is rejected. A vector copy owns a distinct allocation and
does not transfer the original vector's storage.

Normal value lines are `Manual array: 84 91 76 88 `,
`Vector: 84 91 76 88 ` and `unique_ptr array: 84 91 76 88 `, each followed by
a newline. Preserve the reference's explanatory lines and blank lines when
checking the complete program. A changed example with scores 0, 60, 100 and 59
retains that order in each representation. The sum is not an output of this
comparison program and cannot substitute for its actual printed values.

For the file processor, malformed input fails before the staging guard is
acquired. The input handle and record vector release normally or during
unwinding; the prior report is unchanged. A partial temporary write or failed
rename leaves the prior output unchanged, closes the stream, and removes only
owned temporary artifacts where the operating system permits removal. An
existing staging directory is never adopted as owned or recursively erased.

After successful rename, the new report is already published. Failed stdout
acknowledgment returns a diagnostic failure but does not roll back that report.
Distinguish storage ownership, checked file I/O, publication and acknowledgment.
The one-process local-filesystem contract does not imply database transactions,
power-loss durability or cross-platform replacement guarantees.

## Verify the comparison

Compile the exact manual and complete reference programs under strict warnings.
Check normal and changed output before comparing cleanup on exceptional paths.
`verify-ownership-worksheet.py` uses a controlled output stream that throws after
partially writing each representation, and checks ordinary and sanitizer builds
in C++17 and C++20. Worksheet printers must reproduce the complete learner and
worked documents exactly. A passing executed case remains evidence for that
case rather than a guarantee for every possible lifetime.
