CXX ?= c++
CPPFLAGS ?=
CXXFLAGS ?= -std=c++20 -Wall -Wextra -Wpedantic -Wconversion -Wsign-conversion -Werror
LDFLAGS ?=
SOURCES = main.cpp maze.cpp maze_search.cpp

.PHONY: all clean
all: maze-search
maze-search: $(SOURCES) maze.h
	$(CXX) $(CPPFLAGS) $(CXXFLAGS) $(SOURCES) $(LDFLAGS) -o $@
maze-search-debug: $(SOURCES) maze.h
	$(CXX) $(CPPFLAGS) $(CXXFLAGS) -O0 -g -fsanitize=address,undefined -fno-omit-frame-pointer $(SOURCES) $(LDFLAGS) -o $@
clean:
	rm -f maze-search maze-search-debug
