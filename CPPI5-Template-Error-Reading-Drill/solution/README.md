# Template Error Reading Drill

This optional worksheet practices reading a real compiler diagnostic. It has a
separate three-file practice pack (`main.cpp`, `Makefile`, `README.md`). Save the
completed Fraction Toolkit before opening or exporting the drill. Keep the
primary attempt and its project identity; the drill does not replace it.

## Establish the working baseline

Build the ordinary learner with `make CXX=c++ main` and run `./main`. Its actual
supported calls use integers and strings, and produce:

```text
number 3
text apple
```

The ordinary worked copy produces the same output. Wrong argument count returns
2 with `Usage: main` on stderr and no stdout. A failed final stdout flush returns
1. The ordinary program is already working; completing this drill means
triggering, interpreting and fixing the deliberately enabled case.

## Predict and enable the controlled failure

Read `chooseSmaller<T>`: it takes and returns values and evaluates `right < left`.
Its requirements include copying and an ordering operation. The learner `Score`
contains an integer but supplies no comparison. Predict the failed operation
before compiling:

```bash
make CXX=c++ diagnostic
```

The `CPPI5_TRIGGER_TEMPLATE_ERROR` macro enables a call with `Score{84}` and
`Score{59}`. The learner must fail compilation because `<` cannot compare two
Scores. Ordinary `main` remains a separate executable. A compiler diagnostic is
not a runtime exception and `try`/`catch` cannot repair an ill-formed program.

## Read the actual trace

Record the compiler and version, failed build exit status, first relevant error,
expression inside the template, and call that instantiated it. Locate
`chooseSmaller<Score>`, the two Score operands and the missing `<` operation.
Follow the instantiation notes back to the call. GCC and Clang wording and note
order differ, so identify the relationship rather than copying a promised exact
message or reading only the last error. Fix one cause, then compile again before
interpreting follow-on diagnostics.

## Make one narrow correction

Keep `chooseSmaller` unchanged. Add this conventional comparison inside `Score`:

```cpp
friend bool operator<(const Score& left, const Score& right) {
    return left.value < right.value;
}
```

Explain why the function borrows const operands and compares the same property
for every pair. Rebuild the same enabled case with `make CXX=c++ diagnostic`,
then run `./main-diagnostic`. The completed/worked enabled output is `score 59`
followed by a newline, with status 0. The operator adds a missing requirement;
it does not change template syntax to conceal the type mismatch.

## Check fresh evidence

| Probe | Prediction to record |
| --- | --- |
| scores `0` and `100` | smaller value 0 |
| scores `91` and `76` | smaller value 76 |
| scores `84` and `84` | equal values; the helper selects its left argument |
| ordinary build after the correction | the original number/string output is unchanged |

Change only the two Score initializers in a separate copy, then compare actual
stdout, stderr and status with the prediction. Integer Score labels here are
comparison practice, not a validated grading model. Do not introduce a global
comparison that mixes unrelated meanings or ordering by changing metadata.
The value/template lesson provides a tagged tie example so the left choice is
observable even when numeric values are equal.

## Review the decision

Record the original error, its instantiation path, the narrow fix, unchanged
ordinary output and at least two changed enabled cases. Explain why a raw
integer field did not automatically give Score an ordering, why a compile error
is different from a thrown exception, and when a named comparator is clearer
than giving the type one global ordering. In a walkthrough, pause before each
build for a prediction. For independent study, write the prediction first and
use the separate worked record after collecting the evidence.

The source repository retains `template_drill_starter` and
`template_drill_solution` CMake targets for ordinary supported calls. The enabled
case is deliberate opt-in. Run `python3 verify-template-drill.py` on the hosted
Linux toolchain to inspect real GCC/Clang failures, test the ordinary baseline,
and run fixed/changed completed and worked cases. The gate does not grade an
unseen learner explanation.

# Worked template diagnostic record

The ordinary source builds and prints `number 3` and `text apple`. Enabling the
learner's Score call fails during template instantiation: `chooseSmaller<Score>`
evaluates `right < left` but Score has no applicable comparison. Trace the error
at that expression to the enabled call; exact GCC/Clang wording is toolchain
specific. Read the real retained diagnostic from the acceptance run.

The solution adds only a friend `<` comparison borrowing two const Scores and
comparing their integer values. `chooseSmaller` and the existing driver are
unchanged. Its enabled actual result is `score 59`; changed pairs `(0,100)`,
`(91,76)` and `(84,84)` produce `score 0`, `score 76` and `score 84`. Ordinary output
is unchanged. The native gate verifies these bytes against independently chosen
values and distinguishes an actual failed compilation from a runtime failure.

The correction makes this exercise's numeric ordering meaningful. A real type
with multiple ordering interpretations might instead use an explicit comparator.
Equal numeric Scores cannot expose which otherwise identical object was chosen;
the tagged-value lesson shows that the helper keeps the left value on a tie.
Compare a learner record's source, build command, diagnostics and changed output
with this worked reasoning. A fixed checklist alone is not evidence.
