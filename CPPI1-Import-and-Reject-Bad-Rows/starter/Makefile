CXX ?= c++
CXXFLAGS ?= -std=c++20 -Wall -Wextra -Wpedantic -Werror
SOURCES = main.cpp task_manager.cpp command_parser.cpp task_storage.cpp task_import.cpp
HEADERS = task_manager.h command_parser.h task_storage.h task_import.h

.PHONY: all clean
all: task-import
task-import: $(SOURCES) $(HEADERS)
	$(CXX) $(CPPFLAGS) $(CXXFLAGS) $(SOURCES) $(LDFLAGS) $(LDLIBS) -o $@
task-import-debug: $(SOURCES) $(HEADERS)
	$(CXX) $(CPPFLAGS) $(CXXFLAGS) -g -O0 $(SOURCES) $(LDFLAGS) $(LDLIBS) -o $@
clean:
	rm -f task-import task-import-debug
