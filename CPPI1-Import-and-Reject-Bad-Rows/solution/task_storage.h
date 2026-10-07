#ifndef TASK_COURSE_STORAGE_H
#define TASK_COURSE_STORAGE_H

#include "task_manager.h"
#include <filesystem>
#include <string>

namespace taskcourse {
bool loadTasks(const std::filesystem::path& path, TaskLedger& ledger,
               std::string& error, bool allowMissing = false);
bool saveTasks(const std::filesystem::path& path, const TaskLedger& ledger,
               std::string& error);
} // namespace taskcourse
#endif
