#define main publishedOwnershipMain
#include "ownership-reference.cpp"
#undef main
#include <algorithm>
#include <cassert>
#include <ios>
#include <streambuf>

class PartialBuffer final : public std::streambuf {
public:
    std::string bytes;
protected:
    std::streamsize xsputn(const char* data, const std::streamsize count) override {
        const auto remaining = static_cast<std::streamsize>(7 - bytes.size());
        const auto accepted = std::min(remaining, count);
        bytes.append(data, static_cast<std::size_t>(accepted));
        return accepted;
    }
    int_type overflow(const int_type byte) override {
        if (traits_type::eq_int_type(byte, traits_type::eof()))
            return traits_type::not_eof(byte);
        if (bytes.size() == 7) return traits_type::eof();
        bytes.push_back(traits_type::to_char_type(byte));
        return byte;
    }
};

class OutputScope final {
    std::streambuf* originalBuffer;
    std::ios::iostate originalExceptions;
public:
    explicit OutputScope(PartialBuffer& buffer)
        : originalBuffer(std::cout.rdbuf()),
          originalExceptions(std::cout.exceptions()) {
        std::cout.rdbuf(&buffer);
        std::cout.exceptions(std::ios::badbit | std::ios::failbit);
    }
    OutputScope(const OutputScope&) = delete;
    OutputScope& operator=(const OutputScope&) = delete;
    ~OutputScope() noexcept {
        std::cout.exceptions(std::ios::goodbit);
        std::cout.rdbuf(originalBuffer);
        std::cout.exceptions(originalExceptions);
    }
};

void checkActualThrow(void (*demonstration)(), const std::string& prefix) {
    PartialBuffer buffer;
    bool caught = false;
    try {
        OutputScope output(buffer);
        demonstration();
    } catch (const std::ios_base::failure&) {
        caught = true;
    }
    assert(caught);
    assert(buffer.bytes == prefix);
}

int main() {
    checkActualThrow(manualArrayDemo, "Manual ");
    checkActualThrow(vectorDemo, "Vector:");
    checkActualThrow(uniquePointerDemo, "unique_");
    std::cout << "Three real partial-output exceptions observed.\n";
}
