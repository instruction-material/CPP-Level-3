# Inventory Indexer

Store inventory rows in a `vector`, map each unique ID to its sequence position,
and track categories in a `set`. Build selected rows, sorted name projections,
category renames and supplier joins without introducing custom data structures.

## Data and behavior

An `Item` has `int id`, `string name`, `string category` and `int quantity`.
The supplied demonstration uses positive IDs and nonnegative quantities. This
container exercise accepts the field values as provided; input parsing and
business-rule validation are separate concerns. IDs must be unique.

- Adding a new ID returns `true`; a duplicate returns `false` and preserves the
  original row and categories. Rows retain insertion order.
- Selecting a category returns copies of exactly the matching rows in insertion
  order. An absent category produces an empty vector.
- Projecting names returns a new vector sorted by the strings' ordinary
  case-sensitive lexicographic order. Duplicate names remain; the input rows
  and original inventory do not change.
- Renaming a category replaces every matching category and rebuilds the category
  set. It returns `true` when the source category occurs, including when both
  names are equal, and `false` when it is absent. Renaming into an existing
  category combines the category entries without changing IDs or row order.
- Joining suppliers includes only items whose ID exists in the supplied
  `map<int, string>`. Produce `id | name | quantity | supplier` display strings
  in inventory insertion order. Missing suppliers are skipped. These display
  strings are a view, not a persistence format.
- Category printing starts with `Categories:`, then one leading space per
  category in set order, then a newline. An empty index prints `Categories:` and
  a newline.

The starter's camel-case methods correspond to the reference's existing
underscore method names: `selectCategory` / `select_category`, `projectNames` /
`project_names`, `renameCategory` / `rename_category`, `joinSuppliers` /
`join_suppliers`, and `printCategories` / `print_categories`. Original filenames,
method names and demonstration entry points are retained.

## Work sequence

1. Predict the selected rows and projected names from the three starter items.
2. Complete the selection and projection TODOs. Verify an absent category, a
   duplicate name and a one-row view before using the reference.
3. Complete the supplier join TODO. Verify a missing supplier and confirm that
   supplier-map order does not replace inventory insertion order.
4. Complete the category rename TODO. Check a missing category, a rename into an
   existing category and an unchanged-name request. Explain why rebuilding the
   category set matters.
5. Explain the supplied safe insertion. If an allocation fails after a vector
   append, the new category and appended row are rolled back before the exception
   propagates. Existing IDs and rows remain usable. The reference's rename builds
   replacement rows and categories before swapping them into the index, so a
   failed copy or rebuild also preserves the previous state.
6. Record predicted and actual results for at least two additional cases. Keep
   the attempted explanation before comparing with the staff reference.

The starter remains incomplete: empty placeholder query results and a `false`
rename are not evidence of completion. The reference demonstration is a working
example; its exit status alone does not grade another source file.

## Build and verification

Compile a downloaded pack in its own folder; the existing CMake targets also
retain C++17 compatibility. The course IDE's C++20 workflow is supported:

```sh
c++ -std=c++20 -Wall -Wextra -Wpedantic -Werror main.cpp -o inventory
./inventory
```

The untouched starter prints categories `electronics tools`, followed by an
empty `Tool names:` line and no supplier rows. A completed attempt using its
three items should print `Tool names: debug cable hex driver` and three joined
rows, ordered by IDs 101, 102, 103 as inserted. The reference additionally has
item 104, rejects duplicate 101 and renames `electronics` to `lab`.

From the repository root, build the existing targets separately:

```sh
cmake -S . -B build
cmake --build build --target inventory_indexer_starter inventory_indexer_solution
python3 verify-inventory.py
```

The independent verifier runs both original demonstrations, checks the actual
reference views and mutation boundaries, reproduces the starter's unfinished
results, and injects allocation failures across both supplied insertion paths
and the reference rename. Ordinary and address/undefined sanitizer builds must
preserve existing state, allow retry and report no sanitizer diagnostics.
