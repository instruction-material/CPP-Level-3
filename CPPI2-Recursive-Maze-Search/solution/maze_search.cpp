#include "maze.h"

#include <stdexcept>

namespace mazecourse {
namespace {
[[maybe_unused]] std::string event(const char* label, Cell cell) {
    return std::string(label) + " " + std::to_string(cell.row) + " " + std::to_string(cell.column);
}

bool visit(const Maze& maze, Cell cell, std::vector<std::vector<bool>>& visited, SearchResult& result) {
    const int height = static_cast<int>(maze.rows.size());
    const int width = static_cast<int>(maze.rows.front().size());
    if (cell.row < 0 || cell.row >= height || cell.column < 0 || cell.column >= width) return false;
    const auto row = static_cast<std::size_t>(cell.row);
    const auto column = static_cast<std::size_t>(cell.column);
    if (maze.rows[row][column] == '#' || visited[row][column]) return false;
    visited[row][column] = true;
    result.entered.push_back(cell);
    result.path.push_back(cell);
    result.trace.push_back(event("Enter", cell));
    if (cell == maze.exit) return true;
    // The order is part of this project's deterministic traversal contract.
    for (const Cell next : {Cell{cell.row - 1, cell.column}, Cell{cell.row, cell.column + 1},
                           Cell{cell.row + 1, cell.column}, Cell{cell.row, cell.column - 1}}) {
        if (visit(maze, next, visited, result)) return true;
    }
    result.trace.push_back(event("Backtrack", cell));
    result.path.pop_back();
    return false;
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
