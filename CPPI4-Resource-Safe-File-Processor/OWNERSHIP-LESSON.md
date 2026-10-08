# RAII and Single-Owner Resource Design

Private lesson candidate. The examples and changed cases still require native
acceptance before catalog integration.

**Concept focus:** Name the object responsible for each resource and the scope
that ends that responsibility. Continue the container ownership work from
CPPI3 before writing a custom resource guard.

RAII means Resource Acquisition Is Initialization. A resource can be heap
storage, a file handle, a lock or an exclusively acquired temporary directory.
An owning object couples its lifetime to the cleanup responsibility. Its
destructor runs at ordinary scope exit and when a propagated exception
unwinds that scope. A successfully constructed owner can therefore clean up
without a separate cleanup call on every return path. If construction itself
fails, the incomplete object's destructor does not run; already constructed
members and bases are destroyed. Arrange acquisition so every acquired resource
already has a complete owner before later work can fail.

Start with existing owners. A vector owns its element storage. An input stream
owns its open file handle. A unique pointer expresses one owner for dynamically
allocated objects when a container or direct value is unsuitable. Ordinary
course programs do not call an owner's destructor explicitly.

An observer accesses a resource without owning its lifetime. In the following
complete program, the raw pointer returned by `get()` is an observer. Copying
that pointer does not create an owner, and deleting through it would conflict
with the unique pointer's cleanup. Save this as `ownership.cpp` in a separate
practice folder so the file processor's saved attempt remains intact.

```cpp
#include <cstddef>
#include <iostream>
#include <memory>
#include <utility>
#include <vector>

void printScores(const int* values, const std::size_t count) {
    for (std::size_t index = 0; index < count; ++index) {
        if (index != 0) std::cout << ' ';
        std::cout << values[index];
    }
    std::cout << '\n';
}

int main() {
    auto first = std::make_unique<int[]>(3);
    first[0] = 84;
    first[1] = 91;
    first[2] = 76;
    const int* observer = first.get();
    printScores(observer, 3);

    auto second = std::move(first);
    std::cout << std::boolalpha << "first empty: " << !first << '\n';
    printScores(observer, 3);

    const std::vector<int> scores{84, 91, 76};
    printScores(scores.data(), scores.size());
    // second still owns the array while observer is used above.
}
```

Before compiling, predict the four output lines and draw both ownership states:

```text
Before move: first  --owns--> array <--observes-- observer
After move:  second --owns--> array <--observes-- observer
             first owns nothing
```

Compile and run with a native C++20 compiler:

```sh
c++ -std=c++20 -Wall -Wextra -Wpedantic -Wconversion -Wsign-conversion -Werror ownership.cpp -o ownership
./ownership
```

The expected output is:

```text
84 91 76
first empty: true
84 91 76
84 91 76
```

Moving this unique pointer transfers ownership; it does not relocate the array.
The observer still refers to that array while `second` owns it. Destroying or
resetting `second` ends that lifetime. Remove all subsequent observer accesses
before trying a reset. Do not execute a dangling-pointer example. Attempting
`auto second = first;` instead of the move is a separate compile-error exercise:
unique pointers disable copying. Keep the first useful diagnostic and then
restore the valid program.

The array form `unique_ptr<int[]>` uses array cleanup and supports indexing.
It does not remember the array length for bounds checks. A vector is the simpler
choice for a growing list, and `.at()` can check an index. Do not wrap an array
in `unique_ptr<int>`, create two owners from the same raw pointer or adopt a
pointer to an automatic local variable. Each would violate the cleanup contract.
Avoid `release()` here: it relinquishes ownership without deleting the object
and leaves the caller responsible for arranging a new owner.

Use shared ownership only when independently surviving objects actually need
the same lifetime. `shared_ptr` copies participate in shared ownership;
`weak_ptr` observes that shared lifetime without extending it. Obtain a temporary
shared owner with `lock()` before using such an observation, and handle an
expired result. This file processor has no such requirement, so its resource
guard stays noncopyable and its rows stay in a vector.

Change the three scores, predict the new rows and rerun. Then compare the
supplied Level 2 manual-array example in the optional worksheet. For each
version, name the owner, observer, normal-exit cleanup and failed-output cleanup.
An instructor can pause before the move and ask which object owns the array
now. In independent study, write that answer before continuing.

For the required project, draw the input stream, returned vector, staging guard
and output stream as separate owners. The path reference returned by the guard
is borrowed and cannot outlive it. Automatic cleanup does not decide which
records are valid or whether a report is ready to replace the previous output.
The next lesson defines those application boundaries.

Primary wording references: [unique ownership](https://eel.is/c++draft/unique.ptr.single)
and [exception unwinding](https://eel.is/c++draft/except.ctor).
