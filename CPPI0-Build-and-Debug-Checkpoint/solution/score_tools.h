#ifndef SCORE_TOOLS_H
#define SCORE_TOOLS_H

#include <cstddef>
#include <iosfwd>
#include <string_view>
#include <vector>

inline constexpr int MIN_SCORE = 0;
inline constexpr int MAX_SCORE = 100;
inline constexpr std::size_t MAX_SCORES = 20;

// A failed parse leaves score unchanged. Only ASCII decimal digits are accepted.
bool parseScore(std::string_view token, int& score);

// Precondition: at most MAX_SCORES values, each between MIN_SCORE and MAX_SCORE.
// The sum is at most 2000. Trace output observes the calculation, not its state.
int sumScores(const std::vector<int>& scores, std::ostream* trace = nullptr);

#endif
