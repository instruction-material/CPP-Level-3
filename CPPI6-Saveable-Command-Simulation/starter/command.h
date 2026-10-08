#pragma once
#include "rover.h"
#include <memory>
namespace rovercourse {
enum class Verb { Help, Show, Link, Start, Pause, Resume, Finish, Move, Route, Save, Load, Quit };
struct Parsed {
    Verb verb = Verb::Help;
    std::string first;
    std::string second;
    bool operator==(const Parsed&) const = default;
};
bool parseCommand(std::string_view line, Parsed& result, std::string& error);
struct Result { bool ok; std::string message; };
class Command {
public:
    virtual ~Command() = default;
    virtual Result execute(Rover& rover) = 0;
};
std::unique_ptr<Command> makeCommand(const Parsed& parsed);
} // namespace rovercourse
