# Mini Command Scanner

Scan command text into tokens and label each token with its source line, starting at 1. A scanner reports what the text contains. A later parser decides whether those tokens form a valid command.

## Open and run the project

Open the starter in the site IDE, confirm the import and export the project ZIP. Extract it and open a terminal in the folder containing main.cpp. The site IDE edits and saves the project. Compilation uses an installed C++20 compiler.

```sh
c++ -std=c++20 -Wall -Wextra -Wpedantic -Werror main.cpp -o scanner
./scanner
```

The untouched starter builds and prints a trace. Before editing, find where its output splits the quoted text and prints words from the comment. The instructor reference produces the complete trace.

## Token rules

| Input | Token rule |
| --- | --- |
| Letter followed by letters, digits or underscores | One WORD |
| Consecutive decimal digits | One NUMBER containing the digit text |
| Text between two double quotes | One STRING without either quote |
| An opening quote with no closing quote | One UNKNOWN for its contents, labeled with the opening line |
| Each of `(`, `)`, `,`, `:`, `?` | One SYMBOL |
| `#` outside a quoted string | Skip through the end of the line, leaving the newline for line counting |
| Space, tab or carriage return outside a quoted string | Skip |
| Line feed outside or inside quotes | Advance the line counter |
| Any other character | One UNKNOWN on its source line |
| End of source | Exactly one END on the current line |

The exercise uses ASCII words and digits. A string may span lines. Its token carries the line of its opening quote. Backslash is literal text inside quotes, and quote escapes are outside this exercise.

## Build in steps

1. Make the starter collect a full number token. Use a separate test containing `12 3`.
2. Skip comments without consuming the line feed. Predict the next token's line after a comment.
3. Collect quoted text and report an unclosed quote. Compare empty quotes, `"task #1"` and an unclosed quote. Verify the line of a token following a closed, two-line string.
4. Check the sample trace. `write parser` is one STRING on line 1, `2` is a NUMBER on line 1, `?` is a SYMBOL on line 4, `@` is UNKNOWN on line 5, and END is on line 6.

To test an edge case, replace the source string in main, rebuild and compare token type, text and line. Save the original sample so it can be rerun. In a guided session, pause before advancing past a delimiter or line feed and predict the next cursor position.

Submit the source and traces for the supplied sample, empty input, a comment followed by a word and an unclosed quote. Explain why a syntactically valid WORD still needs the parser's command checks.

## Repository build

From the full repository checkout, select the two distinct CMake targets.

```sh
cmake -S . -B build
cmake --build build --target command_scanner_starter command_scanner_solution
```

From the repository root, `python3 verify-mini-command-scanner.py` checks the supplied programs and their scanner cases.
