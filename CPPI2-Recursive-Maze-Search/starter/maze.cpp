#include "maze.h"

#include <charconv>
#include <istream>
#include <sstream>
#include <string_view>
#include <utility>

namespace mazecourse {
namespace {
bool parseDimension(std::string_view token, int& value) {
    if (token.empty()) return false;
    for (const char byte : token) {
        if (byte < '0' || byte > '9') return false;
    }
    const auto parsed = std::from_chars(token.data(), token.data() + token.size(), value);
    return parsed.ec == std::errc{} && parsed.ptr == token.data() + token.size()
        && value >= 1 && value <= maximumDimension;
}

bool dimensions(std::string_view line, int& rows, int& columns) {
    const auto space = [](char byte) { return byte == ' ' || byte == '\t'; };
    while (!line.empty() && space(line.front())) line.remove_prefix(1);
    while (!line.empty() && space(line.back())) line.remove_suffix(1);
    const auto separator = line.find_first_of(" \t");
    if (separator == std::string_view::npos) return false;
    const auto first = line.substr(0, separator);
    auto second = line.substr(separator);
    while (!second.empty() && space(second.front())) second.remove_prefix(1);
    return parseDimension(first, rows) && parseDimension(second, columns);
}

bool physicalLine(std::istream& input, std::string& line) {
    if (!std::getline(input, line)) return false;
    if (!line.empty() && line.back() == '\r') line.pop_back();
    return true;
}
} // namespace

bool validateMaze(const Maze& maze, std::string& error) {
    if (maze.rows.empty() || maze.rows.size() > static_cast<std::size_t>(maximumDimension)) {
        error = "Row count must be from 1 to 20.";
        return false;
    }
    const auto width = maze.rows.front().size();
    if (width == 0 || width > static_cast<std::size_t>(maximumDimension)) {
        error = "Column count must be from 1 to 20.";
        return false;
    }
    int starts = 0;
    int exits = 0;
    Cell start;
    Cell exit;
    for (std::size_t row = 0; row < maze.rows.size(); ++row) {
        if (maze.rows[row].size() != width) {
            error = "Every row must have the declared width.";
            return false;
        }
        for (std::size_t column = 0; column < width; ++column) {
            const char tile = maze.rows[row][column];
            const Cell cell{static_cast<int>(row), static_cast<int>(column)};
            if (tile == 'S') { ++starts; start = cell; }
            else if (tile == 'E') { ++exits; exit = cell; }
            else if (tile != '.' && tile != '#') {
                error = "Cells must be S, E, . or #.";
                return false;
            }
        }
    }
    if (starts != 1 || exits != 1) {
        error = "Maze must contain exactly one S and one E.";
        return false;
    }
    if (maze.start != start || maze.exit != exit) {
        error = "Stored start and exit must match the grid.";
        return false;
    }
    error.clear();
    return true;
}

bool readMaze(std::istream& input, Maze& output, std::string& error) {
    std::string bytes;
    char byte{};
    try {
        while (input.get(byte)) {
            if (bytes.size() == maximumInputBytes) {
                error = "Input exceeds 16384 bytes.";
                return false;
            }
            bytes.push_back(byte);
        }
    } catch (const std::ios_base::failure&) {
        if (input.bad() || !input.eof()) {
            error = "Cannot read maze input.";
            return false;
        }
    }
    if (input.bad() || !input.eof()) {
        error = "Cannot read maze input.";
        return false;
    }
    std::istringstream text(bytes);
    std::string line;
    int rowCount = 0;
    int columnCount = 0;
    if (!physicalLine(text, line) || !dimensions(line, rowCount, columnCount)) {
        error = "First line must give rows and columns from 1 to 20.";
        return false;
    }
    Maze candidate;
    for (int row = 0; row < rowCount; ++row) {
        if (!physicalLine(text, line) || line.size() != static_cast<std::size_t>(columnCount)) {
            error = "Every row must have the declared width.";
            return false;
        }
        for (int column = 0; column < columnCount; ++column) {
            if (line[static_cast<std::size_t>(column)] == 'S') candidate.start = {row, column};
            if (line[static_cast<std::size_t>(column)] == 'E') candidate.exit = {row, column};
        }
        candidate.rows.push_back(line);
    }
    if (physicalLine(text, line)) {
        error = "Extra lines after the maze are not allowed.";
        return false;
    }
    if (!validateMaze(candidate, error)) return false;
    output = std::move(candidate);
    error.clear();
    return true;
}
} // namespace mazecourse
