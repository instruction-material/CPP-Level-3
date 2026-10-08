"""Verify Make and preserved CMake targets for all four CPPI4 packs."""

from datetime import datetime, timezone
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import tempfile

SOURCE = Path(__file__).resolve().parent
TASK = os.environ.get("CLASSES_AUDIT_PARENT_TASK_ID", "cppi4-candidate-builds")
PREVIOUS = b"previous accepted report\n"
REPORT = b"CPPI4_REPORT_V1\nAda\t84\tpass\nLin\t59\treview\nTOTAL\t2\t143\n"
PACKS = [
    ("CPPI4-Resource-Safe-File-Processor", "starter", "file_processor_starter"),
    ("CPPI4-Resource-Safe-File-Processor", "solution", "file_processor_solution"),
    ("CPPI4-Ownership-Rewrite-Reflection", "starter", "ownership_rewrite_starter"),
    ("CPPI4-Ownership-Rewrite-Reflection", "solution", "ownership_rewrite_solution"),
]


def execute(command, cwd, expected=0, timeout=60):
    child = subprocess.Popen(command, cwd=cwd, start_new_session=True,
                             stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
    fields = {"parentTaskId": TASK, "cwd": str(cwd), "command": command,
              "pid": child.pid, "parentPid": os.getpid(), "timeoutSeconds": timeout}

    def record(event, **extra):
        print(json.dumps({"event": event, **fields, **extra,
                          "time": datetime.now(timezone.utc).isoformat()}), flush=True)

    record("start")
    try:
        output, error = child.communicate(timeout=timeout)
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
    assert child.returncode == expected, (command, child.returncode, output, error)
    assert b"AddressSanitizer" not in error and b"runtime error:" not in error, error
    return output, error


def check_program(binary, directory, pack, role):
    if pack == "CPPI4-Resource-Safe-File-Processor":
        (directory / "report.tsv").write_bytes(PREVIOUS)
        output, error = execute([str(binary)], directory, 1 if role == "starter" else 0)
        if role == "starter":
            assert output == b"" and b"Unfinished task: processFile." in error
            assert (directory / "report.tsv").read_bytes() == PREVIOUS
        else:
            assert (output, error) == (b"Published 2 records; total 143.\n", b"")
            assert (directory / "report.tsv").read_bytes() == REPORT
        assert not (directory / "report.tsv.stage").exists()
        assert not (directory / "report.tsv.stage").is_symlink()
    else:
        document = "NOTES.md" if role == "starter" else "WORKED.md"
        assert execute([str(binary)], directory) == ((directory / document).read_bytes(), b"")
        assert execute([str(binary), "extra"], directory, 2) == (b"", b"Usage: main\n")


def main():
    with tempfile.TemporaryDirectory(prefix="cppi4-build-") as name:
        work = Path(name)
        snapshot = work / "source"
        snapshot.mkdir()
        for pack in {entry[0] for entry in PACKS}:
            shutil.copytree(SOURCE / pack, snapshot / pack)
        # CMake configures all preserved public targets, so include their sources.
        for path in SOURCE.iterdir():
            if path.is_dir() and path.name.startswith("CPPI") and not (snapshot/path.name).exists():
                shutil.copytree(path, snapshot/path.name)
        shutil.copyfile(SOURCE / "CMakeLists.txt", snapshot / "CMakeLists.txt")
        for pack, role, _target in PACKS:
            directory = snapshot / pack / role
            execute(["make", "CXX=g++", "main", "main-debug"], directory)
            for filename in ["main", "main-debug"]:
                check_program(directory / filename, directory, pack, role)
            execute(["make", "clean"], directory)
            assert not (directory / "main").exists() and not (directory / "main-debug").exists()
        build = work / "cmake"
        execute(["cmake", "-S", str(snapshot), "-B", str(build),
                 "-DCMAKE_CXX_COMPILER=g++"], work)
        execute(["cmake", "--build", str(build), "--parallel", "1", "--target",
                 *[row[2] for row in PACKS]], work, timeout=120)
        for pack, role, target in PACKS:
            check_program(build / target, snapshot / pack / role, pack, role)
    print(json.dumps({"event": "verified-cppi4-builds", "makePacks": 4,
                      "makeOrdinaryAndSanitized": True, "cmakeTargets": 4,
                      "untouchedLearnerPreservesOutput": True,
                      "referenceReportBytes": True, "exactWorksheetPrinters": 2}))


if __name__ == "__main__":
    main()
