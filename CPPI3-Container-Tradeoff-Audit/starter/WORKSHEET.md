# Container Tradeoff Audit

This optional worksheet extends the completed, saved Inventory Indexer. Keep
that source and attempt. Explain one container decision using the operations
the program actually performs, then test a small proposed change separately.
The preserved optional `main.cpp` is a notes printer, not another inventory
implementation or an automatic assessment of an explanation.

## Prepare and establish the behavior

Complete the primary project's four query and rename TODOs first. Record the
saved source role, revision or ZIP, compiler version and platform. Compile and
run the unchanged saved demonstration before any experiments:

```sh
c++ --version
c++ -std=c++20 -Wall -Wextra -Wpedantic -Werror main.cpp -o inventory
./inventory
```

Retain actual stdout, stderr and exit status. The untouched starter prints an
empty Tool names line and no joined rows; a zero exit status does not establish
that its TODOs are complete. The staff demonstration uses a different number
of rows, so compare your own source's input and behavior rather than treating
the demonstrations as identical fixtures.

The starter uses camel-case query names; the reference uses underscores:
`selectCategory` / `select_category`, `projectNames` / `project_names`,
`joinSuppliers` / `join_suppliers`, `renameCategory` / `rename_category`, and
`printCategories` / `print_categories`. Keep the original names in your source.

## Map the real operations

An owning container keeps its element values alive. A pointer, reference or
iterator can refer to one of those elements without owning it. A numeric
position is a separate value interpreted relative to the current sequence;
it neither owns a row nor automatically tracks that row after a reorder.

Vector keeps non-bool elements contiguous and supports direct access by a
position. Appending is amortized constant work: the cost is bounded across a
sequence of appends, while one capacity-growth append can move or copy the
existing elements. A sorted map or set supports logarithmic key lookup and
sorted traversal. An unordered map uses hashing with average constant lookup
and a linear worst case; its traversal does not provide sorted key order.
These guarantees alone do not identify the fastest choice for a small program.

Worst case bounds one operation over its permitted inputs. An average-case
claim depends on the relevant distribution, while an amortized claim distributes
cost across a sequence of operations. Neither average nor amortized constant
lookup/append promises a fixed number of machine instructions every time.
Space also matters: duplicated indexes, stored strings, allocations and spare
sequence capacity can outweigh a lookup saving. Measure an actual proposed
change before presenting a speed or memory advantage as an observed result.

Read the actual `InventoryIndex` definitions. The sequence owns Item values;
the ID map records sequence positions, and the category set records unique
category strings. The map is not a category index and a stored position is not
a pointer. Query results are copies. There is no public erase or ID-edit
operation in this project.

For each operation, identify the loop or standard-library call and record its
purpose before proposing a replacement:

| Operation | Actual source location | Ordering or uniqueness required | Work as size grows | Possible alternative and cost |
| --- | --- | --- | --- | --- |
| Add and reject an existing ID | [record] | [record] | [record] | [record] |
| Select a category | [record] | [record] | [record] | [record] |
| Project sorted names | [record] | [record] | [record] | [record] |
| Rename a category | [record] | [record] | [record] | [record] |
| Join suppliers by ID | [record] | [record] | [record] | [record] |
| Print unique categories | [record] | [record] | [record] | [record] |

Use N for inventory rows, C for distinct categories, K for selected rows and M
for suppliers. State which quantity each claim measures. Separate traversal,
lookup, allocation and string-copy costs. A complexity bound is not a measured
runtime. Average, amortized and worst-case claims describe different guarantees.

## Predict three probes

Make a separate copy of the saved source as `audit_probe.cpp`. Keep Item and
InventoryIndex definitions unchanged; replace only that copy's demonstration
main with calls that exercise the data below. Print all fields of selected rows,
the projected names, joined display strings, category output and mutation return
values. Run each case on a fresh InventoryIndex. Preserve the original saved
source and record the probe's commands and source separately.

Before running, write predictions for every observation. The input rows here
are ordered by insertion, not by ID, name or supplier-map order.

### Case A: Different orders and a merging rename

Insert these rows in order:

