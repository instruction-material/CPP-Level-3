#include "maze.h"

#include <exception>
#include <iostream>
#include <string>
#include <string_view>

namespace {
constexpr const char* usage =
    "Usage: maze-search [--trace]\n"
    "       maze-search --help\n"
    "Read ROWS COLS, then ROWS grid lines from standard input.\n"
    "Use S (start), E (exit), . (open) and # (wall).\n"
    "Dimensions are 1..20; coordinates are zero-based.\n";
}

int main(int argc, char* argv[]) {
    bool trace = false;
    if (argc == 2 && std::string_view(argv[1]) == "--help") {
        std::cout << usage;
        return 0;
    }
    if (argc == 2 && std::string_view(argv[1]) == "--trace") trace = true;
    else if (argc != 1) {
        std::cerr << "Error: Unknown or extra argument.\n" << usage;
        return 2;
    }
    mazecourse::Maze maze;
    std::string error;
    if (!mazecourse::readMaze(std::cin, maze, error)) {
        std::cerr << "Error: " << error << '\n';
        return 2;
    }
    try {
        const auto result = mazecourse::solveMaze(maze);
        if (trace) {
            for (const auto& event : result.trace) std::cout << event << '\n';
        }
        if (!result.found) std::cout << "No path\n";
        else {
            std::cout << "Path " << result.path.size() << '\n';
            for (const auto cell : result.path) {
                std::cout << cell.row << ' ' << cell.column << '\n';
            }
        }
        return 0;
    } catch (const std::exception& exception) {
        std::cerr << "Error: " << exception.what() << '\n';
        return 3;
    }
}
