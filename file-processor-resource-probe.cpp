// Unvalidated native probe draft; include only the reviewed pack implementation.
#define main fileProcessorProgramMain
#include "program-under-test.cpp"
#undef main
#include <limits>
#include <sstream>
#include <streambuf>
#include <type_traits>

namespace {
void require(bool value, const char* message) {
    if (!value) throw std::logic_error(message);
}
template<class Action>
std::string failure(Action action) {
    try { action(); }
    catch (const std::runtime_error& error) { return error.what(); }
    throw std::logic_error("Expected an observed resource failure.");
}
class ReadFailureBuffer final : public std::streambuf {
    std::string bytes_ = "abcdef";
    std::size_t index_ = 0;
    int_type underflow() override {
        if (index_ == 3) throw std::runtime_error("Injected read fault");
        return index_ < bytes_.size() ? traits_type::to_int_type(bytes_[index_])
                                     : traits_type::eof();
    }
    int_type uflow() override {
        const auto byte = underflow();
        if (!traits_type::eq_int_type(byte, traits_type::eof())) ++index_;
        return byte;
    }
};
class WriteFailureBuffer final : public std::streambuf {
    std::size_t remaining_ = 12;
public:
    std::string accepted;
private:
    int_type overflow(int_type byte) override {
        if (traits_type::eq_int_type(byte, traits_type::eof()))
            return traits_type::not_eof(byte);
        if (remaining_ == 0) return traits_type::eof();
        accepted.push_back(traits_type::to_char_type(byte));
        --remaining_;
        return byte;
    }
    std::streamsize xsputn(const char* data, std::streamsize count) override {
        std::streamsize written = 0;
        while (written < count &&
               !traits_type::eq_int_type(overflow(traits_type::to_int_type(data[written])),
                                        traits_type::eof())) ++written;
        return written;
    }
};
} // namespace

int main(int argc, char* argv[]) {
    using namespace filecourse;
    static_assert(!std::is_copy_constructible_v<StagingDirectory>);
    static_assert(!std::is_copy_assignable_v<StagingDirectory>);
    static_assert(!std::is_move_constructible_v<StagingDirectory>);
    static_assert(std::is_nothrow_destructible_v<StagingDirectory>);
    require(argc == 2, "Provide a private probe directory.");
    const fs::path root(argv[1]);
    require(fs::is_directory(root), "Probe directory must exist.");
    std::string line;
    std::size_t bytes = 0;
    ReadFailureBuffer failingBuffer;
    std::istream broken(&failingBuffer);
    require(failure([&] { readBoundedLine(broken, line, bytes); }) == "Input read failed.",
            "Observe the real stream failure.");
    require(bytes == 3 && line == "abc" && broken.bad(), "Keep consumed-byte evidence.");
    std::string exact;
    for (std::size_t i = 0; i < maxFileBytes / 2; ++i) exact += "x\n";
    std::istringstream bounded(exact);
    bytes = 0;
    std::size_t rows = 0;
    while (readBoundedLine(bounded, line, bytes)) {
        require(line == "x", "Reader changes accepted bytes.");
        ++rows;
    }
    require(bytes == maxFileBytes && rows == maxFileBytes / 2, "Exact byte bound is accepted.");
    std::istringstream tooLarge(exact + "y");
    bytes = 0;
    require(failure([&] { while (readBoundedLine(tooLarge, line, bytes)) {} }) ==
            "Input exceeds 16384 bytes.", "Reject a real additional input byte.");
    require(bytes == maxFileBytes, "Do not increment past the byte limit.");
    std::istringstream exhausted("z");
    bytes = std::numeric_limits<std::size_t>::max();
    require(failure([&] { readBoundedLine(exhausted, line, bytes); }) ==
            "Input exceeds 16384 bytes.", "Reject a saturated counter.");
    require(bytes == std::numeric_limits<std::size_t>::max(), "Counter must not wrap.");
    std::istringstream exactLine(std::string(maxLineBytes, 'x') + "\n");
    bytes = 0;
    require(readBoundedLine(exactLine, line, bytes) && line.size() == maxLineBytes,
            "Exact physical line length is accepted.");
    std::istringstream longLine(std::string(maxLineBytes + 1, 'x') + "\n");
    bytes = 0;
    require(failure([&] { readBoundedLine(longLine, line, bytes); }) ==
            "Physical line exceeds 128 bytes.", "Reject excess line storage.");
    require(line.size() == maxLineBytes, "Never store an unbounded line.");
    const auto parsed = parseScoreRow(" keep spaces \t00060");
    require(parsed.name == " keep spaces " && parsed.score == 60, "Preserve accepted fields.");
    std::ostringstream untouched;
    const std::vector<Record> invalid{{"Valid", 70}, {"Invalid", 101}};
    require(failure([&] { writeReport(untouched, invalid); }) ==
            "Report record violates its invariant.", "Validate all rows before rendering.");
    require(untouched.str().empty() && invalid[0].score == 70 && invalid[1].score == 101,
            "Validation emits nothing and leaves source values unchanged.");
    const std::vector<Record> valid{{"Ada", 84}, {"Lin", 59}};
    WriteFailureBuffer failedWrite;
    std::ostream failingOutput(&failedWrite);
    require(failure([&] { writeReport(failingOutput, valid); }) == "Report write failed.",
            "Observe a real partial stream write.");
    require(failedWrite.accepted == "CPPI4_REPORT" && valid[0].score == 84 &&
            valid[1].name == "Lin", "Capture partial bytes without mutating input.");
    const auto normal = root / "normal.tsv";
    const auto normalStage = root / "normal.tsv.stage";
    {
        StagingDirectory owner(normal);
        const auto* observer = &owner.temporaryFile();
        require(observer == &owner.temporaryFile() &&
                *observer == normalStage / "report.tmp", "Observer borrows the owner's path.");
        std::ofstream file(*observer);
        file << "owned temporary";
        file.close();
        require(fs::exists(*observer), "Owner holds acquired resources.");
    }
    require(!fs::exists(normalStage), "Normal return cleans owned resources.");
    const auto unwindStage = root / "unwind.tsv.stage";
    require(failure([&] {
        StagingDirectory owner(root / "unwind.tsv");
        std::ofstream file(owner.temporaryFile());
        file << "temporary";
        file.close();
        throw std::runtime_error("After acquisition");
    }) == "After acquisition", "Preserve the primary failure.");
    require(!fs::exists(unwindStage), "Unwinding cleans owned resources.");
    const auto foreignStage = root / "foreign.tsv.stage";
    {
        StagingDirectory owner(root / "foreign.tsv");
        std::ofstream foreign(foreignStage / "foreign.txt");
        foreign << "leave foreign contents";
    }
    require(fs::is_regular_file(foreignStage / "foreign.txt"),
            "Cleanup must not recursively erase unexpected files.");
    require(failure([&] { StagingDirectory collision(root / "foreign.tsv"); }) ==
            "Cannot acquire output staging directory.", "Failed acquisition owns nothing.");
    require(fs::is_regular_file(foreignStage / "foreign.txt"), "Preserve staging collisions.");
    fs::remove(foreignStage / "foreign.txt");
    fs::remove(foreignStage);
    std::cout << "Observed bounded reads, partial output, borrowed paths, ownership and unwinding.\n";
}
