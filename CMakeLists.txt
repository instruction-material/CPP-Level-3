cmake_minimum_required(VERSION 3.20)
project(CPPLevel3 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

function(add_course_executable target source)
    add_executable(${target} ${source} ${ARGN})
    target_compile_options(${target} PRIVATE
        $<$<CXX_COMPILER_ID:Clang,AppleClang,GNU>:-Wall -Wextra -Wpedantic>
        $<$<CXX_COMPILER_ID:MSVC>:/W4>
    )
endfunction()

add_course_executable(build_debug_starter
    CPPI0-Build-and-Debug-Checkpoint/starter/main.cpp
    CPPI0-Build-and-Debug-Checkpoint/starter/score_ledger.cpp
    CPPI0-Build-and-Debug-Checkpoint/starter/score_tools.cpp)
add_course_executable(build_debug_solution
    CPPI0-Build-and-Debug-Checkpoint/solution/main.cpp
    CPPI0-Build-and-Debug-Checkpoint/solution/score_ledger.cpp
    CPPI0-Build-and-Debug-Checkpoint/solution/score_tools.cpp)
add_course_executable(warnings_notebook_starter CPPI0-Warnings-and-Debugger-Notebook/starter/main.cpp)
add_course_executable(warnings_notebook_solution CPPI0-Warnings-and-Debugger-Notebook/solution/main.cpp)
add_course_executable(task_manager_starter
    CPPI1-Saveable-Task-Manager/starter/main.cpp
    CPPI1-Saveable-Task-Manager/starter/task_manager.cpp
    CPPI1-Saveable-Task-Manager/starter/command_parser.cpp
    CPPI1-Saveable-Task-Manager/starter/task_storage.cpp)
add_course_executable(task_manager_solution
    CPPI1-Saveable-Task-Manager/solution/main.cpp
    CPPI1-Saveable-Task-Manager/solution/task_manager.cpp
    CPPI1-Saveable-Task-Manager/solution/command_parser.cpp
    CPPI1-Saveable-Task-Manager/solution/task_storage.cpp)
add_course_executable(bad_rows_starter
    CPPI1-Import-and-Reject-Bad-Rows/starter/main.cpp
    CPPI1-Import-and-Reject-Bad-Rows/starter/task_manager.cpp
    CPPI1-Import-and-Reject-Bad-Rows/starter/command_parser.cpp
    CPPI1-Import-and-Reject-Bad-Rows/starter/task_storage.cpp
    CPPI1-Import-and-Reject-Bad-Rows/starter/task_import.cpp)
add_course_executable(bad_rows_solution
    CPPI1-Import-and-Reject-Bad-Rows/solution/main.cpp
    CPPI1-Import-and-Reject-Bad-Rows/solution/task_manager.cpp
    CPPI1-Import-and-Reject-Bad-Rows/solution/command_parser.cpp
    CPPI1-Import-and-Reject-Bad-Rows/solution/task_storage.cpp
    CPPI1-Import-and-Reject-Bad-Rows/solution/task_import.cpp)
add_course_executable(command_scanner_starter CPPI1-Mini-Command-Scanner/starter/main.cpp)
add_course_executable(command_scanner_solution CPPI1-Mini-Command-Scanner/solution/main.cpp)
add_course_executable(maze_search_starter
    CPPI2-Recursive-Maze-Search/starter/main.cpp
    CPPI2-Recursive-Maze-Search/starter/maze.cpp
    CPPI2-Recursive-Maze-Search/starter/maze_search.cpp)
add_course_executable(maze_search_solution
    CPPI2-Recursive-Maze-Search/solution/main.cpp
    CPPI2-Recursive-Maze-Search/solution/maze.cpp
    CPPI2-Recursive-Maze-Search/solution/maze_search.cpp)
add_course_executable(trace_drill_starter CPPI2-Recursion-Trace-Drill/starter/main.cpp)
add_course_executable(trace_drill_solution CPPI2-Recursion-Trace-Drill/solution/main.cpp)
add_course_executable(inventory_indexer_starter CPPI3-Inventory-Indexer/starter/main.cpp)
add_course_executable(inventory_indexer_solution CPPI3-Inventory-Indexer/solution/main.cpp)
add_course_executable(container_audit_starter CPPI3-Container-Tradeoff-Audit/starter/main.cpp)
add_course_executable(container_audit_solution CPPI3-Container-Tradeoff-Audit/solution/main.cpp)
add_course_executable(file_processor_starter CPPI4-Resource-Safe-File-Processor/starter/main.cpp)
add_course_executable(file_processor_solution CPPI4-Resource-Safe-File-Processor/solution/main.cpp)
add_course_executable(ownership_rewrite_starter CPPI4-Ownership-Rewrite-Reflection/starter/main.cpp)
add_course_executable(ownership_rewrite_solution CPPI4-Ownership-Rewrite-Reflection/solution/main.cpp)
add_course_executable(fraction_toolkit_starter CPPI5-Fraction-Toolkit/starter/main.cpp)
add_course_executable(fraction_toolkit_solution CPPI5-Fraction-Toolkit/solution/main.cpp)
add_course_executable(template_drill_starter CPPI5-Template-Error-Reading-Drill/starter/main.cpp)
add_course_executable(template_drill_solution CPPI5-Template-Error-Reading-Drill/solution/main.cpp)
add_course_executable(command_sim_starter CPPI6-Saveable-Command-Simulation/starter/main.cpp)
add_course_executable(command_sim_solution CPPI6-Saveable-Command-Simulation/solution/main.cpp)
add_course_executable(state_review_starter CPPI6-Enum-vs-Polymorphic-State-Review/starter/main.cpp)
add_course_executable(state_review_solution CPPI6-Enum-vs-Polymorphic-State-Review/solution/main.cpp)

# The setup checkpoint establishes the course's documented C++20 path.
set_target_properties(build_debug_starter build_debug_solution PROPERTIES
    CXX_STANDARD 20 CXX_STANDARD_REQUIRED ON CXX_EXTENSIONS OFF)
foreach(target build_debug_starter build_debug_solution)
    target_compile_options(${target} PRIVATE
        $<$<CXX_COMPILER_ID:Clang,AppleClang,GNU>:-Werror>
        $<$<CXX_COMPILER_ID:MSVC>:/WX>)
endforeach()
enable_testing()
add_test(NAME build_debug_reference COMMAND build_debug_solution --check)
add_test(NAME build_debug_deliberate_failure COMMAND build_debug_starter --check)
set_tests_properties(build_debug_deliberate_failure PROPERTIES WILL_FAIL TRUE)

# CPPI1 continues the C++20 multi-translation-unit path from the checkpoint.
set_target_properties(task_manager_starter task_manager_solution PROPERTIES
    CXX_STANDARD 20 CXX_STANDARD_REQUIRED ON CXX_EXTENSIONS OFF)
foreach(target task_manager_starter task_manager_solution)
    target_compile_options(${target} PRIVATE
        $<$<CXX_COMPILER_ID:Clang,AppleClang,GNU>:-Werror>
        $<$<CXX_COMPILER_ID:MSVC>:/WX>)
endforeach()

# Selective import extends the same C++20 Task Manager, with its own policy.
set_target_properties(bad_rows_starter bad_rows_solution PROPERTIES
    CXX_STANDARD 20 CXX_STANDARD_REQUIRED ON CXX_EXTENSIONS OFF)
foreach(target bad_rows_starter bad_rows_solution)
    target_compile_options(${target} PRIVATE
        $<$<CXX_COMPILER_ID:Clang,AppleClang,GNU>:-Werror>
        $<$<CXX_COMPILER_ID:MSVC>:/WX>)
endforeach()

# The bounded recursive grid search continues the C++20 multi-file sequence.
set_target_properties(maze_search_starter maze_search_solution PROPERTIES
    CXX_STANDARD 20 CXX_STANDARD_REQUIRED ON CXX_EXTENSIONS OFF)
foreach(target maze_search_starter maze_search_solution)
    target_compile_options(${target} PRIVATE
        $<$<CXX_COMPILER_ID:Clang,AppleClang,GNU>:-Werror>
        $<$<CXX_COMPILER_ID:MSVC>:/WX>)
endforeach()

# Worksheet printers preserve the documented strict-warning workflow.
foreach(target trace_drill_starter trace_drill_solution
               container_audit_starter container_audit_solution)
    target_compile_options(${target} PRIVATE
        $<$<CXX_COMPILER_ID:Clang,AppleClang,GNU>:-Werror>
        $<$<CXX_COMPILER_ID:MSVC>:/WX>)
endforeach()
