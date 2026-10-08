"""Verify real CPPI4 behavior, source roles and bounded failures."""

from contextlib import ExitStack
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import resource
import signal
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parent
PACK = ROOT / "CPPI4-Resource-Safe-File-Processor"
TASK = os.environ.get("CLASSES_AUDIT_PARENT_TASK_ID", "cppi4-file-processor-source")
BASE_FLAGS = ["-Wall", "-Wextra", "-Wpedantic", "-Wconversion", "-Wsign-conversion",
              "-Werror", "-g", "-O0"]
HEADER = b"CPPI4_SCORES_V1\n"
PREVIOUS = b"previous accepted report\n"
SIGNATURES = [
    "Record parseScoreRow(const std::string& line)",
    "std::vector<Record> readScores(const fs::path& inputPath)",
    "Summary writeReport(std::ostream& output, const std::vector<Record>& records)",
    "Summary processFile(const fs::path& inputPath, const fs::path& outputPath)",
]


def execute(command, cwd, expected=0, limit=None, timeout=45, stdout_path=None):
    def set_file_limit():
        signal.signal(signal.SIGXFSZ, signal.SIG_IGN)
        resource.setrlimit(resource.RLIMIT_FSIZE, (limit, limit))
    with ExitStack() as streams:
        target = streams.enter_context(open(stdout_path, "wb")) if stdout_path else subprocess.PIPE
        child = subprocess.Popen(command, cwd=cwd, start_new_session=True,
                                 stdin=subprocess.DEVNULL, stdout=target,
                                 stderr=subprocess.PIPE, text=True,
                                 preexec_fn=set_file_limit if limit is not None else None)
        fields = {"parentTaskId": TASK, "cwd": str(cwd), "command": list(map(str, command)),
                  "pid": child.pid, "parentPid": os.getpid(), "timeoutSeconds": timeout}
        def event(kind, **extra):
            print(json.dumps({"event": kind, "time": datetime.now(timezone.utc).isoformat(),
                              **fields, **extra}), flush=True)
        event("start")
        try:
            output, error = child.communicate(timeout=timeout)
        except BaseException:
            os.killpg(child.pid, signal.SIGTERM)
            try:
                child.wait(timeout=5)
            except subprocess.TimeoutExpired:
                os.killpg(child.pid, signal.SIGKILL)
                child.wait()
            event("child-process-group-cleanup", exitCode=child.returncode)
            raise
        event("end", exitCode=child.returncode)
    output = output or ""
    assert child.returncode == expected, (command, child.returncode, output, error)
    assert "AddressSanitizer" not in error and "runtime error:" not in error, error
    return output, error


def body_range(text, signature):
    opening = text.index("{", text.index(signature) + len(signature))
    depth = 1
    ending = opening + 1
    # These named bodies contain no braces inside string/character literals.
    while depth:
        if text[ending] == "{":
            depth += 1
        elif text[ending] == "}":
            depth -= 1
        ending += 1
    return opening + 1, ending - 1


def complete_learner(learner, reference):
    result = learner
    for signature in SIGNATURES:
        start, end = body_range(result, signature)
        reference_start, reference_end = body_range(reference, signature)
        assert "// TODO:" in result[start:end]
        result = result[:start] + reference[reference_start:reference_end] + result[end:]
    assert result == reference, "Only four named task bodies may differ."
    return result


def report_model(rows):
    """Independent plain-row model, without reading implementation output."""
    lines = ["CPPI4_REPORT_V1"]
    total = 0
    for name, score in rows:
        total += score
        lines.append(name + "\t" + str(score) + "\t" + ("pass" if score >= 60 else "review"))
    lines.append("TOTAL\t" + str(len(rows)) + "\t" + str(total))
    return ("\n".join(lines) + "\n").encode("ascii")


def assert_no_stage(directory, output="report.tsv"):
    stage = directory / (output + ".stage")
    assert not stage.exists()
    assert not stage.is_symlink()


