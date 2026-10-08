#include "rover.h"
#include <charconv>
#include <filesystem>
#include <fstream>
#include <sstream>
#include <stdexcept>
#include <system_error>
#include <utility>
namespace rovercourse {
namespace {
[[maybe_unused]] bool number(std::string_view text, std::uint32_t& result) {
    if (text.empty()) return false;
    for (char c : text) if (c < '0' || c > '9') return false;
    const auto parsed = std::from_chars(text.data(), text.data() + text.size(), result);
    return parsed.ec == std::errc{} && parsed.ptr == text.data() + text.size();
}
class StagingDirectory {
    std::filesystem::path directory_;
public:
    explicit StagingDirectory(std::filesystem::path directory) : directory_(std::move(directory)) {}
    const std::filesystem::path& directory() const { return directory_; }
    ~StagingDirectory() {
        std::error_code ignored;
        std::filesystem::remove(directory_ / "snapshot", ignored);
        std::filesystem::remove(directory_, ignored);
    }
    StagingDirectory(const StagingDirectory&) = delete;
    StagingDirectory& operator=(const StagingDirectory&) = delete;
};
} // namespace
std::string encodeSnapshot(const Snapshot& state) {
    std::string error;
    if (!validSnapshot(state, error)) throw std::invalid_argument(error);
    std::ostringstream out;
    out << "ROVER 1\nphase " << phaseName(state.phase) << "\nposition " << state.position
        << "\nmoves " << state.moves << "\nzones " << state.graph.size() << '\n';
    for (const auto& [zone, edges] : state.graph) { (void)edges; out << zone << '\n'; }
    std::size_t count = 0;
    for (const auto& [zone, edges] : state.graph) { (void)zone; count += edges.size(); }
    out << "edges " << count << '\n';
    for (const auto& [zone, edges] : state.graph) for (const auto& edge : edges) out << zone << ' ' << edge << '\n';
    out << "end\n";
    auto bytes = out.str();
    if (bytes.size() > maxSnapshotBytes) throw std::length_error("Snapshot exceeds byte limit.");
    return bytes;
}
bool decodeSnapshot(std::string_view bytes, Snapshot& result, std::string& error) {
    // BEGIN TASK decode
    const auto reject = [&error]() { error = "Malformed or inconsistent snapshot."; return false; };
    if (bytes.empty() || bytes.size() > maxSnapshotBytes || bytes.back() != '\n') return reject();
    std::istringstream input{std::string(bytes)};
    std::string line;
    const auto prefixed = [&input, &line](std::string_view prefix, std::string& value) {
        if (!std::getline(input, line) || !line.starts_with(prefix)) return false;
        value = line.substr(prefix.size()); return true;
    };
    Snapshot candidate;
    std::string value;
    if (!std::getline(input, line) || line != "ROVER 1") return reject();
    if (!prefixed("phase ", value) || !parsePhase(value, candidate.phase)) return reject();
    if (!prefixed("position ", candidate.position) || !validZone(candidate.position)) return reject();
    if (!prefixed("moves ", value) || !number(value, candidate.moves)) return reject();
    std::uint32_t zones = 0;
    if (!prefixed("zones ", value) || !number(value, zones) || zones == 0 || zones > maxZones) return reject();
    std::string previous;
    for (std::uint32_t i = 0; i < zones; ++i) {
        if (!std::getline(input, line) || !validZone(line) || (!previous.empty() && line <= previous)) return reject();
        candidate.graph.emplace(line, std::set<std::string>{}); previous = line;
    }
    std::uint32_t edges = 0;
    if (!prefixed("edges ", value) || !number(value, edges) || edges > zones * zones || edges > maxEdges) return reject();
    previous.clear();
    for (std::uint32_t i = 0; i < edges; ++i) {
        if (!std::getline(input, line) || (!previous.empty() && line <= previous)) return reject();
        const auto split = line.find(' ');
        if (split == std::string::npos) return reject();
        const auto from = line.substr(0, split), to = line.substr(split + 1);
        if (!validZone(from) || !validZone(to) || !candidate.graph.contains(from) || !candidate.graph.contains(to)) return reject();
        if (!candidate.graph.at(from).insert(to).second) return reject();
        previous = line;
    }
    if (!std::getline(input, line) || line != "end" || std::getline(input, line)) return reject();
    if (!validSnapshot(candidate, error)) return false;
    result = std::move(candidate); error.clear(); return true;
    // END TASK decode
}
bool saveSnapshot(const Snapshot& state, std::string_view path, std::string& error) {
    if (!validPath(path)) { error = "Invalid file path."; return false; }
    const std::string bytes = encodeSnapshot(state);
    const std::filesystem::path target{std::string(path)};
    std::error_code code;
    auto stagePath = target; stagePath += ".rover-stage";
    if (!std::filesystem::create_directory(stagePath, code)) { error = "Could not acquire staging directory."; return false; }
    StagingDirectory stage(stagePath);
    const auto file = stage.directory() / "snapshot";
    std::ofstream output(file, std::ios::binary | std::ios::trunc);
    if (!output) { error = "Could not open staged snapshot."; return false; }
    output.write(bytes.data(), static_cast<std::streamsize>(bytes.size()));
    output.close();
    if (!output) { error = "Could not complete staged snapshot."; return false; }
    std::filesystem::rename(file, target, code);
    if (code) { error = "Could not publish snapshot."; return false; }
    error.clear(); return true;
}
bool loadSnapshot(Rover& rover, std::string_view path, std::string& error) {
    if (!validPath(path)) { error = "Invalid file path."; return false; }
    const std::filesystem::path source{std::string(path)};
    std::error_code code;
    if (!std::filesystem::is_regular_file(source, code) || code) { error = "Snapshot is not a readable regular file."; return false; }
    std::ifstream input(source, std::ios::binary);
    if (!input) { error = "Could not open snapshot."; return false; }
    std::string bytes;
    char c = 0;
    while (input.get(c)) {
        if (bytes.size() == maxSnapshotBytes) { error = "Snapshot exceeds byte limit."; return false; }
        bytes.push_back(c);
    }
    if (input.bad()) { error = "Could not finish reading snapshot."; return false; }
    Snapshot candidate;
    if (!decodeSnapshot(bytes, candidate, error)) return false;
    return rover.replace(std::move(candidate), error);
}
} // namespace rovercourse
