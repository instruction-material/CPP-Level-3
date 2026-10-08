#include "command.h"
#include <iomanip>
#include <sstream>
#include <stdexcept>
#include <utility>
namespace rovercourse {
bool parseCommand(std::string_view line, Parsed& result, std::string& error) {
    // BEGIN TASK parse
    (void)line; (void)result;
    // TODO: validate token counts, zone IDs and quoted file paths before assigning result.
    error = "Unfinished command parser."; return false;
    // END TASK parse
}
namespace {
class PhaseCommand final : public Command {
    Event event_;
public:
    explicit PhaseCommand(Event event) : event_(event) {}
    Result execute(Rover& rover) override {
        std::string error;
        if (!rover.transition(event_, error)) return {false, error};
        return {true, "phase " + phaseName(rover.snapshot().phase) + "\n"};
    }
};
class MoveCommand final : public Command {
    std::string target_;
public:
    explicit MoveCommand(std::string target) : target_(std::move(target)) {}
    Result execute(Rover& rover) override {
        std::string error;
        if (!rover.move(target_, error)) return {false, error};
        return {true, "position " + rover.snapshot().position + " moves " + std::to_string(rover.snapshot().moves) + "\n"};
    }
};
class LinkCommand final : public Command {
    std::string from_, to_;
public:
    LinkCommand(std::string from, std::string to) : from_(std::move(from)), to_(std::move(to)) {}
    Result execute(Rover& rover) override {
        std::string error;
        if (!rover.link(from_, to_, error)) return {false, error};
        return {true, "linked " + from_ + " -> " + to_ + "\n"};
    }
};
class InspectCommand final : public Command {
    Verb verb_;
    std::string target_;
public:
    InspectCommand(Verb verb, std::string target) : verb_(verb), target_(std::move(target)) {}
    Result execute(Rover& rover) override {
        if (verb_ == Verb::Help) return {true, "help | show | link FROM TO | start | pause | resume | finish | move TO | route TO | save PATH | load PATH | quit\n"};
        if (verb_ == Verb::Show) return {true, describe(rover)};
        const auto path = rover.route(target_);
        if (path.empty()) return {true, "route unavailable\n"};
        std::string message = "route ";
        for (std::size_t i = 0; i < path.size(); ++i) { if (i) message += " -> "; message += path[i]; }
        return {true, message + "\n"};
    }
};
class StorageCommand final : public Command {
    bool save_;
    std::string path_;
public:
    StorageCommand(bool save, std::string path) : save_(save), path_(std::move(path)) {}
    Result execute(Rover& rover) override {
        std::string error;
        const bool ok = save_ ? saveSnapshot(rover.snapshot(), path_, error) : loadSnapshot(rover, path_, error);
        return ok ? Result{true, save_ ? "saved\n" : "loaded\n"} : Result{false, error};
    }
};
} // namespace
std::unique_ptr<Command> makeCommand(const Parsed& parsed) {
    switch (parsed.verb) {
    case Verb::Start: return std::make_unique<PhaseCommand>(Event::Start);
    case Verb::Pause: return std::make_unique<PhaseCommand>(Event::Pause);
    case Verb::Resume: return std::make_unique<PhaseCommand>(Event::Resume);
    case Verb::Finish: return std::make_unique<PhaseCommand>(Event::Finish);
    case Verb::Move: return std::make_unique<MoveCommand>(parsed.first);
    case Verb::Link: return std::make_unique<LinkCommand>(parsed.first, parsed.second);
    case Verb::Help: case Verb::Show: case Verb::Route: return std::make_unique<InspectCommand>(parsed.verb, parsed.first);
    case Verb::Save: case Verb::Load: return std::make_unique<StorageCommand>(parsed.verb == Verb::Save, parsed.first);
    case Verb::Quit: break;
    }
    throw std::invalid_argument("Quit is handled by the input loop.");
}
} // namespace rovercourse
