# Mini Command Scanner

Build a small scanner for command-driven programs. This project adapts the
scanner/token-stream idea from the CS236 Datalog assignments without turning
C++ Level 3 into a compiler course.

## Goals

Students should be able to:

- Convert raw command text into typed tokens.
- Track line numbers for useful error messages.
- Recognize words, numbers, quoted strings, punctuation, comments, and unknown
  characters.
- Keep scanning and validation separate from the code that mutates application
  state.

## Starter Expectations

The starter already scans words and symbols. Complete the TODOs so it also
handles:

- Whole-number tokens.
- Quoted string tokens.
- `#` comments that run to the end of the line.
- Unknown tokens that preserve the source line.

## Build

From the repository root:

```bash
cmake -S . -B build
cmake --build build
```

Run:

```bash
./build/command_scanner_starter
./build/command_scanner_solution
```
