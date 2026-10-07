"""Verify real multi-file checkpoint behavior and its intentional learner bug."""

from datetime import datetime, timezone
import json
import os
from pathlib import Path
import signal
import subprocess
import tempfile


ROOT = Path(__file__).resolve().parent
PACK = ROOT / "CPPI0-Build-and-Debug-Checkpoint"
TASK = os.environ.get("CLASSES_AUDIT_PARENT_TASK_ID", "cppi0-build-debug-source")
SOURCES = ["main.cpp", "score_ledger.cpp", "score_tools.cpp"]
FLAGS = ["-std=c++20", "-Wall", "-Wextra", "-Wpedantic", "-Wconversion",
         "-Wsign-conversion", "-Werror", "-g", "-O0"]


def run(command, cwd, expected=0, timeout=45):
    child = subprocess.Popen(command, cwd=cwd, start_new_session=True,
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                             text=True)
    fields = {"parentTaskId": TASK, "cwd": str(cwd), "command": [str(c) for c in command],
              "pid": child.pid, "parentPid": os.getpid(), "timeoutSeconds": timeout}

    def record(event, **extra):
        print(json.dumps({"event": event, "time": datetime.now(timezone.utc).isoformat(),
                          **fields, **extra}), flush=True)

    record("start")
    try:
        out, err = child.communicate(timeout=timeout)
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


def check_cli(executable, work, role):
    correct = role == "solution"
    out, err = run([str(executable)], work)
    assert out == "Scores: 40 60 80\nTotal: " + ("180" if correct else "140") + "\n"
    assert err == ""
    out, err = run([str(executable), "--check"], work, expected=0 if correct else 1)
    assert len(out.splitlines()) == 7 and err == ""
    assert out.count(" PASS\n") == (7 if correct else 3)
    assert out.count(" FAIL\n") == (0 if correct else 4)
    for tokens, expected in [([], 0), (["85"], 85 if correct else 0),
                             (["0", "60"], 60), (["60", "0"], 60 if correct else 0),
                             (["100"] * 20, 2000 if correct else 1900),
                             (["000", "060"], 60),
                             (["12", "23", "34", "0", "5"], 74 if correct else 62)]:
        out, err = run([str(executable), "--scores", *tokens], work)
        scores = "".join(" " + str(int(t)) for t in tokens)
        assert out == f"Scores:{scores}\nTotal: {expected}\n" and err == ""
    out, err = run([str(executable), "--trace", "--scores", "40", "60", "80"], work)
    lines = (["trace index=0 score=40 running=40"] if correct else [])
    lines += [f"trace index=1 score=60 running={100 if correct else 60}",
              f"trace index=2 score=80 running={180 if correct else 140}"]
    assert out == "Scores: 40 60 80\n" + "\n".join(lines) + f"\nTotal: {180 if correct else 140}\n"
    assert err == ""
    for token in ["-1", "+1", "101", "2147483648", "", " 1", "1 ", "1.0", "1x", "１２"]:
        out, err = run([str(executable), "--scores", "50", token], work, expected=2)
        assert out == "" and "error:" in err
    out, err = run([str(executable), "--scores", *(["1"] * 21)], work, expected=2)
    assert out == "" and "at most 20 scores" in err
    for options in [["--unknown"], ["--check", "extra"], ["--scores", "--trace"]]:
        out, err = run([str(executable), *options], work, expected=2)
        assert out == "" and err
    out, err = run([str(executable), "--help"], work)
    assert "Usage: checkpoint" in out and "--check" in out and err == ""


