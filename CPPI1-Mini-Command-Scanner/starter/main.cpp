#include <cctype>
#include <iostream>
#include <string>
#include <vector>

enum class TokenType {
	Word,
	Number,
	StringLiteral,
	Symbol,
	End,
	Unknown
};

struct Token {
	TokenType type;
	std::string lexeme;
	int line;
};

std::string tokenTypeName(TokenType type) {
	switch (type) {
	case TokenType::Word:
		return "WORD";
	case TokenType::Number:
		return "NUMBER";
	case TokenType::StringLiteral:
		return "STRING";
	case TokenType::Symbol:
		return "SYMBOL";
	case TokenType::End:
		return "END";
	case TokenType::Unknown:
		return "UNKNOWN";
	}

	return "UNKNOWN";
}

class Scanner {
public:
	explicit Scanner(std::string source)
		: source_(source) {}

	std::vector<Token> scan() {
		std::vector<Token> tokens;

		while (!isAtEnd()) {
			const char current = advance();
			if (current == ' ' || current == '\t' || current == '\r') {
				continue;
			}
			if (current == '\n') {
				++line_;
				continue;
			}
			if (std::isalpha(static_cast<unsigned char>(current))) {
				tokens.push_back(scanWord(current));
				continue;
			}
			if (isSymbol(current)) {
				tokens.push_back({ TokenType::Symbol, std::string(1, current), line_ });
				continue;
			}

			// TODO: handle numbers, quoted strings, comments, and unknown tokens.
			tokens.push_back({ TokenType::Unknown, std::string(1, current), line_ });
		}

		tokens.push_back({ TokenType::End, "", line_ });
		return tokens;
	}

private:
	bool isAtEnd() const {
		return position_ >= source_.size();
	}

	char advance() {
		return source_[position_++];
	}

	char peek() const {
		if (isAtEnd()) {
			return '\0';
		}
		return source_[position_];
	}

	Token scanWord(char first) {
		std::string lexeme(1, first);
		while (!isAtEnd() && (std::isalnum(static_cast<unsigned char>(peek())) || peek() == '_')) {
			lexeme += advance();
		}
		return { TokenType::Word, lexeme, line_ };
	}

	static bool isSymbol(char current) {
		return current == '(' || current == ')' || current == ',' || current == ':' || current == '?';
	}

	std::string source_;
	std::size_t position_ = 0;
	int line_ = 1;
};

int main() {
	const std::string source =
		"ADD task \"write parser\" PRIORITY 2\n"
		"DONE task\n"
		"# comment ignored by the finished scanner\n"
		"QUERY task?\n";

	Scanner scanner(source);
	for (const Token& token : scanner.scan()) {
		std::cout << token.line << " " << tokenTypeName(token.type) << " " << token.lexeme << "\n";
	}
}
