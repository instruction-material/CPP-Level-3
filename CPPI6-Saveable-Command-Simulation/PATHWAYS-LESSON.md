# Advanced Pathways and Program Framing

By the end of this lesson, frame a bounded program around an observable contract,
connect readiness evidence to actual behavior, and choose the next C++ course
based on its purpose. Review command parsing, validated state, containers,
recursion and runtime roles from the preceding modules.

## Frame one vertical slice

Describe one command's input, validation, mutation, output and failure state.
The rover starts with show, then legal transitions and direct movement. Recursive
route is read-only. Save/load has a separate candidate/publication boundary.
Implementing a medium-size program means organizing these responsibilities,
not producing a larger checklist printer. Name a deferred feature and its reason.

## A complete read-only subsystem

This separate example chooses one DFS route from a small directed graph. It does
not move a rover or save data. Save as `pathway-lesson.cpp` and build/run:

```sh
c++ -std=c++20 -Wall -Wextra -Wpedantic -Wconversion -Wsign-conversion -Werror pathway-lesson.cpp -o pathway-lesson
./pathway-lesson
```

```cpp
#include <iostream>
#include <map>
#include <set>
#include <stdexcept>
#include <string>
#include <vector>
using Graph = std::map<std::string, std::set<std::string>>;
bool visit(const Graph& graph, const std::string& here, const std::string& target,
           std::set<std::string>& entered, std::vector<std::string>& path) {
    if (!entered.insert(here).second) return false;
    path.push_back(here);
    if (here == target) return true;
    for (const auto& next : graph.at(here)) if (visit(graph, next, target, entered, path)) return true;
    path.pop_back(); return false;
}
int main(int argc, char*[]) {
    if (argc != 1) { std::cerr << "Usage: pathway-lesson\n"; return 2; }
    try {
        const Graph graph{{"archive", {"dock"}}, {"dock", {}},
                          {"entry", {"archive", "lab"}}, {"lab", {"dock"}}};
        std::set<std::string> entered;
        std::vector<std::string> path;
        const bool found = visit(graph, "entry", "dock", entered, path);
        std::cout << "found " << std::boolalpha << found << '\n';
        for (std::size_t i = 0; i < path.size(); ++i) {
            if (i) std::cout << " -> ";
            std::cout << path[i];
        }
        std::cout << "\nentered " << entered.size() << '\n';
        std::cout.flush();
        if (!std::cout) throw std::runtime_error("Could not write result.");
        return 0;
    } catch (const std::exception& failure) {
        std::cerr << "Rejected: " << failure.what() << '\n'; return 1;
    }
}
```

Expected stdout:

```text
found true
entry -> archive -> dock
entered 3
```

Ordered neighbors enter archive before lab. The current-target test ends the
successful branch. Failed branches pop their path entry; entered nodes remain
marked to avoid cycling and repeated work. The printed path is simple and
reachable, not a shortest-path guarantee. Inputs here are a fixed valid four-zone
graph. The capstone additionally validates all zones/edges, limits the graph,
rejects an absent target and checks file input before graph traversal.

Normal completion returns 0. Extra arguments produce `Usage: pathway-lesson`
on stderr and status 2. Unexpected lookup/output failures return 1; already
written output cannot be undone.

## Change the graph and predict

Change archive's neighbors from dock to entry. The recursive cycle stops at the
already entered entry; archive is popped, then the lab branch reaches dock.
Predict `entry -> lab -> dock` and four entered zones. Next remove both outgoing
paths to dock. Predict `found false`, an empty path line, and three entered zones.
Restore the original graph before comparing it with the required project's data.
The failed branch leaves no stale path entries for a later query.

## Choose a distinct next purpose

| Course | Main next gap | Example continuation |
| --- | --- | --- |
| Data Structures and Algorithms in C++ | Complexity, performance, trees, graphs and container tradeoffs | Compare DFS reachability with BFS shortest paths and measure graph operations. |
| Design Patterns in C++ | Architectural roles, replaceable behavior, factories, adapters and boundaries | Compare enum phases with actual State objects and reason about ownership costs. |
| C Systems Engineering | Representation, compilation, memory and operating-system interfaces | Study binary records, atomic publication/durability and native resource lifetime. |

These paths overlap in examples but have different learning goals. The bridge
capstone proves readiness for a deliberate next step; it does not replace a full
algorithm, architecture or systems course. A later CS236-inspired project can add
a scanner/parser, command or AST objects, table evaluation and a dependency graph.
Keep that project smaller than a college-scale original and define its scope.

## Completion evidence

Retain a warning-clean C++20 build, accepted/rejected command traces, the complete
phase table, route base/cycle/unreachable cases, real save/restart equivalence,
malformed-file state preservation and an ownership diagram. Explain a failure
using the line that enforces its boundary. A passing regression suite establishes
those tested cases, not correctness for unbounded input or a finished course grade.

In a walkthrough, predict one vertical slice and inspect its actual state/output.
For independent study, write the prediction and limitation before running it.
Choose the next course based on the stated gap and concrete evidence, rather than
adding an advanced title to the same project without changing its purpose.
