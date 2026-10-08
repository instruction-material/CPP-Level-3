"""Check rover behavior against independent phase, graph and serialization models."""

from datetime import datetime, timezone
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parent
PACK = ROOT / "CPPI6-Saveable-Command-Simulation"
TASK = os.environ.get("CLASSES_AUDIT_PARENT_TASK_ID", "cppi6-rover-source")
SOURCES = ["main.cpp", "rover.cpp", "command.cpp", "storage.cpp"]
HEADERS = ["rover.h", "command.h"]
FLAGS = ["-std=c++20", "-Wall", "-Wextra", "-Wpedantic", "-Wconversion",
         "-Wsign-conversion", "-Werror", "-g", "-O0"]



def run(command, cwd, expected=0, stdin=None, timeout=45, stdout_stream=None):
    child = subprocess.Popen(command, cwd=cwd, start_new_session=True,
                             stdin=subprocess.PIPE if stdin is not None else subprocess.DEVNULL,
                             stdout=subprocess.PIPE if stdout_stream is None else stdout_stream, stderr=subprocess.PIPE, text=True)
    fields = {"parentTaskId": TASK, "cwd": str(cwd), "command": [str(c) for c in command],
              "pid": child.pid, "parentPid": os.getpid(), "timeoutSeconds": timeout}

    def record(event, **extra):
        print(json.dumps({"event": event, "time": datetime.now(timezone.utc).isoformat(),
                          **fields, **extra}), flush=True)

    record("start")
    try:
        out, err = child.communicate(input=stdin, timeout=timeout)
    except BaseException:
        os.killpg(child.pid, signal.SIGTERM)
        try:
            child.wait(timeout=5)
        except subprocess.TimeoutExpired:
            os.killpg(child.pid, signal.SIGKILL)
            child.wait()
        record("child-process-group-cleanup", exitCode=child.returncode)
        raise
    record("end", exitCode=child.returncode)
    assert child.returncode == expected, (command, child.returncode, out, err)
    return out, err



import random
import re
from collections import deque

