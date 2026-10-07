"""Independent maze reachability, path, parser and recursion-trace acceptance."""

from collections import deque
import importlib.util
import json
import os
from pathlib import Path
import random
import shutil
import tempfile

ROOT = Path(__file__).resolve().parent
PACK = ROOT / 'CPPI2-Recursive-Maze-Search'
SOURCES = ['main.cpp', 'maze.cpp', 'maze_search.cpp']
FILES = set(SOURCES + ['maze.h', 'Makefile', 'README.md'])
FLAGS = ['-std=c++20', '-Wall', '-Wextra', '-Wpedantic', '-Wconversion', '-Wsign-conversion', '-Werror', '-g', '-O0']

HARNESS = r'''
#include "maze.h"
#include <cassert>
#include <sstream>
#include <stdexcept>
using namespace mazecourse;
class ReadFailure : public std::stringbuf {
  public:
    explicit ReadFailure(const std::string& bytes) : std::stringbuf(bytes) {}
  protected:
    int_type underflow() override { throw std::runtime_error("read failure"); }
};
int main() {
    Maze maze{{"SE"}, {0,0}, {0,1}};
    const auto before = maze;
    std::string error = "old";
    for (const std::string& bytes : std::vector<std::string>{"", "0 2\nSE\n", "1 2\nSS\n", "1 2\nSE\n\n", std::string(16385, 'x')}) {
        std::istringstream input(bytes);
        assert(!readMaze(input, maze, error));
        assert(maze == before && !error.empty());
    }
    ReadFailure failure("1 2\nSE\n");
    std::istream failed(&failure);
    assert(!readMaze(failed, maze, error));
    assert(failed.bad() && maze == before && error == "Cannot read maze input.");
    std::istringstream input("01\t02\r\nSE");
    assert(readMaze(input, maze, error) && error.empty() && maze == before);
    std::istringstream throwingEof("1 2\nSE\n");
    throwingEof.exceptions(std::ios::failbit | std::ios::badbit);
    assert(readMaze(throwingEof, maze, error) && error.empty());
    const auto first = solveMaze(maze);
    assert(first.found && (first.path == std::vector<Cell>{{0,0},{0,1}}));
    assert(solveMaze(maze) == first && maze == before);
    Maze blocked{{"S#E"}, {0,0}, {0,2}};
    const auto noPath = solveMaze(blocked);
    assert(!noPath.found && noPath.path.empty() && noPath.entered.size() == 1);
    assert(solveMaze(maze) == first);
    for (const Maze& bad : std::vector<Maze>{Maze{}, Maze{{"SE", "#"},{0,0},{0,1}}, Maze{{"SE"},{1,0},{0,1}}, Maze{{"SE"},{0,0},{1,1}}, Maze{{"SSE"},{0,0},{0,2}}}) {
        try { static_cast<void>(solveMaze(bad)); assert(false); }
        catch (const std::invalid_argument&) {}
    }
}
'''


def encoded(rows, crlf=False, final=True):
    newline = '\r\n' if crlf else '\n'
    return newline.join([f'{len(rows)} {len(rows[0])}', *rows]) + (newline if final else '')


def endpoint(rows, tile):
    return next((r, c) for r, row in enumerate(rows) for c, value in enumerate(row) if value == tile)


def reachable(rows):
    """Breadth-first reachability is independent of the recursive implementation."""
    start, end = endpoint(rows, 'S'), endpoint(rows, 'E')
    queue = deque([start])
    seen = {start}
    while queue:
        r, c = queue.popleft()
        for nr, nc in [(r + 1, c), (r, c - 1), (r - 1, c), (r, c + 1)]:
            cell = nr, nc
            if 0 <= nr < len(rows) and 0 <= nc < len(rows[0]) and rows[nr][nc] != '#' and cell not in seen:
                seen.add(cell)
                queue.append(cell)
    return end in seen, seen


