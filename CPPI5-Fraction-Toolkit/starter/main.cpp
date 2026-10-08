#include <algorithm>
#include <cstdint>
#include <iostream>
#include <numeric>
#include <sstream>
#include <stdexcept>
#include <string_view>
#include <vector>

namespace valuecourse {
inline constexpr std::int64_t maxComponent = 1000000;
inline constexpr std::int64_t maxIntermediate = 2000000000000;

class Fraction {
    struct Normalized {
        std::int64_t numerator;
        std::int64_t denominator;
    };

    static Normalized normalize(std::int64_t numerator, std::int64_t denominator) {
        if (numerator < -maxIntermediate || numerator > maxIntermediate ||
            denominator < -maxIntermediate || denominator > maxIntermediate)
            throw std::out_of_range("Intermediate component exceeds the bound.");
        if (denominator == 0)
            throw std::invalid_argument("A denominator cannot be zero.");
        if (denominator < 0) {
            numerator = -numerator;
            denominator = -denominator;
        }
        const auto divisor = std::gcd(numerator, denominator);
        numerator /= divisor;
        denominator /= divisor;
        if (numerator < -maxComponent || numerator > maxComponent ||
            denominator > maxComponent)
            throw std::out_of_range("Result exceeds the component bound.");
        return {numerator, denominator};
    }

    explicit Fraction(Normalized value)
        : numerator_(value.numerator), denominator_(value.denominator) {}
    std::int64_t numerator_ = 0;
    std::int64_t denominator_ = 1;

public:
    explicit Fraction(std::int64_t numerator = 0, std::int64_t denominator = 1) {
        // TODO BEGIN constructFraction
        (void)numerator;
        (void)denominator;
        throw std::logic_error("Unfinished task: constructFraction.");
        // TODO END constructFraction
    }

    bool lessThan(const Fraction& right) const {
        // TODO BEGIN compareFraction
        (void)right;
        throw std::logic_error("Unfinished task: compareFraction.");
        // TODO END compareFraction
    }

    Fraction add(const Fraction& right) const {
        // TODO BEGIN addFraction
        (void)right;
        throw std::logic_error("Unfinished task: addFraction.");
        // TODO END addFraction
    }

    Fraction multiply(const Fraction& right) const {
        // TODO BEGIN multiplyFraction
        (void)right;
        throw std::logic_error("Unfinished task: multiplyFraction.");
        // TODO END multiplyFraction
    }

    friend bool operator==(const Fraction& left, const Fraction& right) {
        return left.numerator_ == right.numerator_ &&
               left.denominator_ == right.denominator_;
    }
    friend bool operator<(const Fraction& left, const Fraction& right) {
        return left.lessThan(right);
    }
    friend Fraction operator+(const Fraction& left, const Fraction& right) {
        return left.add(right);
    }
    friend Fraction operator*(const Fraction& left, const Fraction& right) {
        return left.multiply(right);
    }
    friend std::ostream& operator<<(std::ostream& output, const Fraction& value) {
        return output << value.numerator_ << '/' << value.denominator_;
    }
};

template <typename T>
T chooseSmaller(T left, T right) {
    // TODO BEGIN chooseSmaller
    (void)left;
    (void)right;
    throw std::logic_error("Unfinished task: chooseSmaller.");
    // TODO END chooseSmaller
}

std::int64_t parseComponent(std::string_view text) {
    const bool negative = !text.empty() && text.front() == '-';
    if (negative) text.remove_prefix(1);
    if (text.empty()) throw std::invalid_argument("A component requires digits.");
    std::int64_t magnitude = 0;
    for (const char character : text) {
        if (character < '0' || character > '9')
            throw std::invalid_argument("A component requires signed decimal digits.");
        const auto digit = static_cast<std::int64_t>(character - '0');
        if (magnitude > (maxComponent - digit) / 10)
            throw std::out_of_range("Input component exceeds the bound.");
        magnitude = magnitude * 10 + digit;
    }
    return negative ? -magnitude : magnitude;
}

Fraction parseFraction(std::string_view text) {
    const auto slash = text.find('/');
    if (slash == std::string_view::npos || text.find('/', slash + 1) !=
                                           std::string_view::npos)
        throw std::invalid_argument("A fraction requires numerator/denominator.");
    const auto numerator = parseComponent(text.substr(0, slash));
    const auto denominator = parseComponent(text.substr(slash + 1));
    return Fraction(numerator, denominator);
}
} // namespace valuecourse

int main(int argc, char* argv[]) {
    if (argc != 1 && argc != 3) {
        std::cerr << "Usage: main [LEFT_FRACTION RIGHT_FRACTION]\n";
        return 2;
    }
    try {
        using valuecourse::Fraction;
        const Fraction left = valuecourse::parseFraction(argc == 1 ? "1/2" : argv[1]);
        const Fraction right = valuecourse::parseFraction(argc == 1 ? "2/3" : argv[2]);
        const Fraction sum = left + right;
        const Fraction product = left * right;
        const Fraction smaller = valuecourse::chooseSmaller(left, right);
        std::vector<Fraction> sorted{right, Fraction(), left};
        std::sort(sorted.begin(), sorted.end());
        std::ostringstream output;
        output << "LEFT " << left << "\nRIGHT " << right
               << "\nLESS " << std::boolalpha << (left < right)
               << "\nSUM " << sum << "\nPRODUCT " << product
               << "\nSMALLER " << smaller << "\nSORTED";
        for (const auto& value : sorted) output << ' ' << value;
        output << '\n';
        if (!output) throw std::runtime_error("Could not render the result.");
        std::cout << output.str() << std::flush;
        if (!std::cout) throw std::runtime_error("Could not write the result.");
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "Rejected: " << error.what() << '\n';
        return 1;
    }
}
