"""Independent selective-import acceptance, including real native workflows."""

from datetime import datetime, timezone
import importlib.util
import json
import os
from pathlib import Path
import random
import shutil
import tempfile

ROOT = Path(__file__).resolve().parent
PACK = ROOT / 'CPPI1-Import-and-Reject-Bad-Rows'
SOURCES = ['main.cpp', 'task_manager.cpp', 'command_parser.cpp', 'task_storage.cpp', 'task_import.cpp']
HEADERS = ['task_manager.h', 'command_parser.h', 'task_storage.h', 'task_import.h']
FLAGS = ['-std=c++20', '-Wall', '-Wextra', '-Wpedantic', '-Wconversion', '-Wsign-conversion', '-Werror', '-g', '-O0']
HEADER = b'CLASSES_TASKS_V1\n'

HARNESS = r'''
#include "task_import.h"
#include "command_parser.h"
#include "task_storage.h"
#include <cassert>
#include <filesystem>
#include <fstream>
#include <sstream>
#include <stdexcept>
using namespace taskcourse;
class ReadFailure : public std::stringbuf {
  public:
    explicit ReadFailure(const std::string& bytes) : std::stringbuf(bytes) {}
  protected:
    int_type underflow() override { throw std::runtime_error("read failure"); }
};
int main() {
    Task row{42, true, "keep"};
    const auto previous = row;
    std::string error;
    for (const auto* bytes : {"", "1", "1\t0", "1\t0\tx\ty", "0\t0\tx",
         "+1\t0\tx", "1x\t0\tx", "1000000\t0\tx", "1\t01\tx", "1\t2\tx",
         "1\t0\t", "1\t0\t   ", "1\t0\tbad\"text", "1\t0\té"}) {
        assert(!parseImportRow(bytes, row, error) && row == previous && !error.empty());
    }
    assert(!parseImportRow("1\t0\t" + std::string(81, 'x'), row, error) && row == previous);
    assert(parseImportRow("0007\t1\t  spaces  ", row, error) && error.empty());
    assert(row.id == 7 && row.done && row.text == "  spaces  ");
    assert(parseImportRow("999999\t0\t" + std::string(80, 'x'), row, error));
    Command command{Verb::Done, "keep", 42, Filter::Done};
    const auto oldCommand = command;
    for (const auto* text : {"import", "IMPORT \"x\"", "import x", "import \"\"",
         "import \"  \"", "import \"x\" y", "import \"x\" \"y\"", "import \"a\tb\""})
        assert(!parseCommand(text, command, error) && command == oldCommand && !error.empty());
    assert(!parseCommand("import \"" + std::string(1025, 'x') + "\"", command, error));
    assert(command == oldCommand);
    assert(parseCommand(" \timport \"incoming tasks.tsv\"\r ", command, error));
    assert(command.verb == Verb::Import && command.text == "incoming tasks.tsv" && error.empty());
    assert(parseCommand("import \"" + std::string(1024, 'x') + "\"", command, error));
    TaskLedger ledger;
    assert(ledger.replace({{3, true, "existing"}}, error));
    ImportReport report{9, {{42, "earlier"}}};
    std::istringstream mixed("CLASSES_TASKS_V1\r\n4\t0\t  first  \r\n4\t1\tduplicate\n\n2\t0\tlow\n8\t1\tdone");
    assert(importTaskRows(mixed, ledger, report, error) && error.empty());
    assert((ledger.tasks() == std::vector<Task>{{3, true, "existing"}, {4, false, "  first  "}, {8, true, "done"}}));
    assert((report == ImportReport{2, {{3, "ID must increase beyond the current last ID"},
        {4, "expected ID<TAB>status<TAB>text"}, {5, "ID must increase beyond the current last ID"}}}));
    auto oldRows = ledger.tasks();
    const auto oldReport = report;
    for (const std::string& bytes : std::vector<std::string>{"", "wrong\n9\t0\tvalid\n", "CLASSES_TASKS_V1 \n", std::string(65537, 'x')}) {
        std::istringstream input(bytes);
        assert(!importTaskRows(input, ledger, report, error));
        assert(!error.empty() && ledger.tasks() == oldRows && report == oldReport);
    }
    ReadFailure bad("CLASSES_TASKS_V1\n9\t0\twould be valid\n");
    std::istream input(&bad);
    assert(!importTaskRows(input, ledger, report, error) && input.bad());
    assert(error == "Cannot read import file." && ledger.tasks() == oldRows && report == oldReport);
    std::istringstream oversized("CLASSES_TASKS_V1\n9\t0\tvalid\n" + std::string(65536, 'x'));
    assert(!importTaskRows(oversized, ledger, report, error));
    assert(ledger.tasks() == oldRows && report == oldReport);
    std::istringstream exact("CLASSES_TASKS_V1\n" + std::string(65536 - std::string("CLASSES_TASKS_V1\n").size(), 'x'));
    assert(importTaskRows(exact, ledger, report, error));
    assert(report.accepted == 0 && report.rejected.size() == 1 && ledger.tasks() == oldRows);
    std::istringstream empty("CLASSES_TASKS_V1");
    assert(importTaskRows(empty, ledger, report, error) && report == ImportReport{});
    assert(ledger.tasks() == oldRows);
    int id = 0;
    assert(ledger.add("after import", id, error) && id == 9);
    assert(ledger.replace({}, error));
    for (int i = 1; i <= 99; ++i) assert(ledger.add("base", id, error));
    std::istringstream full("CLASSES_TASKS_V1\n100\t0\thundred\n101\t1\tover\n100\t0\tduplicate\n102\t2\tinvalid\n");
    assert(importTaskRows(full, ledger, report, error));
    assert((report == ImportReport{1, {{3, "task limit reached"},
        {4, "ID must increase beyond the current last ID"}, {5, "invalid status"}}}));
    assert(ledger.size() == 100 && !ledger.add("too many", id, error));
    assert(ledger.replace({}, error));
    std::istringstream last("CLASSES_TASKS_V1\n999999\t0\tlast\n");
    assert(importTaskRows(last, ledger, report, error));
    id = 77;
    assert(!ledger.add("exhausted", id, error) && id == 77);
    oldRows = ledger.tasks();
    const auto preservedReport = report;
    for (const auto* path : {"missing.tsv", "directory.tsv", "link.tsv", "dangling.tsv"}) {
        if (std::string(path) == "directory.tsv") std::filesystem::create_directory(path);
        if (std::string(path) == "link.tsv") {
            std::ofstream good("target.tsv"); good << "CLASSES_TASKS_V1\n"; good.close();
            std::filesystem::create_symlink("target.tsv", path);
        }
        if (std::string(path) == "dangling.tsv") std::filesystem::create_symlink("absent", path);
        assert(!importTasks(path, ledger, report, error));
        assert(ledger.tasks() == oldRows && report == preservedReport && !error.empty());
    }
    // The same mixed input has separate import and full-file reload policies.
    std::ofstream mixedFile("mixed.tsv"); mixedFile << "CLASSES_TASKS_V1\n1\t0\tone\nbroken\n2\t1\ttwo\n"; mixedFile.close();
    assert(ledger.replace({}, error) && importTasks("mixed.tsv", ledger, report, error));
    oldRows = ledger.tasks();
    assert(!loadTasks("mixed.tsv", ledger, error) && ledger.tasks() == oldRows);
    assert(report.accepted == 2 && report.rejected.size() == 1);
}
'''