HARNESS = r'''#include "score_ledger.h"
#include "score_tools.h"
#include <cassert>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>
int main() {
    int output = 47;
    for (const auto* token : {"", "-1", "+1", "101", "1x", " 1", "1 ", "9999999999999"}) {
        assert(!parseScore(token, output) && output == 47);
    }
    assert(parseScore("00085", output) && output == 85);
    ScoreLedger ledger;
    int expected = 0;
    for (int i = 0; i < 20; ++i) {
        ledger.add(i);
        expected += i;
        assert(ledger.total() == expected);
        assert(ledger.scores().size() == static_cast<std::size_t>(i + 1));
    }
    const auto before = ledger.scores();
    try { ledger.add(-1); assert(false); } catch (const std::invalid_argument&) {}
    try { ledger.add(101); assert(false); } catch (const std::invalid_argument&) {}
    try { ledger.add(50); assert(false); } catch (const std::length_error&) {}
    assert(ledger.scores() == before && ledger.total() == 190);
    ScoreLedger copy = ledger;
    ScoreLedger empty;
    copy = empty;
    assert(copy.scores().empty() && copy.total() == 0 && ledger.scores() == before);
    assert(sumScores({}) == 0 && sumScores({100}) == 100);
    std::ostringstream trace;
    assert(sumScores({85, 0, 10}, &trace) == 95);
    assert(trace.str() == "trace index=0 score=85 running=85\ntrace index=1 score=0 running=85\ntrace index=2 score=10 running=95\n");
}
'''


def main():
    # This presence gate is retained separately from the behavioral acceptance.
    run(["bash", str(ROOT / "verify-course-source.sh")], ROOT)
    compiler = os.environ.get("CXX", "clang++")
    with tempfile.TemporaryDirectory(prefix="cppi0-build-debug-") as temporary:
        work = Path(temporary)
        for role in ["starter", "solution"]:
            pack = PACK / role
            assert all((pack / name).is_file() for name in [*SOURCES, "score_ledger.h", "score_tools.h", "README.md", "Makefile"])
            for sanitizer in [False, True]:
                flags = FLAGS + (["-fsanitize=address,undefined", "-fno-sanitize-recover=all"] if sanitizer else [])
                exe = work / (role + ("-sanitized" if sanitizer else "-ordinary"))
                out, err = run([compiler, *flags, *[str(pack / name) for name in SOURCES], "-o", str(exe)], work)
                assert out == "" and err == "", "warning-clean compilation required"
                check_cli(exe, work, role)
                if role == "solution":
                    harness = work / "acceptance.cpp"
                    harness.write_text(HARNESS)
                    native = work / ("acceptance-" + str(sanitizer))
                    out, err = run([compiler, *flags, "-I" + str(pack), str(harness), str(pack / "score_ledger.cpp"), str(pack / "score_tools.cpp"), "-o", str(native)], work)
                    assert out == "" and err == ""
                    out, err = run([str(native)], work)
                    assert out == "" and err == ""
            # Build copied packs to avoid generating files in the source checkout.
            import shutil
            copied = work / role
            shutil.copytree(pack, copied)
            run(["make", "checkpoint", "checkpoint-debug"], copied)
            for name in ["checkpoint", "checkpoint-debug"]:
                check_cli(copied / name, copied, role)
            for header in ["score_ledger.h", "score_tools.h"]:
                out, _ = run(["make", "-n", "-W", header, "checkpoint", "checkpoint-debug"], copied)
                assert out.count(" -o checkpoint") == 2, header
            run(["make", "clean"], copied)
            assert not (copied / "checkpoint").exists() and not (copied / "checkpoint-debug").exists()
        build = work / "cmake"
        run(["cmake", "-S", str(ROOT), "-B", str(build), "-DCMAKE_BUILD_TYPE=Debug"], work)
        run(["cmake", "--build", str(build), "--target", "build_debug_starter", "build_debug_solution"], work)
        run(["ctest", "--test-dir", str(build), "-R", "build_debug_", "--output-on-failure"], work)
        for role in ["starter", "solution"]:
            check_cli(build / ("build_debug_" + role), work, role)
    print(json.dumps({"event": "verified", "project": "CPPI0-Build-and-Debug-Checkpoint",
                      "sourceFilesPerPack": 5, "learnerIntentionalFailures": 4,
                      "referenceChecks": 7, "nativeAndSanitizer": True,
                      "makeHeaderDependencies": True, "cmakeBothTargets": True}))


if __name__ == "__main__":
    main()
