#include "task_storage.h"
#include "command_parser.h"
#include <fstream>
#include <sstream>
#include <system_error>
#include <utility>

namespace taskcourse {
namespace {
constexpr std::size_t maxFileBytes = 64 * 1024;
constexpr const char* header = "CLASSES_TASKS_V1";

bool inspect(const std::filesystem::path& path, bool& exists,
             std::string& error) {
    std::error_code code;
    const auto status = std::filesystem::symlink_status(path, code);
    if (status.type() == std::filesystem::file_type::not_found ||
        code == std::errc::no_such_file_or_directory) {
        exists = false;
        return true;
    }
    if (code) {
        error = "Cannot inspect task file.";
        return false;
    }
    exists = true;
    if (!std::filesystem::is_regular_file(status)) {
        error = "Expected a regular task file.";
        return false;
    }
    return true;
}

void discardTemporary(const std::filesystem::path& path) {
    std::error_code ignored;
    std::filesystem::remove(path, ignored);
}
} // namespace

bool loadTasks(const std::filesystem::path& path, TaskLedger& ledger,
               std::string& error, bool allowMissing) {
    bool exists = false;
    if (!inspect(path, exists, error)) return false;
    if (!exists) {
        if (allowMissing) return ledger.replace({}, error);
        error = "Task file is missing.";
        return false;
    }
    std::ifstream input(path, std::ios::binary);
    if (!input.is_open()) {
        error = "Cannot open task file.";
        return false;
    }
    std::string bytes;
    char byte = 0;
    while (input.get(byte)) {
        if (bytes.size() == maxFileBytes) {
            error = "Task file exceeds 64 KiB.";
            return false;
        }
        bytes.push_back(byte);
    }
    if (input.bad() || !input.eof()) {
        error = "Cannot read task file.";
        return false;
    }
    std::istringstream lines(bytes);
    const auto stripCR = [](std::string& line) {
        if (!line.empty() && line.back() == '\r') line.pop_back();
    };
    std::string line;
    if (!std::getline(lines, line)) {
        error = "Invalid task file header.";
        return false;
    }
    stripCR(line);
    if (line != header) {
        error = "Invalid task file header.";
        return false;
    }
    std::vector<Task> rows;
    while (std::getline(lines, line)) {
        stripCR(line);
        const auto first = line.find('\t');
        const auto second = first == std::string::npos ? std::string::npos :
            line.find('\t', first + 1);
        if (first == std::string::npos || second == std::string::npos ||
            line.find('\t', second + 1) != std::string::npos) {
            error = "Invalid task file row.";
            return false;
        }
        int id = 0;
        const std::string_view view(line);
        const auto status = view.substr(first + 1, second - first - 1);
        const auto text = view.substr(second + 1);
        if (!parsePositiveId(view.substr(0, first), id) ||
            (status != "0" && status != "1") || !validTaskText(text) ||
            (!rows.empty() && id <= rows.back().id) || rows.size() >= maxTasks) {
            error = "Invalid task file row.";
            return false;
        }
        rows.push_back({id, status == "1", std::string(text)});
    }
    return ledger.replace(std::move(rows), error);
}

bool saveTasks(const std::filesystem::path& path, const TaskLedger& ledger,
               std::string& error) {
    bool exists = false;
    if (!inspect(path, exists, error)) return false;
    auto temporary = path;
    temporary += ".tmp";
    // Refuse every existing temporary entry, including a dangling symlink.
    std::error_code code;
    const auto status = std::filesystem::symlink_status(temporary, code);
    if (code && code != std::errc::no_such_file_or_directory) {
        error = "Cannot inspect temporary task file.";
        return false;
    }
    if (status.type() != std::filesystem::file_type::not_found && !code) {
        error = "Temporary task file already exists.";
        return false;
    }
    std::ofstream output(temporary, std::ios::binary | std::ios::trunc);
    if (!output.is_open()) {
        discardTemporary(temporary);
        error = "Cannot open temporary task file.";
        return false;
    }
    output << header << '\n';
    for (const Task& row : ledger.tasks())
        output << row.id << '\t' << (row.done ? '1' : '0') << '\t' << row.text << '\n';
    output.flush();
    const bool wrote = static_cast<bool>(output);
    output.close();
    if (!wrote || output.fail()) {
        discardTemporary(temporary);
        error = "Cannot write temporary task file.";
        return false;
    }
    std::filesystem::rename(temporary, path, code);
    if (code) {
        discardTemporary(temporary);
        error = "Cannot replace task file.";
        return false;
    }
    error.clear();
    return true;
}
} // namespace taskcourse
