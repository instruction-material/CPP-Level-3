# Container Tradeoff Audit: staff worked example

Use this after the learner has recorded predictions and actual observations.
The example describes the supplied Inventory Indexer reference. Check a saved
attempt's own source and probe; neither a notes printer nor a checklist of
invented evidence counts assesses it.

## What the current containers do

`vector<Item>` owns the rows in insertion order. `map<int, size_t>` is a unique
ID-to-position index used by add to reject duplicate IDs and record accepted
positions. `set<string>` provides sorted unique category output. A category
query still loops over the vector. The supplier map is a separate argument;
the join loops over inventory rows and finds each ID in that map.

Selection copies matching Item values in inventory order. Projection copies
their names and sorts the new vector; it does not remove duplicate names.
Joining skips missing suppliers and emits display strings in inventory order.
Rename copies the stored rows, changes matches in the copy, rebuilds categories
and swaps only after that work succeeds. Copies returned before rename retain
their earlier values. An unchanged-name rename returns true when the source
category occurs; an absent source returns false.

## Case A: Different orders and a merging rename

Add IDs 7, 2 and 9 with the worksheet's fields in that order. Each add returns
true. The replacement request for ID 7 returns false. It introduces no ghost
category and changes no original row.

The tools selection contains these copies in insertion order:

```text
7 | beta | tools | 2
2 | alpha | tools | 0
```

Their projected names are alpha, then beta. The supplier map has key order 2,
then 7, but the joined result is:

```text
7 | beta | 2 | First
2 | alpha | 0 | Second
```

ID 9 has no supplied supplier and is skipped. The initial category line is
`Categories: lab tools`. Rename tools to lab returns true. The new category line
is `Categories: lab`, the tools view is empty and the lab view contains:

```text
7 | beta | lab | 2
2 | alpha | lab | 0
9 | alpha | lab | 3
```

The earlier tools selection still contains category tools. It is a copied view,
not a live reference to the rows. Zero quantity is accepted by this container
exercise. Additional business validation would be a separately specified change.

### Verified probe transcript

```text
Case A
Adds: true true true
Duplicate: false
Categories: lab tools
Selected:
7 | beta | tools | 2
2 | alpha | tools | 0
Names: alpha beta
Suppliers:
7 | beta | 2 | First
2 | alpha | 0 | Second
Rename tools to lab: true
Categories: lab
Old view:
7 | beta | tools | 2
2 | alpha | tools | 0
Tools after:
Lab after:
7 | beta | lab | 2
2 | alpha | lab | 0
9 | alpha | lab | 3
```

## Case B: Empty inventory

Selection, projected names and joined strings are empty vectors. The supplier
entry with ID 8 contributes no output because there is no matching inventory
row. Rename missing to new returns false. The category output is exactly
`Categories:` followed by a newline. These are ordinary valid empty results.

### Verified probe transcript

```text
Case B
Adds:
Categories:
Selected:
Names:
Suppliers:
Rename missing to new: false
Categories:
```

## Case C: Duplicate names and an unchanged-name request

The lab view retains both rows, in order 5 then 3. Projection produces two
copies of same, because this is a sorted vector projection, not a set projection.
Joining the one supplied supplier produces:

```text
5 | same | 1 | Known
```

Rename lab to lab returns true and leaves `Categories: lab`. Rename missing to
ghost returns false with the same category output. Editing the selected copy's
first name affects that local copy. A fresh lab selection again yields the
original two same names and original quantities. A test that compares only row
counts would miss this copy boundary.

### Verified probe transcript

```text
Case C
Adds: true true
Selected:
5 | same | lab | 1
3 | same | lab | 0
Names: same same
Suppliers:
5 | same | 1 | Known
Rename lab to lab: true
Categories: lab
Rename missing to ghost: false
Categories: lab
Edited copy:
5 | copy-only | lab | 1
3 | same | lab | 0
Fresh query:
5 | same | lab | 1
3 | same | lab | 0
```

## Bound the work before proposing a change

Let N be inventory rows, C distinct categories, K selected rows and M suppliers.
The following are source-based bounds, treating a comparison, hash or field
copy as unit work. Variable string lengths, allocations and emitted output add
their own costs. None of these bounds is a timing measurement.

| Operation | Current source work | Design consequence |
| --- | --- | --- |
| Accepted add | Logarithmic ID lookup and insertion, logarithmic category insertion, amortized vector append | A vector growth event can still move or copy N rows. Duplicate rejection performs only the ID lookup. |
| Select category | Visits all N rows and copies K matches | Changing the private ID map cannot remove this scan. |
| Project names | Copies K names and sorts them in O(K log K) comparisons | Sorting a copied view preserves stored insertion order; duplicate names remain. |
| Rename | Copies N rows, visits them, then inserts N category values into a replacement set | The rebuild is at most O(N log(N + 1)) comparisons plus copies, rather than a constant-time map edit. Even an absent category is checked after the initial copy in this implementation. |
| Join suppliers | Visits N rows and performs a logarithmic supplier lookup for each | Use O(N log(M + 1)) lookup/traversal work plus string construction; result order follows inventory traversal. |
| Print categories | Visits C category strings in sorted order | Replacing the set with an unordered set would require separate ordering work to preserve this output. |

The primary verifier already checks real allocation failures in accepted add and
reference rename. A proposed container rewrite must preserve rollback rather
than assuming that a successful small probe demonstrates exception safety.

## One defensible decision

For this small teaching project, retaining vector rows plus the current map and
set is reasonable. It expresses insertion order, unique IDs and sorted unique
categories directly. There is no measured evidence that its runtime is a problem.
The unused stored ID positions are an explicit extension point; current queries
do not use them to access a row.

An unordered ID map is a bounded alternative if average lookup cost is the
specific requirement. Its lookup has an average constant bound and a linear
worst case in the number of entries. That does not establish a faster program:
hashing, allocation, input size and collision behavior matter. Keep inventory
traversal for output order and keep the public supplier map contract. The change
does not improve the category query or supplier lookups, which use other paths.

Vector relocation invalidates pointers, references and iterators into its
elements. The stored numeric positions still identify the same logical rows
after the project's append-only insertion, including capacity growth. A future
erase or reorder would make some positions stale unless the index is rebuilt.
Erasing a vector element invalidates references and iterators at or after it.
An unordered container rehash has different validity rules; do not assume its
iterators can be retained across every mutation.

A category index could accelerate selection when category queries dominate,
but adds maintenance to accepted insertion and category rename. It must also
preserve insertion order and handle partial allocation failure. That additional
design has not been implemented in the supplied project and is not evidence
that merely replacing the ID map achieves the same improvement.

## Review prompts

Ask the learner to connect each observed output to its actual traversal or
lookup. Keep an incorrect original prediction and the subsequent explanation.
Check that duplicate IDs and duplicate names are distinguished, a join's map
order is not mistaken for row order, and a copied result is not called a live
view. Accept a justified decision to keep the original design.

For a prototype, compare the same three cases and two learner-created cases
before and after the change. Require source identity, commands, actual outputs,
statuses and a stated limitation. If timing evidence is absent, the conclusion
must remain a complexity argument or hypothesis. A successful optional notes
printer has no bearing on the saved inventory implementation.

Library guarantees are supported by the standard working draft's
[vector overview](https://eel.is/c++draft/vector.overview),
[vector invalidation rules](https://eel.is/c++draft/vector.modifiers),
[associative requirements](https://eel.is/c++draft/associative.reqmts) and
[unordered requirements](https://eel.is/c++draft/unord.req).
These living draft pages include newer APIs; this example uses only C++17/20
facilities already present in the pack.