def valid_cases(binary, directory):
    cases = [
        (HEADER, []),
        (HEADER + b"Ada\t84\nLin\t59\n", [("Ada", 84), ("Lin", 59)]),
        (b"CPPI4_SCORES_V1\r\n  keep spaces  \t00060\r\nrepeat\t0\r\nrepeat\t100",
         [("  keep spaces  ", 60), ("repeat", 0), ("repeat", 100)]),
        (HEADER + b"Edge\t59\nEdge\t60\n", [("Edge", 59), ("Edge", 60)]),
        (HEADER + b"x" * 40 + b"\t100", [("x" * 40, 100)]),
        (HEADER + b"a\t" + b"0" * 123 + b"100\n", [("a", 100)]),
        (HEADER + b"r\t100\n" * 100, [("r", 100)] * 100),
    ]
    for index, (data, rows) in enumerate(cases):
        (directory / "scores.tsv").write_bytes(data)
        (directory / "report.tsv").write_bytes(PREVIOUS)
        arguments = [str(binary)] if index % 2 == 0 else [str(binary), "scores.tsv", "report.tsv"]
        output, error = execute(arguments, directory)
        assert error == ""
        assert output == f"Published {len(rows)} records; total {sum(score for _, score in rows)}.\n"
        assert (directory / "report.tsv").read_bytes() == report_model(rows)
        assert (directory / "scores.tsv").read_bytes() == data
        assert_no_stage(directory)
    # First publication must also work when the chosen output does not exist.
    rows = [("Fresh", 60)]
    data = HEADER + b"Fresh\t60\n"
    (directory / "scores.tsv").write_bytes(data)
    old_default_report = (directory / "report.tsv").read_bytes()
    fresh = directory / "first-report.tsv"
    assert not fresh.exists() and not fresh.is_symlink()
    output, error = execute([str(binary), "scores.tsv", fresh.name], directory)
    assert (output, error) == ("Published 1 records; total 60.\n", "")
    assert fresh.read_bytes() == report_model(rows)
    assert (directory / "scores.tsv").read_bytes() == data
    assert (directory / "report.tsv").read_bytes() == old_default_report
    assert_no_stage(directory, fresh.name)
    fresh.unlink()
    return len(cases) + 1


def rejected_cases(binary, directory):
    invalid = [b"", b"wrong\n", HEADER + b"\n", HEADER + b"x\n", HEADER + b"x\t1\t2\n",
               HEADER + b"\t5\n", HEADER + b"   \t5\n", HEADER + b"x" * 41 + b"\t5\n",
               HEADER + b"x\x00\t5\n", HEADER + b"\xc3\xa9\t5\n", HEADER + b"x\r\t5\n",
               HEADER + b"good\t70\nbroken\n", HEADER + b"x\t0\n" * 101,
               HEADER + b"a\t" + b"0" * 124 + b"100\n", b"x" * 16385]
    for token in [b"", b"-1", b"+1", b"101", b"1.0", b" 1", b"1 ", b"1x", b"9999999999999999999999"]:
        invalid.append(HEADER + b"valid\t70\nx\t" + token + b"\n")
    for data in invalid:
        (directory / "scores.tsv").write_bytes(data)
        (directory / "report.tsv").write_bytes(PREVIOUS)
        output, error = execute([str(binary)], directory, expected=1)
        assert output == "" and error.startswith("Processing stopped: ")
        assert (directory / "report.tsv").read_bytes() == PREVIOUS
        assert (directory / "scores.tsv").read_bytes() == data
        assert_no_stage(directory)
    return len(invalid)


