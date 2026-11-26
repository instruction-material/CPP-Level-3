"""Exercise the supplied scanner roles and line-boundary cases."""

import json
import os
from pathlib import Path
import runpy
import tempfile

ROOT = Path(__file__).resolve().parent
PACK = ROOT / "CPPI1-Mini-Command-Scanner"
run = runpy.run_path(str(ROOT / "verify-build-debug.py"))["run"]
FLAGS = ["-std=c++20", "-Wall", "-Wextra", "-Wpedantic", "-Werror"]

EXPECTED = "\n".join([
    "1 WORD ADD", "1 WORD task", "1 STRING write parser", "1 WORD PRIORITY",
    "1 NUMBER 2", "2 WORD DONE", "2 WORD task", "4 WORD QUERY", "4 WORD task",
    "4 SYMBOL ?", "5 WORD BAD", "5 UNKNOWN @", "6 END ", "",
])

HARNESS = r"""
#include <cassert>
#include <initializer_list>

void expect(const std::string& input, std::initializer_list<Token> expected) {
    Scanner scanner(input);
    const auto observed = scanner.scan();
    assert(observed.size() == expected.size());
    auto token = observed.begin();
    for (const auto& wanted : expected) {
        assert(token->type == wanted.type);
        assert(token->lexeme == wanted.lexeme);
        assert(token->line == wanted.line);
        ++token;
    }
}

int main() {
    using enum TokenType;
    expect("", {{End, "", 1}});
    expect("# last line", {{End, "", 1}});
    expect("# ignored\r\nword_2 009\n", {{Word, "word_2", 2}, {Number, "009", 2}, {End, "", 3}});
    expect("\"task #1\"# note\n", {{StringLiteral, "task #1", 1}, {End, "", 2}});
    expect("\"\"", {{StringLiteral, "", 1}, {End, "", 1}});
    expect("\"two\nlines\" tail", {{StringLiteral, "two\nlines", 1}, {Word, "tail", 2}, {End, "", 2}});
    expect("\n\"open\nnext", {{Unknown, "open\nnext", 2}, {End, "", 3}});
    expect("a(9),:?", {{Word, "a", 1}, {Symbol, "(", 1}, {Number, "9", 1},
        {Symbol, ")", 1}, {Symbol, ",", 1}, {Symbol, ":", 1}, {Symbol, "?", 1}, {End, "", 1}});
    expect("\t_2 -3\r@", {{Unknown, "_", 1}, {Number, "2", 1}, {Unknown, "-", 1},
        {Number, "3", 1}, {Unknown, "@", 1}, {End, "", 1}});
}
"""


def check_demonstration(executable, work, role):
    out, err = run([str(executable)], work)
    assert err == ""
    if role == "solution":
        assert out == EXPECTED
    else:
        assert out.startswith("1 WORD ADD\n1 WORD task\n")
        assert "4 SYMBOL ?\n5 WORD BAD\n5 UNKNOWN @\n6 END \n" in out
        assert "1 STRING write parser\n" not in out and "1 NUMBER 2\n" not in out
        assert "3 WORD comment\n" in out


def main():
    compiler = os.environ.get("CXX", "c++")
    readme = (PACK / "README.md").read_bytes()
    with tempfile.TemporaryDirectory(prefix="cpp-mini-scanner-") as tmp:
        work = Path(tmp)
        for role in ("starter", "solution"):
            assert (PACK / role / "README.md").read_bytes() == readme
            program = work / role
            run([compiler, *FLAGS, str(PACK / role / "main.cpp"), "-o", str(program)], work)
            check_demonstration(program, work, role)

        source = (PACK / "solution" / "main.cpp").read_text()
        before_driver, marker, _ = source.partition("\nint main() {")
        assert marker
        harness_file = work / "cases.cpp"
        harness_file.write_text(before_driver + "\n" + HARNESS)
        for suffix, flags in (("ordinary", []), ("sanitized", [
            "-g", "-fsanitize=address,undefined", "-fno-omit-frame-pointer",
        ])):
            executable = work / suffix
            run([compiler, *FLAGS, *flags, str(harness_file), "-o", str(executable)], work)
            assert run([str(executable)], work) == ("", "")

        build = work / "build"
        targets = ("command_scanner_starter", "command_scanner_solution")
        run(["cmake", "-S", str(ROOT), "-B", str(build)], work)
        run(["cmake", "--build", str(build), "--target", *targets], work)
        for role, target in zip(("starter", "solution"), targets, strict=True):
            check_demonstration(build / target, work, role)

    print(json.dumps({"project": PACK.name, "nativeAndSanitizedCases": 9, "cmakeBothRoles": True,
                      "readmeInBothRoles": True, "sharedSampleVerified": True}))


if __name__ == "__main__":
    main()
