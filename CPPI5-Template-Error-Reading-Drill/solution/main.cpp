#include <iostream>
#include <string>

struct Score {
    int value;
    friend bool operator<(const Score& left, const Score& right) {
        return left.value < right.value;
    }
};

template <typename T>
T chooseSmaller(T left, T right) {
    return right < left ? right : left;
}

int main(int argc, char*[]) {
    if (argc != 1) {
        std::cerr << "Usage: main\n";
        return 2;
    }
#ifdef CPPI5_TRIGGER_TEMPLATE_ERROR
    const auto smaller = chooseSmaller(Score{84}, Score{59});
    std::cout << "score " << smaller.value << '\n';
#else
    std::cout << "number " << chooseSmaller(7, 3) << '\n';
    std::cout << "text " << chooseSmaller(std::string("pear"), std::string("apple"))
              << '\n';
#endif
    std::cout.flush();
    if (!std::cout) {
        std::cerr << "Could not write the result.\n";
        return 1;
    }
    return 0;
}
