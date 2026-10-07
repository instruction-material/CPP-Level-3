#ifndef TASK_COURSE_IMPORT_H
#define TASK_COURSE_IMPORT_H

#include "task_manager.h"
#include <filesystem>
#include <istream>
#include <string>
#include <string_view>
#include <vector>

namespace taskcourse {
struct RowRejection {
    std::size_t line = 0;
    std::string reason;
    bool operator==(const RowRejection&) const = default;
};
struct ImportReport {
    std::size_t accepted = 0;
    std::vector<RowRejection> rejected;
    bool operator==(const ImportReport&) const = default;
};

// A failed parse leaves row unchanged. Successful operations clear error.
bool parseImportRow(std::string_view text, Task& row, std::string& error);
// Fatal header, size or read errors leave BOTH ledger and report unchanged.
// Row-level errors are collected; valid rows append only after the full read.
bool importTaskRows(std::istream& input, TaskLedger& ledger,
                    ImportReport& report, std::string& error);
bool importTasks(const std::filesystem::path& path, TaskLedger& ledger,
                 ImportReport& report, std::string& error);
} // namespace taskcourse
#endif
