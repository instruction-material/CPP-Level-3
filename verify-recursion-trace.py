"""Check the worksheet against an iterative model and actual saved maze packs."""

from collections import deque
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import tempfile

ROOT = Path(__file__).resolve().parent
PACK = ROOT / 'CPPI2-Recursion-Trace-Drill'
MAZE = ROOT / 'CPPI2-Recursive-Maze-Search'
FLAGS = ['-Wall', '-Wextra', '-Wpedantic', '-Wconversion',
         '-Wsign-conversion', '-Werror', '-g', '-O0']
NEIGHBORS = [(-1, 0), (0, 1), (1, 0), (0, -1)]


def sections(document):
    matches = list(re.finditer(r'^## Case ([ABC])(?:[^\n]*)\n', document, re.M))
    assert [match[1] for match in matches] == ['A', 'B', 'C']
    return {match[1]: document[match.end():matches[index + 1].start()
            if index + 1 < len(matches) else len(document)]
            for index, match in enumerate(matches)}


def endpoint(rows, label):
    return next((r, c) for r, row in enumerate(rows)
                for c, value in enumerate(row) if value == label)


def iterative_trace(rows):
    """Explicit stack frames and cursors, independent of recursive C++ calls."""
    start, exit_cell = endpoint(rows, 'S'), endpoint(rows, 'E')
    frames = [[start, 0]]
    seen, events = {start}, [f'Enter {start[0]} {start[1]}']
    while frames:
        cell, cursor = frames[-1]
        if cell == exit_cell:
            path = [frame[0] for frame in frames]
            result = [f'Path {len(path)}', *[f'{r} {c}' for r, c in path]]
            return '\n'.join(events + result) + '\n', path
        if cursor == len(NEIGHBORS):
            events.append(f'Backtrack {cell[0]} {cell[1]}')
            frames.pop()
            continue
        frames[-1][1] += 1
        dr, dc = NEIGHBORS[cursor]
        nr, nc = cell[0] + dr, cell[1] + dc
        neighbor = nr, nc
        if (0 <= nr < len(rows) and 0 <= nc < len(rows[0])
                and rows[nr][nc] != '#' and neighbor not in seen):
            seen.add(neighbor)
            frames.append([neighbor, 0])
            events.append(f'Enter {nr} {nc}')
    return '\n'.join(events + ['No path']) + '\n', []


def reachable(rows):
    """Separate breadth-first reachability oracle with a different neighbor order."""
    queue = deque([endpoint(rows, 'S')])
    seen = set(queue)
    while queue:
        r, c = queue.popleft()
        for nr, nc in [(r, c - 1), (r + 1, c), (r, c + 1), (r - 1, c)]:
            neighbor = nr, nc
            if (0 <= nr < len(rows) and 0 <= nc < len(rows[0])
                    and rows[nr][nc] != '#' and neighbor not in seen):
                seen.add(neighbor)
                queue.append(neighbor)
    return endpoint(rows, 'E') in seen


def check_documents():
    learner = (PACK / 'starter/WORKSHEET.md').read_text()
    staff = (PACK / 'solution/WORKED-TRACE.md').read_text()
    assert (PACK / 'README.md').read_text() == learner
    for field in ['Predicted full Enter/Backtrack sequence:',
                  'Predicted final Path line and coordinates, or No path:',
                  'Source role, revision or ZIP and compiler/platform:',
                  'Exact command and actual stdout, stderr and exit status for A:',
                  'Exact command and actual stdout, stderr and exit status for B:',
                  'Exact command and actual stdout, stderr and exit status for C:',
                  'Earliest difference from a prediction and its source location:']:
        assert field + ' [record]' in learner
    assert '\nEnter 0 0\n' not in learner and 'Actual trace and final result' not in learner
    assert 'optional worksheet' in learner and 'C++20' in learner
    assert 'status 3' in learner and 'up, right, down, left' in learner
    learner_cases, staff_cases = sections(learner), sections(staff)
    cases = []
    for label in ['A', 'B', 'C']:
        inputs = re.findall(r'```text\n(.*?)```', learner_cases[label], re.S)
        worked = re.findall(r'```text\n(.*?)```', staff_cases[label], re.S)
        assert len(inputs) == 1 and len(worked) == 2
        input_text, expected = worked
        assert input_text == inputs[0]
        lines = input_text.splitlines()
        height, width = map(int, lines[0].split())
        rows = lines[1:]
        assert height == len(rows) and all(len(row) == width for row in rows)
        assert ''.join(rows).count('S') == ''.join(rows).count('E') == 1
        assert set(''.join(rows)) <= set('SE.#')
        modeled, path = iterative_trace(rows)
        assert expected == modeled, (label, 'worked trace differs from iterative model')
        assert bool(path) == reachable(rows), label
        if path:
            assert path[0] == endpoint(rows, 'S') and path[-1] == endpoint(rows, 'E')
            assert len(path) == len(set(path))
            assert all(abs(a[0] - b[0]) + abs(a[1] - b[1]) == 1
                       for a, b in zip(path, path[1:]))
        cases.append((label, input_text, expected, rows))
    assert [len(iterative_trace(case[3])[1]) for case in cases] == [2, 6, 0]
    return learner, staff, cases


