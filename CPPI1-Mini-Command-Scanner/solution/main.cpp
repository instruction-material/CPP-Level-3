#include <cctype>
#include <iostream>
#include <string>
#include <utility>
#include <vector>

/*****************
*   CONSTANTS   *
*****************/

constexpr char SPACE_CHARACTER = ' ';
constexpr char TAB_CHARACTER = '\t';
constexpr char CARRIAGE_RETURN_CHARACTER = '\r';
constexpr char NEWLINE_CHARACTER = '\n';
constexpr char COMMENT_CHARACTER = '#';
constexpr char STRING_DELIMITER = '"';
constexpr char UNDERSCORE_CHARACTER = '_';
constexpr char END_OF_INPUT_CHARACTER = '\0';
constexpr int INITIAL_LINE_NUMBER = 1;
const std::string WORD_TOKEN_NAME = "WORD";
const std::string NUMBER_TOKEN_NAME = "NUMBER";
const std::string STRING_TOKEN_NAME = "STRING";
const std::string SYMBOL_TOKEN_NAME = "SYMBOL";
const std::string END_TOKEN_NAME = "END";
const std::string UNKNOWN_TOKEN_NAME = "UNKNOWN";
const std::string SAMPLE_SOURCE = "ADD task \"write parser\" PRIORITY 2\n"
                                  "DONE task\n"
                                  "# comment ignored by the scanner\n"
                                  "QUERY task?\n"
                                  "BAD @\n";

/*************
*   TYPES   *
*************/

// Define the token categories produced by the scanner
enum class TokenType { Word, Number, StringLiteral, Symbol, End, Unknown };

// Store one scanned token
struct Token {
    TokenType type;
    std::string lexeme;
    int line;
};

/*****************
*   FUNCTIONS   *
*****************/

/**
 * @brief Return the display name for a token type
 *
 * @param type Token type to name
 *
 * @return Display name for the token type
 */
std::string token_type_name(TokenType type) {
    // Convert each known token type into the expected label
    switch (type) {
    case TokenType::Word:
        return WORD_TOKEN_NAME;
    case TokenType::Number:
        return NUMBER_TOKEN_NAME;
    case TokenType::StringLiteral:
        return STRING_TOKEN_NAME;
    case TokenType::Symbol:
        return SYMBOL_TOKEN_NAME;
    case TokenType::End:
        return END_TOKEN_NAME;
    case TokenType::Unknown:
    default:
        return UNKNOWN_TOKEN_NAME;
    }
}

// Scan a command language source string into tokens
class Scanner {
  public:
    /**
	 * @brief Build a scanner for one source string
	 *
	 * @param source Source text to scan
	 */
    explicit Scanner(std::string source) : source_(std::move(source)) {
    }

    /**
	 * @brief Scan the source into tokens
	 *
	 * @return Tokens found in the source
	 */
    std::vector<Token> scan() {
        std::vector<Token> tokens;

        // Continue scanning until every character has been consumed
        while (!is_at_end()) {
            const char current = advance();

            // Ignore horizontal whitespace
            if (current == SPACE_CHARACTER || current == TAB_CHARACTER ||
                current == CARRIAGE_RETURN_CHARACTER) {
                continue;
            }

            // Track line numbers for diagnostics
            if (current == NEWLINE_CHARACTER) {
                ++line_;
                continue;
            }

            // Skip comments that run to the end of the line
            if (current == COMMENT_CHARACTER) {
                skip_comment();
                continue;
            }

            // Scan identifiers and keywords
            if (std::isalpha(static_cast<unsigned char>(current))) {
                tokens.push_back(scan_word(current));
                continue;
            }

            // Scan integer literals
            if (std::isdigit(static_cast<unsigned char>(current))) {
                tokens.push_back(scan_number(current));
                continue;
            }

            // Scan quoted strings
            if (current == STRING_DELIMITER) {
                tokens.push_back(scan_string_literal());
                continue;
            }

            // Scan single-character symbols
            if (is_symbol(current)) {
                tokens.push_back(
                    {TokenType::Symbol, std::string(1, current), line_});
                continue;
            }

            tokens.push_back(
                {TokenType::Unknown, std::string(1, current), line_});
        }

        tokens.push_back({TokenType::End, "", line_});
        return tokens;
    }

  private:
    // Check whether the scanner has consumed the whole source
    bool is_at_end() const {
        return position_ >= source_.size();
    }

    // Consume and return the current character
    char advance() {
        return source_[position_++];
    }

    // Inspect the current character without consuming it
    char peek() const {
        // Return a sentinel when the scanner is at the end
        if (is_at_end()) {
            return END_OF_INPUT_CHARACTER;
        }

        return source_[position_];
    }

    // Skip characters until the end of the current comment line
    void skip_comment() {
        // Consume comment text until newline or end of input
        while (!is_at_end() && peek() != NEWLINE_CHARACTER) {
            advance();
        }
    }

    // Scan an identifier-like word token
    Token scan_word(char first) {
        std::string lexeme(1, first);

        // Keep consuming alphanumeric and underscore characters
        while (!is_at_end() &&
               (std::isalnum(static_cast<unsigned char>(peek())) ||
                peek() == UNDERSCORE_CHARACTER)) {
            lexeme += advance();
        }

        return {TokenType::Word, lexeme, line_};
    }

    // Scan an integer token
    Token scan_number(char first) {
        std::string lexeme(1, first);

        // Keep consuming decimal digits
        while (!is_at_end() &&
               std::isdigit(static_cast<unsigned char>(peek()))) {
            lexeme += advance();
        }

        return {TokenType::Number, lexeme, line_};
    }

    // Scan a string token without the surrounding quotes
    Token scan_string_literal() {
        const int start_line = line_;
        std::string lexeme;

        // Consume string contents until the closing delimiter or end of input
        while (!is_at_end() && peek() != STRING_DELIMITER) {
            const char current = advance();

            // Keep line numbers accurate for multi-line strings
            if (current == NEWLINE_CHARACTER) {
                ++line_;
            }

            lexeme += current;
        }

        // Report unterminated strings as unknown tokens
        if (is_at_end()) {
            return {TokenType::Unknown, lexeme, start_line};
        }

        advance();
        return {TokenType::StringLiteral, lexeme, start_line};
    }

    // Check whether a character is a single-character symbol
    static bool is_symbol(char current) {
        return current == '(' || current == ')' || current == ',' ||
               current == ':' || current == '?';
    }

    std::string source_;
    std::size_t position_ = 0;
    int line_ = INITIAL_LINE_NUMBER;
};

/**
 * @brief Scan and print tokens from the sample source
 *
 * @return Process exit code
 */
int main() {
    Scanner scanner(SAMPLE_SOURCE);

    // Print each token with line number, type, and lexeme
    for (const Token& token : scanner.scan()) {
        std::cout << token.line << " " << token_type_name(token.type) << " "
                  << token.lexeme << "\n";
    }
}