def oracle(rows, initial):
    current = list(initial)
    reasons = []
    accepted = 0
    for line_number, line in enumerate(rows, 2):
        fields = line.split('\t')
        reason = None
        if len(fields) != 3:
            reason = 'expected ID<TAB>status<TAB>text'
        elif not fields[0] or any(c not in '0123456789' for c in fields[0]) or not 1 <= int(fields[0]) <= 999999:
            reason = 'invalid ID'
        elif fields[1] not in ('0', '1'):
            reason = 'invalid status'
        elif not 1 <= len(fields[2].encode()) <= 80 or not fields[2].strip(' ') or any(not 32 <= ord(c) <= 126 or c == '"' for c in fields[2]):
            reason = 'invalid text'
        elif current and int(fields[0]) <= current[-1][0]:
            reason = 'ID must increase beyond the current last ID'
        elif len(current) >= 100:
            reason = 'task limit reached'
        else:
            current.append((int(fields[0]), fields[1] == '1', fields[2]))
            accepted += 1
        if reason:
            reasons.append(f'Rejected line {line_number}: {reason}\n')
    out = f'Imported {accepted} rejected {len(reasons)}\n' + ''.join(reasons)
    return current, out

def encoded(tasks):
    return HEADER + ''.join(f'{number}\t{int(done)}\t{text}\n' for number, done, text in tasks).encode()

