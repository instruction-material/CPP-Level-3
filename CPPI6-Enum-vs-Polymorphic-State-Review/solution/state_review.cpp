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
    if (phase == Phase::Ready && event == Event::Start) return Phase::Running;
    if (phase == Phase::Running && event == Event::Pause) return Phase::Paused;
    if (phase == Phase::Paused && event == Event::Resume) return Phase::Running;
    if ((phase == Phase::Running || phase == Phase::Paused) && event == Event::Finish) return Phase::Finished;
    return std::nullopt;
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
        if (event == Event::Resume) return Phase::Running;
        if (event == Event::Finish) return Phase::Finished;
        return std::nullopt;
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
    switch (phase) {
    case Phase::Ready: return std::make_unique<Ready>();
    case Phase::Running: return std::make_unique<Running>();
    case Phase::Paused: return std::make_unique<Paused>();
    case Phase::Finished: return std::make_unique<Finished>();
    }
    throw std::invalid_argument("Invalid phase.");
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
