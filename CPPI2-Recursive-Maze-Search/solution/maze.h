#ifndef CLASSES_RECURSIVE_MAZE_H
#define CLASSES_RECURSIVE_MAZE_H

#include <cstddef>
#include <iosfwd>
#include <string>
#include <vector>

namespace mazecourse {
constexpr int maximumDimension = 20;
constexpr std::size_t maximumInputBytes = 16384;

struct Cell {
    int row{};
    int column{};
    bool operator==(const Cell&) const = default;
};

struct Maze {
    std::vector<std::string> rows;
    Cell start;
    Cell exit;
    bool operator==(const Maze&) const = default;
};

struct SearchResult {
    bool found{};
    std::vector<Cell> path;
    std::vector<Cell> entered;
    std::vector<std::string> trace;
    bool operator==(const SearchResult&) const = default;
};

// On failure, preserve output. Success clears error.
bool readMaze(std::istream& input, Maze& output, std::string& error);
bool validateMaze(const Maze& maze, std::string& error);

// Input is borrowed without mutation. Every call has its own search state.
SearchResult solveMaze(const Maze& maze);
} // namespace mazecourse
#endif