HARNESS = r"""
#include "command.h"
#include <cassert>
#include <csignal>
#include <filesystem>
#include <fstream>
#include <iterator>
#include <type_traits>
#include <sys/resource.h>
using namespace rovercourse;
void write(const std::string& path, const std::string& bytes) {
    std::ofstream out(path, std::ios::binary); out << bytes; out.close(); assert(out);
}
std::string read(const std::string& path) {
    std::ifstream in(path, std::ios::binary); assert(in);
    return {std::istreambuf_iterator<char>(in), std::istreambuf_iterator<char>()};
}
struct Probe final : Command {
    bool& destroyed;
    explicit Probe(bool& flag) : destroyed(flag) {}
    ~Probe() override { destroyed = true; }
    Result execute(Rover&) override { return {true, "probe\n"}; }
};
int main() {
    static_assert(std::is_abstract_v<Command>);
    static_assert(std::has_virtual_destructor_v<Command>);
    std::string error;
    Rover rover;
    const auto initial = rover.snapshot();
    Parsed parsed{Verb::Move, "lab", "untouched"}; const auto prior = parsed;
    for (const auto& text : std::vector<std::string>{"", "  ", "SHOW", "unknown", "show extra",
          "link entry", "link entry lab extra", "move", "move 9bad", "route missing extra",
          "save \"\"", "save \"unfinished", "save \"file\"tail", "save a b", "start extra",
          "quit extra", "load", "link a-b lab", "show\r", std::string(1025, 'x')}) {
        assert(!parseCommand(text, parsed, error) && parsed == prior && !error.empty());
    }
    assert(!parseCommand(std::string("show\0tail", 9), parsed, error) && parsed == prior);
    assert(parseCommand("\t save \"state with spaces.txt\" \t", parsed, error));
    assert(parsed.verb == Verb::Save && parsed.first == "state with spaces.txt" && error.empty());
    assert(parseCommand("link Alpha z_9", parsed, error) && parsed.first == "Alpha" && parsed.second == "z_9");
    assert(!validZone("") && !validZone("9a") && !validZone(std::string(25, 'a')));
    assert(validZone(std::string(24, 'a')) && !validPath(std::string(513, 'x')) && validPath(std::string(512, 'x')));
    const std::vector<Phase> phases{Phase::Ready, Phase::Running, Phase::Paused, Phase::Finished};
    const std::vector<Event> events{Event::Start, Event::Pause, Event::Resume, Event::Finish};
    // An independent explicit four-by-four oracle. -1 means reject.
    const int table[4][4] = {{1,-1,-1,-1},{-1,2,-1,3},{-1,-1,1,3},{-1,-1,-1,-1}};
    for (std::size_t p = 0; p < 4; ++p) for (std::size_t e = 0; e < 4; ++e) {
        Phase after = Phase::Ready;
        const bool allowed = nextPhase(phases[p], events[e], after);
        assert(allowed == (table[p][e] >= 0));
        if (allowed) assert(after == phases[static_cast<std::size_t>(table[p][e])]);
        else assert(after == Phase::Ready);
    }
    assert(!rover.move("lab", error) && rover.snapshot() == initial);
    assert(rover.link("dock", "entry", error));
    assert(rover.link("entry", "archive", error));
    assert(rover.link("archive", "dock", error));
    assert((rover.route("dock") == std::vector<std::string>{"entry","archive","dock"}));
    assert((rover.route("entry") == std::vector<std::string>{"entry"}));
    assert(rover.transition(Event::Start, error));
    auto before = rover.snapshot();
    assert(!rover.move("dock", error) && rover.snapshot() == before);
    assert(!rover.link("entry", "other", error) && rover.snapshot() == before);
    assert(rover.move("lab", error));
    assert(rover.transition(Event::Pause, error));
    before = rover.snapshot();
    assert(!rover.move("dock", error) && rover.snapshot() == before);
    assert(rover.transition(Event::Resume, error)); assert(rover.move("dock", error));
    assert(rover.snapshot().position == "dock" && rover.snapshot().moves == 2);
    const auto bytes = encodeSnapshot(rover.snapshot());
    assert(saveSnapshot(rover.snapshot(), "round trip.txt", error));
    assert(read("round trip.txt") == bytes);
    assert(rover.transition(Event::Finish, error));
    assert(loadSnapshot(rover, "round trip.txt", error)); assert(encodeSnapshot(rover.snapshot()) == bytes);
    before = rover.snapshot();
    assert(!loadSnapshot(rover, "missing.txt", error) && rover.snapshot() == before);
    write("invalid.txt", "ROVER 2\n");
    assert(!loadSnapshot(rover, "invalid.txt", error) && rover.snapshot() == before);
    write("oversized.txt", std::string(maxSnapshotBytes + 1, 'x'));
    assert(!loadSnapshot(rover, "oversized.txt", error) && rover.snapshot() == before);
    assert(!loadSnapshot(rover, ".", error) && rover.snapshot() == before);
    assert(!saveSnapshot(before, "absent-directory/state.txt", error));
    assert(saveSnapshot(before, "preserved.txt", error)); const auto previousFile = read("preserved.txt");
    assert(std::filesystem::create_directory("preserved.txt.rover-stage"));
    write("preserved.txt.rover-stage/sentinel", "keep");
    assert(!saveSnapshot(initial, "preserved.txt", error));
    assert(read("preserved.txt") == previousFile && read("preserved.txt.rover-stage/sentinel") == "keep");
    std::filesystem::remove("preserved.txt.rover-stage/sentinel");
    std::filesystem::remove("preserved.txt.rover-stage");
    assert(std::filesystem::create_directory("blocked.txt")); write("blocked.txt/sentinel", "keep");
    assert(!saveSnapshot(initial, "blocked.txt", error) && read("blocked.txt/sentinel") == "keep");
    assert(!std::filesystem::exists("blocked.txt.rover-stage"));
    struct rlimit original{}; assert(getrlimit(RLIMIT_FSIZE, &original) == 0);
    std::signal(SIGXFSZ, SIG_IGN);
    auto small = original; small.rlim_cur = 12; assert(setrlimit(RLIMIT_FSIZE, &small) == 0);
    assert(!saveSnapshot(initial, "preserved.txt", error));
    assert(setrlimit(RLIMIT_FSIZE, &original) == 0);
    assert(read("preserved.txt") == previousFile && !std::filesystem::exists("preserved.txt.rover-stage"));
    auto invalid = before; invalid.moves = maxMoves + 1;
    assert(!rover.replace(invalid, error) && rover.snapshot() == before);
    invalid = before; invalid.phase = static_cast<Phase>(42);
    assert(!rover.replace(invalid, error) && rover.snapshot() == before);
    invalid = before; invalid.phase = Phase::Ready;
    assert(!rover.replace(invalid, error) && rover.snapshot() == before);
    invalid = before; invalid.position = "absent";
    assert(!rover.replace(invalid, error) && rover.snapshot() == before);
    invalid = before; invalid.graph["lab"].insert("absent");
    assert(!rover.replace(invalid, error) && rover.snapshot() == before);
    auto maximum = before; maximum.moves = maxMoves; assert(rover.replace(maximum, error));
    assert(!rover.move("entry", error) && rover.snapshot() == maximum);
    Snapshot decoded = initial;
    assert(!decodeSnapshot("ROVER 2\n", decoded, error) && decoded == initial);
    assert(decodeSnapshot(bytes, decoded, error) && decoded == before);
    bool destroyed = false;
    { std::unique_ptr<Command> command = std::make_unique<Probe>(destroyed);
      assert(command->execute(rover).ok && !destroyed); }
    assert(destroyed);
    for (const auto* text : {"show", "help", "route lab"}) {
        assert(parseCommand(text, parsed, error)); auto command = makeCommand(parsed);
        assert(command->execute(rover).ok);
    }
}
"""


