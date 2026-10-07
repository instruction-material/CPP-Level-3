#include "command_parser.h"
#include "task_manager.h"
#include "task_storage.h"
#include <filesystem>
#include <iostream>
#include <string>

namespace {
constexpr const char* usage = "Usage: task-manager [--file PATH]\n       task-manager --help\n";
void help() {
    std::cout << usage
        << "Commands: add \"text\", done ID, list [all|open|done], save, reload, help, quit\n"
        << "Save explicitly before quit or end-of-input; neither saves automatically.\n";
}
}

int main(int argc, char* argv[]) {
    using namespace taskcourse;
    std::filesystem::path path = "tasks.tsv";
    if (argc == 2 && std::string(argv[1]) == "--help") {
        help();
        return 0;
    }
    if (argc == 3 && std::string(argv[1]) == "--file" && argv[2][0] != '\0') {
        path = argv[2];
    } else if (argc != 1) {
        std::cerr << usage;
        return 2;
    }
    TaskLedger ledger;
    std::string error;
    if (!loadTasks(path, ledger, error, true)) {
        std::cerr << "Error: " << error << '\n';
        return 1;
    }
    std::cout << "Loaded " << ledger.size() << '\n';
    std::string line;
    while (std::getline(std::cin, line)) {
        if (trimCommandWhitespace(line).empty()) continue;
        Command command;
        if (!parseCommand(line, command, error)) {
            std::cerr << "Error: " << error << '\n';
            continue;
        }
        if (command.verb == Verb::Quit) {
            std::cout << "Bye.\n";
            break;
        }
        bool success = true;
        switch (command.verb) {
        case Verb::Add: {
            int id = 0;
            success = ledger.add(command.text, id, error);
            if (success) std::cout << "Added " << id << '\n';
            break;
        }
        case Verb::Done:
            success = ledger.complete(command.id, error);
            if (success) std::cout << "Completed " << command.id << '\n';
            break;
        case Verb::List: {
            const auto rows = ledger.select(command.filter);
            std::cout << "Tasks " << rows.size() << '\n';
            for (const Task& task : rows)
                std::cout << task.id << " [" << (task.done ? "done" : "open") << "] " << task.text << '\n';
            break;
        }
        case Verb::Save:
            success = saveTasks(path, ledger, error);
            if (success) std::cout << "Saved " << ledger.size() << '\n';
            break;
        case Verb::Reload:
            success = loadTasks(path, ledger, error);
            if (success) std::cout << "Loaded " << ledger.size() << '\n';
            break;
        case Verb::Help:
            help();
            break;
        case Verb::Quit:
            break;
        }
        if (!success) std::cerr << "Error: " << error << '\n';
    }
    if (std::cin.bad()) {
        std::cerr << "Error: Cannot read commands.\n";
        return 1;
    }
    return 0;
}
