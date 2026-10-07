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
    // TODO: implement the exact command grammar without mutating result on error.
    // Use a local Command; validate quoting, arguments and filters before commit.
    (void)text;
    (void)result;
    error = "UNFINISHED: implement command parsing.";
    return false;
}
} // namespace taskcourse
