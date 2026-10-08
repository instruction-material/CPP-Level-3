#include "rover.h"
#include <sstream>
#include <stdexcept>
#include <utility>
namespace rovercourse {
bool validZone(std::string_view name) {
    const auto letter = [](char c) { return (c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z'); };
    if (name.empty() || name.size() > maxZoneBytes || !letter(name.front())) return false;
    for (char c : name) if (!letter(c) && !(c >= '0' && c <= '9') && c != '_') return false;
    return true;
}
bool validPath(std::string_view path) {
    if (path.empty() || path.size() > maxPathBytes) return false;
    for (char c : path) if (c < ' ' || c > '~') return false;
    return true;
}
std::string phaseName(Phase phase) {
    switch (phase) {
    case Phase::Ready: return "ready";
    case Phase::Running: return "running";
    case Phase::Paused: return "paused";
    case Phase::Finished: return "finished";
    }
    throw std::invalid_argument("Invalid phase.");
}
bool parsePhase(std::string_view text, Phase& phase) {
    for (Phase candidate : {Phase::Ready, Phase::Running, Phase::Paused, Phase::Finished}) {
        if (phaseName(candidate) == text) { phase = candidate; return true; }
    }
    return false;
}
bool validSnapshot(const Snapshot& state, std::string& error) {
    if (state.graph.empty() || state.graph.size() > maxZones ||
        !state.graph.contains(state.position) || state.moves > maxMoves ||
        (state.phase == Phase::Ready && state.moves != 0)) {
        error = "Invalid snapshot bounds or position."; return false;
    }
    if (state.phase != Phase::Ready && state.phase != Phase::Running &&
        state.phase != Phase::Paused && state.phase != Phase::Finished) {
        error = "Invalid phase."; return false;
    }
    std::size_t edgeCount = 0;
    for (const auto& [zone, edges] : state.graph) {
        edgeCount += edges.size();
        if (edgeCount > maxEdges) { error = "Edge limit reached."; return false; }
        if (!validZone(zone)) { error = "Invalid zone ID."; return false; }
        for (const auto& target : edges) {
            if (!state.graph.contains(target)) { error = "Edge names an absent zone."; return false; }
        }
    }
    error.clear(); return true;
}
bool nextPhase(Phase before, Event event, Phase& after) {
    // BEGIN TASK transition
    (void)before; (void)event; (void)after;
    // TODO: implement the phase/event table without changing after on rejection.
    throw std::logic_error("Unfinished phase transitions.");
    // END TASK transition
}
bool visitRoute(const Graph& graph, const std::string& here,
                const std::string& target, std::set<std::string>& visited,
                std::vector<std::string>& path) {
    // BEGIN TASK route
    (void)graph; (void)here; (void)target; (void)visited; (void)path;
    // TODO: recursively explore sorted neighbors, skip visited nodes and backtrack failed path entries.
    throw std::logic_error("Unfinished recursive route.");
    // END TASK route
}
Rover::Rover() : state_{Graph{{"dock", {}}, {"entry", {"lab"}}, {"lab", {"dock"}}},
                          "entry", Phase::Ready, 0} {}
void Rover::swap(Rover& other) noexcept {
    state_.graph.swap(other.state_.graph);
    state_.position.swap(other.state_.position);
    std::swap(state_.phase, other.state_.phase);
    std::swap(state_.moves, other.state_.moves);
}
bool Rover::replace(Snapshot candidate, std::string& error) {
    if (!validSnapshot(candidate, error)) return false;
    // All allocation and validation finish before this no-throw swap.
    state_.graph.swap(candidate.graph);
    state_.position.swap(candidate.position);
    std::swap(state_.phase, candidate.phase);
    std::swap(state_.moves, candidate.moves);
    return true;
}
bool Rover::link(std::string_view from, std::string_view to, std::string& error) {
    if (state_.phase != Phase::Ready) { error = "Links require ready phase."; return false; }
    if (!validZone(from) || !validZone(to)) { error = "Invalid zone ID."; return false; }
    Snapshot candidate = state_;
    const std::string first(from), second(to);
    candidate.graph.try_emplace(first);
    candidate.graph.try_emplace(second);
    if (!candidate.graph[first].insert(second).second) { error = "Link already exists."; return false; }
    return replace(std::move(candidate), error);
}
bool Rover::transition(Event event, std::string& error) {
    Phase after = state_.phase;
    if (!nextPhase(state_.phase, event, after)) { error = "Transition is not allowed."; return false; }
    state_.phase = after; error.clear(); return true;
}
bool Rover::move(std::string_view target, std::string& error) {
    // BEGIN TASK move
    (void)target;
    // TODO: validate phase, direct edge and movement bound before committing.
    error = "Unfinished movement."; return false;
    // END TASK move
}
std::vector<std::string> Rover::route(std::string_view target) const {
    if (!state_.graph.contains(std::string(target))) throw std::invalid_argument("Unknown route target.");
    std::set<std::string> visited;
    std::vector<std::string> path;
    (void)visitRoute(state_.graph, state_.position, std::string(target), visited, path);
    return path;
}
std::string describe(const Rover& rover) {
    const auto& state = rover.snapshot();
    std::ostringstream out;
    out << "phase " << phaseName(state.phase) << " position " << state.position << " moves " << state.moves << '\n';
    for (const auto& [zone, edges] : state.graph) {
        out << zone << ':';
        for (const auto& edge : edges) out << ' ' << edge;
        out << '\n';
    }
    return out.str();
}
} // namespace rovercourse