def check_result(output, rows, trace):
    found, reachable_cells = reachable(rows)
    lines = output.splitlines()
    events = []
    while lines and lines[0].split()[0] in ('Enter', 'Backtrack'):
        parts = lines.pop(0).split()
        assert len(parts) == 3
        events.append((parts[0], (int(parts[1]), int(parts[2]))))
    assert bool(events) == trace
    if not found:
        assert lines == ['No path'], (rows, output)
        path = []
    else:
        assert lines and lines[0].startswith('Path '), (rows, output)
        count = int(lines.pop(0).split()[1])
        path = [tuple(map(int, line.split())) for line in lines]
        assert count == len(path) <= len(rows) * len(rows[0])
        assert path[0] == endpoint(rows, 'S') and path[-1] == endpoint(rows, 'E')
        assert len(set(path)) == len(path)
        assert all(cell in reachable_cells for cell in path)
        assert all(abs(a[0] - b[0]) + abs(a[1] - b[1]) == 1 for a, b in zip(path, path[1:]))
    if trace:
        stack, entered = [], set()
        for label, cell in events:
            if label == 'Enter':
                assert cell in reachable_cells and cell not in entered
                if stack:
                    assert abs(stack[-1][0] - cell[0]) + abs(stack[-1][1] - cell[1]) == 1
                else:
                    assert not entered and cell == endpoint(rows, 'S')
                entered.add(cell)
                stack.append(cell)
            else:
                assert stack and stack.pop() == cell
        assert stack == path
        if not found:
            assert entered == reachable_cells
    return path


