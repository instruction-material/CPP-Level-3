#include <charconv>
#include <cstddef>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <stdexcept>
#include <string>
#include <system_error>
#include <vector>

namespace filecourse {
namespace fs = std::filesystem;
inline constexpr std::size_t maxLineBytes = 128;
inline constexpr std::size_t maxFileBytes = 16384;
inline constexpr std::size_t maxRecords = 100;

struct Record {
    std::string name;
    int score = 0;
};

struct Summary {
    std::size_t count = 0;
    int total = 0;
};

bool validName(const std::string& name) {
    if (name.empty() || name.size() > 40) return false;
    bool nonSpace = false;
    for (const char byte : name) {
        const auto value = static_cast<unsigned char>(byte);
        if (value < 32 || value > 126) return false;
        if (value != 32) nonSpace = true;
    }
    return nonSpace;
}

bool readBoundedLine(std::istream& input, std::string& line,
                     std::size_t& fileBytes) {
    line.clear();
    char byte = 0;
    while (input.get(byte)) {
        if (fileBytes >= maxFileBytes)
            throw std::runtime_error("Input exceeds 16384 bytes.");
        ++fileBytes;
        if (byte == '\n') return true;
        if (line.size() == maxLineBytes)
            throw std::runtime_error("Physical line exceeds 128 bytes.");
        line.push_back(byte);
    }
    if (input.bad() || (!input.eof() && input.fail()))
        throw std::runtime_error("Input read failed.");
    return !line.empty();
}

void stripLineEnding(std::string& line) {
    if (!line.empty() && line.back() == '\r') line.pop_back();
}

// Task 1: validate a complete record before accepting either field.
Record parseScoreRow(const std::string& line) {
    const auto separator = line.find('\t');
    if (separator == std::string::npos ||
        line.find('\t', separator + 1) != std::string::npos)
        throw std::runtime_error("Expected exactly two tab-separated fields.");
    const std::string name = line.substr(0, separator);
    const std::string token = line.substr(separator + 1);
    if (!validName(name)) throw std::runtime_error("Invalid record name.");
    if (token.empty()) throw std::runtime_error("Score is empty.");
    for (const char digit : token)
        if (digit < '0' || digit > '9')
            throw std::runtime_error("Score needs only ASCII decimal digits.");
    int score = 0;
    const auto result = std::from_chars(token.data(), token.data() + token.size(), score);
    if (result.ec != std::errc{} || result.ptr != token.data() + token.size() || score > 100)
        throw std::runtime_error("Score must be from 0 through 100.");
    return {name, score};
}

// Task 2: only return a complete, bounded and validated set of rows.
std::vector<Record> readScores(const fs::path& inputPath) {
    std::ifstream input(inputPath, std::ios::binary);
    if (!input.is_open()) throw std::runtime_error("Unable to open input.");
    std::size_t bytes = 0;
    std::string line;
    if (!readBoundedLine(input, line, bytes))
        throw std::runtime_error("Input header is missing.");
    stripLineEnding(line);
    if (line != "CPPI4_SCORES_V1")
        throw std::runtime_error("Input header must be CPPI4_SCORES_V1.");
    std::vector<Record> records;
    records.reserve(maxRecords);
    std::size_t physicalLine = 1;
    while (readBoundedLine(input, line, bytes)) {
        ++physicalLine;
        stripLineEnding(line);
        if (records.size() == maxRecords)
            throw std::runtime_error("Input exceeds 100 records.");
        try {
            records.push_back(parseScoreRow(line));
        } catch (const std::exception& error) {
            throw std::runtime_error("Line " + std::to_string(physicalLine) + ": " + error.what());
        }
    }
    // EOF is expected. Preserve real read errors above before clearing it.
    input.clear();
    input.close();
    if (input.fail()) throw std::runtime_error("Input close failed.");
    return records;
}

// Task 3: validate the in-memory contract before emitting the report.
Summary writeReport(std::ostream& output, const std::vector<Record>& records) {
    if (records.size() > maxRecords) throw std::runtime_error("Too many report rows.");
    Summary summary{records.size(), 0};
    for (const auto& record : records) {
        if (!validName(record.name) || record.score < 0 || record.score > 100)
            throw std::runtime_error("Report record violates its invariant.");
        summary.total += record.score;
    }
    output << "CPPI4_REPORT_V1\n";
    for (const auto& record : records)
        output << record.name << '\t' << record.score << '\t'
               << (record.score >= 60 ? "pass" : "review") << '\n';
    output << "TOTAL\t" << summary.count << '\t' << summary.total << '\n';
    if (!output) throw std::runtime_error("Report write failed.");
    return summary;
}

class StagingDirectory {
public:
    explicit StagingDirectory(const fs::path& output)
        : directory_(stagePath(output)), temporary_(directory_ / "report.tmp") {
        // Prepare both path objects before acquiring the directory.
        std::error_code error;
        if (!fs::create_directory(directory_, error))
            throw std::runtime_error("Cannot acquire output staging directory.");
    }
    StagingDirectory(const StagingDirectory&) = delete;
    StagingDirectory& operator=(const StagingDirectory&) = delete;
    ~StagingDirectory() noexcept {
        std::error_code ignored;
        fs::remove(temporary_, ignored);
        ignored.clear();
        fs::remove(directory_, ignored);
    }
    const fs::path& temporaryFile() const noexcept { return temporary_; }
private:
    static fs::path stagePath(fs::path output) {
        output += ".stage";
        return output;
    }
    fs::path directory_;
    fs::path temporary_;
};

void validatePaths(const fs::path& input, const fs::path& output) {
    if (input.empty() || output.empty() || output.filename().empty())
        throw std::runtime_error("Input and output need file paths.");
    std::error_code error;
    if (!fs::is_regular_file(input, error) || error)
        throw std::runtime_error("Input must be an accessible regular file.");
    error.clear();
    const auto outputStatus = fs::symlink_status(output, error);
    if (error && outputStatus.type() != fs::file_type::not_found)
        throw std::runtime_error("Cannot inspect output path.");
    if (outputStatus.type() != fs::file_type::not_found) {
        if (!fs::is_regular_file(outputStatus))
            throw std::runtime_error("Existing output must be a regular file, not a symlink.");
        error.clear();
        const bool same = fs::equivalent(input, output, error);
        if (error || same)
            throw std::runtime_error("Input and output must be different files.");
    }
}

// Task 4: acquire, check and release resources around one commit point.
Summary processFile(const fs::path& inputPath, const fs::path& outputPath) {
    validatePaths(inputPath, outputPath);
    const auto records = readScores(inputPath);
    StagingDirectory staging(outputPath);
    const auto& temporary = staging.temporaryFile();
    std::ofstream output(temporary, std::ios::binary | std::ios::trunc);
    if (!output.is_open()) throw std::runtime_error("Unable to open staged output.");
    const auto summary = writeReport(output, records);
    output.flush();
    if (!output) throw std::runtime_error("Output flush failed.");
    output.close();
    if (output.fail()) throw std::runtime_error("Output close failed.");
    std::error_code error;
    fs::rename(temporary, outputPath, error);
    if (error) throw std::runtime_error("Output publication failed.");
    return summary;
}
} // namespace filecourse

int main(const int argc, char* argv[]) {
    if (argc != 1 && argc != 3) {
        std::cerr << "Usage: project [INPUT OUTPUT]\n";
        return 2;
    }
    try {
        const auto summary = filecourse::processFile(
            argc == 3 ? argv[1] : "scores.tsv", argc == 3 ? argv[2] : "report.tsv");
        std::cout << "Published " << summary.count << " records; total "
                  << summary.total << ".\n";
        std::cout.flush();
        if (!std::cout) {
            std::cerr << "Report committed; success message could not be written.\n";
            return 1;
        }
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "Processing stopped: " << error.what() << '\n';
        return 1;
    }
}
