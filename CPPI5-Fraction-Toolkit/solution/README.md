# Fraction Toolkit

Build a small copyable value type whose construction, comparison and arithmetic
have predictable meanings. This core project connects class invariants to const
operations, conventional operators, standard sorting and a reusable template.
The optional template diagnostic drill is separate practice.

Read [value types and operators](https://github.com/instruction-material/CPP-Level-3/blob/main/CPPI5-Fraction-Toolkit/VALUE-TYPE-LESSON.md) and
[template requirements and diagnostics](https://github.com/instruction-material/CPP-Level-3/blob/main/CPPI5-Fraction-Toolkit/TEMPLATE-LESSON.md) first. In an
extracted standalone pack, these teaching documents are available in the parent
project on GitHub. The source and this complete brief travel with the pack.

## Data and behavior

A Fraction stores signed 64-bit numerator and denominator components. Successful
construction always produces a positive denominator, gcd-reduced components,
and zero as `0/1`. A zero denominator is rejected. Raw input magnitudes and final
normalized component magnitudes are at most 1,000,000; normalized denominators
are at least one. These bounds are part of this exercise, not an arbitrary-size
fraction library. Construction that throws produces no Fraction object.

`lessThan`, `add` and `multiply` are const operations. Compare exactly using cross
multiplication. Addition and multiplication return new normalized values without
changing either operand. The conventional `==`, `<`, `+`, `*` and output operators
reuse this value behavior. Named operations establish the meaning before the
operators provide shorter notation. Copying a Fraction copies its value.

Multiplication and comparison intermediates have magnitude at most 10^12; the
sum numerator has magnitude at most 2 x 10^12. Signed 64-bit arithmetic represents
these bounds. The supplied normalization helper checks its intermediate bounds
before sign changes and gcd calculation, reduces first and then checks the final
component bounds. Do not apply the raw 1,000,000 constructor bound to an
unreduced arithmetic intermediate. Reject a final result that exceeds the bound.

`chooseSmaller<T>` takes two values and returns a value. It requires copyable
values with a meaningful strict ordering under `<`; equal values retain the left
argument. It is an instructional helper. Prefer standard helpers such as
`std::min` in ordinary application code, and understand their reference/lifetime
contracts rather than treating every helper as interchangeable.

## Command and output contract

Run `./main` for `1/2` and `2/3`, or pass exactly two fraction tokens:
`./main -1/2 2/3`. Each token contains signed decimal digits, one slash and signed
decimal digits. A minus sign and leading zeroes are accepted. Plus signs,
whitespace, decimal points, exponent syntax, missing parts, extra slashes,
trailing characters and a zero denominator are rejected. There is no interactive
input or saved file in this project.

All parsing and arithmetic finish before any result is written. The default
completed/reference output is exactly:

```text
LEFT 1/2
RIGHT 2/3
LESS true
SUM 7/6
PRODUCT 1/3
SMALLER 1/2
SORTED 0/1 1/2 2/3
```

Each line ends with a newline. `SORTED` contains the two original fractions and
zero, ordered by value. Success returns 0 with no diagnostic. Invalid values or
out-of-range results return 1, write a `Rejected:` diagnostic to stderr and emit
no result output. Wrong argument count returns 2, writes
`Usage: main [LEFT_FRACTION RIGHT_FRACTION]` to stderr and emits no result output.
The program checks the final stdout flush. An output-device failure can follow
partial output bytes; this check cannot roll back bytes already written.

| Case | Expected behavior |
| --- | --- |
| `-1/-2 2/-3` | left `1/2`, right `-2/3`, sum `-1/6`, product `-1/3` |
| `0/-4 0003/0009` | zero `0/1`, right `1/3`, product `0/1` |
| `999999/1000000 1/1000000` | sum reduces to `1/1`; the product is rejected because its final denominator exceeds the bound |
| `1000000/1 -1000000/1` | sum is zero; product is rejected because its final numerator exceeds the bound |
| `1/0 1/2` | denominator rejection, no result output, status 1 |
| `1/2` | usage diagnostic, no result output, status 2 |

An operation can be individually representable while the complete command is
rejected by a later required operation. Use direct value probes to test that
addition reduces its wide intermediate before enforcing the final bound.

## Work sequence

1. Build and run the untouched learner. It deliberately returns 1 with
   `Unfinished task: constructFraction.` and no result output. A successful build
   is not a completed project.
2. Complete only the five `TODO BEGIN` / `TODO END` bodies: `constructFraction`,
   `compareFraction`, `addFraction`, `multiplyFraction` and `chooseSmaller`.
   Preserve the public driver, parser, output format and supplied invariant
   helper. The other unfinished bodies throw until they are implemented.
3. Establish constructor normalization and rejection first. Predict zero,
   negative-denominator and unreduced cases before running them.
4. Implement exact const comparison, then nonmutating addition and multiplication.
   Check both operands after successful and rejected operations. Explain the
   bounds that make cross multiplication and addition safe.
5. Implement the value-returning template and compare integers, strings and
   Fractions. Check a tied tagged value to explain the left-on-tie policy.
6. Run the default and changed commands, then check invalid input and a rejected
   arithmetic result. Record stdout, stderr and exit status separately.

## Build and verification

A supported C++20 compiler and Make are required for these standalone commands.
The site IDE edits and exports source; extract its ZIP before native compilation.
Run from the pack directory:

```bash
make CXX=c++ main
./main
./main -1/2 2/3
make CXX=c++ main-debug
./main-debug -1/-2 2/-3
make clean
```

`main-debug` enables AddressSanitizer and UndefinedBehaviorSanitizer. Strict
warnings include conversion checks and are errors. On Linux the sanitizer build
also disables PIE for repeatable startup. Sanitizers check executed paths; they
do not prove a type contract or ordering law. C++17 compatibility is separately
checked by the acceptance gate; the course's documented build path is C++20.

The source repository retains `fraction_toolkit_starter` and
`fraction_toolkit_solution` CMake target names. From the repository root:

```bash
cmake -S . -B build -DCMAKE_CXX_COMPILER=c++
cmake --build build --target fraction_toolkit_starter fraction_toolkit_solution
./build/fraction_toolkit_solution
python3 verify-fraction-toolkit.py
```

The verifier compiles untouched, completed and reference programs, compares
fixed and generated inputs with Python's independent exact Fraction model, and
runs copy/const, operand-preservation and ordering-law probes in ordinary and
sanitizer builds. Full repository acceptance also checks the teaching programs,
standalone packs and preserved CMake targets on hosted Linux workers.

## Completion and walkthrough evidence

Keep the saved primary IDE project and export its complete files. Record the
compiler/version, exact build command, default and two changed successful cases,
one zero-denominator rejection, one final-result bound rejection, and each exit
status. Include a direct copy/const probe, a nonmutation check after failure and
one ordering-law explanation. In a walkthrough, predict the output and invariant
before each run, then connect the observed result to the relevant operation. For
independent study, answer the same questions in writing before checking the
reference. Worked source is for comparison after recording reasoning; its
presence does not validate a learner attempt.
