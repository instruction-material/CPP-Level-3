#include "task_import.h"
#include "command_parser.h"
#include <fstream>
#include <sstream>
#include <system_error>
#include <utility>

namespace taskcourse {
bool parseImportRow(std::string_view text, Task& row, std::string& error) {
    const auto first = text.find('\t');
    const auto second = first == std::string_view::npos ? std::string_view::npos :
        text.find('\t', first + 1);
    if (first == std::string_view::npos || second == std::string_view::npos ||
        text.find('\t', second + 1) != std::string_view::npos) {
        error = "expected ID<TAB>status<TAB>text";
        return false;
    }
    Task candidate;
    if (!parsePositiveId(text.substr(0, first), candidate.id)) {
        error = "invalid ID";
        return false;
    }
    const auto status = text.substr(first + 1, second - first - 1);
    if (status != "0" && status != "1") {
        error = "invalid status";
        return false;
    }
    const auto value = text.substr(second + 1);
    if (!validTaskText(value)) {
        error = "invalid text";
        return false;
    }
    candidate.done = status == "1";
    candidate.text = value;
    row = std::move(candidate);
    error.clear();
    return true;
}

bool importTaskRows(std::istream& input, TaskLedger& ledger,
                    ImportReport& report, std::string& error) {
    constexpr std::size_t maxImportBytes = 64 * 1024;
    std::string bytes;
    char byte = 0;
    while (input.get(byte)) {
        if (bytes.size() == maxImportBytes) {
            error = "Import file exceeds 64 KiB.";
            return false;
        }
        bytes.push_back(byte);
    }
    if (input.bad() || !input.eof()) {
        error = "Cannot read import file.";
        return false;
    }
    std::istringstream lines(bytes);
    std::string line;
    const auto stripCR = [](std::string& value) {
        if (!value.empty() && value.back() == '\r') value.pop_back();
    };
    if (!std::getline(lines, line)) {
        error = "Invalid import file header.";
        return false;
    }
    stripCR(line);
    if (line != "CLASSES_TASKS_V1") {
        error = "Invalid import file header.";
        return false;
    }
    auto candidate = ledger.tasks();
    ImportReport pending;
    std::size_t number = 1;
    while (std::getline(lines, line)) {
        ++number;
        stripCR(line);
        Task row;
        std::string reason;
        if (parseImportRow(line, row, reason)) {
            if (!candidate.empty() && row.id <= candidate.back().id)
                reason = "ID must increase beyond the current last ID";
            else if (candidate.size() >= maxTasks)
                reason = "task limit reached";
            else {
                candidate.push_back(std::move(row));
                ++pending.accepted;
                continue;
            }
        }
        pending.rejected.push_back({number, std::move(reason)});
    }
    // Validation and ordinary read failures occur before the single commit.
    if (!ledger.replace(std::move(candidate), error)) return false;
    report = std::move(pending);
    error.clear();
    return true;
}

bool importTasks(const std::filesystem::path& path, TaskLedger& ledger,
                 ImportReport& report, std::string& error) {
    std::error_code code;
    const auto status = std::filesystem::symlink_status(path, code);
    if (code || !std::filesystem::is_regular_file(status)) {
        error = "Expected a readable regular import file.";
        return false;
    }
    std::ifstream input(path, std::ios::binary);
    if (!input.is_open()) {
        error = "Cannot open import file.";
        return false;
    }
    return importTaskRows(input, ledger, report, error);
}
} // namespace taskcourse
