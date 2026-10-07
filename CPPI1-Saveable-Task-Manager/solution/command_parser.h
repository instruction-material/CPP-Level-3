#ifndef TASK_COURSE_COMMAND_PARSER_H
#define TASK_COURSE_COMMAND_PARSER_H

#include "task_manager.h"
#include <string>
#include <string_view>

namespace taskcourse {
enum class Verb { Add, Done, List, Save, Reload, Help, Quit };
struct Command {
    Verb verb = Verb::Help;
    std::string text;
    int id = 0;
    Filter filter = Filter::All;
    bool operator==(const Command&) const = default;
};

std::string_view trimCommandWhitespace(std::string_view text);
bool parsePositiveId(std::string_view text, int& result);
bool parseCommand(std::string_view text, Command& result, std::string& error);
} // namespace taskcourse
#endif
