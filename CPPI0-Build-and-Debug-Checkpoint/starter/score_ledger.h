#ifndef SCORE_LEDGER_H
#define SCORE_LEDGER_H

#include <iosfwd>
#include <vector>

class ScoreLedger {
public:
    // Reject an out-of-range value or a full ledger before changing its scores.
    void add(int score);
    const std::vector<int>& scores() const noexcept;
    int total(std::ostream* trace = nullptr) const;

private:
    std::vector<int> scores_;
};

#endif
