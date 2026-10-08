"""Execute the complete value/template lesson programs and changed cases."""
import json
import os
from pathlib import Path
import re
import tempfile
from cppi5_native_checks import ROOT, execute, flags

PACK = ROOT / 'CPPI5-Fraction-Toolkit'


def program(name):
    document = (PACK / name).read_text()
    examples = re.findall(r'```cpp\n(.*?)\n```', document, re.S)
    expected = re.findall(r'```text\n(.*?)\n```', document, re.S)
    assert len(examples) == len(expected) == 1
    return examples[0] + '\n', (expected[0] + '\n').encode()


def value_result(original, delta):
    if not 0 <= original <= 100 or not 0 <= original + delta <= 100:
        return 1, b'', b'Rejected: Score outside 0 through 100.\n'
    copy = original + delta
    rejected = copy > 0
    return 0, (f'original {original}\ncopy {copy}\noperator {copy}\n'
               f'less {str(original < copy).lower()}\n'
               f'rejected {str(rejected).lower()}\n'
               f'preserved {str(rejected).lower()}\n').encode(), b''


def main():
    compiler = os.environ.get('CXX', 'g++')
    value, value_expected = program('VALUE-TYPE-LESSON.md')
    template, template_expected = program('TEMPLATE-LESSON.md')
    assert value_result(84, 7) == (0, value_expected, b'')
    assert template_expected == b'number 3\ntext apple\nreading 59\ntie left\n'
    with tempfile.TemporaryDirectory(prefix='cppi5-lessons-') as name:
        work = Path(name)
        for standard in [17, 20]:
            for sanitized in [False, True]:
                for label, text, expected in [('value', value, value_expected),
                                               ('template', template, template_expected)]:
                    source = work / (label + '.cpp')
                    source.write_text(text)
                    binary = work / label
                    execute([compiler, *flags(standard, sanitized), str(source),
                             '-o', str(binary)], work)
                    assert execute([str(binary)], work) == (expected, b'')
                    assert execute([str(binary), 'extra'], work, 2) == (
                        b'', f'Usage: {label}-lesson\n'.encode())
                for original, delta in [(59, 1), (84, 0), (100, 0), (0, 0), (0, 1),
                                         (-1, 7), (101, 7), (100, 1)]:
                    changed = value.replace('Score original(84)', f'Score original({original})')
                    changed = changed.replace('copy.raisedBy(7)', f'copy.raisedBy({delta})')
                    changed = changed.replace('original + 7', f'original + {delta}')
                    (work / 'value-case.cpp').write_text(changed)
                    execute([compiler, *flags(standard, sanitized), 'value-case.cpp',
                             '-o', 'value-case'], work)
                    status, output, error = value_result(original, delta)
                    assert execute(['./value-case'], work, status) == (output, error)
                changed = template.replace('chooseSmaller(7, 3)', 'chooseSmaller(-4, 6)')
                changed = changed.replace('std::string("pear"), std::string("apple")',
                                          'std::string("z"), std::string("aa")')
                changed = changed.replace('Reading{84, "high"}, Reading{59, "low"}',
                                          'Reading{0, "high"}, Reading{100, "low"}')
                changed = changed.replace('Reading{59, "left"}, Reading{59, "right"}',
                                          'Reading{59, "right"}, Reading{59, "left"}')
                (work / 'template-case.cpp').write_text(changed)
                execute([compiler, *flags(standard, sanitized), 'template-case.cpp',
                         '-o', 'template-case'], work)
                assert execute(['./template-case'], work) == (
                    b'number -4\ntext aa\nreading 0\ntie right\n', b'')
        comparison = '''    friend bool operator<(const Reading& left, const Reading& right) {
        return left.value < right.value;
    }
'''
        assert template.count(comparison) == 1
        (work / 'missing-comparison.cpp').write_text(template.replace(comparison, ''))
        output, error = execute([compiler, *flags(20, False), '-fsyntax-only',
                                 'missing-comparison.cpp'], work, 1)
        assert output == b'' and b'Reading' in error and b'chooseSmaller' in error
        (work / 'mixed-type.cpp').write_text(template.replace('chooseSmaller(7, 3)',
                                                             'chooseSmaller(7, 3.5)'))
        output, error = execute([compiler, *flags(20, False), '-fsyntax-only',
                                 'mixed-type.cpp'], work, 1)
        assert output == b'' and b'chooseSmaller' in error and b'int' in error and b'double' in error
        (work / 'const-assignment.cpp').write_text(value.replace('const Score original(84);',
                                                                'const Score original(84);\n        original = Score(0);'))
        output, error = execute([compiler, *flags(20, False), '-fsyntax-only',
                                 'const-assignment.cpp'], work, 1)
        assert output == b'' and b'const' in error
    print(json.dumps({'event': 'verified-cppi5-lessons', 'fullPrograms': 2,
                      'standards': [17, 20], 'ordinaryAndSanitized': True,
                      'changedValueCases': 8, 'changedTemplateOutput': True,
                      'actualMissingComparisonFailure': True,
                      'actualMixedDeductionFailure': True,
                      'actualConstAssignmentFailure': True}))


if __name__ == '__main__':
    main()
