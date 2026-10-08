"""Independent native acceptance for the Fraction Toolkit.

Source integration also requires the separate teaching, template-diagnostic
and build-pack gates. The result model uses Python's arbitrary-precision
Fraction, rather than repeating the C++ normalization/arithmetic implementation.
"""
from fractions import Fraction
import json
import os
from pathlib import Path
import random
import re
import tempfile
from cppi5_native_checks import ROOT, execute, flags as compiler_flags

LIMIT = 1_000_000


def component(text):
    negative = text.startswith('-')
    magnitude = text.removeprefix('-').lstrip('0') or '0'
    if len(magnitude) > 7 or int(magnitude) > LIMIT:
        raise ValueError('input bound')
    return -int(magnitude) if negative else int(magnitude)


def parse(text):
    if not re.fullmatch(r'-?[0-9]+/-?[0-9]+', text):
        raise ValueError('syntax')
    first, second = text.split('/')
    return Fraction(component(first), component(second))


def model(arguments):
    if len(arguments) not in [0, 2]:
        return 2, b''
    try:
        left, right = [parse(x) for x in (arguments or ['1/2', '2/3'])]
        total, product = left + right, left * right
        for value in [total, product]:
            if abs(value.numerator) > LIMIT or value.denominator > LIMIT:
                raise ValueError('result bound')
    except (ValueError, ZeroDivisionError):
        return 1, b''

    def text(value):
        return f'{value.numerator}/{value.denominator}'

    lines = [f'LEFT {text(left)}', f'RIGHT {text(right)}',
             'LESS ' + str(left < right).lower(), f'SUM {text(total)}',
             f'PRODUCT {text(product)}', f'SMALLER {text(min(left, right))}',
             'SORTED ' + ' '.join(text(x) for x in sorted([left, right, Fraction(0)]))]
    return 0, ('\n'.join(lines) + '\n').encode()


def main():
    reference = (ROOT / 'CPPI5-Fraction-Toolkit/solution/main.cpp').read_text()
    starter = (ROOT / 'CPPI5-Fraction-Toolkit/starter/main.cpp').read_text()
    pattern = re.compile(r'(// TODO BEGIN (\w+)\n)(.*?)(        // TODO END \2|    // TODO END \2)', re.S)
    bodies = {m[2]: m[3] for m in pattern.finditer(reference)}
    assert len(bodies) == 5
    completed = pattern.sub(lambda m: m[1] + bodies[m[2]] + m[4], starter)
    assert completed == reference
    cases = [[], ['-1/2', '2/3'], ['-1/-2', '2/-3'], ['0/-4', '0003/0009'],
             ['1000000/1', '0/1'], ['-1000000/1', '0/1'], ['1/1000000', '0/1'],
             ['1/4', '1/5'], ['1000/1', '1000/1'], ['1001/1', '1000/1'],
             ['1000000/1', '1/1'], ['1/1001', '1000/1001'],
             ['2/2', '-3/-3'], ['0/-1', '-0/9']]
    invalid = ['1/0', '0/0', '1000001/1', '-1000001/1', '1/1000001',
               '1/-1000001', '1', '/1', '1/', '1/2/3', '+1/2', '1/+2',
               ' 1/2', '1/2 ', '1.0/2', '1e2/3', '--1/2', '1/2x',
               '١/2', '9' * 40 + '/1']
    cases += [[text, '1/2'] for text in invalid]
    cases += [['1/2', text] for text in invalid]
    cases += [['1/2'], ['1/2', '2/3', '3/4']]
    generator = random.Random(20261008)
    cases += [[f'{generator.randint(-300, 300)}/{generator.randint(1, 90)}'
               for _ in range(2)] for _ in range(40)]
    cases += [['0' * 5000 + '1/0002', '2/3'], ['999999/1000000', '1/1000000'],
              ['1000000/999999', '999999/1000000'], ['1000000/1', '-1000000/1'],
              ['999999/1000000', '999999/1000000']]
    with tempfile.TemporaryDirectory(prefix='cppi5-value-') as name:
        work = Path(name)
        (work / 'completed.cpp').write_text(completed)
        probe = (ROOT / 'test/fraction-value-probe.cpp').read_text()
        for standard in [17, 20]:
            for sanitized in [False, True]:
                build_flags = compiler_flags(standard, sanitized)
                for label, source in [('learner', ROOT / 'CPPI5-Fraction-Toolkit/starter/main.cpp'),
                                      ('reference', ROOT / 'CPPI5-Fraction-Toolkit/solution/main.cpp'),
                                      ('completed', work / 'completed.cpp')]:
                    binary = work / f'{label}-{standard}-{int(sanitized)}'
                    execute([os.environ.get('CXX', 'c++'), *build_flags, str(source),
                             '-o', str(binary)], work)
                    if label == 'learner':
                        output, error = execute([str(binary)], work, 1)
                        assert output == b'' and b'Unfinished task: constructFraction.' in error
                        continue
                    for arguments in cases:
                        status, expected = model(arguments)
                        output, error = execute([str(binary), *arguments], work, status)
                        assert output == expected, (arguments, output, expected)
                        if status == 0:
                            assert error == b''
                        elif status == 2:
                            assert error == b'Usage: main [LEFT_FRACTION RIGHT_FRACTION]\n'
                        else:
                            assert error.startswith(b'Rejected: ')
                    assert probe.count('CPPI5_VALUE_SOURCE') == 1
                    (work / 'probe.cpp').write_text(probe.replace('CPPI5_VALUE_SOURCE', str(source.resolve())))
                    probe_binary = work / f'probe-{label}-{standard}-{int(sanitized)}'
                    execute([os.environ.get('CXX', 'c++'), *build_flags, 'probe.cpp', '-o', str(probe_binary)], work)
                    assert execute([str(probe_binary)], work) == (b'Copy, const, order and failure invariants verified.\n', b'')
    print(json.dumps({'event': 'verified-fraction-toolkit', 'casesPerCompletedProgram': len(cases),
                      'compilerVariants': 12, 'independentFractionModel': True,
                      'completedLearnerEqualsReference': True,
                      'ordinaryAndSanitized': True, 'copyConstAndOrderingProbes': 8, 'sourceIntegration': 'requires exact-commit hosted review'}))


if __name__ == '__main__':
    main()