def path_failures(binary, directory):
    good = HEADER + b"Ada\t84\n"
    source = directory / "scores.tsv"
    destination = directory / "report.tsv"
    source.write_bytes(good)
    destination.write_bytes(PREVIOUS)
    for arguments in [["missing.tsv", "report.tsv"], ["scores.tsv", "missing/report.tsv"],
                      ["scores.tsv", "scores.tsv"], ["scores.tsv", "./scores.tsv"],
                      ["scores.tsv", "report.tsv/"]]:
        output, error = execute([str(binary), *arguments], directory, expected=1)
        assert output == "" and error
        assert source.read_bytes() == good and destination.read_bytes() == PREVIOUS
        assert_no_stage(directory)
    execute([str(binary), "only-one-path"], directory, expected=2)
    execute([str(binary), "a", "b", "c"], directory, expected=2)
    destination.unlink()
    destination.mkdir()
    execute([str(binary)], directory, expected=1)
    assert destination.is_dir()
    destination.rmdir()
    for target in ["scores.tsv", "missing-target"]:
        destination.symlink_to(target)
        execute([str(binary)], directory, expected=1)
        assert destination.is_symlink() and os.readlink(destination) == target
        destination.unlink()
        assert_no_stage(directory)
    os.link(source, destination)
    execute([str(binary)], directory, expected=1)
    assert source.read_bytes() == destination.read_bytes() == good
    destination.unlink()
    destination.write_bytes(PREVIOUS)
    stage = directory / "report.tsv.stage"
    stage.write_bytes(b"foreign staging file\n")
    execute([str(binary)], directory, expected=1)
    assert stage.read_bytes() == b"foreign staging file\n"
    stage.unlink()
    stage.mkdir()
    (stage / "foreign.txt").write_bytes(b"foreign staging contents\n")
    execute([str(binary)], directory, expected=1)
    assert (stage / "foreign.txt").read_bytes() == b"foreign staging contents\n"
    (stage / "foreign.txt").unlink()
    stage.rmdir()
    stage.symlink_to("missing-staging-target")
    execute([str(binary)], directory, expected=1)
    assert stage.is_symlink() and os.readlink(stage) == "missing-staging-target"
    stage.unlink()
    assert destination.read_bytes() == PREVIOUS and source.read_bytes() == good


def partial_write_and_retry(binary, directory):
    rows = [("record" + str(i), 100) for i in range(100)]
    data = HEADER + b"".join((name + "\t100\n").encode() for name, _ in rows)
    (directory / "scores.tsv").write_bytes(data)
    (directory / "report.tsv").write_bytes(PREVIOUS)
    output, error = execute([str(binary)], directory, expected=1, limit=128)
    assert output == "" and ("write failed" in error or "flush failed" in error or "close failed" in error)
    assert (directory / "report.tsv").read_bytes() == PREVIOUS
    assert (directory / "scores.tsv").read_bytes() == data
    assert_no_stage(directory)
    execute([str(binary)], directory)
    assert (directory / "report.tsv").read_bytes() == report_model(rows)
    assert_no_stage(directory)


def post_commit_acknowledgment_failure(binary, directory):
    assert Path("/dev/full").exists(), "Hosted Linux /dev/full fault is required."
    rows = [("Ada", 84)]
    data = HEADER + b"Ada\t84\n"
    (directory / "scores.tsv").write_bytes(data)
    (directory / "report.tsv").write_bytes(PREVIOUS)
    output, error = execute([str(binary)], directory, expected=1, stdout_path="/dev/full")
    assert output == "" and error == "Report committed; success message could not be written.\n"
    assert (directory / "report.tsv").read_bytes() == report_model(rows)
    assert (directory / "scores.tsv").read_bytes() == data
    assert_no_stage(directory)


