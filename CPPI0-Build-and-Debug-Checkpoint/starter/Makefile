CXX ?= c++
CXXFLAGS ?= -std=c++20 -Wall -Wextra -Wpedantic -Werror
SOURCES = main.cpp score_ledger.cpp score_tools.cpp
HEADERS = score_ledger.h score_tools.h

.PHONY: all check clean
all: checkpoint
checkpoint: $(SOURCES) $(HEADERS)
	$(CXX) $(CPPFLAGS) $(CXXFLAGS) $(SOURCES) $(LDFLAGS) $(LDLIBS) -o $@
checkpoint-debug: $(SOURCES) $(HEADERS)
	$(CXX) $(CPPFLAGS) $(CXXFLAGS) -g -O0 $(SOURCES) $(LDFLAGS) $(LDLIBS) -o $@
check: checkpoint
	./checkpoint --check
clean:
	rm -f checkpoint checkpoint-debug
