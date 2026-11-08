cmake_minimum_required(VERSION 3.20)
project(cl_Taiwankeyin_R2B VERSION 0.2.1 LANGUAGES CXX)
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)
find_package(ICU REQUIRED COMPONENTS uc i18n)
find_package(SQLite3 REQUIRED)
enable_testing()
add_subdirectory("${CMAKE_CURRENT_SOURCE_DIR}/../R2_Zhuyin" "${CMAKE_CURRENT_BINARY_DIR}/r2a")
add_executable(cellkeyin_import_terra src/import_terra.cpp)
target_link_libraries(cellkeyin_import_terra PRIVATE cellkeyin_zhuyin ICU::i18n)
add_executable(cellkeyin_r2b_verify tests/verify_import.cpp)
target_link_libraries(cellkeyin_r2b_verify PRIVATE cellkeyin_zhuyin)
if(MSVC)
 target_compile_options(cellkeyin_import_terra PRIVATE /W4 /utf-8)
 target_compile_options(cellkeyin_r2b_verify PRIVATE /W4 /utf-8)
else()
 target_compile_options(cellkeyin_import_terra PRIVATE -Wall -Wextra -Wpedantic -Werror)
 target_compile_options(cellkeyin_r2b_verify PRIVATE -Wall -Wextra -Wpedantic -Werror)
endif()
add_test(NAME R2B_ImporterSmoke
 COMMAND ${CMAKE_COMMAND}
 -DIMPORTER=$<TARGET_FILE:cellkeyin_import_terra>
 -DSOURCE=${CMAKE_CURRENT_SOURCE_DIR}/tests/terra_sample.yaml
 -DDEST=${CMAKE_CURRENT_BINARY_DIR}/import-smoke.tsv
 -P ${CMAKE_CURRENT_SOURCE_DIR}/tests/run_smoke.cmake)
set_tests_properties(R2B_ImporterSmoke PROPERTIES FIXTURES_SETUP imported_data)
add_test(NAME R2B_ImportedLexiconVerify
 COMMAND cellkeyin_r2b_verify "${CMAKE_CURRENT_BINARY_DIR}/import-smoke.tsv")
set_tests_properties(R2B_ImportedLexiconVerify PROPERTIES FIXTURES_REQUIRED imported_data)
