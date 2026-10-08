"""Verify standalone packs and the four preserved CPPI5 CMake names."""
import json
import os
from pathlib import Path
import shutil
import tempfile
from cppi5_native_checks import ROOT, execute

PACKS = [("CPPI5-Fraction-Toolkit", "starter", "fraction_toolkit_starter"),
         ("CPPI5-Fraction-Toolkit", "solution", "fraction_toolkit_solution"),
         ("CPPI5-Template-Error-Reading-Drill", "starter", "template_drill_starter"),
         ("CPPI5-Template-Error-Reading-Drill", "solution", "template_drill_solution")]
FRACTION = b'LEFT 1/2\nRIGHT 2/3\nLESS true\nSUM 7/6\nPRODUCT 1/3\nSMALLER 1/2\nSORTED 0/1 1/2 2/3\n'
TEMPLATE = b'number 3\ntext apple\n'


def check(binary, directory, pack, role):
    if pack == 'CPPI5-Fraction-Toolkit' and role == 'starter':
        output, error = execute([str(binary)], directory, 1)
        assert output == b'' and error == b'Rejected: Unfinished task: constructFraction.\n'
    else:
        assert execute([str(binary)], directory) == (
            FRACTION if pack == 'CPPI5-Fraction-Toolkit' else TEMPLATE, b'')


def main():
    compiler = os.environ.get('CXX', 'g++')
    with tempfile.TemporaryDirectory(prefix='cppi5-build-') as name:
        work = Path(name)
        snapshot = work / 'source'
        snapshot.mkdir()
        for path in ROOT.iterdir():
            if path.is_dir() and path.name.startswith('CPPI'):
                shutil.copytree(path, snapshot / path.name)
        shutil.copyfile(ROOT / 'CMakeLists.txt', snapshot / 'CMakeLists.txt')
        for pack, role, target in PACKS:
            directory = snapshot / pack / role
            assert all((directory / f).is_file() for f in ['main.cpp', 'Makefile', 'README.md'])
            execute(['make', 'CXX=' + compiler, 'main', 'main-debug'], directory)
            for binary in ['main', 'main-debug']:
                check(directory / binary, directory, pack, role)
            if pack == 'CPPI5-Template-Error-Reading-Drill':
                output, error = execute(['make', 'CXX=' + compiler, 'diagnostic'], directory,
                                        2 if role == 'starter' else 0)
                if role == 'starter':
                    assert b'chooseSmaller' in error and b'Score' in error
                    assert not (directory / 'main-diagnostic').exists()
                else:
                    assert execute([str(directory / 'main-diagnostic')], directory) == (b'score 59\n', b'')
            execute(['make', 'clean'], directory)
            assert not any((directory / f).exists() for f in ['main', 'main-debug', 'main-diagnostic'])
        build = work / 'cmake'
        execute(['cmake', '-S', str(snapshot), '-B', str(build),
                 '-DCMAKE_CXX_COMPILER=' + compiler], work)
        execute(['cmake', '--build', str(build), '--parallel', '1', '--target',
                 *[entry[2] for entry in PACKS]], work, timeout=120)
        for pack, role, target in PACKS:
            check(build / target, snapshot / pack / role, pack, role)
    print(json.dumps({'event': 'verified-cppi5-builds', 'makePacks': 4,
                      'makeOrdinaryAndSanitized': True, 'cmakeTargets': 4,
                      'explicitUnfinishedPrimary': True,
                      'workingOrdinaryDrill': True, 'actualDiagnosticTarget': True}))


if __name__ == '__main__':
    main()
