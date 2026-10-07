"""Verify inventory views and state preservation against real allocation failures."""

import ast
import json
import os
from pathlib import Path
import tempfile

ROOT = Path(__file__).resolve().parent
tree = ast.parse((ROOT / "verify-build-debug.py").read_text())
selected = [node for node in tree.body if isinstance(node, (ast.Import, ast.ImportFrom))
            or isinstance(node, ast.FunctionDef) and node.name == "run"]
namespace = {"TASK": os.environ.get("CLASSES_AUDIT_PARENT_TASK_ID", "cpp3-inventory-source")}
exec(compile(ast.Module(body=selected, type_ignores=[]), "verified-process-helper", "exec"), namespace)
run = namespace["run"]

COMMON = r'''
#include <cassert>
#include <cstdlib>
#include <new>
#include <sstream>
static int allocation_countdown=-1;
void* operator new(std::size_t n) {
    if (allocation_countdown>0 && --allocation_countdown==0) throw std::bad_alloc();
    if (void* p=std::malloc(n ? n : 1)) return p;
    throw std::bad_alloc();
}
void operator delete(void* p) noexcept { std::free(p); }
void operator delete(void* p,std::size_t) noexcept { std::free(p); }
std::string categories(const InventoryIndex& index) {
    std::ostringstream out;
    auto* previous=std::cout.rdbuf(out.rdbuf());
    index.PRINT();
    std::cout.rdbuf(previous);
    return out.str();
}
int main() {
    int add_failures=0;
    for (int nth=1; nth<=32; ++nth) {
        InventoryIndex index;
        assert(index.add({1,"existing","tools",2}));
        const auto before=categories(index);
        const Item next{2,std::string(200,'n'),std::string(200,'c'),3};
        bool threw=false;
        allocation_countdown=nth;
        try { assert(index.add(next)); } catch(const std::bad_alloc&) { threw=true; }
        allocation_countdown=-1;
        if (!threw) break;
        ++add_failures;
        assert(categories(index)==before);
        assert(index.add(next));
        assert(!index.add({1,"replacement","ghost",99}));
        assert(!index.add(next));
        assert(categories(index)=="Categories: "+std::string(200,'c')+" tools\n");
        ROLE_ADD_CHECK
    }
    assert(add_failures>=3);
    InventoryIndex empty;
    assert(categories(empty)=="Categories:\n");
    ROLE_CHECKS
    std::cout << "supplied insertion allocation failures checked: " << add_failures << '\n';
}
'''
REFERENCE_CHECKS = r'''
    assert(empty.select_category("absent").empty());
    assert(empty.project_names({}).empty() && empty.join_suppliers({}).empty());
    InventoryIndex index;
    assert(index.add({7,"beta","tools",2}) && index.add({2,"alpha","tools",0}) && index.add({9,"alpha","lab",3}));
    assert(!index.add({7,"replaced","ghost",99}));
    assert(categories(index)=="Categories: lab tools\n");
    const auto tools=index.select_category("tools");
    assert(tools.size()==2 && tools[0].id==7 && tools[1].id==2);
    assert((index.project_names(tools)==std::vector<std::string>{"alpha","beta"}));
    assert((index.project_names({{1,"same","",0},{2,"same","",0}})==std::vector<std::string>{"same","same"}));
    assert(index.select_category("absent").empty());
    assert((index.join_suppliers({{2,"Second"},{7,"First"}})==std::vector<std::string>{"7 | beta | 2 | First","2 | alpha | 0 | Second"}));
    assert(index.rename_category("tools","lab") && categories(index)=="Categories: lab\n");
    assert(index.select_category("tools").empty() && index.select_category("lab").size()==3);
    assert(index.rename_category("lab","lab") && !index.rename_category("missing","other"));
    int rename_failures=0;
    for (int nth=1; nth<=32; ++nth) {
        InventoryIndex current;
        assert(current.add({4,"one","old",1}) && current.add({5,"two","old",2}));
        const auto before=current.join_suppliers({{4,"A"},{5,"B"}});
        const std::string replacement(200,'x');
        bool threw=false;
        allocation_countdown=nth;
        try { assert(current.rename_category("old",replacement)); } catch(const std::bad_alloc&) { threw=true; }
        allocation_countdown=-1;
        if (!threw) break;
        ++rename_failures;
        assert(categories(current)=="Categories: old\n");
        assert(current.select_category("old").size()==2 && current.select_category(replacement).empty());
        assert(current.join_suppliers({{4,"A"},{5,"B"}})==before);
        assert(current.rename_category("old",replacement));
        assert(current.select_category("old").empty() && current.select_category(replacement).size()==2);
        assert(categories(current)=="Categories: "+replacement+"\n");
    }
    assert(rename_failures>=3);
    std::cout << "reference views and rename allocation failures checked: " << rename_failures << '\n';
'''
STARTER_CHECKS = r'''
    InventoryIndex incomplete;
    assert(incomplete.add({8,"unfinished","tools",1}));
    assert(incomplete.selectCategory("tools").empty());
    assert(incomplete.projectNames({{8,"unfinished","tools",1}}).empty());
    assert(incomplete.joinSuppliers({{8,"Lab"}}).empty());
    assert(!incomplete.renameCategory("tools","lab"));
    assert(categories(incomplete)=="Categories: tools\n");
'''

