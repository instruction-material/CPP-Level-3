#include "score_tools.h"

#include <algorithm>
#include <charconv>
#include <ostream>
#include <system_error>

bool parseScore(std::string_view token, int& score) {
    if (token.empty() || !std::all_of(token.begin(), token.end(), [](char c) {
            return c >= '0' && c <= '9';
        })) {
        return false;
    }
    int candidate = 0;
    const auto result = std::from_chars(token.data(), token.data() + token.size(), candidate);
    if (result.ec != std::errc{} || result.ptr != token.data() + token.size()
        || candidate < MIN_SCORE || candidate > MAX_SCORE) {
        return false;
    }
    score = candidate;
    return true;
}

int sumScores(const std::vector<int>& scores, std::ostream* trace) {
    int total = 0;
    for (std::size_t index = 0; index < scores.size(); ++index) {
        total += scores[index];
        if (trace != nullptr) {
            *trace << "trace index=" << index << " score=" << scores[index]
                   << " running=" << total << '\n';
        }
    }
    return total;
}