def check_cli(program, work, run):
    saved = work / 'saved tasks.tsv'
    incoming = work / 'incoming tasks.tsv'
    original = [(1, True, 'existing')]
    saved.write_bytes(encoded(original))
    incoming.write_bytes(HEADER + b'2\t0\tfirst\nbroken\n5\t1\tfinished\n')
    original_input = incoming.read_bytes()
    args = [str(program), '--file', str(saved)]
    commands = f'import "{incoming}"\nlist\nquit\n'
    out, err = run(args, work, stdin=commands)
    assert out == ('Loaded 1\nImported 2 rejected 1\nRejected line 3: expected ID<TAB>status<TAB>text\n'
                   'Tasks 3\n1 [done] existing\n2 [open] first\n5 [done] finished\nBye.\n') and not err
    assert saved.read_bytes() == encoded(original) and incoming.read_bytes() == original_input
    out, err = run(args, work, stdin=f'import "{incoming}"\nsave\nquit\n')
    assert out.endswith('Saved 3\nBye.\n') and not err
    accepted = original + [(2, False, 'first'), (5, True, 'finished')]
    assert saved.read_bytes() == encoded(accepted) and incoming.read_bytes() == original_input
    out, err = run(args, work, stdin='list\nadd "next"\nquit\n')
    assert out.endswith('Added 6\nBye.\n') and not err and saved.read_bytes() == encoded(accepted)
    incoming.write_bytes(b'wrong\n9\t0\tignored\n')
    out, err = run(args, work, stdin=f'import "{incoming}"\nlist\nquit\n')
    assert err == 'Error: Invalid import file header.\n' and 'Tasks 3\n' in out and 'Imported' not in out
    assert saved.read_bytes() == encoded(accepted)
    # Independent seeded black-box comparisons exercise file-order effects.
    rng = random.Random(1731)
    for case in range(40):
        initial = [(n, n % 2 == 0, 'base') for n in range(1, rng.choice([1, 4, 100, 101]))]
        rows = []
        for _ in range(rng.randrange(1, 45)):
            rows.append(rng.choice([
                f'{rng.randrange(1, 160)}\t{rng.randrange(2)}\ttask',
                'bad', '', '0\t0\tzero', '999999999999999999999\t0\toverflow',
                f'{rng.randrange(1, 160)}\t2\tbad', '0008\t0\t  spaces  ',
                '7\t0\t' + 'x' * rng.choice([80, 81]), '6\t1\tbad\tfield', '9\t0\té',
                '999999\t0\tlast', '11\t0\t   ', '+12\t0\tsigned']))
        expected, report = oracle(rows, initial)
        saved.write_bytes(encoded(initial))
        # Always retain the newline when the last generated row is blank.
        ending = '\r\n' if case % 2 else '\n'
        contents = ending.join(['CLASSES_TASKS_V1', *rows]) + (ending if case % 3 or rows[-1] == '' else '')
        incoming.write_bytes(contents.encode())
        before = incoming.read_bytes()
        out, err = run(args, work, stdin=f'import "{incoming}"\nlist\nsave\nquit\n')
        listing = f'Tasks {len(expected)}\n' + ''.join(f'{n} [{"done" if d else "open"}] {t}\n' for n, d, t in expected)
        assert out == f'Loaded {len(initial)}\n' + report + listing + f'Saved {len(expected)}\nBye.\n', (case, out, report)
        assert not err and saved.read_bytes() == encoded(expected) and incoming.read_bytes() == before
    print(json.dumps({'event':'checked-independent-import-streams','count':40}))

