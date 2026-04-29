#include <algorithm>
#include <iostream>
#include <map>
#include <string>
#include <vector>

namespace {
struct CheckResult {
    std::string label;
    bool passed;
};

void printResults(const std::vector<CheckResult>& results) {
    for (const auto& result : results) {
        std::cout << result.label << ": " << (result.passed ? "pass" : "review") << '\n';
    }
}
}

int main() {
    std::cout << "Build and Debug Checkpoint reference solution\n";

    std::map<std::string, int> evidence {
        {"input cases", 2},
        {"validation checks", 2},
        {"design notes", 1},
    };

    std::vector<CheckResult> results;
    for (const auto& [label, count] : evidence) {
        results.push_back({label, count > 0});
    }

    std::sort(results.begin(), results.end(), [](const auto& left, const auto& right) {
        return left.label < right.label;
    });

    printResults(results);
    return 0;
}
