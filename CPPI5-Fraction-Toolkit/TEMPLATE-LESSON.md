# Templates, Requirements and Diagnostic Reading

By the end of this lesson, read a small function template as a set of required
operations, predict type deduction, distinguish value-returning behavior from
borrowing, and trace a compiler diagnostic from its failed expression to the
call that instantiated it. Use the preceding value-type lesson as the baseline.

## One algorithm, explicit requirements

`chooseSmaller<T>` receives two copies and returns a value. Its body evaluates
`right < left`; T must support a meaningful ordering and copying. Template
syntax does not automatically provide missing operations. With both arguments
of the same type, the compiler deduces T from the call. A call such as
`chooseSmaller(7, 3.5)` gives conflicting deductions for this signature. Choose
one intended type explicitly or convert deliberately; do not hide a type-design
problem by adding unrelated overloads.

For integer values, smaller means numeric order. For strings it means their
lexicographic ordering, not length. For Reading below, the comparison consistently
uses value and ignores label. Equal numeric Readings are equivalent under that
ordering even when labels differ. The helper returns the left argument on a tie;
its label makes this policy observable.

## Complete program and predictions

Save the following as `template-lesson.cpp`. Build with
`c++ -std=c++20 -Wall -Wextra -Wpedantic -Wconversion -Wsign-conversion -Werror
template-lesson.cpp -o template-lesson` as one command, then run
`./template-lesson`.

```cpp
#include <iostream>
#include <string>

struct Reading {
    int value;
    std::string label;
    friend bool operator<(const Reading& left, const Reading& right) {
        return left.value < right.value;
    }
};

template <typename T>
T chooseSmaller(T left, T right) {
    return right < left ? right : left;
}

int main(int argc, char*[]) {
    if (argc != 1) {
        std::cerr << "Usage: template-lesson\n";
        return 2;
    }
    std::cout << "number " << chooseSmaller(7, 3)
              << "\ntext " << chooseSmaller(std::string("pear"), std::string("apple"))
              << "\nreading " << chooseSmaller(Reading{84, "high"}, Reading{59, "low"}).value
              << "\ntie " << chooseSmaller(Reading{59, "left"}, Reading{59, "right"}).label
              << '\n';
    std::cout.flush();
    if (!std::cout) {
        std::cerr << "Could not write the result.\n";
        return 1;
    }
    return 0;
}
```

Expected output:

```text
number 3
text apple
reading 59
tie left
```

A successful run returns 0. Extra arguments return 2 with `Usage: template-lesson`
on stderr and no stdout. Final output flush failure returns 1; it does not undo
bytes already written. The helper returns a separate value, so it can outlive
its argument objects. That is a different contract from a helper returning a
reference to an argument. Standard `std::min` is useful in application code, but
its usual two-argument overload returns a const reference. Store or copy the
result appropriately and reason about temporary lifetimes.

## Connect requirements to an actual diagnostic

In a separate copy, remove Reading's friend `<` definition. The integer and
string calls still supply the operation, but `chooseSmaller<Reading>` becomes
ill-formed at `right < left`. Find that expression and the instantiating call in
the actual diagnostic. A try/catch around the call cannot repair code that fails
to compile. GCC and Clang can phrase the failure and arrange notes differently.
Read the type and call relationship, then fix the first relevant cause and
recompile before investigating follow-on messages.

The optional Template Error Reading Drill provides the same controlled missing
operation with a Score type and an explicit macro. Its ordinary program remains
working. Save the primary Fraction project and use a separate practice project;
opening the worksheet itself should not replace or import an application.
Record reasoning before consulting the worked correction.

## Guided checks and independent study

1. Change integers `7` and `3` to `-4` and `6`. Predict `-4`. Change strings to `z` and `aa`;
   predict `aa` and explain why shortest length is not the comparison rule.
2. Change the two different Reading values to `0` and `100`. Predict the smaller
   numeric value. Keep labels unrelated to numeric order.
3. Reverse the labels in the tied call. Predict the returned label from the
   left argument, not alphabetical order. Explain the one-comparison choice.
4. Try the mixed numeric call in a separate copy. Record the deduced types and
   decide what common type the application actually intends before fixing it.
5. Compare the helper's copy-returning contract with taking a const reference
   from `std::min`. Explain why a reference to a temporary cannot be retained
   after its lifetime ends. No dangling-reference execution is required.
6. Explain why an inconsistent comparator, or floating values with unordered
   NaNs, can violate the ordering assumptions. This helper does not repair those
   type semantics. Use the project's bounded exact Fraction order instead.

In a walkthrough, predict the type and required expression before each build.
For independent study, write the predicted type, operation and output first.
The primary project applies the helper to normalized Fractions; the optional
worksheet deepens diagnostic reading without adding a second core assignment.