def repeated_search_harness(cases):
    checks = []
    # A, then C, then A in one process catches retained visited/path state.
    for index in [0, 2, 0]:
        _, input_text, output, rows = cases[index]
        trace = [line for line in output.splitlines()
                 if line.startswith(('Enter ', 'Backtrack '))]
        _, path = iterative_trace(rows)
        trace_cpp = ','.join(json.dumps(line) for line in trace)
        path_cpp = ','.join('Cell{' + f'{r},{c}' + '}' for r, c in path)
        checks.append('''{
            std::istringstream input(%s);
            Maze maze;
            std::string error;
            assert(readMaze(input, maze, error));
            const auto original = maze;
            const auto result = solveMaze(maze);
            assert(result.found == %s && maze == original);
            assert((result.trace == std::vector<std::string>{%s}));
            assert((result.path == std::vector<Cell>{%s}));
        }''' % (json.dumps(input_text), 'true' if path else 'false', trace_cpp, path_cpp))
    return '''#include "maze.h"
#include <cassert>
#include <sstream>
using namespace mazecourse;
int main() {
%s
}
''' % '\n'.join(checks)


def main():
    learner, staff, cases = check_documents()
    spec = importlib.util.spec_from_file_location('trace_process_runner', ROOT / 'verify-task-manager.py')
    runner = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(runner)
    runner.TASK = os.environ.get('CLASSES_AUDIT_PARENT_TASK_ID', 'cppi2-recursion-trace-source')
    run = runner.run
    compiler = os.environ.get('CXX', 'clang++')
    with tempfile.TemporaryDirectory(prefix='cppi2-recursion-trace-') as directory:
        work = Path(directory)
        completed = work / 'completed-learner'
        shutil.copytree(MAZE / 'starter', completed)
        shutil.copyfile(MAZE / 'solution/maze_search.cpp', completed / 'maze_search.cpp')
        for sanitized in [False, True]:
            flags = FLAGS + (['-fsanitize=address,undefined', '-fno-sanitize-recover=all'] if sanitized else [])
            prefix = ['env', 'ASAN_OPTIONS=detect_leaks=0'] if sanitized else []
            for role, document in [('starter', learner), ('solution', staff)]:
                binary = work / f'notes-{role}-{sanitized}'
                out, error = run([compiler, '-std=c++17', *flags, str(PACK / role / 'main.cpp'), '-o', str(binary)], work)
                assert not out and not error
                out, error = run([*prefix, str(binary)], work)
                assert out == document and not error, (role, 'printer differs from worksheet')
            for role, source in [('starter', MAZE / 'starter'), ('solution', MAZE / 'solution'), ('completed-learner', completed)]:
                binary = work / f'maze-{role}-{sanitized}'
                out, error = run([compiler, '-std=c++20', *flags,
                                  *[str(source / name) for name in ['main.cpp', 'maze.cpp', 'maze_search.cpp']], '-o', str(binary)], work)
                assert not out and not error
                for label, input_text, expected, _ in [*cases, cases[0]]:
                    case_file = work / f'case-{label.lower()}.txt'
                    case_file.write_text(input_text)
                    before = case_file.read_bytes()
                    out, error = run([*prefix, str(binary), '--trace'], work,
                                     expected=3 if role == 'starter' else 0,
                                     stdin=case_file.read_text())
                    assert case_file.read_bytes() == before
                    if role == 'starter':
                        assert not out and error == 'Error: UNFINISHED: implement recursive search.\n'
                    else:
                        assert out == expected and not error, (role, sanitized, label)
                if role != 'starter':
                    harness = work / 'repeated.cpp'
                    harness.write_text(repeated_search_harness(cases))
                    executable = work / 'repeated'
                    out, error = run([compiler, '-std=c++20', *flags, '-I', str(source), str(harness),
                                      str(source / 'maze.cpp'), str(source / 'maze_search.cpp'), '-o', str(executable)], work)
                    assert not out and not error
                    out, error = run([*prefix, str(executable)], work)
                    assert not out and not error
                print(json.dumps({'event': 'verified-trace-maze-role', 'role': role,
                                  'sanitized': sanitized, 'worksheetCases': 3, 'repeatCaseA': True}))
        cmake = work / 'cmake'
        run(['cmake', '-S', str(ROOT), '-B', str(cmake)], work)
        run(['cmake', '--build', str(cmake), '--target', 'trace_drill_starter', 'trace_drill_solution'], work)
        for role, document in [('starter', learner), ('solution', staff)]:
            out, error = run([str(cmake / f'trace_drill_{role}')], work)
            assert out == document and not error
    print(json.dumps({'event': 'verified-recursion-worksheet-contract', 'worksheetCases': 3,
                      'independentModels': ['iterative-frame-stack', 'breadth-first-reachability'],
                      'mazeVariants': 6, 'printerVariants': 4, 'cmakePrinters': 2,
                      'sameProcessFreshStateVariants': 4}))


if __name__ == '__main__':
    main()
