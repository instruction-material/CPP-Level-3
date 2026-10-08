#include "state_review.h"
#include <stdexcept>
namespace statecourse {
std::string phaseName(Phase phase) {
    switch (phase) {
    case Phase::Ready: return "ready";
    case Phase::Running: return "running";
    case Phase::Paused: return "paused";
    case Phase::Finished: return "finished";
    }
    throw std::invalid_argument("Invalid phase.");
}
bool parseEvent(std::string_view text, Event& event) {
    if (text == "start") event = Event::Start;
    else if (text == "pause") event = Event::Pause;
    else if (text == "resume") event = Event::Resume;
    else if (text == "finish") event = Event::Finish;
    else return false;
    return true;
}
std::optional<Phase> enumNext(Phase phase, Event event) {
    // BEGIN TASK enum
    (void)phase; (void)event;
    // TODO: implement the same five legal transitions as the core rover.
    throw std::logic_error("Unfinished enum transition table.");

    // END TASK enum
}
namespace {
class Ready final : public State {
public:
    Phase phase() const override { return Phase::Ready; }
    std::optional<Phase> next(Event event) const override {
        return event == Event::Start ? std::optional{Phase::Running} : std::nullopt;
    }
};
class Running final : public State {
public:
    Phase phase() const override { return Phase::Running; }
    std::optional<Phase> next(Event event) const override {
        if (event == Event::Pause) return Phase::Paused;
        if (event == Event::Finish) return Phase::Finished;
        return std::nullopt;
    }
};
class Paused final : public State {
public:
    Phase phase() const override { return Phase::Paused; }
    std::optional<Phase> next(Event event) const override {
        // BEGIN TASK paused
        (void)event;
        // TODO: handle Resume and Finish; reject all other events.
        throw std::logic_error("Unfinished paused-state behavior.");

        // END TASK paused
    }
};
class Finished final : public State {
public:
    Phase phase() const override { return Phase::Finished; }
    std::optional<Phase> next(Event) const override { return std::nullopt; }
};
} // namespace
std::unique_ptr<State> makeState(Phase phase) {
    // BEGIN TASK factory
    (void)phase;
    // TODO: return unique ownership of the actual derived type for each phase.
    throw std::logic_error("Unfinished state factory.");

    // END TASK factory
}
bool Machine::apply(Event event) {
    const auto next = state_->next(event);
    if (!next) return false;
    auto candidate = makeState(*next); // Allocate successfully before replacing current state.
    state_.swap(candidate);
    return true;
}
} // namespace statecourse