def check_cli(binary, cwd, run):
    fixtures = [
        ['SE'], ['S#E'], ['S.', '.E'], ['S#E', '...'],
        ['#####', '#S..#', '#.#E#', '#...#', '#####'],
        ['S...', '.##.', '...E'], ['S##', '###', '##E'],
        ['S' + '.' * 19] + ['.' * 20] * 18 + ['.' * 19 + 'E'],
    ]
    for rows in fixtures:
        ordinary, error = run([str(binary)], cwd, stdin=encoded(rows))
        assert not error
        check_result(ordinary, rows, False)
        traced, error = run([str(binary), '--trace'], cwd, stdin=encoded(rows, crlf=True, final=False))
        assert not error
        path = check_result(traced, rows, True)
        expected = ('Path ' + str(len(path)) + '\n' + ''.join(f'{r} {c}\n' for r, c in path)) if path else 'No path\n'
        assert ordinary == expected and traced.endswith(expected)
    out, error = run([str(binary)], cwd, stdin='2 3\nS#E\n...\n')
    assert out == 'Path 5\n0 0\n1 0\n1 1\n1 2\n0 2\n' and not error
    # Up/right/down/left produces a valid deliberate detour, not a shortest path.
    out, error = run([str(binary)], cwd, stdin='2 3\n...\nSE.\n')
    assert out == 'Path 6\n1 0\n0 0\n0 1\n0 2\n1 2\n1 1\n' and not error
    malformed = ['', '1\nSE\n', '1 2 3\nSE\n', '0 2\nSE\n', '21 2\nSE\n', '1 21\nSE\n', '+1 2\nSE\n', '1 -2\nSE\n', '1 2x\nSE\n', '1 2\nS\n', '2 2\nSE\n', '1 2\nSE\nextra\n', '1 2\nSE\n\n', '1 2\nSS\n', '1 2\nEE\n', '1 2\n..\n', '1 3\nS E\n', '1 3\nSxE\n', '1 3\nS\0E\n', '\ufeff1 2\nSE\n', '1 3\nSéE\n', '9' * 80 + ' 2\nSE\n', 'x' * 16385]
    for input_bytes in malformed:
        out, error = run([str(binary)], cwd, expected=2, stdin=input_bytes)
        assert not out and error.startswith('Error: ')
    for args in [['--unknown'], ['--trace', '--trace'], ['--help', '--trace'], ['extra']]:
        out, error = run([str(binary), *args], cwd, expected=2)
        assert not out and error.startswith('Error: ')
    out, error = run([str(binary), '--help'], cwd)
    assert out.startswith('Usage: maze-search') and not error
    # Test the exact byte limit with a valid header containing leading spaces.
    exact = ' ' * (16384 - len('1 2\nSE\n')) + '1 2\nSE\n'
    out, error = run([str(binary)], cwd, stdin=exact)
    assert out == 'Path 2\n0 0\n0 1\n' and not error
    out, error = run([str(binary)], cwd, expected=2, stdin=' ' + exact)
    assert not out and error == 'Error: Input exceeds 16384 bytes.\n'
    rng = random.Random(20261007)
    for index in range(120):
        height, width = rng.randint(2, 8), rng.randint(2, 8)
        grid = [['#' if rng.random() < .32 else '.' for _ in range(width)] for _ in range(height)]
        a, b = rng.sample(range(height * width), 2)
        grid[a // width][a % width] = 'S'
        grid[b // width][b % width] = 'E'
        rows = [''.join(row) for row in grid]
        traced = index % 2 == 0
        out, error = run([str(binary), *(['--trace'] if traced else [])], cwd, stdin=encoded(rows, crlf=index % 3 == 0, final=index % 4 != 0))
        assert not error
        check_result(out, rows, traced)
    print(json.dumps({'event': 'verified-independent-maze-graphs', 'count': 120}))


def main():
    spec = importlib.util.spec_from_file_location('task_verifier', ROOT / 'verify-task-manager.py')
    verifier = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(verifier)
    verifier.TASK = os.environ.get('CLASSES_AUDIT_PARENT_TASK_ID', 'cppi2-maze-search-source')
    run = verifier.run
    for role in ['starter', 'solution']:
        assert {p.name for p in (PACK / role).iterdir() if p.is_file()} == FILES
    for name in FILES - {'maze_search.cpp'}:
        assert (PACK / 'starter' / name).read_bytes() == (PACK / 'solution' / name).read_bytes()
    assert (PACK / 'starter/maze_search.cpp').read_text().count('// TODO:') == 1
    assert 'UNFINISHED' not in (PACK / 'solution/maze_search.cpp').read_text()
    compiler = os.environ.get('CXX', 'clang++')
    with tempfile.TemporaryDirectory(prefix='cppi2-maze-search-') as directory:
        work = Path(directory)
        completed = work / 'completed-learner'
        shutil.copytree(PACK / 'starter', completed)
        shutil.copyfile(PACK / 'solution/maze_search.cpp', completed / 'maze_search.cpp')
        for sanitized in [False, True]:
            flags = FLAGS + (['-fsanitize=address,undefined', '-fno-sanitize-recover=all'] if sanitized else [])
            for role, pack in [('starter', PACK / 'starter'), ('solution', PACK / 'solution'), ('completed-learner', completed)]:
                cwd = work / (role + ('-sanitized' if sanitized else '-ordinary'))
                cwd.mkdir()
                binary = cwd / 'maze-search'
                out, error = run([compiler, *flags, *[str(pack / name) for name in SOURCES], '-o', str(binary)], cwd)
                assert not out and not error
                if role == 'starter':
                    out, error = run([str(binary)], cwd, expected=3, stdin='1 2\nSE\n')
                    assert not out and error == 'Error: UNFINISHED: implement recursive search.\n'
                else:
                    check_cli(binary, cwd, run)
                    fixture = cwd / 'acceptance.cpp'
                    fixture.write_text(HARNESS)
                    check = cwd / 'acceptance'
                    out, error = run([compiler, *flags, '-I', str(pack), str(fixture), str(pack / 'maze.cpp'), str(pack / 'maze_search.cpp'), '-o', str(check)], cwd)
                    assert not out and not error
                    out, error = run([str(check)], cwd)
                    assert not out and not error
                print(json.dumps({'event': 'verified-maze-role', 'role': role, 'sanitized': sanitized}))
        for role in ['starter', 'solution']:
            pack = work / ('make-' + role)
            shutil.copytree(PACK / role, pack)
            run(['make', 'maze-search', 'maze-search-debug'], pack)
            (pack / 'maze.txt').write_text('1 2\nSE\n')
            run(['make', 'clean'], pack)
            assert (pack / 'maze.txt').read_text() == '1 2\nSE\n'
            assert not (pack / 'maze-search').exists() and not (pack / 'maze-search-debug').exists()
        cmake = work / 'cmake'
        run(['cmake', '-S', str(ROOT), '-B', str(cmake)], work)
        run(['cmake', '--build', str(cmake), '--target', 'maze_search_starter', 'maze_search_solution'], work)
        out, error = run([str(cmake / 'maze_search_starter')], work, expected=3, stdin='1 2\nSE\n')
        assert not out and 'UNFINISHED' in error
        out, error = run([str(cmake / 'maze_search_solution')], work, stdin='1 2\nSE\n')
        assert out == 'Path 2\n0 0\n0 1\n' and not error
    print(json.dumps({'event': 'verified-maze-native-contract', 'randomGraphsPerCompletedVariant': 120, 'totalIndependentGraphComparisons': 480, 'maximumGridCells': 400}))


if __name__ == '__main__':
    main()
