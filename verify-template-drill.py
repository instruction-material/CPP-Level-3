"""Inspect real GCC/Clang errors and run ordinary/fixed template practice."""
import json
import os
from pathlib import Path
import shutil
import tempfile
from cppi5_native_checks import ROOT, execute, flags

PACK = ROOT / 'CPPI5-Template-Error-Reading-Drill'
BASELINE = b'number 3\ntext apple\n'
FIX = '''    friend bool operator<(const Score& left, const Score& right) {
        return left.value < right.value;
    }
'''


def main():
    starter = (PACK / 'starter/main.cpp').read_text()
    worked = (PACK / 'solution/main.cpp').read_text()
    assert starter.count('    int value;\n') == 1
    completed = starter.replace('    int value;\n', '    int value;\n' + FIX)
    assert completed == worked
    compilers = {'GCC': shutil.which('g++'), 'Clang': shutil.which('clang++')}
    assert all(compilers.values()), 'Both supported diagnostic compilers are required.'
    compiler = os.environ.get('CXX', 'g++')
    with tempfile.TemporaryDirectory(prefix='cppi5-template-') as name:
        work = Path(name)
        (work / 'completed.cpp').write_text(completed)
        for label, cxx in compilers.items():
            version = execute([cxx, '--version'], work)[0].decode()
            print(json.dumps({'event': 'diagnostic-compiler', 'compiler': label,
                              'version': version.splitlines()[0]}), flush=True)
            for standard in [17, 20]:
                output, error = execute([cxx, *flags(standard, False),
                                         '-DCPPI5_TRIGGER_TEMPLATE_ERROR',
                                         '-fsyntax-only', str(PACK / 'starter/main.cpp')],
                                        work, 1)
                assert output == b'' and b'Score' in error and b'chooseSmaller' in error
                assert b'<' in error and (b'operator' in error or b'operands' in error)
                print(json.dumps({'event': 'verified-controlled-template-diagnostic',
                                  'compiler': label, 'standard': standard,
                                  'stderr': error.decode()}), flush=True)
            # Correct the same call on each actual diagnostic toolchain.
            binary = work / ('fixed-' + label)
            execute([cxx, *flags(20, False), '-DCPPI5_TRIGGER_TEMPLATE_ERROR',
                     str(work / 'completed.cpp'), '-o', str(binary)], work)
            assert execute([str(binary)], work) == (b'score 59\n', b'')
        for standard in [17, 20]:
            for sanitized in [False, True]:
                for label, source in [('learner', PACK / 'starter/main.cpp'),
                                      ('worked', PACK / 'solution/main.cpp'),
                                      ('completed', work / 'completed.cpp')]:
                    binary = work / f'{label}-{standard}-{int(sanitized)}'
                    execute([compiler, *flags(standard, sanitized), str(source),
                             '-o', str(binary)], work)
                    assert execute([str(binary)], work) == (BASELINE, b'')
                    assert execute([str(binary), 'extra'], work, 2) == (b'', b'Usage: main\n')
                for label, source in [('worked', PACK / 'solution/main.cpp'),
                                      ('completed', work / 'completed.cpp')]:
                    binary = work / f'enabled-{label}-{standard}-{int(sanitized)}'
                    execute([compiler, *flags(standard, sanitized),
                             '-DCPPI5_TRIGGER_TEMPLATE_ERROR', str(source),
                             '-o', str(binary)], work)
                    assert execute([str(binary)], work) == (b'score 59\n', b'')
                    assert execute([str(binary), 'extra'], work, 2) == (b'', b'Usage: main\n')
        for sanitized in [False, True]:
            for label, text in [('worked', worked), ('completed', completed)]:
                for first, second in [(0, 100), (91, 76), (84, 84)]:
                    assert text.count('Score{84}') == text.count('Score{59}') == 1
                    changed = text.replace('Score{84}', f'Score{{{first}}}')
                    changed = changed.replace('Score{59}', f'Score{{{second}}}')
                    source = work / 'changed.cpp'
                    source.write_text(changed)
                    binary = work / f'changed-{label}-{first}-{second}-{int(sanitized)}'
                    execute([compiler, *flags(20, sanitized),
                             '-DCPPI5_TRIGGER_TEMPLATE_ERROR', str(source),
                             '-o', str(binary)], work)
                    assert execute([str(binary)], work) == (
                        f'score {min(first, second)}\n'.encode(), b'')
    print(json.dumps({'event': 'verified-template-drill', 'realDiagnostics': 4,
                      'diagnosticCompilers': ['GCC', 'Clang'],
                      'completedLearnerEqualsWorked': True,
                      'ordinaryAndSanitized': True, 'standards': [17, 20],
                      'changedPairs': [[0, 100], [91, 76], [84, 84]],
                      'unchangedOrdinaryBehavior': True}))


if __name__ == '__main__':
    main()