def main():
    learner = (PACK / "starter/main.cpp").read_text()
    reference = (PACK / "solution/main.cpp").read_text()
    completed = complete_learner(learner, reference)
    results = []
    resource_probe_results = []
    with tempfile.TemporaryDirectory(prefix="cppi4-file-processor-") as name:
        work = Path(name)
        for standard in [17, 20]:
            for sanitized in [False, True]:
                suffix = f"{standard}-{'sanitized' if sanitized else 'ordinary'}"
                flags = [f"-std=c++{standard}", *BASE_FLAGS]
                if sanitized:
                    flags.extend(["-fsanitize=address,undefined", "-fno-omit-frame-pointer", "-fno-pie", "-no-pie"])
                for role, code in [("learner", learner), ("reference", reference), ("completed", completed)]:
                    source = work / f"{role}-{suffix}.cpp"
                    source.write_text(code)
                    binary = work / f"{role}-{suffix}"
                    execute(["g++", *flags, str(source), "-o", str(binary)], work)
                    run_directory = work / f"run-{role}-{suffix}"
                    run_directory.mkdir()
                    if role == "learner":
                        (run_directory / "scores.tsv").write_bytes(HEADER + b"Ada\t84\n")
                        (run_directory / "report.tsv").write_bytes(PREVIOUS)
                        output, error = execute([str(binary)], run_directory, expected=1)
                        assert output == "" and "Unfinished task: processFile." in error
                        assert (run_directory / "report.tsv").read_bytes() == PREVIOUS
                        assert_no_stage(run_directory)
                        results.append({"role": role, "standard": standard, "sanitized": sanitized,
                                        "unfinishedPreservesOutput": True})
                    else:
                        accepted = valid_cases(binary, run_directory)
                        rejected = rejected_cases(binary, run_directory)
                        path_failures(binary, run_directory)
                        partial_write_and_retry(binary, run_directory)
                        post_commit_acknowledgment_failure(binary, run_directory)
                        results.append({"role": role, "standard": standard, "sanitized": sanitized,
                                        "acceptedCases": accepted, "rejectedCases": rejected,
                                        "pathAndStagingPreserved": True, "realPartialWriteAndRetry": True,
                                        "postCommitFailedAcknowledgmentPreservesPublishedBytes": True})
        (work / "program-under-test.cpp").write_text(reference)
        probe_source = work / "resource-probe.cpp"
        probe_source.write_text((ROOT / "file-processor-resource-probe.cpp").read_text())
        for standard in [17, 20]:
            for sanitized in [False, True]:
                suffix = f"{standard}-{'sanitized' if sanitized else 'ordinary'}"
                flags = [f"-std=c++{standard}", *BASE_FLAGS]
                if sanitized:
                    flags.extend(["-fsanitize=address,undefined", "-fno-omit-frame-pointer", "-fno-pie", "-no-pie"])
                binary = work / ("resource-probe-" + suffix)
                execute(["g++", *flags, str(probe_source), "-o", str(binary)], work)
                directory = work / ("resource-probe-case-" + suffix)
                directory.mkdir()
                output, error = execute([str(binary), str(directory)], work)
                assert error == "" and output == "Observed bounded reads, partial output, borrowed paths, ownership and unwinding.\n"
                assert not list(directory.iterdir())
                resource_probe_results.append({"standard": standard, "sanitized": sanitized,
                    "boundedReaderAndFailingStream": True, "counterDoesNotWrap": True,
                    "invalidRowsEmitNothing": True, "partialOutputPreservesSource": True,
                    "ownerObserverNormalUnwindAndCollision": True})
        # Remove the staged source immediately before the actual rename.
        # The prior accepted report still exists, so verify its exact bytes.
        marker = "    fs::rename(temporary, outputPath, error);"
        assert reference.count(marker) == 1
        fault = ("    std::error_code injected;\n"
                 "    if (!fs::remove(temporary, injected) || injected)\n"
                 "        throw std::logic_error(\"Fault could not remove staged file.\");\n")
        faulted = reference.replace(marker, fault + marker)
        source = work / "rename-failure.cpp"
        source.write_text(faulted)
        binary = work / "rename-failure"
        execute(["g++", "-std=c++20", *BASE_FLAGS, str(source), "-o", str(binary)], work)
        directory = work / "rename-failure-case"
        directory.mkdir()
        input_bytes = HEADER + b"Ada\t84\n"
        (directory / "scores.tsv").write_bytes(input_bytes)
        (directory / "report.tsv").write_bytes(PREVIOUS)
        output, error = execute([str(binary)], directory, expected=1)
        assert output == "" and "Output publication failed." in error
        assert (directory / "report.tsv").read_bytes() == PREVIOUS
        assert (directory / "scores.tsv").read_bytes() == input_bytes
        assert_no_stage(directory)
    print(json.dumps({"event": "verified-file-processor", "parentTaskId": TASK,
                      "variants": results, "completedLearnerTaskBodiesOnly": True,
                      "renameFailure": "staged source removed immediately before actual rename; prior output preserved",
                      "buildWorkflowGate": "verify-cppi4-builds.py",
                      "resourceProbeVariants": resource_probe_results,
                      "ownershipWorksheetGate": "verify-ownership-worksheet.py"}), flush=True)


if __name__ == "__main__":
    main()
