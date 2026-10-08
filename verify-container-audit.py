"""Check the optional audit against real inventory calls and a plain-row model."""

import importlib.util
import json
import os
from pathlib import Path
import re
import tempfile

ROOT = Path(__file__).resolve().parent
PACK = ROOT / 'CPPI3-Container-Tradeoff-Audit'
INVENTORY = ROOT / 'CPPI3-Inventory-Indexer'
FLAGS = ['-Wall', '-Wextra', '-Wpedantic', '-Werror', '-g', '-O0']
METHODS = [('selectCategory', 'select_category'),
           ('projectNames', 'project_names'),
           ('joinSuppliers', 'join_suppliers'),
           ('renameCategory', 'rename_category')]


def case_sections(document):
    matches = list(re.finditer(r'^#{2,3} Case ([ABC]):[^\n]*\n', document, re.M))
    assert [m[1] for m in matches] == ['A', 'B', 'C']
    return {m[1]: document[m.end():matches[i + 1].start()
            if i + 1 < len(matches) else len(document)] for i, m in enumerate(matches)}


def document_cases(learner):
    sections = case_sections(learner)
    rows = []
    for line in re.search(r'```text\n(.*?)```', sections['A'], re.S)[1].splitlines():
        fields = line.split(' | ')
        assert len(fields) == 4
        rows.append((int(fields[0]), fields[1], fields[2], int(fields[3])))
    item_pattern = r'\{(-?\d+), "([^"\n]+)", "([^"\n]+)", (-?\d+)\}'
    duplicate = re.findall(item_pattern, sections['A'])
    c_rows = re.findall(item_pattern, sections['C'])
    assert len(duplicate) == 1 and len(c_rows) == 2
    def item(fields):
        return int(fields[0]), fields[1], fields[2], int(fields[3])
    suppliers = {}
    for label, section in sections.items():
        text = re.search(r'\{\{.*?\}\}', section)[0]
        pairs = re.findall(r'\{(-?\d+), "([^"\n]+)"\}', text)
        assert pairs
        suppliers[label] = [(int(k), v) for k, v in pairs]
    assert 'Select tools' in sections['A'] and 'rename tools to lab' in sections['A']
    assert 'select missing' in sections['B'] and 'rename missing to new' in sections['B']
    assert 'Rename lab to lab' in sections['C'] and 'rename\nmissing to ghost' in sections['C']
    assert 'name to `copy-only` locally' in sections['C']
    return {'A': {'rows': rows, 'duplicate': item(duplicate[0]), 'suppliers': suppliers['A']},
            'B': {'rows': [], 'suppliers': suppliers['B']},
            'C': {'rows': [item(x) for x in c_rows], 'suppliers': suppliers['C']}}


def row_text(row):
    return ' | '.join(map(str, row))


def model(label, data, complete=True):
    """Plain rows and linear ID/supplier comparisons, independent of C++ indexes."""
    rows = []
    lines = ['Case ' + label]
    def add(row):
        if any(existing[0] == row[0] for existing in rows):
            return False
        rows.append(list(row))
        return True
    def boolean(value):
        return 'true' if value else 'false'
    def select(category):
        return [row[:] for row in rows if row[2] == category] if complete else []
    def show(label_text, selected):
        lines.extend([label_text + ':', *[row_text(row) for row in selected]])
    def categories():
        values = sorted({row[2] for row in rows})
        lines.append('Categories:' + ''.join(' ' + value for value in values))
    def names(selected):
        projected = sorted(row[1] for row in selected) if complete else []
        lines.append('Names:' + ''.join(' ' + name for name in projected))
    def join():
        lines.append('Suppliers:')
        if complete:
            for row in rows:
                match = next((v for k, v in data['suppliers'] if k == row[0]), None)
                if match is not None:
                    lines.append(f'{row[0]} | {row[1]} | {row[3]} | {match}')
    def rename(source, target):
        found = complete and any(row[2] == source for row in rows)
        if found:
            for row in rows:
                if row[2] == source:
                    row[2] = target
        lines.append('Rename ' + source + ' to ' + target + ': ' + boolean(found))
    accepted = [boolean(add(row)) for row in data['rows']]
    lines.append('Adds:' + ''.join(' ' + value for value in accepted))
    if label == 'A':
        lines.append('Duplicate: ' + boolean(add(data['duplicate'])))
        categories()
        selected = select('tools')
        show('Selected', selected)
        names(selected)
        join()
        rename('tools', 'lab')
        categories()
        show('Old view', selected)
        show('Tools after', select('tools'))
        show('Lab after', select('lab'))
    elif label == 'B':
        categories()
        selected = select('missing')
        show('Selected', selected)
        names(selected)
        join()
        rename('missing', 'new')
        categories()
    else:
        selected = select('lab')
        show('Selected', selected)
        names(selected)
        join()
        rename('lab', 'lab')
        categories()
        rename('missing', 'ghost')
        categories()
        if selected:
            selected[0][1] = 'copy-only'
        show('Edited copy', selected)
        show('Fresh query', select('lab'))
    return '\n'.join(lines) + '\n'


