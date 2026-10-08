#include "command.h"
#include <iostream>
#include <stdexcept>
#include <string>
namespace {
enum class LineStatus { Line, End, TooLong, Failed };
LineStatus boundedLine(std::istream& input, std::string& line) {
    line.clear();
    bool tooLong = false;
    char c = 0;
    while (input.get(c)) {
        if (c == '\n') return tooLong ? LineStatus::TooLong : LineStatus::Line;
        if (line.size() < rovercourse::maxCommandBytes) line.push_back(c);
        else tooLong = true;
    }
    if (input.bad()) return LineStatus::Failed;
    if (tooLong) return LineStatus::TooLong;
    return line.empty() ? LineStatus::End : LineStatus::Line;
}
} // namespace
int main(int argc, char*[]) {
    using namespace rovercourse;
    if (argc != 1) { std::cerr << "Usage: rover\n"; return 2; }
    try {
        Rover rover;
        std::string line;
        while (true) {
            const auto status = boundedLine(std::cin, line);
            if (status == LineStatus::End) break;
            if (status == LineStatus::Failed) throw std::runtime_error("Could not read commands.");
            if (status == LineStatus::TooLong) { std::cerr << "Rejected: command exceeds 1024 bytes.\n"; continue; }
            if (line.find_first_not_of(" \t") == std::string::npos) continue;
            Parsed parsed;
            std::string error;
            if (!parseCommand(line, parsed, error)) { std::cerr << "Rejected: " << error << '\n'; continue; }
            if (parsed.verb == Verb::Quit) break;
            try {
                auto command = makeCommand(parsed);
                Rover candidate = rover;
                const Result result = command->execute(candidate);
                if (result.ok) rover.swap(candidate);
                if (result.ok) std::cout << result.message;
                else std::cerr << "Rejected: " << result.message << '\n';
            } catch (const std::exception& failure) {
                std::cerr << "Rejected: " << failure.what() << '\n';
            }
            std::cout.flush(); std::cerr.flush();
            if (!std::cout || !std::cerr) throw std::runtime_error("Could not write command result.");
        }
        std::cout.flush(); std::cerr.flush();
        if (!std::cout || !std::cerr) throw std::runtime_error("Could not write command result.");
        return 0;
    } catch (const std::exception& failure) {
        std::cerr << "Failed: " << failure.what() << '\n'; return 1;
    }
}
