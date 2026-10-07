#include "task_import.h"
#include "command_parser.h"
#include <fstream>
#include <sstream>
#include <system_error>
#include <utility>

namespace taskcourse {
bool parseImportRow(std::string_view text, Task& row, std::string& error) {
    // TODO: Split exactly three tab-delimited fields, check ID/status/text,
    // and assign a temporary Task only after all checks pass. Follow the
    // documented reason order and leave row unchanged after failure.
    (void)text;
    (void)row;
    error = "UNFINISHED: implement import row parsing.";
    return false;
}

bool importTaskRows(std::istream& input, TaskLedger& ledger,
                    ImportReport& report, std::string& error) {
    // TODO: Read a bounded file fully before mutation, validate the header,
    // collect accepted/rejected data rows with physical line numbers, then
    // commit a valid candidate ledger and report. Fatal failures preserve both.
    (void)input;
    (void)ledger;
    (void)report;
    error = "UNFINISHED: implement selective import.";
    return false;
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
