#ifndef TASK_COURSE_MANAGER_H
#define TASK_COURSE_MANAGER_H

#include <cstddef>
#include <string>
#include <string_view>
#include <vector>

namespace taskcourse {
constexpr std::size_t maxTasks = 100;
constexpr std::size_t maxTextBytes = 80;
constexpr int maxTaskId = 999999;

enum class Filter { All, Open, Done };
struct Task {
    int id = 0;
    bool done = false;
    std::string text;
    bool operator==(const Task&) const = default;
};

bool validTaskText(std::string_view text);

class TaskLedger {
  public:
    bool add(const std::string& text, int& assignedId, std::string& error);
    bool complete(int id, std::string& error);
    std::vector<Task> select(Filter filter) const;
    bool replace(std::vector<Task> rows, std::string& error);
    const std::vector<Task>& tasks() const noexcept { return tasks_; }
    std::size_t size() const noexcept { return tasks_.size(); }

  private:
    std::vector<Task> tasks_;
    int nextId_ = 1;
};
} // namespace taskcourse
#endif
