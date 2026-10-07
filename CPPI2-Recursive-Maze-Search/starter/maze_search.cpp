#include "maze.h"

#include <stdexcept>

namespace mazecourse {
namespace {
[[maybe_unused]] std::string event(const char* label, Cell cell) {
    return std::string(label) + " " + std::to_string(cell.row) + " " + std::to_string(cell.column);
}

bool visit(const Maze& maze, Cell cell, std::vector<std::vector<bool>>& visited, SearchResult& result) {
    static_cast<void>(maze);
    static_cast<void>(cell);
    static_cast<void>(visited);
    static_cast<void>(result);
    // TODO: Implement base cases, ordered recursion and failed-path backtracking.
    throw std::logic_error("UNFINISHED: implement recursive search.");
}

} // namespace

SearchResult solveMaze(const Maze& maze) {
    std::string error;
    if (!validateMaze(maze, error)) throw std::invalid_argument(error);
    std::vector<std::vector<bool>> visited(maze.rows.size(), std::vector<bool>(maze.rows.front().size(), false));
    SearchResult result;
    result.found = visit(maze, maze.start, visited, result);
    return result;
}
} // namespace mazecourse