def main():
    spec = importlib.util.spec_from_file_location('task_verifier', ROOT/'verify-task-manager.py')
    verifier = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(verifier)
    verifier.TASK = os.environ.get('CLASSES_AUDIT_PARENT_TASK_ID', 'cppi1-row-import-source')
    run = verifier.run
    for role in ('starter', 'solution'):
        files = {p.name for p in (PACK/role).iterdir() if p.is_file()}
        assert files == set(SOURCES + HEADERS + ['README.md', 'Makefile'])
    for name in SOURCES + HEADERS + ['Makefile']:
        if name == 'task_import.cpp':
            assert (PACK/'starter'/name).read_text().count('// TODO:') == 2
            assert 'UNFINISHED' in (PACK/'starter'/name).read_text()
            assert 'UNFINISHED' not in (PACK/'solution'/name).read_text()
        else:
            assert (PACK/'starter'/name).read_bytes() == (PACK/'solution'/name).read_bytes()
    compiler = os.environ.get('CXX', 'clang++')
    with tempfile.TemporaryDirectory(prefix='cppi1-row-import-') as directory:
        work = Path(directory)
        completed = work/'completed-learner'
        shutil.copytree(PACK/'starter', completed)
        shutil.copyfile(PACK/'solution/task_import.cpp', completed/'task_import.cpp')
        for sanitized in (False, True):
            flags = FLAGS + (['-fsanitize=address,undefined', '-fno-sanitize-recover=all'] if sanitized else [])
            for role, pack in [('starter', PACK/'starter'), ('solution', PACK/'solution'), ('completed-learner', completed)]:
                cwd = work/(role + ('-sanitized' if sanitized else '-ordinary'))
                cwd.mkdir()
                binary = cwd/'task-import'
                out, err = run([compiler, *flags, *[str(pack/n) for n in SOURCES], '-o', str(binary)], cwd)
                assert not out and not err
                if role == 'starter':
                    (cwd/'incoming.tsv').write_bytes(HEADER + b'1\t0\tnew\n')
                    out, err = run([str(binary)], cwd, stdin='add "base"\nimport "incoming.tsv"\nlist\nquit\n')
                    assert out == 'Loaded 0\nAdded 1\nTasks 1\n1 [open] base\nBye.\n'
                    assert err == 'Error: UNFINISHED: implement selective import.\n' and not (cwd/'tasks.tsv').exists()
                else:
                    check_cli(binary, cwd, run)
                    fixture = cwd/'acceptance.cpp'
                    fixture.write_text(HARNESS)
                    check = cwd/'acceptance'
                    out, err = run([compiler, *flags, '-I', str(pack), str(fixture), *[str(pack/n) for n in SOURCES[1:]], '-o', str(check)], cwd)
                    assert not out and not err
                    out, err = run([str(check)], cwd)
                    assert not out and not err
                print(json.dumps({'event':'checked','project':'row-import','role':role,'sanitized':sanitized}))
        for role in ('starter', 'solution'):
            makepack = work/('make-' + role)
            shutil.copytree(PACK/role, makepack)
            run(['make'], makepack)
            run(['make', 'task-import-debug'], makepack)
            (makepack/'retain.tsv').write_bytes(HEADER)
            run(['make', 'clean'], makepack)
            assert (makepack/'retain.tsv').read_bytes() == HEADER
            assert not (makepack/'task-import').exists() and not (makepack/'task-import-debug').exists()
        build = work/'cmake'
        run(['cmake', '-S', str(ROOT), '-B', str(build)], work)
        run(['cmake', '--build', str(build), '--target', 'bad_rows_starter', 'bad_rows_solution'], work)
        check_cli(build/'bad_rows_solution', work, run)
    print(json.dumps({'event':'verified','project':'CPPI1-Import-and-Reject-Bad-Rows',
        'unfinishedLearner':True,'completedLearnerAndReference':True,'selectiveImportDistinctFromReload':True,
        'fatalReadPreservesLedgerAndReport':True,'ordinaryAndSanitized':True,'independentStreamsPerCompletedBuild':40}))

if __name__ == '__main__':
    main()
