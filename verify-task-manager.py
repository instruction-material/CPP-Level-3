"""Check real task commands, state and persistence, keeping the learner unfinished."""

from datetime import datetime, timezone
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parent
PACK = ROOT / "CPPI1-Saveable-Task-Manager"
TASK = os.environ.get("CLASSES_AUDIT_PARENT_TASK_ID", "cppi1-task-manager-source")
SOURCES = ["main.cpp", "task_manager.cpp", "command_parser.cpp", "task_storage.cpp"]
HEADERS = ["task_manager.h", "command_parser.h", "task_storage.h"]
FLAGS = ["-std=c++20", "-Wall", "-Wextra", "-Wpedantic", "-Wconversion",
         "-Wsign-conversion", "-Werror", "-g", "-O0"]
HEADER = b"CLASSES_TASKS_V1\n"


def run(command, cwd, expected=0, stdin=None, timeout=45):
    child = subprocess.Popen(command, cwd=cwd, start_new_session=True,
                             stdin=subprocess.PIPE if stdin is not None else subprocess.DEVNULL,
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
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


HARNESS = r'''
#include "task_manager.h"
#include "command_parser.h"
#include "task_storage.h"
#include <cassert>
#include <csignal>
#include <filesystem>
#include <fstream>
#include <iterator>
#include <string>
#include <vector>
#include <sys/resource.h>
using namespace taskcourse;
void write(const std::filesystem::path& path, const std::string& bytes) {
    std::ofstream out(path, std::ios::binary);
    out << bytes;
    out.close();
    assert(out);
}
std::string read(const std::filesystem::path& path) {
    std::ifstream in(path, std::ios::binary);
    assert(in);
    return {std::istreambuf_iterator<char>(in), std::istreambuf_iterator<char>()};
}
int main() {
    std::string error;
    int number = 42;
    for (const auto* text : {"", "0", "-1", "+1", "1.0", "1x", " 1", "1 ",
                             "1000000", "999999999999999999999", "１２"})
        assert(!parsePositiveId(text, number) && number == 42);
    assert(parsePositiveId("0007", number) && number == 7);
    assert(parsePositiveId("999999", number) && number == 999999);
    Command command{Verb::Done, "untouched", 33, Filter::Done};
    const auto beforeCommand = command;
    for (const std::string text : {"", "ADD \"x\"", "add x", "add \"\"", "add \"   \"",
         "add \"a\" \"b\"", "add \"a\" trailing", "add \"a\tb\"", "done +1", "done 1 2",
         "list closed", "save extra", "reload extra", "help extra", "quit extra", "unknown"}) {
        assert(!parseCommand(text, command, error) && command == beforeCommand && !error.empty());
    }
    assert(!parseCommand("add \"" + std::string(81, 'x') + "\"", command, error));
    assert(command == beforeCommand);
    assert(parseCommand(" \tadd \"  keep spaces  \"\r ", command, error));
    assert(command.verb == Verb::Add && command.text == "  keep spaces  " && error.empty());
    assert(parseCommand("done 0008", command, error) && command.id == 8);
    for (const auto* text : {"list", "list all", "list open", "list done", "save", "reload", "help", "quit"})
        assert(parseCommand(text, command, error) && error.empty());
    assert(!validTaskText(std::string(1, '\0')) && !validTaskText("é") && !validTaskText("quote\""));
    assert(validTaskText(std::string(80, 'x')) && !validTaskText(std::string(81, 'x')));
    TaskLedger ledger;
    assert(ledger.size() == 0 && ledger.select(Filter::All).empty());
    int id = 77;
    assert(!ledger.add("", id, error) && id == 77 && ledger.size() == 0);
    assert(ledger.add("first", id, error) && id == 1 && error.empty());
    assert(ledger.add("second", id, error) && id == 2);
    assert(ledger.complete(1, error) && ledger.complete(1, error));
    const std::vector<Task> expected{{1, true, "first"}, {2, false, "second"}};
    assert(ledger.tasks() == expected);
    assert((ledger.select(Filter::Open) == std::vector<Task>{{2, false, "second"}}));
    assert((ledger.select(Filter::Done) == std::vector<Task>{{1, true, "first"}}));
    auto copy = ledger.select(Filter::All);
    copy[0].text = "changed copy";
    assert(ledger.tasks() == expected && !ledger.complete(90, error));
    for (auto rows : std::vector<std::vector<Task>>{
             {{0, false, "zero"}}, {{-1, false, "negative"}}, {{1000000, false, "large"}},
             {{1, false, "one"}, {1, true, "duplicate"}}, {{2, false, "two"}, {1, false, "one"}},
             {{1, false, ""}}}) {
        assert(!ledger.replace(rows, error) && ledger.tasks() == expected);
    }
    assert(ledger.add("third", id, error) && id == 3);
    assert(ledger.replace({{999999, false, "last"}}, error));
    id = 123;
    assert(!ledger.add("exhausted", id, error) && id == 123 && ledger.size() == 1);
    assert(ledger.replace({}, error));
    for (int i = 1; i <= 100; ++i) assert(ledger.add("task", id, error) && id == i);
    const auto full = ledger.tasks();
    assert(!ledger.add("overflow", id, error) && id == 100 && ledger.tasks() == full);
    auto tooMany = full;
    tooMany.push_back({101, false, "overflow"});
    assert(!ledger.replace(tooMany, error) && ledger.tasks() == full);

    const std::filesystem::path path = "tasks.tsv";
    assert(ledger.replace(expected, error) && saveTasks(path, ledger, error));
    const std::string saved = "CLASSES_TASKS_V1\n1\t1\tfirst\n2\t0\tsecond\n";
    assert(read(path) == saved && !std::filesystem::exists("tasks.tsv.tmp"));
    assert(ledger.add("unsaved", id, error) && loadTasks(path, ledger, error));
    assert(ledger.tasks() == expected && ledger.add("after load", id, error) && id == 3);
    const auto before = ledger.tasks();
    const std::string prefix = "CLASSES_TASKS_V1\n1\t0\tvalid first row\n";
    std::vector<std::string> invalid{
        "", "wrong\n", prefix + "broken\n", prefix + "1\t1\tduplicate\n",
        prefix + "0\t0\tzero\n", prefix + "2\t2\tbad status\n", prefix + "2\t0\t\n",
        prefix + "2\t0\t   \n", prefix + "2\t0\tbad\ttext\n", prefix + "2\t0\tbad\"text\n",
        prefix + "2\t0\t" + std::string(81, 'x') + "\n", prefix + "\n",
        prefix + "2x\t0\tbad ID\n", prefix + "2\t0\t" + std::string(1, '\0') + "\n",
        std::string(65537, 'x')};
    std::string many = "CLASSES_TASKS_V1\n";
    for (int i = 1; i <= 101; ++i) many += std::to_string(i) + "\t0\ttask\n";
    invalid.push_back(many);
    for (const auto& bytes : invalid) {
        write(path, bytes);
        assert(!loadTasks(path, ledger, error) && ledger.tasks() == before && !error.empty());
        assert(read(path) == bytes);
    }
    std::filesystem::remove(path);
    assert(!loadTasks(path, ledger, error) && ledger.tasks() == before);
    assert(loadTasks(path, ledger, error, true) && ledger.size() == 0);
    write(path, "CLASSES_TASKS_V1\r\n0004\t0\t  spaces  \r\n9\t1\tdone");
    assert(loadTasks(path, ledger, error) && ledger.size() == 2 && error.empty());
    assert(ledger.tasks()[0].text == "  spaces  " && ledger.add("next", id, error) && id == 10);
    write(path, "CLASSES_TASKS_V1");
    assert(loadTasks(path, ledger, error) && ledger.size() == 0);
    assert(ledger.add("retry", id, error) && id == 1);
    write(path, saved);
    write("tasks.tsv.tmp", "busy temp");
    assert(!saveTasks(path, ledger, error) && read(path) == saved && read("tasks.tsv.tmp") == "busy temp");
    std::filesystem::remove("tasks.tsv.tmp");
    std::filesystem::create_directory("tasks.tsv.tmp");
    assert(!saveTasks(path, ledger, error) && read(path) == saved && std::filesystem::is_directory("tasks.tsv.tmp"));
    std::filesystem::remove("tasks.tsv.tmp");
    std::filesystem::create_symlink("nonexistent-target", "tasks.tsv.tmp");
    assert(!saveTasks(path, ledger, error) && read(path) == saved && std::filesystem::is_symlink("tasks.tsv.tmp"));
    std::filesystem::remove("tasks.tsv.tmp");
    std::filesystem::create_directory("directory.tsv");
    const auto current = ledger.tasks();
    assert(!saveTasks("directory.tsv", ledger, error) && !loadTasks("directory.tsv", ledger, error));
    assert(ledger.tasks() == current && !std::filesystem::exists("directory.tsv.tmp"));
    std::filesystem::create_symlink("tasks.tsv", "link.tsv");
    assert(!saveTasks("link.tsv", ledger, error) && !loadTasks("link.tsv", ledger, error));
    assert(read(path) == saved && ledger.tasks() == current);
    assert(!saveTasks("missing-parent/tasks.tsv", ledger, error) && read(path) == saved);
    // A real write failure, rather than a pre-existing path rejection.
    struct rlimit previous {};
    assert(getrlimit(RLIMIT_FSIZE, &previous) == 0);
    auto limited = previous;
    limited.rlim_cur = 10;
    const auto handler = std::signal(SIGXFSZ, SIG_IGN);
    assert(setrlimit(RLIMIT_FSIZE, &limited) == 0);
    const bool wrote = saveTasks(path, ledger, error);
    assert(setrlimit(RLIMIT_FSIZE, &previous) == 0);
    std::signal(SIGXFSZ, handler);
    assert(!wrote && read(path) == saved && !std::filesystem::exists("tasks.tsv.tmp"));
    assert(saveTasks(path, ledger, error) && read(path) == "CLASSES_TASKS_V1\n1\t0\tretry\n");
    assert(error.empty() && !std::filesystem::exists("tasks.tsv.tmp"));
}
'''


def check_cli(program, work):
    path = work / "saved tasks.tsv"
    args = [str(program), "--file", str(path)]
    out, err = run(args, work, stdin='add "first"\nadd "second"\ndone 1\nlist open\nlist done\n'
                   'list all\nsave\nquit\nadd "ignored"\n')
    assert out == ("Loaded 0\nAdded 1\nAdded 2\nCompleted 1\nTasks 1\n2 [open] second\n"
                   "Tasks 1\n1 [done] first\nTasks 2\n1 [done] first\n2 [open] second\nSaved 2\nBye.\n")
    assert not err
    saved = HEADER + b"1\t1\tfirst\n2\t0\tsecond\n"
    assert path.read_bytes() == saved
    out, err = run(args, work, stdin=' \t\r\nadd bad\ndone 99\ndone 1\nlist\nadd "unsaved"\nquit\n')
    assert out == ("Loaded 2\nCompleted 1\nTasks 2\n1 [done] first\n2 [open] second\nAdded 3\nBye.\n")
    assert err == "Error: Expected one quoted task text.\nError: Unknown task ID.\n"
    assert path.read_bytes() == saved
    out, err = run(args, work, stdin='add "eof unsaved"\n')
    assert out == "Loaded 2\nAdded 3\n" and not err and path.read_bytes() == saved
    out, err = run(args, work, stdin='add "discard"\nreload\nadd "next"\nlist done\nquit\n')
    assert out == "Loaded 2\nAdded 3\nLoaded 2\nAdded 3\nTasks 1\n1 [done] first\nBye.\n" and not err
    path.unlink()
    out, err = run(args, work, stdin='add "kept"\nreload\nlist\nquit\n')
    assert out == "Loaded 0\nAdded 1\nTasks 1\n1 [open] kept\nBye.\n"
    assert err == "Error: Task file is missing.\n" and not path.exists()
    path.write_bytes(HEADER + b"1\t0\tvalid\nbad last row\n")
    before = path.read_bytes()
    out, err = run(args, work, expected=1, stdin='add "cannot run"\nsave\n')
    assert not out and err == "Error: Invalid task file row.\n" and path.read_bytes() == before
    out, err = run([str(program), "--help"], work)
    assert "Commands: add" in out and not err and path.read_bytes() == before
    for options in [["--file"], ["--file", ""], ["--unknown"], ["--help", "extra"],
                    ["--file", str(path), "--help"]]:
        out, err = run([str(program), *options], work, expected=2)
        assert not out and err.startswith("Usage:") and path.read_bytes() == before
    default = work / "tasks.tsv"
    if default.exists():
        default.unlink()
    out, err = run([str(program)], work, stdin="save\nquit\n")
    assert out == "Loaded 0\nSaved 0\nBye.\n" and not err and default.read_bytes() == HEADER
    out, err = run([str(program)], work, stdin="list\nquit\n")
    assert out == "Loaded 0\nTasks 0\nBye.\n" and not err


def main():
    compiler = os.environ.get("CXX", "clang++")
    for role in ("starter", "solution"):
        files = {p.name for p in (PACK / role).iterdir() if p.is_file()}
        assert files == set(SOURCES + HEADERS + ["README.md", "Makefile"]), files
    assert (PACK / "starter/main.cpp").read_bytes() == (PACK / "solution/main.cpp").read_bytes()
    for name in ("task_manager.cpp", "command_parser.cpp", "task_storage.cpp"):
        assert "// TODO:" in (PACK / "starter" / name).read_text()
        assert "UNFINISHED" in (PACK / "starter" / name).read_text()
        assert (PACK / "starter" / name).read_bytes() != (PACK / "solution" / name).read_bytes()
    with tempfile.TemporaryDirectory(prefix="cppi1-task-manager-") as directory:
        work = Path(directory)
        completed = work / "completed-learner"
        shutil.copytree(PACK / "starter", completed)
        # Complete only the actual learner TODO files, retaining its driver,
        # headers and build instructions, then apply independent black-box oracles.
        for name in ("task_manager.cpp", "command_parser.cpp", "task_storage.cpp"):
            shutil.copyfile(PACK / "solution" / name, completed / name)
        for sanitized in (False, True):
            flags = FLAGS + (["-fsanitize=address,undefined", "-fno-sanitize-recover=all"] if sanitized else [])
            for role, pack in [("starter", PACK / "starter"), ("solution", PACK / "solution"),
                               ("completed-learner", completed)]:
                cwd = work / (role + ("-sanitized" if sanitized else "-ordinary"))
                cwd.mkdir()
                program = cwd / "task-manager"
                out, err = run([compiler, *flags, *[str(pack / name) for name in SOURCES], "-o", str(program)], cwd)
                assert not out and not err
                if role == "starter":
                    out, err = run([str(program)], cwd, expected=1)
                    assert not out and err == "Error: UNFINISHED: implement loading a task file.\n"
                    assert not (cwd / "tasks.tsv").exists()
                    out, err = run([str(program), "--help"], cwd)
                    assert "Commands: add" in out and not err
                else:
                    check_cli(program, cwd)
                    fixture = cwd / "acceptance.cpp"
                    fixture.write_text(HARNESS)
                    check = cwd / "acceptance"
                    out, err = run([compiler, *flags, "-I", str(pack), str(fixture),
                                    *[str(pack / name) for name in SOURCES[1:]], "-o", str(check)], cwd)
                    assert not out and not err
                    out, err = run([str(check)], cwd)
                    assert not out and not err
                print(json.dumps({"event": "checked", "role": role, "sanitized": sanitized,
                                  "unfinishedOrActualBehavior": True}))
        makepack = work / "make-pack"
        shutil.copytree(PACK / "solution", makepack)
        run(["make"], makepack)
        run(["make", "task-manager-debug"], makepack)
        (makepack / "retained.tsv").write_bytes(HEADER)
        run(["make", "clean"], makepack)
        assert not (makepack / "task-manager").exists() and not (makepack / "task-manager-debug").exists()
        assert (makepack / "retained.tsv").read_bytes() == HEADER
        build = work / "cmake"
        run(["cmake", "-S", str(ROOT), "-B", str(build)], work)
        run(["cmake", "--build", str(build), "--target", "task_manager_starter", "task_manager_solution"], work)
        out, err = run([str(build / "task_manager_starter")], work, expected=1)
        assert not out and "UNFINISHED" in err
        check_cli(build / "task_manager_solution", work)
    print(json.dumps({"event": "verified", "project": "CPPI1-Saveable-Task-Manager",
                      "commandStateAndPersistence": True, "lateBadRowsPreserveState": True,
                      "realWriteFailureAndRetry": True, "ordinaryAndSanitized": True,
                      "starterIncomplete": True, "completedLearnerAndReference": True}))


if __name__ == "__main__":
    main()