def check_documents():
    learner = (PACK / 'starter/WORKSHEET.md').read_text()
    staff = (PACK / 'solution/WORKED-AUDIT.md').read_text()
    assert (PACK / 'README.md').read_text() == learner
    for field in ['Duplicate-add return and preserved data:',
                  'Earlier selected copy after the rename:',
                  'Actual probe outputs, commands, statuses and source identity:',
                  'Two custom cases, predictions and observations:',
                  'One limitation and the additional evidence needed to resolve it:']:
        assert field + ' [record]' in learner
    assert 'optional worksheet' in learner and 'C++17/20' in learner
    assert 'zero exit status does not establish' in learner
    assert 'same worksheet' in learner and 'saved' in learner
    assert 'Verified probe transcript' not in learner
    cases = document_cases(learner)
    for label, section in case_sections(staff).items():
        transcript = re.search(r'### Verified probe transcript\n\n```text\n(.*?)```', section, re.S)
        assert transcript and transcript[1] == model(label, cases[label])
    assert model('A', cases['A']) != model('A', cases['A'], False)
    assert model('C', cases['C']) != model('C', cases['C'], False)
    return learner, staff, cases


def body_span(source, name):
    match = re.search(r'\b' + name + r'\s*\([^;{}]*\)\s*(?:const\s*)?\{', source, re.S)
    assert match, name
    start = match.end() - 1
    depth = 0
    for index in range(start, len(source)):
        if source[index] == '{':
            depth += 1
        elif source[index] == '}':
            depth -= 1
            if not depth:
                return start, index + 1
    raise AssertionError('unclosed function ' + name)


def completed_learner(starter, reference):
    assert starter.count('// TODO:') == 4
    for learner_name, staff_name in METHODS:
        a, b = body_span(starter, learner_name)
        c, d = body_span(reference, staff_name)
        body = reference[c:d]
        if learner_name == 'joinSuppliers':
            body = body.replace('supplier_by_id', 'supplierById')
        starter = starter[:a] + body + starter[b:]
    assert '// TODO:' not in starter
    return '#include <sstream>\n' + starter


def cpp_items(rows):
    return '{' + ','.join('{' + ','.join([str(r[0]), json.dumps(r[1]),
                                        json.dumps(r[2]), str(r[3])]) + '}' for r in rows) + '}'


def cpp_suppliers(rows):
    return '{' + ','.join('{' + str(k) + ',' + json.dumps(v) + '}' for k, v in rows) + '}'


PROBE = r'''
void rows(const char* label, const std::vector<Item>& selected) {
    std::cout << label << ":\n";
    for (const auto& row : selected) {
        std::cout << row.id << " | " << row.name << " | "
                  << row.category << " | " << row.quantity << '\n';
    }
}
void names(const std::vector<std::string>& values) {
    std::cout << "Names:";
    for (const auto& value : values) std::cout << ' ' << value;
    std::cout << '\n';
}
void suppliers(const std::vector<std::string>& values) {
    std::cout << "Suppliers:\n";
    for (const auto& value : values) std::cout << value << '\n';
}
void caseA() {
    std::cout << "Case A\nAdds:";
    InventoryIndex inventory;
    for (const auto& item : std::vector<Item>ITEMS_A) std::cout << ' ' << inventory.add(item);
    std::cout << "\nDuplicate: " << inventory.add(ItemDUPLICATE) << '\n';
    inventory.PRINT();
    const auto selected = inventory.SELECT("tools");
    rows("Selected", selected);
    names(inventory.PROJECT(selected));
    suppliers(inventory.JOIN(std::map<int, std::string>SUPPLIERS_A));
    std::cout << "Rename tools to lab: " << inventory.RENAME("tools", "lab") << '\n';
    inventory.PRINT();
    rows("Old view", selected);
    rows("Tools after", inventory.SELECT("tools"));
    rows("Lab after", inventory.SELECT("lab"));
}
void caseB() {
    std::cout << "Case B\nAdds:\n";
    InventoryIndex inventory;
    inventory.PRINT();
    const auto selected = inventory.SELECT("missing");
    rows("Selected", selected);
    names(inventory.PROJECT(selected));
    suppliers(inventory.JOIN(std::map<int, std::string>SUPPLIERS_B));
    std::cout << "Rename missing to new: " << inventory.RENAME("missing", "new") << '\n';
    inventory.PRINT();
}
void caseC() {
    std::cout << "Case C\nAdds:";
    InventoryIndex inventory;
    for (const auto& item : std::vector<Item>ITEMS_C) std::cout << ' ' << inventory.add(item);
    std::cout << '\n';
    auto selected = inventory.SELECT("lab");
    rows("Selected", selected);
    names(inventory.PROJECT(selected));
    suppliers(inventory.JOIN(std::map<int, std::string>SUPPLIERS_C));
    std::cout << "Rename lab to lab: " << inventory.RENAME("lab", "lab") << '\n';
    inventory.PRINT();
    std::cout << "Rename missing to ghost: " << inventory.RENAME("missing", "ghost") << '\n';
    inventory.PRINT();
    if (!selected.empty()) selected.front().name = "copy-only";
    rows("Edited copy", selected);
    rows("Fresh query", inventory.SELECT("lab"));
}
int main() {
    std::cout << std::boolalpha;
    caseA(); caseB(); caseC(); caseA();
}
'''


