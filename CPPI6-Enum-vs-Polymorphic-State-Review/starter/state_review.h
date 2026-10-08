#pragma once
#include <cstddef>
#include <memory>
#include <optional>
#include <string>
#include <string_view>
namespace statecourse {
enum class Phase { Ready, Running, Paused, Finished };
enum class Event { Start, Pause, Resume, Finish };
std::string phaseName(Phase phase);
bool parseEvent(std::string_view text, Event& event);
std::optional<Phase> enumNext(Phase phase, Event event);
struct Lifetime { static inline std::size_t created = 0, destroyed = 0; };
class State {
public:
    State() { ++Lifetime::created; }
    virtual ~State() { ++Lifetime::destroyed; }
    State(const State&) = delete;
    State& operator=(const State&) = delete;
    virtual Phase phase() const = 0;
    virtual std::optional<Phase> next(Event event) const = 0;
};
std::unique_ptr<State> makeState(Phase phase);
class Machine {
    std::unique_ptr<State> state_;
public:
    Machine() : state_(makeState(Phase::Ready)) {}
    Phase phase() const { return state_->phase(); }
    bool apply(Event event);
};
} // namespace statecourse
