#include "state_review.h"
#include <iostream>
#include <stdexcept>
#include <string>
namespace {
enum class LineStatus { Line, End, TooLong, Failed };
LineStatus boundedLine(std::istream& input, std::string& line) {
    line.clear(); bool tooLong = false; char c = 0;
    while (input.get(c)) {
        if (c == '\n') return tooLong ? LineStatus::TooLong : LineStatus::Line;
        if (line.size() < 24) line.push_back(c); else tooLong = true;
    }
    if (input.bad()) return LineStatus::Failed;
    if (tooLong) return LineStatus::TooLong;
    return line.empty() ? LineStatus::End : LineStatus::Line;
}
} // namespace
int main(int argc, char*[]) {
    using namespace statecourse;
    if (argc != 1) { std::cerr << "Usage: state-review\n"; return 2; }
    try {
        {
            Phase simple = Phase::Ready;
            Machine polymorphic;
            std::string line;
            while (true) {
                const auto status = boundedLine(std::cin, line);
                if (status == LineStatus::End) break;
                if (status == LineStatus::Failed) throw std::runtime_error("Could not read events.");
                if (status == LineStatus::TooLong) { std::cerr << "Rejected: command exceeds 24 bytes.\n"; continue; }
                if (line.empty()) continue;
                if (line == "quit") break;
                if (line == "show") {
                    std::cout << "enum " << phaseName(simple) << " poly " << phaseName(polymorphic.phase()) << '\n';
                    continue;
                }
                Event event{};
                if (!parseEvent(line, event)) { std::cerr << "Rejected: unknown event.\n"; continue; }
                const auto expected = enumNext(simple, event);
                const bool accepted = polymorphic.apply(event);
                if (expected.has_value() != accepted) throw std::logic_error("Transition results differ.");
                if (expected) simple = *expected;
                if (simple != polymorphic.phase()) throw std::logic_error("Resulting phases differ.");
                std::cout << line << (accepted ? " accepted" : " rejected") << " enum "
                          << phaseName(simple) << " poly " << phaseName(polymorphic.phase()) << '\n';
                std::cout.flush();
                if (!std::cout) throw std::runtime_error("Could not write transition result.");
            }
            if (std::cin.bad()) throw std::runtime_error("Could not read events.");
        }
        std::cout << "lifetime balanced " << std::boolalpha << (Lifetime::created == Lifetime::destroyed) << '\n';
        std::cout.flush(); std::cerr.flush();
        if (!std::cout || !std::cerr) throw std::runtime_error("Could not write result.");
        return Lifetime::created == Lifetime::destroyed ? 0 : 1;
    } catch (const std::exception& failure) {
        std::cerr << "Failed: " << failure.what() << '\n'; return 1;
    }
}
