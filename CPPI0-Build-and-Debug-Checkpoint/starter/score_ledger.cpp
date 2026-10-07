#include "score_ledger.h"
#include "score_tools.h"

#include <stdexcept>

void ScoreLedger::add(int score) {
    if (score < MIN_SCORE || score > MAX_SCORE) {
        throw std::invalid_argument("score must be from 0 to 100");
    }
    if (scores_.size() == MAX_SCORES) {
        throw std::length_error("at most 20 scores are allowed");
    }
    scores_.push_back(score);
}

const std::vector<int>& ScoreLedger::scores() const noexcept {
    return scores_;
}

int ScoreLedger::total(std::ostream* trace) const {
    return sumScores(scores_, trace);
}
