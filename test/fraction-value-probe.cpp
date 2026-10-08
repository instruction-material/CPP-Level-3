#define main fractionCourseDriver
#include "CPPI5_VALUE_SOURCE"
#undef main
#include <limits>
#include <type_traits>
#include <utility>

using valuecourse::Fraction;
static_assert(std::is_copy_constructible_v<Fraction>);
static_assert(std::is_copy_assignable_v<Fraction>);
static_assert(std::is_same_v<decltype(std::declval<const Fraction&>().add(
    std::declval<const Fraction&>())), Fraction>);
static_assert(std::is_same_v<decltype(std::declval<const Fraction&>().multiply(
    std::declval<const Fraction&>())), Fraction>);

void require(bool value) {
    if (!value) throw std::runtime_error("Value invariant probe failed.");
}
std::string render(const Fraction& value) {
    std::ostringstream output;
    output << value;
    return output.str();
}
struct Tagged {
    int value;
    const char* label;
    friend bool operator<(const Tagged& left, const Tagged& right) {
        return left.value < right.value;
    }
};

int main() {
    const Fraction original(2, 4);
    Fraction copy = original;
    copy = copy.add(Fraction(1, 2));
    require(render(original) == "1/2" && render(copy) == "1/1");
    require(Fraction(-1, -2) == original);
    require(render(Fraction(0, -9)) == "0/1");
    require(valuecourse::chooseSmaller(Tagged{3, "left"}, Tagged{3, "right"}).label ==
            std::string_view("left"));
    require(valuecourse::chooseSmaller(7, 3) == 3);
    require(valuecourse::chooseSmaller(std::string("pear"), std::string("apple")) == "apple");
    const Fraction wideLeft(999999, 1000000);
    const Fraction wideRight(1, 1000000);
    require(wideLeft.add(wideRight) == Fraction(1));
    require(Fraction(1000000, 999999).multiply(Fraction(999999, 1000000)) == Fraction(1));
    const Fraction limit(1000000);
    const Fraction one(1);
    bool rejected = false;
    try { (void)limit.add(one); } catch (const std::out_of_range&) { rejected = true; }
    require(rejected && render(limit) == "1000000/1" && render(one) == "1/1");
    rejected = false;
    try { (void)limit.multiply(Fraction(2)); }
    catch (const std::out_of_range&) { rejected = true; }
    require(rejected && render(limit) == "1000000/1");
    for (const auto minimum : {std::numeric_limits<std::int64_t>::min(),
                               std::numeric_limits<std::int64_t>::max()}) {
        rejected = false;
        try { (void)Fraction(minimum, 1); }
        catch (const std::out_of_range&) { rejected = true; }
        require(rejected);
        rejected = false;
        try { (void)Fraction(1, minimum); }
        catch (const std::out_of_range&) { rejected = true; }
        require(rejected);
    }
    const std::vector<Fraction> values{Fraction(-2), Fraction(-1, 2), Fraction(-2, 4),
                                      Fraction(), Fraction(0, -4), Fraction(1, 3),
                                      Fraction(2, 6), Fraction(1, 2), Fraction(2)};
    for (const auto& a : values) {
        require(!(a < a));
        for (const auto& b : values) {
            if (a < b) require(!(b < a));
            require((a == b) == (!(a < b) && !(b < a)));
            for (const auto& c : values) {
                if (a < b && b < c) require(a < c);
                if (!(a < b) && !(b < a) && !(b < c) && !(c < b))
                    require(!(a < c) && !(c < a));
            }
        }
    }
    auto sorted = values;
    std::sort(sorted.begin(), sorted.end());
    const std::vector<std::string> expected{"-2/1", "-1/2", "-1/2", "0/1", "0/1",
                                             "1/3", "1/3", "1/2", "2/1"};
    for (std::size_t index = 0; index < sorted.size(); ++index)
        require(render(sorted[index]) == expected[index]);
    std::cout << "Copy, const, order and failure invariants verified.\n";
}
