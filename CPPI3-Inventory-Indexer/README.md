# Inventory Indexer

Use vectors, maps, sets, and sorting to build searchable inventory views. This
project also introduces small relation-style operations inspired by CS236:
select rows, project columns, rename a category, and join inventory rows to a
supplier table.

## Tasks

1. Add items while rejecting duplicate IDs.
2. Implement `selectCategory` to return only rows in a requested category.
3. Implement `projectNames` to return sorted item names from a selected view.
4. Implement `joinSuppliers` to combine item rows with a supplier lookup table.
5. Add or run at least two custom checks before comparing with the solution.

## Build

From the repository root:

```bash
cmake -S . -B build
cmake --build build
```

Each project also contains a standalone `starter/main.cpp` and `solution/main.cpp` file that can be compiled directly with a C++17 compiler.
