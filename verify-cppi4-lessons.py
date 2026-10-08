"""Verify actual ownership and error-boundary lesson programs."""

from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import signal
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parent
TASK = os.environ.get("CLASSES_AUDIT_PARENT_TASK_ID", "cppi4-lesson-candidates")
FLAGS = ["-Wall", "-Wextra", "-Wpedantic", "-Wconversion",
         "-Wsign-conversion", "-Werror", "-O0", "-g"]


def execute(command, cwd, expected=0):
    child = subprocess.Popen(command, cwd=cwd, start_new_session=True,
                             stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
    fields = {"parentTaskId": TASK, "cwd": str(cwd), "command": command,
              "pid": child.pid, "parentPid": os.getpid(), "timeoutSeconds": 60}

    def record(event, **extra):
        print(json.dumps({"event": event, **fields, **extra,
                          "time": datetime.now(timezone.utc).isoformat()}),
              flush=True)

    record("start")
    try:
        output, error = child.communicate(timeout=60)
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
    if expected == "compile-rejected":
        assert child.returncode != 0 and b"deleted" in error.lower(), error
    else:
        assert child.returncode == expected, (command, child.returncode, output, error)
    assert b"AddressSanitizer" not in error and b"runtime error:" not in error, error
    return output, error


def program(title):
    document = ROOT / "CPPI4-Resource-Safe-File-Processor" / ("OWNERSHIP-LESSON.md" if title == "ownership" else "ERROR-BOUNDARY-LESSON.md")
    examples = re.findall(r"```cpp\n(.*?)\n```", document.read_text(), re.S)
    assert len(examples) == 1
    return document, examples[0] + "\n"


def main():
    compiler = os.environ.get("CXX", "c++")
    ownership_doc, ownership = program("ownership")
    boundary_doc, boundary = program("error-boundary")
    with tempfile.TemporaryDirectory(prefix="cppi4-lesson-native-") as directory:
        cwd = Path(directory)
        for standard in [17, 20]:
            for sanitized in [False, True]:
                flags = [f"-std=c++{standard}", *FLAGS]
                if sanitized:
                    flags += ["-fsanitize=address,undefined",
                              "-fno-sanitize-recover=all", "-fno-omit-frame-pointer", "-fno-pie", "-no-pie"]
                for changed, values in [(False, [84, 91, 76]),
                                        (True, [0, 60, 100])]:
                    text = ownership
                    if changed:
                        for index, old in enumerate([84, 91, 76]):
                            text = text.replace(f"first[{index}] = {old};",
                                                f"first[{index}] = {values[index]};")
                        text = text.replace("scores{84, 91, 76}", "scores{0, 60, 100}")
                    (cwd / "ownership.cpp").write_text(text)
                    execute([compiler, *flags, "ownership.cpp", "-o", "ownership"], cwd)
                    row = " ".join(map(str, values)) + "\n"
                    expected = (row + "first empty: true\n" + row + row).encode()
                    assert execute(["./ownership"], cwd) == (expected, b"")

                (cwd / "boundary.cpp").write_text(boundary)
                execute([compiler, *flags, "boundary.cpp", "-o", "boundary"], cwd)
                assert execute(["./boundary"], cwd) == (b"Accepted: 84 91 76\n", b"")
                assert execute(["./boundary", "reject"], cwd, 1) == (
                    b"Accepted: 84\n", b"Rejected: Score outside 0 through 100.\n")
                assert execute(["./boundary", "extra"], cwd, 2) == (
                    b"", b"Usage: boundary [reject]\n")
                for score in [0, 59, 60, 100, -1, 101]:
                    text = boundary.replace("{91, argc == 2 ? 101 : 76}", f"{{91, {score}}}")
                    (cwd / "boundary-case.cpp").write_text(text)
                    execute([compiler, *flags, "boundary-case.cpp", "-o", "boundary-case"], cwd)
                    if 0 <= score <= 100:
                        assert execute(["./boundary-case"], cwd) == (
                            f"Accepted: 84 91 {score}\n".encode(), b"")
                    else:
                        assert execute(["./boundary-case"], cwd, 1) == (
                            b"Accepted: 84\n", b"Rejected: Score outside 0 through 100.\n")

                # A direct mutation retains the valid prefix when a late row fails.
                mutation = boundary.replace("    auto candidate = accepted;\n", "")
                mutation = mutation.replace("candidate.push_back(score)", "accepted.push_back(score)")
                mutation = mutation.replace("    accepted.swap(candidate);\n", "")
                (cwd / "boundary-mutation.cpp").write_text(mutation)
                execute([compiler, *flags, "boundary-mutation.cpp", "-o", "boundary-mutation"], cwd)
                assert execute(["./boundary-mutation", "reject"], cwd, 1) == (
                    b"Accepted: 84 91\n", b"Rejected: Score outside 0 through 100.\n")

                copying = ownership.replace("std::move(first)", "first")
                (cwd / "ownership-copy.cpp").write_text(copying)
                execute([compiler, *flags, "-fsyntax-only", "ownership-copy.cpp"],
                        cwd, "compile-rejected")
    print(json.dumps({"event": "verified-cppi4-lessons",
                      "standards": [17, 20], "ordinaryAndSanitized": True,
                      "changedOwnershipScores": [0, 60, 100],
                      "boundaryScores": [0, 59, 60, 100, -1, 101],
                      "lateFailureComparedWithDirectMutation": True,
                      "copyOwnershipCompileRejected": True,
                      "documents": {str(p): hashlib.sha256(p.read_bytes()).hexdigest()
                                    for p in [ownership_doc, boundary_doc]}}))


if __name__ == "__main__":
    main()
