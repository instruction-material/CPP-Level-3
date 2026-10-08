# Polymorphism, Composition and Runtime Dispatch

By the end of this lesson, distinguish ownership from borrowed access, choose
composition for simulation data, call actual derived behavior through a narrow
interface, and explain virtual destruction and slicing. Review classes,
constructors, references, `unique_ptr` and exception boundaries first.

## A role is different from owned state

One Rover owns its position. A Move or Report acts on a borrowed Rover.
A base Command promises one operation; it does not own another copy of the
simulation. Inheritance represents substitutable command roles here. Composition
stores the simulation's parts. Avoid inheriting Rover from each command, and avoid
building an inheritance tree merely to share fields.

`virtual` selects the actual derived implementation through a base pointer or
reference. `override` asks the compiler to check that a derived declaration really
matches the interface. `Command` is abstract, so a base-value copy cannot silently
slice away its derived part. With a concrete base, copying a derived object into
a base value could lose that part; owning pointers do not copy an object value.
A virtual base destructor is necessary when deleting a derived object through the
base interface. `unique_ptr<Command>` gives one owner, not shared ownership.

## Predict a complete example

Save this whole program as `dispatch-lesson.cpp`. Build and run:

```sh
c++ -std=c++20 -Wall -Wextra -Wpedantic -Wconversion -Wsign-conversion -Werror dispatch-lesson.cpp -o dispatch-lesson
./dispatch-lesson
```

```cpp
#include <iostream>
#include <memory>
#include <stdexcept>
#include <vector>
struct Rover { int position = 0; };
class Command {
public:
    virtual ~Command() = default;
    virtual void execute(Rover& rover) const = 0;
};
class Move final : public Command {
    int amount_;
    int& destroyed_;
public:
    Move(int amount, int& destroyed) : amount_(amount), destroyed_(destroyed) {}
    ~Move() override { ++destroyed_; }
    void execute(Rover& rover) const override {
        if (amount_ < 0 || amount_ > 10 || rover.position > 100 - amount_)
            throw std::out_of_range("Move outside the lesson bounds.");
        rover.position += amount_;
        std::cout << "move " << rover.position << '\n';
    }
};
class Report final : public Command {
    int& destroyed_;
public:
    explicit Report(int& destroyed) : destroyed_(destroyed) {}
    ~Report() override { ++destroyed_; }
    void execute(Rover& rover) const override { std::cout << "read " << rover.position << '\n'; }
};
int main(int argc, char*[]) {
    if (argc != 1) { std::cerr << "Usage: dispatch-lesson\n"; return 2; }
    try {
        Rover rover;
        int destroyed = 0; // Outlives every command that borrows this counter.
        {
            std::vector<std::unique_ptr<Command>> commands;
            commands.push_back(std::make_unique<Move>(1, destroyed));
            commands.push_back(std::make_unique<Report>(destroyed));
            commands.push_back(std::make_unique<Move>(2, destroyed));
            commands.push_back(std::make_unique<Report>(destroyed));
            for (const auto& command : commands) command->execute(rover);
        }
        std::cout << "destroyed " << destroyed << '\n';
        std::cout.flush();
        if (!std::cout) throw std::runtime_error("Could not write result.");
        return 0;
    } catch (const std::exception& failure) {
        std::cerr << "Rejected: " << failure.what() << '\n'; return 1;
    }
}
```

Expected stdout is exactly:

```text
move 1
read 1
move 3
read 3
destroyed 4
```

The same base-pointer call executes both Move and Report behavior. The shared
Rover advances twice; reports read its current position. Four actual derived
objects are destroyed when the vector leaves the inner scope. The counter was
declared earlier and outlives all borrowed references. The final value measures
this actual lifetime, not a fixed message. It is not a thread-safe resource audit.

The example returns 0 on normal completion. Extra arguments return 2 with
`Usage: dispatch-lesson` on stderr and no stdout. Invalid move bounds or a failed
final output flush return 1. Earlier stdout cannot be undone. This small example
is deliberately separate from the capstone's candidate-before-commit driver;
an allocation or output failure after mutation is not a general rollback promise.

## Connect to the capstone

The rover composes graph, position, phase and moves into one Snapshot. Each
actual Command borrows a candidate Rover. An already completed Result and a
no-throw swap establish its expected-rejection boundary. File publication and
external output remain different boundaries. The command's lifetime ends after
execution. A saved snapshot contains data, not vtables or owning pointer addresses.

An `enum class` is sufficient for the four closed phase values. Runtime command
dispatch does not require every phase to be a State object. The separate optional
State Review compares the same transition table and allocation/destruction
behavior; it does not replace the core rover or add a second required capstone.

## Guided checks and independent study

1. Change the two Move amounts from 1/2 to 3/4. Predict positions 3 and 7,
   unchanged Report behavior and the same four actual destructions.
2. Change the first amount to 11 in a separate copy. Predict the checked failure,
   status 1 and no successful move/report output. Restore the valid example.
3. Draw `vector -> unique_ptr -> actual Move/Report` and the borrowed Rover/counter
   arrows. Explain why those borrowed objects outlive every command.
4. Explain why an absent virtual destructor is not repaired by having `override`
   on execute. Keep the correct destructor; no undefined-behavior run is needed.
5. Explain which fields belong to Snapshot, which belong to one command, and
   why saved data cannot be a dumped Command object.

In a walkthrough, pause before each base-pointer call and scope exit. For
independent study, write actual type, resulting position and lifetime prediction
before compiling. Use the supplied full rover brief for the required assignment.
