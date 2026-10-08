CXX ?= c++
CXXFLAGS ?= -std=c++20 -Wall -Wextra -Wpedantic -Wconversion -Wsign-conversion -Werror -g -O0
.PHONY: all clean
all: main
main: main.cpp state_review.cpp state_review.h
	$(CXX) $(CXXFLAGS) main.cpp state_review.cpp -o $@
clean:
	rm -f main