FLAGS = ["-std=c++20", "-Wall", "-Wextra", "-Wpedantic", "-Werror", "-g", "-O0"]
with tempfile.TemporaryDirectory(prefix="cpp3-inventory-") as directory:
    work = Path(directory)
    for role in ("starter", "solution"):
        path = ROOT / "CPPI3-Inventory-Indexer" / role / "main.cpp"
        text = path.read_text()
        assert text.count("int main() {") == 1
        if role == "starter":
            assert text.count("// TODO:") == 4
        for sanitized in (False, True):
            flags = FLAGS + (["-fsanitize=address,undefined", "-fno-sanitize-recover=all"] if sanitized else [])
            program = work / (role + "-demo")
            out, err = run(["clang++", *flags, str(path), "-o", str(program)], work)
            assert not out and not err
            out, err = run([str(program)], work)
            assert err == ""
            if role == "starter":
                assert out == "Categories: electronics tools\nTool names:\n"
            else:
                assert out == ("Duplicate accepted? no\nCategories: electronics tools\n"
                               "Tool names: debug cable hex driver\nCategories: lab tools\n"
                               "101 | debug cable | 6 | North Lab\n102 | sensor kit | 3 | Circuit House\n"
                               "103 | hex driver | 10 | North Lab\n104 | breadboard | 8 | Circuit House\n")
            harness = text.split("int main() {", 1)[0] + COMMON
            harness = harness.replace("PRINT()", "printCategories()" if role == "starter" else "print_categories()")
            harness = harness.replace("ROLE_ADD_CHECK", "" if role == "starter" else
                                      'assert(index.select_category("tools").size()==1 && index.select_category(std::string(200,\'c\')).size()==1);')
            harness = harness.replace("ROLE_CHECKS", STARTER_CHECKS if role == "starter" else REFERENCE_CHECKS)
            # This demonstration-only constant is retained in the original source.
            if role == "solution":
                harness = harness.replace('int main() {\n    int add_failures', 'int main() {\n    assert(DUPLICATE_QUANTITY==1 && LAB_CATEGORY=="lab");\n    int add_failures')
            fixture = work / (role + "-checks.cpp")
            fixture.write_text(harness)
            executable = work / (role + "-checks")
            out, err = run(["clang++", *flags, str(fixture), "-o", str(executable)], work)
            assert not out and not err
            out, err = run([str(executable)], work)
            assert "supplied insertion allocation failures checked:" in out and not err
            print(json.dumps({"event": "checked", "role": role, "sanitized": sanitized, "actualEvidence": out}))
print(json.dumps({"event": "verified", "project": "CPPI3-Inventory-Indexer",
                  "ordinaryAndSanitized": True, "realViewsAndFaultInjection": True,
                  "originalDemoAndMethodsRetained": True, "learnerRemainsIncomplete": True}))
