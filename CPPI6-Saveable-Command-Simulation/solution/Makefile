CXX ?= c++
CXXFLAGS ?= -std=c++20 -Wall -Wextra -Wpedantic -Wconversion -Wsign-conversion -Werror -g -O0
SOURCES = main.cpp rover.cpp command.cpp storage.cpp
HEADERS = rover.h command.h
.PHONY: all clean
all: main
main: $(SOURCES) $(HEADERS)
	$(CXX) $(CXXFLAGS) $(SOURCES) -o $@
clean:
	rm -f main
