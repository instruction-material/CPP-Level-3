CXX ?= c++
CXXFLAGS ?= -std=c++20 -Wall -Wextra -Wpedantic -Werror
SOURCES = main.cpp task_manager.cpp command_parser.cpp task_storage.cpp
HEADERS = task_manager.h command_parser.h task_storage.h

.PHONY: all clean
all: task-manager
task-manager: $(SOURCES) $(HEADERS)
	$(CXX) $(CPPFLAGS) $(CXXFLAGS) $(SOURCES) $(LDFLAGS) $(LDLIBS) -o $@
task-manager-debug: $(SOURCES) $(HEADERS)
	$(CXX) $(CPPFLAGS) $(CXXFLAGS) -g -O0 $(SOURCES) $(LDFLAGS) $(LDLIBS) -o $@
clean:
	rm -f task-manager task-manager-debug
