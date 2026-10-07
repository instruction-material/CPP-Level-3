#include "task_manager.h"
#include <utility>

namespace taskcourse {
bool validTaskText(std::string_view text) {
    if (text.empty() || text.size() > maxTextBytes) return false;
    bool visible = false;
    for (char ch : text) {
        const auto byte = static_cast<unsigned char>(ch);
        if (byte < 32 || byte > 126 || ch == '"') return false;
        if (ch != ' ') visible = true;
    }
    return visible;
}

bool TaskLedger::add(const std::string& text, int& assignedId,
                     std::string& error) {
    if (!validTaskText(text)) {
        error = "Invalid task text.";
        return false;
    }
    if (tasks_.size() >= maxTasks) {
        error = "At most 100 tasks are allowed.";
        return false;
    }
    if (nextId_ > maxTaskId) {
        error = "Task IDs are exhausted.";
        return false;
    }
    const int id = nextId_;
    tasks_.push_back({id, false, text});
    ++nextId_;
    assignedId = id;
    error.clear();
    return true;
}

bool TaskLedger::complete(int id, std::string& error) {
    for (Task& task : tasks_) {
        if (task.id == id) {
            task.done = true;
            error.clear();
            return true;
        }
    }
    error = "Unknown task ID.";
    return false;
}

std::vector<Task> TaskLedger::select(Filter filter) const {
    std::vector<Task> result;
    for (const Task& task : tasks_) {
        if (filter == Filter::All || (filter == Filter::Open && !task.done) ||
            (filter == Filter::Done && task.done)) result.push_back(task);
    }
    return result;
}

bool TaskLedger::replace(std::vector<Task> rows, std::string& error) {
    if (rows.size() > maxTasks) {
        error = "At most 100 tasks are allowed.";
        return false;
    }
    int previous = 0;
    for (const Task& row : rows) {
        if (row.id <= previous || row.id > maxTaskId ||
            !validTaskText(row.text)) {
            error = "Invalid task rows.";
            return false;
        }
        previous = row.id;
    }
    tasks_.swap(rows);
    nextId_ = previous + 1;
    error.clear();
    return true;
}
} // namespace taskcourse
