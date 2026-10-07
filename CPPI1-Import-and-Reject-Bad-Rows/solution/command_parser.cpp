#include "command_parser.h"
#include <charconv>
#include <system_error>
#include <utility>

namespace taskcourse {
std::string_view trimCommandWhitespace(std::string_view text) {
    const auto whitespace = [](char c) { return c == ' ' || c == '\t' || c == '\r'; };
    while (!text.empty() && whitespace(text.front())) text.remove_prefix(1);
    while (!text.empty() && whitespace(text.back())) text.remove_suffix(1);
    return text;
}

bool parsePositiveId(std::string_view text, int& result) {
    if (text.empty()) return false;
    for (char ch : text) if (ch < '0' || ch > '9') return false;
    int candidate = 0;
    const auto parsed = std::from_chars(text.data(), text.data() + text.size(), candidate);
    if (parsed.ec != std::errc{} || parsed.ptr != text.data() + text.size() ||
        candidate < 1 || candidate > maxTaskId) return false;
    result = candidate;
    return true;
}

bool parseCommand(std::string_view text, Command& result, std::string& error) {
    text = trimCommandWhitespace(text);
    const auto split = text.find_first_of(" \t\r");
    const auto word = text.substr(0, split);
    const auto arguments = split == std::string_view::npos ? std::string_view{} :
        trimCommandWhitespace(text.substr(split));
    Command command;
    if (word == "add") {
        if (arguments.size() < 2 || arguments.front() != '"' || arguments.back() != '"') {
            error = "Expected one quoted task text.";
            return false;
        }
        const auto value = arguments.substr(1, arguments.size() - 2);
        if (!validTaskText(value)) {
            error = "Invalid task text.";
            return false;
        }
        command.verb = Verb::Add;
        command.text = value;
    } else if (word == "import") {
        if (arguments.size() < 3 || arguments.front() != '"' || arguments.back() != '"') {
            error = "Expected one quoted import path.";
            return false;
        }
        const auto path = arguments.substr(1, arguments.size() - 2);
        bool visible = false;
        if (path.size() > 1024) {
            error = "Invalid import path.";
            return false;
        }
        for (char ch : path) {
            const auto byte = static_cast<unsigned char>(ch);
            if (byte < 32 || byte > 126 || ch == '"') {
                error = "Invalid import path.";
                return false;
            }
            if (ch != ' ') visible = true;
        }
        if (!visible) {
            error = "Invalid import path.";
            return false;
        }
        command.verb = Verb::Import;
        command.text = path;
    } else if (word == "done") {
        command.verb = Verb::Done;
        if (!parsePositiveId(arguments, command.id)) {
            error = "Expected one task ID from 1 to 999999.";
            return false;
        }
    } else if (word == "list") {
        command.verb = Verb::List;
        if (arguments.empty() || arguments == "all") command.filter = Filter::All;
        else if (arguments == "open") command.filter = Filter::Open;
        else if (arguments == "done") command.filter = Filter::Done;
        else {
            error = "Expected list [all|open|done].";
            return false;
        }
    } else {
        if (word == "save") command.verb = Verb::Save;
        else if (word == "reload") command.verb = Verb::Reload;
        else if (word == "help") command.verb = Verb::Help;
        else if (word == "quit") command.verb = Verb::Quit;
        else {
            error = "Unknown command.";
            return false;
        }
        if (!arguments.empty()) {
            error = "Unexpected arguments.";
            return false;
        }
    }
    result = std::move(command);
    error.clear();
    return true;
}
} // namespace taskcourse
