CXX ?= c++
CXXFLAGS := -std=c++20 -Wall -Wextra -Wpedantic -Wconversion -Wsign-conversion -Werror -g

SANITIZER_FLAGS := -fsanitize=address,undefined -fno-sanitize-recover=all -fno-omit-frame-pointer
ifeq ($(shell uname -s),Linux)
SANITIZER_FLAGS += -fno-pie -no-pie
endif

.PHONY: clean
main: main.cpp
	$(CXX) $(CXXFLAGS) -O0 main.cpp -o main
main-debug: main.cpp
	$(CXX) $(CXXFLAGS) -O0 $(SANITIZER_FLAGS) main.cpp -o main-debug
clean:
	rm -f main main-debug
	rm -rf main.dSYM main-debug.dSYM
