#include "task_storage.h"

namespace taskcourse {
bool loadTasks(const std::filesystem::path& path, TaskLedger& ledger,
               std::string& error, bool allowMissing) {
    // TODO: read a bounded regular file and parse into a temporary row list.
    // Only commit after the entire file is valid; a missing startup file is
    // allowed only when allowMissing is true. Missing reload must fail.
    (void)path;
    (void)ledger;
    (void)allowMissing;
    error = "UNFINISHED: implement loading a task file.";
    return false;
}

bool saveTasks(const std::filesystem::path& path, const TaskLedger& ledger,
               std::string& error) {
    // TODO: refuse an existing PATH.tmp; write, flush and close a new one.
    // Rename only after success. On failure preserve PATH and remove only
    // the temporary file created by this save attempt.
    (void)path;
    (void)ledger;
    error = "UNFINISHED: implement saving a task file.";
    return false;
}
} // namespace taskcourse
