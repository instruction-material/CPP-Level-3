#include <cstddef>
#include <iostream>
#include <memory>
#include <string>
#include <vector>

void printScores(const std::string& label, const int scores[], const std::size_t size) {
    std::cout << label << ": ";
    for (std::size_t i = 0; i < size; ++i) std::cout << scores[i] << " ";
    std::cout << '\n';
}

void manualArrayDemo() {
    const std::size_t size = 4;
    int* scores = new int[size]{84, 91, 76, 88};
    try {
        printScores("Manual array", scores, size);
        std::cout << "Manual responsibility: delete[] must run exactly once.\n";
    } catch (...) {
        delete[] scores;
        throw;
    }
    delete[] scores;
    scores = nullptr;
}

int main() {
    try {
        manualArrayDemo();
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "Ownership comparison stopped: " << error.what() << '\n';
        return 1;
    }
}
