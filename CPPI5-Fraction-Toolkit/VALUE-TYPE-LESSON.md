# Value Types, Invariants and Conventional Operators

By the end of this lesson, distinguish an independent value copy from an alias,
enforce a constructor invariant, make read-only operations const, and explain an
operator in terms of an already meaningful named operation. Review classes,
constructors, const references and exceptions from the earlier modules first.

## A type promises a valid value

An invariant is a condition every successfully constructed object maintains.
The Score below represents an integer from 0 through 100. Its private member
prevents direct arbitrary changes. The constructor checks the condition and
throws on invalid input; a throwing constructor creates no complete Score.
`value()` only reads and is const. Copy construction and assignment copy the
integer, so changing a copy does not change the original.

`raisedBy` returns a new checked Score. It checks delta before addition: value is
0..100 and delta is -100..100, so their sum lies within -100..200 and cannot
overflow an int. The resulting constructor enforces the narrower Score range.
`operator+` delegates to that same operation. It does not mutate either input,
print messages or give addition an unrelated meaning.

## Predict, build and inspect a complete example

Save this entire program as `value-lesson.cpp`. Predict all six output lines,
then build with `c++ -std=c++20 -Wall -Wextra -Wpedantic -Wconversion
-Wsign-conversion -Werror value-lesson.cpp -o value-lesson` and run
`./value-lesson`. The command is one line. Export and extract source from the site
IDE before using a native compiler.

```cpp
#include <iostream>
#include <stdexcept>

class Score {
    int value_;
public:
    explicit Score(int value = 0) : value_(value) {
        if (value < 0 || value > 100)
            throw std::out_of_range("Score outside 0 through 100.");
    }
    int value() const { return value_; }
    Score raisedBy(int delta) const {
        if (delta < -100 || delta > 100)
            throw std::out_of_range("Delta outside -100 through 100.");
        return Score(value_ + delta);
    }
    friend bool operator<(const Score& left, const Score& right) {
        return left.value_ < right.value_;
    }
    friend Score operator+(const Score& left, int delta) {
        return left.raisedBy(delta);
    }
};

int main(int argc, char*[]) {
    if (argc != 1) {
        std::cerr << "Usage: value-lesson\n";
        return 2;
    }
    try {
        const Score original(84);
        Score copy = original;
        copy = copy.raisedBy(7);
        const Score viaOperator = original + 7;
        std::cout << "original " << original.value()
                  << "\ncopy " << copy.value()
                  << "\noperator " << viaOperator.value()
                  << "\nless " << std::boolalpha << (original < copy) << '\n';
        const int before = copy.value();
        bool rejected = false;
        try {
            copy = copy.raisedBy(100);
        } catch (const std::out_of_range&) {
            rejected = true;
        }
        std::cout << "rejected " << rejected
                  << "\npreserved " << (copy.value() == before) << '\n';
        std::cout.flush();
        if (!std::cout) throw std::runtime_error("Could not write the result.");
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "Rejected: " << error.what() << '\n';
        return 1;
    }
}
```

Expected output, with one newline after each line:

```text
original 84
copy 91
operator 91
less true
rejected true
preserved true
```

The const original remains 84 while the independent copy becomes 91. Both the
named method and `+` produce the same new value. `copy.raisedBy(100)` throws while
evaluating the right side, so assignment never takes place and the copy remains
91. This shows preservation for this operation; it does not establish rollback
for arbitrary side effects, I/O or every class operation. The demonstrated
rejection is caught as part of the lesson and the program exits 0. Extra arguments
produce a usage diagnostic and exit 2. Unexpected exceptions or failed final
stdout flush return 1; already emitted output bytes cannot be rolled back.

## From Score to Fraction

The core Fraction Toolkit uses two private components. Normalize sign, reduce by
gcd and represent zero as 0/1 so equality compares one canonical representation.
The raw constructor and the result normalizer have different bounds: a bounded
arithmetic intermediate may be larger than a raw component and reduce to a valid
final value. Establish named `add`, `multiply` and `lessThan` behavior first,
then let `+`, `*` and `<` delegate. Do not silently convert to floating point for
exact comparison or round an out-of-range result into acceptance.

`==` asks whether normalized values are equal. `<` gives one consistent ordering.
It must be irreflexive, asymmetric and transitive, with transitive equivalence
for incomparable equal values; sorting relies on that strict weak ordering.
Test negative, zero and equivalent fractions and explain the law, rather than
using one sorted list as a proof. Const references avoid operand copies while
preventing mutation through these parameters; const is not a blanket guarantee
that a function has no observable side effects.

## Guided checks and independent study

1. Change original 84 to 59 and both increments 7 to 1. Predict 59, 60 and 60,
   followed by the same three true values. Explain why the rejected assignment
   still preserves the copy.
2. Change both increments to zero. Predict a tied comparison and explain why
   `original < copy` becomes false while the values remain valid.
3. In a separate copy, try original -1 or 101. Record stdout, stderr and status.
   Explain why there is no valid original object to copy after that construction.
4. Explain why a const original can be read and used as an operand but cannot be
   reassigned. Try an assignment in a separate practice copy and read the actual
   compiler diagnostic; restore the working program afterward.
5. Design one Fraction input with a negative denominator, one equivalent pair
   and one individually valid operation that reduces a wide intermediate.
   Distinguish a value-law probe from the complete command's later operations.

In a walkthrough, pause before each run for a prediction and identify the line
that enforces the invariant or preserves the value. For independent study, write
the prediction and explanation before comparing with actual output. This lesson
leads into template requirements; it is teaching material, not another required
application or a fixed grading checklist.
