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

void vectorDemo() {
    const std::vector<int> scores{84, 91, 76, 88};
    std::cout << "Vector: ";
    for (const int score : scores) std::cout << score << " ";
    std::cout << "\nVector responsibility: the vector cleans up its own storage.\n";
}

void uniquePointerDemo() {
    const std::size_t size = 4;
    std::unique_ptr<int[]> scores(new int[size]{84, 91, 76, 88});
    printScores("unique_ptr array", scores.get(), size);
    std::cout << "unique_ptr responsibility: ownership is still explicit, but cleanup is automatic.\n";
}

int main(const int argc, char*[]) {
    if (argc != 1) { std::cerr << "Usage: main\n"; return 2; }
    try {
        manualArrayDemo(); std::cout << '\n';
        vectorDemo(); std::cout << '\n';
        uniquePointerDemo();
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "Ownership comparison stopped: " << error.what() << '\n';
        return 1;
    }
}
