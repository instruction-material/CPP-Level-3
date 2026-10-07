"""Check notebook output and examples against real paired checkpoint builds."""

import ast
import json
import os
from pathlib import Path
import tempfile

ROOT = Path(__file__).resolve().parent
tree = ast.parse((ROOT / "verify-build-debug.py").read_text())
selected = [node for node in tree.body if isinstance(node, (ast.Import, ast.ImportFrom))
            or isinstance(node, ast.FunctionDef) and node.name == "run"]
namespace = {"TASK": os.environ.get("CLASSES_AUDIT_PARENT_TASK_ID", "cppi0-notebook-source")}
exec(compile(ast.Module(body=selected, type_ignores=[]), "verified-process-helper", "exec"), namespace)
run = namespace["run"]
FLAGS = ["-std=c++20", "-Wall", "-Wextra", "-Wpedantic", "-Werror", "-g", "-O0"]
with tempfile.TemporaryDirectory(prefix="cppi0-notebook-") as directory:
    work = Path(directory)
    for role in ("starter", "solution"):
        folder = ROOT / "CPPI0-Warnings-and-Debugger-Notebook" / role
        notes = (folder / "EVIDENCE.md").read_text()
        assert "[record]" in notes if role == "starter" else "[record]" not in notes
        assert "INPUT_CASE_COUNT" not in (folder / "main.cpp").read_text()
        for sanitized in (False, True):
            flags = FLAGS + (["-fsanitize=address,undefined", "-fno-sanitize-recover=all"] if sanitized else [])
            printer = work / (role + "-notebook")
            printer_flags = [flag.replace("-std=c++20", "-std=c++17") for flag in flags]
            run(["clang++", *printer_flags, str(folder / "main.cpp"), "-o", str(printer)], work)
            out, err = run([str(printer)], work)
            assert out == notes and err == ""
            checkpoint = ROOT / "CPPI0-Build-and-Debug-Checkpoint" / role
            executable = work / (role + "-checkpoint")
            run(["clang++", *flags, *[str(checkpoint / name) for name in
                ("main.cpp", "score_ledger.cpp", "score_tools.cpp")], "-o", str(executable)], work)
            out, err = run([str(executable), "--scores", "85"], work)
            assert out == "Scores: 85\nTotal: " + ("0" if role == "starter" else "85") + "\n" and err == ""
            out, err = run([str(executable), "--check"], work, expected=1 if role == "starter" else 0)
            assert out.count(" PASS\n") == (3 if role == "starter" else 7)
            assert out.count(" FAIL\n") == (4 if role == "starter" else 0) and err == ""
            out, err = run([str(executable), "--trace", "--scores", "40", "60", "80"], work)
            if role == "starter":
                expected = "Scores: 40 60 80\ntrace index=1 score=60 running=60\ntrace index=2 score=80 running=140\nTotal: 140\n"
            else:
                expected = "Scores: 40 60 80\ntrace index=0 score=40 running=40\ntrace index=1 score=60 running=100\ntrace index=2 score=80 running=180\nTotal: 180\n"
            assert out == expected and err == ""
            if role == "solution":
                assert "```text\n" + expected + "```" in notes
                for args, expected in [([], "Scores:\nTotal: 0\n"), (["60", "0"], "Scores: 60 0\nTotal: 60\n")]:
                    out, err = run([str(executable), "--scores", *args], work)
                    assert out == expected and err == ""
                out, err = run([str(executable), "--scores", "50", "-1"], work, expected=2)
                assert out == "" and "error:" in err
print(json.dumps({"event": "verified", "project": "CPPI0-Warnings-and-Debugger-Notebook",
                  "separateWorksheetAndExample": True, "examplesMatchActualCheckpoint": True,
                  "ordinaryAndSanitized": True, "noChecklistGrading": True}))