def completed(destination):
    shutil.copytree(PACK / "starter", destination)
    tasks = 0
    for name in SOURCES:
        learner = (destination / name).read_text()
        reference = (PACK / "solution" / name).read_text()
        pattern = r"(\s*// BEGIN TASK (\w+)\n)[\s\S]*?(\s*// END TASK \2\n)"
        bodies = {m[2]: m[0] for m in re.finditer(pattern, reference)}
        found = list(re.finditer(pattern, learner)); tasks += len(found)
        revised = re.sub(pattern, lambda m: bodies[m[2]], learner)
        assert revised == reference, name
        (destination / name).write_text(revised)
    assert tasks == 5


def encode(graph, phase="running", position="entry", moves=0):
    edges = sorted((a, b) for a, neighbors in graph.items() for b in neighbors)
    return (f"ROVER 1\nphase {phase}\nposition {position}\nmoves {moves}\nzones {len(graph)}\n"
            + "".join(f"{name}\n" for name in sorted(graph))
            + f"edges {len(edges)}\n" + "".join(f"{a} {b}\n" for a, b in edges) + "end\n")


def reachable(graph, start, target):
    seen = {start}; queue = deque([start])
    while queue:
        here = queue.popleft()
        if here == target: return True
        for nxt in graph[here]:
            if nxt not in seen: seen.add(nxt); queue.append(nxt)
    return False