def probe(source, cases, camel_case):
    assert source.count('int main() {') == 1 and source.rstrip().endswith('}')
    source = source.replace('int main() {', 'int inventoryDemonstration() {', 1)
    end = source.rfind('}')
    source = source[:end] + '    return 0;\n' + source[end:]
    code = PROBE
    for label in ['A', 'B', 'C']:
        code = code.replace('ITEMS_' + label, cpp_items(cases[label]['rows']))
        code = code.replace('SUPPLIERS_' + label, cpp_suppliers(cases[label]['suppliers']))
    code = code.replace('DUPLICATE', cpp_items([cases['A']['duplicate']])[1:-1])
    for placeholder, pair in [('SELECT', METHODS[0]), ('PROJECT', METHODS[1]),
                              ('JOIN', METHODS[2]), ('RENAME', METHODS[3]),
                              ('PRINT', ('printCategories', 'print_categories'))]:
        code = code.replace(placeholder, pair[0 if camel_case else 1])
    return source + '\n' + code


def main():
    learner, staff, cases = check_documents()
    spec = importlib.util.spec_from_file_location('container_process_runner', ROOT / 'verify-task-manager.py')
    runner = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(runner)
    runner.TASK = os.environ.get('CLASSES_AUDIT_PARENT_TASK_ID', 'cppi3-container-audit-source')
    run = runner.run
    starter_path = INVENTORY / 'starter/main.cpp'
    reference_path = INVENTORY / 'solution/main.cpp'
    source_before = [starter_path.read_bytes(), reference_path.read_bytes()]
    starter, reference = [x.decode() for x in source_before]
    completed = completed_learner(starter, reference)
    compiler = os.environ.get('CXX', 'clang++')
    with tempfile.TemporaryDirectory(prefix='cppi3-container-audit-') as directory:
        work = Path(directory)
        for sanitized in [False, True]:
            flags = FLAGS + (['-fsanitize=address,undefined', '-fno-sanitize-recover=all'] if sanitized else [])
            prefix = ['env', 'ASAN_OPTIONS=detect_leaks=0'] if sanitized else []
            for role, source, camel, complete in [('starter', starter, True, False),
                    ('reference', reference, False, True), ('completed-learner', completed, True, True)]:
                fixture = work / 'probe.cpp'
                fixture.write_text(probe(source, cases, camel))
                binary = work / 'probe'
                out, err = run([compiler, '-std=c++20', *flags, str(fixture), '-o', str(binary)], work)
                assert not out and not err
                out, err = run([*prefix, str(binary)], work)
                expected = ''.join(model(label, cases[label], complete) for label in ['A', 'B', 'C', 'A'])
                assert out == expected and not err, (role, sanitized, out, expected, err)
                print(json.dumps({'event': 'verified-container-probe', 'role': role,
                    'sanitized': sanitized, 'worksheetCases': 3, 'repeatCaseA': True,
                    'independentModel': 'plain-row-linear-lookups', 'complete': complete}))
            for role, document in [('starter', learner), ('solution', staff)]:
                binary = work / ('notes-' + role)
                out, err = run([compiler, '-std=c++17', *flags, str(PACK / role / 'main.cpp'), '-o', str(binary)], work)
                assert not out and not err
                out, err = run([*prefix, str(binary)], work)
                assert out == document and not err
        cmake = work / 'cmake'
        run(['cmake', '-S', str(ROOT), '-B', str(cmake)], work)
        run(['cmake', '--build', str(cmake), '--target', 'container_audit_starter', 'container_audit_solution'], work)
        for role, document in [('starter', learner), ('solution', staff)]:
            out, err = run([str(cmake / ('container_audit_' + role))], work)
            assert out == document and not err
    assert [starter_path.read_bytes(), reference_path.read_bytes()] == source_before
    print(json.dumps({'event': 'verified-container-worksheet-contract', 'worksheetCases': 3,
        'inventoryProbeVariants': 6, 'printerVariants': 4, 'cmakePrinters': 2,
        'sameProcessFreshInstanceVariants': 4, 'primaryInventorySourceUnchanged': True,
        'independentModel': 'plain-row-linear-lookups'}))


if __name__ == '__main__':
    main()
