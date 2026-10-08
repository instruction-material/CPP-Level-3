# Worked template diagnostic record

The ordinary source builds and prints `number 3` and `text apple`. Enabling the
learner's Score call fails during template instantiation: `chooseSmaller<Score>`
evaluates `right < left` but Score has no applicable comparison. Trace the error
at that expression to the enabled call; exact GCC/Clang wording is toolchain
specific. Read the real retained diagnostic from the acceptance run.

The solution adds only a friend `<` comparison borrowing two const Scores and
comparing their integer values. `chooseSmaller` and the existing driver are
unchanged. Its enabled actual result is `score 59`; changed pairs `(0,100)`,
`(91,76)` and `(84,84)` produce `score 0`, `score 76` and `score 84`. Ordinary output
is unchanged. The native gate verifies these bytes against independently chosen
values and distinguishes an actual failed compilation from a runtime failure.

The correction makes this exercise's numeric ordering meaningful. A real type
with multiple ordering interpretations might instead use an explicit comparator.
Equal numeric Scores cannot expose which otherwise identical object was chosen;
the tagged-value lesson shows that the helper keeps the left value on a tie.
Compare a learner record's source, build command, diagnostics and changed output
with this worked reasoning. A fixed checklist alone is not evidence.