def check_driver(executable, cwd):
    out, err = run([executable], cwd, stdin="")
    assert out == err == ""
    out, err = run([executable, "extra"], cwd, expected=2)
    assert out == "" and err == "Usage: rover\n"
    trace = "show\nroute dock\nstart\nmove lab\npause\nmove dock\nresume\nmove dock\nfinish\nshow\nquit\nshow\n"
    expected = ("phase ready position entry moves 0\ndock:\nentry: lab\nlab: dock\n"
                "route entry -> lab -> dock\nphase running\nposition lab moves 1\nphase paused\n"
                "phase running\nposition dock moves 2\nphase finished\n"
                "phase finished position dock moves 2\ndock:\nentry: lab\nlab: dock\n")
    out, err = run([executable], cwd, stdin=trace)
    assert out == expected and err == "Rejected: Move requires running phase.\n"
    out, err = run([executable], cwd, stdin="x" * 1025 + "\nshow\n")
    assert out.startswith("phase ready position entry moves 0\n") and err.count("Rejected:") == 1
    out, err = run([executable], cwd, stdin="start\nmove lab\nsave \"restart state.txt\"\nquit\n")
    assert out.endswith("saved\n") and err == ""
    out, err = run([executable], cwd, stdin="load \"restart state.txt\"\nshow")
    assert out.startswith("loaded\nphase running position lab moves 1\n") and err == ""
    graph = {"entry": {"lab"}, "lab": {"dock"}, "dock": set()}
    valid = encode(graph)
    damaged = [valid.replace("ROVER 1", "ROVER 2"), valid[:-1], valid + "extra\n", valid + "\n",
               valid.replace("zones 3", "zones 0"), valid.replace("zones 3", "zones 65"),
               valid.replace("moves 0", "moves -1"), valid.replace("moves 0", "moves +1"),
               valid.replace("moves 0", "moves 1000001"), valid.replace("phase running", "phase unknown"),
               valid.replace("position entry", "position nowhere"), valid.replace("entry lab", "entry absent"),
               valid.replace("edges 2", "edges 1"), valid.replace("edges 2", "edges 4097"),
               valid.replace("dock\nentry\nlab", "entry\ndock\nlab"),
               valid.replace("dock\nentry\nlab", "dock\ndock\nlab"),
               valid.replace("entry lab\nlab dock", "lab dock\nentry lab"),
               valid.replace("phase running", "phase ready").replace("moves 0", "moves 1"),
               valid.replace("moves 0", "moves 1x"), valid.replace("zones 3", "zones 3 "),
               valid.replace("entry lab", "entry  lab"), valid.replace("entry lab", "entry lab ")]
    for i, data in enumerate(damaged):
        (cwd / "damaged.txt").write_text(data)
        out, err = run([executable], cwd, stdin="start\nmove lab\nload damaged.txt\nshow\n")
        assert out.endswith("phase running position lab moves 1\ndock:\nentry: lab\nlab: dock\n"), (i, out)
        assert "Rejected:" in err, (i, err)
    rng = random.Random(6102026)
    comparisons = 0
    for case in range(32):
        names = ["entry"] + [f"z{i}" for i in range(1, 8)]
        graph = {name: {other for other in names if rng.random() < .18} for name in names}
        (cwd / "graph.txt").write_text(encode(graph))
        out, err = run([executable], cwd, stdin="load graph.txt\n" + "".join(f"route {target}\n" for target in names))
        assert err == "" and out.startswith("loaded\n")
        lines = out.splitlines()[1:]; assert len(lines) == len(names)
        for target, line in zip(names, lines):
            exists = reachable(graph, "entry", target)
            assert (line != "route unavailable") == exists
            if exists:
                path = line.removeprefix("route ").split(" -> ")
                assert path[0] == "entry" and path[-1] == target and len(path) == len(set(path))
                assert all(b in graph[a] for a, b in zip(path, path[1:]))
            comparisons += 1
    # A maximal-depth graph proves the stated recursion bound without relying on short examples.
    names = ["entry"] + [f"z{i}" for i in range(1, 64)]
    graph = {a: ({names[i+1]} if i+1 < len(names) else set()) for i, a in enumerate(names)}
    (cwd / "graph.txt").write_text(encode(graph))
    out, err = run([executable], cwd, stdin="load graph.txt\nroute z63\nsave graph-output.txt\n")
    assert err == "" and out.endswith("saved\n") and len(out.splitlines()[1].split(" -> ")) == 64
    assert (cwd / "graph-output.txt").read_text() == encode(graph)
    return comparisons, len(damaged)


def main():
    compiler = os.environ.get("CXX", "g++")
    counts = []
    with tempfile.TemporaryDirectory(prefix="cppi6-rover-native-") as tmp:
        area = Path(tmp)
        complete = area / "completed"; completed(complete)
        harness = area / "harness.cpp"; harness.write_text(HARNESS)
        for sanitized in [False, True]:
            extra = ["-fsanitize=address,undefined", "-fno-omit-frame-pointer", "-fno-pie", "-no-pie"] if sanitized else []
            for label, source in [("starter", PACK / "starter"), ("completed", complete), ("reference", PACK / "solution")]:
                folder = area / (label + ("-sanitized" if sanitized else "-ordinary")); folder.mkdir()
                app = folder / "rover"
                run([compiler, *FLAGS, *extra, *(source / name for name in SOURCES), "-o", app], folder, timeout=120)
                if label == "starter":
                    out, err = run([app], folder, stdin="show\n")
                    assert out == "" and err == "Rejected: Unfinished command parser.\n"
                    continue
                probe = folder / "probe"
                run([compiler, *FLAGS, *extra, "-I", source, harness, *(source / name for name in SOURCES[1:]), "-o", probe], folder, timeout=120)
                run([probe], folder)
                counts.append(check_driver(app, folder))
                if Path("/dev/full").exists():
                    with open('/dev/full','wb') as sink:
                        out, err = run([app], folder, expected=1, stdin="show\n", stdout_stream=sink)
                    assert out is None and "Could not write" in err
    assert len(counts) == 4 and all(row == (256,22) for row in counts), counts
    print(json.dumps({"event":"verified-rover-simulation","programVariants":6,"completedLearnerEqualsReference":True,
                      "phasePairs":16,"independentBFSComparisonsPerProgram":256,"corruptSnapshotsPerProgram":22,
                      "maxDepthRoute":64,"actualRestart":True,"realPartialWriteAndRenameRollback":True,
                      "virtualDestruction":True,"ordinaryAndSanitized":True}), flush=True)

if __name__ == "__main__": main()