```text
7 | beta | tools | 2
2 | alpha | tools | 0
9 | alpha | lab | 3
```

Try adding `{7, "replacement", "ghost", 99}`. Select tools and project those
selected names. Join the supplier map `{{2, "Second"}, {7, "First"}}`. Record
categories, rename tools to lab, then record categories and both category views.
Retain the original selected copy and show whether the rename changes that copy.

- Duplicate-add return and preserved data: [record]
- Selected rows and projected names in their respective orders: [record]
- Joined rows, including the missing-supplier decision: [record]
- Categories and rename return before and after the mutation: [record]
- Earlier selected copy after the rename: [record]

### Case B: Empty inventory

With no rows, select missing, project that result, join `{{8, "Unused"}}`, and
rename missing to new. Record category output and every result. Distinguish an
empty vector from an error, and a false rename result from an exception.

- Predicted empty results, rename return and exact category line: [record]

### Case C: Duplicate names and an unchanged-name request

Insert `{5, "same", "lab", 1}` followed by `{3, "same", "lab", 0}`. Select lab,
project those names and join `{{5, "Known"}}`. Rename lab to lab, then rename
missing to ghost. Record categories after both calls. Change the first selected
copy's name to `copy-only` locally, then select lab again to test whether a query copy can
mutate the inventory.

- Selected rows and duplicate-name behavior: [record]
- Join, both rename returns and categories: [record]
- Local copy edit and new query: [record]

Compile and run the probe separately:

```sh
c++ -std=c++20 -Wall -Wextra -Wpedantic -Werror audit_probe.cpp -o audit-probe
./audit-probe
c++ -std=c++20 -Wall -Wextra -Wpedantic -Werror -g -O0 -fsanitize=address,undefined -fno-sanitize-recover=all audit_probe.cpp -o audit-probe-debug
ASAN_OPTIONS=detect_leaks=0 ./audit-probe-debug
```

Record actual stdout, stderr and exit status, or the exact tool limitation.
Sanitizer success for these executions is not a proof of leak freedom or all
possible inputs. Find the first prediction mismatch and its actual source cause
before consulting the separate staff example.

## Propose one bounded change

Choose one: retain the current ID map, prototype an unordered ID map, or retain
the vector after comparing another row container. State the operation you expect
to improve and the behavior you must preserve. Do not change the public supplier
map argument merely because the private ID index changes.

Use a separate experimental copy. Preserve insertion-order selection and joins,
duplicate ID rejection, sorted projected names with duplicates retained, sorted
unique categories, and failed-mutation rollback. An ID index change does not
accelerate the category scan. A category index would need updates during both
insertion and rename, including allocation-failure recovery.

Describe iterator and reference validity. Vector reallocation invalidates
element pointers, references and iterators; numeric positions still identify
the same logical rows after append, but an erase or reorder would require index
maintenance. Do not add unsupported erase behavior silently. An unordered map's
iteration order does not become the inventory's required output order.

Rerun all three probes before and after the change. Add two cases of your own,
including one that could expose a stale index or lost ordering. If you report
timings, record input sizes, compiler flags, repetitions and actual measurements;
otherwise label performance claims as source-based bounds and hypotheses.

## Review the decision

- Chosen container, operation and preserved requirements: [record]
- Source-based complexity and memory tradeoffs, with assumptions: [record]
- Actual probe outputs, commands, statuses and source identity: [record]
- First mismatch and corrected explanation: [record]
- Two custom cases, predictions and observations: [record]
- Proposed change or reason to keep the current design: [record]
- One limitation and the additional evidence needed to resolve it: [record]

Submit these notes with the saved primary project and separate probe. An
instructor can pause at each prediction, observation and design decision using
the same worksheet. The staff example describes one verified implementation;
it does not certify a saved attempt or substitute invented evidence counts.

For library guarantees, consult the standard working draft's
[vector overview](https://eel.is/c++draft/vector.overview),
[vector invalidation rules](https://eel.is/c++draft/vector.modifiers),
[associative requirements](https://eel.is/c++draft/associative.reqmts) and
[unordered requirements](https://eel.is/c++draft/unord.req).
These are living draft pages; use only features available in this C++17/20 pack.
