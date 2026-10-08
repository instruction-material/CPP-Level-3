#pragma once
#include <cstdint>
#include <map>
#include <set>
#include <string>
#include <string_view>
#include <vector>
namespace rovercourse {
inline constexpr std::size_t maxZones = 64;
inline constexpr std::size_t maxZoneBytes = 24;
inline constexpr std::size_t maxEdges = 1024;
inline constexpr std::size_t maxCommandBytes = 1024;
inline constexpr std::size_t maxSnapshotBytes = 65536;
inline constexpr std::size_t maxPathBytes = 512;
inline constexpr std::uint32_t maxMoves = 1000000;
enum class Phase { Ready, Running, Paused, Finished };
enum class Event { Start, Pause, Resume, Finish };
using Graph = std::map<std::string, std::set<std::string>>;
struct Snapshot {
    Graph graph;
    std::string position;
    Phase phase = Phase::Ready;
    std::uint32_t moves = 0;
    bool operator==(const Snapshot&) const = default;
};
bool validZone(std::string_view name);
bool validPath(std::string_view path);
std::string phaseName(Phase phase);
bool parsePhase(std::string_view text, Phase& phase);
bool validSnapshot(const Snapshot& state, std::string& error);
bool nextPhase(Phase before, Event event, Phase& after);
bool visitRoute(const Graph& graph, const std::string& here,
                const std::string& target, std::set<std::string>& visited,
                std::vector<std::string>& path);
class Rover {
    Snapshot state_;
public:
    Rover();
    void swap(Rover& other) noexcept;
    const Snapshot& snapshot() const { return state_; }
    bool replace(Snapshot candidate, std::string& error);
    bool link(std::string_view from, std::string_view to, std::string& error);
    bool transition(Event event, std::string& error);
    bool move(std::string_view target, std::string& error);
    std::vector<std::string> route(std::string_view target) const;
};
std::string describe(const Rover& rover);
std::string encodeSnapshot(const Snapshot& state);
bool decodeSnapshot(std::string_view bytes, Snapshot& result, std::string& error);
bool saveSnapshot(const Snapshot& state, std::string_view path, std::string& error);
bool loadSnapshot(Rover& rover, std::string_view path, std::string& error);
} // namespace rovercourse
