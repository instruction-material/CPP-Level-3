#include <algorithm>
#include <iostream>
#include <map>
#include <string>
#include <vector>


/*****************
*   CONSTANTS   *
*****************/

const std::string PASS_LABEL = "pass";
const std::string REVIEW_LABEL = "review";
const std::string INPUT_CASES_LABEL = "input cases";
const std::string VALIDATION_CHECKS_LABEL = "validation checks";
const std::string DESIGN_NOTES_LABEL = "design notes";
constexpr int INPUT_CASE_COUNT = 2;
constexpr int VALIDATION_CHECK_COUNT = 2;
constexpr int DESIGN_NOTE_COUNT = 1;
constexpr int MINIMUM_PASSING_EVIDENCE = 0;


/*************
*   TYPES   *
*************/

namespace {
// Store one checklist outcome for the reference solution
struct CheckResult {
	std::string label;
	bool passed;
};


/*****************
*   FUNCTIONS   *
*****************/

// Print checklist outcomes in display order
void print_results(const std::vector<CheckResult>& results) {
	// Print one status line for each checklist result
	for (const auto& result : results) {
		std::cout << result.label << ": " << (result.passed ? PASS_LABEL : REVIEW_LABEL) << '\n';
	}
}

// Build the evidence counts used by this reference checklist
std::map<std::string, int> build_evidence() {
	return {
		{INPUT_CASES_LABEL, INPUT_CASE_COUNT},
		{VALIDATION_CHECKS_LABEL, VALIDATION_CHECK_COUNT},
		{DESIGN_NOTES_LABEL, DESIGN_NOTE_COUNT},
	};
}

// Convert evidence counts into checklist results
std::vector<CheckResult> build_results(const std::map<std::string, int>& evidence) {
	std::vector<CheckResult> results;

	// Treat every positive evidence count as passing
	for (const auto& [label, count] : evidence) {
		results.push_back({label, count > MINIMUM_PASSING_EVIDENCE});
	}

	return results;
}

// Sort checklist results alphabetically by label
bool compare_results_by_label(const CheckResult& left, const CheckResult& right) {
	return left.label < right.label;
}
}

/**
 * @brief Print the Container Tradeoff Audit reference checklist
 *
 * @return Process exit code
 */
int main() {
	std::cout << "Container Tradeoff Audit reference solution\n";

	const auto evidence = build_evidence();
	auto results = build_results(evidence);

	// Keep output order stable for review
	std::sort(results.begin(), results.end(), compare_results_by_label);

	print_results(results);
	return 0;
}
