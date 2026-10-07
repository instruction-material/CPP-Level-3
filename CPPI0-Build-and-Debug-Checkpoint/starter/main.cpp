#include "score_ledger.h"
#include "score_tools.h"

#include <iostream>
#include <stdexcept>
#include <string_view>
#include <vector>

namespace {
void printUsage(std::ostream& out) {
    out << "Usage: checkpoint [--trace] [--scores [SCORE ...]]\n"
        << "       checkpoint --check\n"
        << "       checkpoint --help\n"
        << "Scores are ASCII decimal integers from 0 to 100; at most 20.\n";
}

int checkExamples() {
    struct Example {
        const char* name;
        std::vector<int> scores;
        int expected;
    };
    const std::vector<Example> examples {
        {"empty", {}, 0},
        {"single", {85}, 85},
        {"mixed", {40, 60, 80}, 180},
        {"zero-prefix", {0, 60}, 60},
        {"zero-suffix", {60, 0}, 60},
        {"boundaries", {0, 100}, 100},
        {"capacity", std::vector<int>(MAX_SCORES, MAX_SCORE), 2000},
    };
    bool passed = true;
    for (const auto& example : examples) {
        ScoreLedger ledger;
        for (int score : example.scores) ledger.add(score);
        const int actual = ledger.total();
        const bool matches = actual == example.expected;
        passed = passed && matches;
        std::cout << example.name << ": expected=" << example.expected
                  << " actual=" << actual << ' ' << (matches ? "PASS" : "FAIL") << '\n';
    }
    return passed ? 0 : 1;
}
} // namespace

int main(int argc, char* argv[]) {
    try {
        if (argc == 2 && std::string_view(argv[1]) == "--help") {
            printUsage(std::cout);
            return std::cout ? 0 : 1;
        }
        if (argc == 2 && std::string_view(argv[1]) == "--check") {
            const int result = checkExamples();
            return std::cout ? result : 1;
        }
        int position = 1;
        bool trace = false;
        if (position < argc && std::string_view(argv[position]) == "--trace") {
            trace = true;
            ++position;
        }
        std::vector<int> inputs;
        if (position == argc) {
            inputs = {40, 60, 80};
        } else {
            if (std::string_view(argv[position]) != "--scores") {
                printUsage(std::cerr);
                return 2;
            }
            ++position;
            for (; position < argc; ++position) {
                int score = 0;
                if (!parseScore(argv[position], score)) {
                    throw std::invalid_argument("score must be a decimal integer from 0 to 100");
                }
                if (inputs.size() == MAX_SCORES) {
                    throw std::length_error("at most 20 scores are allowed");
                }
                inputs.push_back(score);
            }
        }
        ScoreLedger ledger;
        for (int score : inputs) ledger.add(score);
        std::cout << "Scores:";
        for (int score : ledger.scores()) std::cout << ' ' << score;
        std::cout << '\n';
        const int total = ledger.total(trace ? &std::cout : nullptr);
        std::cout << "Total: " << total << '\n';
        return std::cout ? 0 : 1;
    } catch (const std::invalid_argument& error) {
        std::cerr << "error: " << error.what() << '\n';
        return 2;
    } catch (const std::length_error& error) {
        std::cerr << "error: " << error.what() << '\n';
        return 2;
    } catch (const std::exception& error) {
        std::cerr << "failure: " << error.what() << '\n';
        return 1;
    }
}
