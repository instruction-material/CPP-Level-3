#include <iostream>
#include <string>
#include <vector>

int main() {
    std::cout << "Build and Debug Checkpoint starter\n";
    std::vector<std::string> notes {"read the prompt", "fill the TODOs"};

    // TODO: Replace this placeholder with the project-specific implementation.
    for (const auto& note : notes) {
        std::cout << "- " << note << '\n';
    }

    return 0;
}
