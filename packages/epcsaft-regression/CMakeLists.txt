cmake_minimum_required(VERSION 3.20...4.2)

if(NOT DEFINED SKBUILD_PROJECT_NAME)
    set(SKBUILD_PROJECT_NAME epcsaft_regression)
endif()
if(NOT DEFINED SKBUILD_PROJECT_VERSION)
    file(READ "${CMAKE_CURRENT_SOURCE_DIR}/pyproject.toml" EPCSAFT_REGRESSION_PYPROJECT_TOML)
    string(REGEX MATCH "version[ \t]*=[ \t]*\"([^\"]+)\"" EPCSAFT_REGRESSION_VERSION_MATCH "${EPCSAFT_REGRESSION_PYPROJECT_TOML}")
    if(NOT CMAKE_MATCH_1)
        message(FATAL_ERROR "Could not derive SKBUILD_PROJECT_VERSION from packages/epcsaft-regression/pyproject.toml")
    endif()
    set(SKBUILD_PROJECT_VERSION "${CMAKE_MATCH_1}")
endif()

project(${SKBUILD_PROJECT_NAME}
    VERSION ${SKBUILD_PROJECT_VERSION}
    LANGUAGES CXX
)

option(EPCSAFT_ENABLE_CPPAD "Enable package-wide CppAD support" ON)
option(EPCSAFT_USE_SYSTEM_CPPAD "Use installed CppAD instead of FetchContent" OFF)
option(EPCSAFT_ENABLE_CERES "Enable Ceres Solver support for native regression solves" ON)
option(EPCSAFT_USE_SYSTEM_CERES "Use an installed Ceres Solver package instead of FetchContent" OFF)
option(EPCSAFT_ENABLE_IPOPT "Enable native Ipopt support" OFF)
option(EPCSAFT_BUILD_EXTENSION_NATIVE "Build the epcsaft-regression package-owned native module" ON)
set(EPCSAFT_PROVIDER_SDK_CMAKE_CONFIG "" CACHE FILEPATH "Path to epcsaft provider_native_sdk_v1 CMake config")
option(EPCSAFT_WARNINGS_AS_ERRORS "Treat native warnings as errors" OFF)
set(EPCSAFT_CERES_VERSION "2.2.0")

if(NOT EPCSAFT_BUILD_EXTENSION_NATIVE)
    message(STATUS "Configuring epcsaft-regression editable package without native module build.")
    return()
endif()

if(NOT EPCSAFT_ENABLE_CPPAD)
    message(FATAL_ERROR "EPCSAFT_ENABLE_CPPAD=OFF is invalid; extension native builds require CppAD.")
endif()
if(NOT EPCSAFT_ENABLE_CERES)
    message(FATAL_ERROR "EPCSAFT_ENABLE_CERES=OFF is invalid for production epcsaft-regression package builds.")
endif()
if(EPCSAFT_ENABLE_IPOPT)
    message(FATAL_ERROR "EPCSAFT_ENABLE_IPOPT=ON is invalid for default epcsaft-regression package builds.")
endif()
if(NOT EPCSAFT_PROVIDER_SDK_CMAKE_CONFIG OR NOT EXISTS "${EPCSAFT_PROVIDER_SDK_CMAKE_CONFIG}")
    message(FATAL_ERROR "EPCSAFT_PROVIDER_SDK_CMAKE_CONFIG must point at provider_native_sdk_v1/epcsaft_provider_sdk.cmake.")
endif()

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)
set(PYBIND11_FINDPYTHON ON)

find_package(pybind11 CONFIG REQUIRED)

execute_process(
    COMMAND "${Python_EXECUTABLE}" -c "import includeigen; print(includeigen.get_include())"
    OUTPUT_VARIABLE EPCSAFT_EIGEN_INCLUDE
    OUTPUT_STRIP_TRAILING_WHITESPACE
    COMMAND_ERROR_IS_FATAL ANY
)
file(TO_CMAKE_PATH "${EPCSAFT_EIGEN_INCLUDE}" EPCSAFT_EIGEN_INCLUDE_CMAKE)

if(NOT Eigen3_DIR)
    set(EPCSAFT_EIGEN3_CONFIG_DIR "${CMAKE_CURRENT_BINARY_DIR}/generated_eigen3_config")
    file(MAKE_DIRECTORY "${EPCSAFT_EIGEN3_CONFIG_DIR}")
    file(WRITE "${EPCSAFT_EIGEN3_CONFIG_DIR}/Eigen3Config.cmake"
"if(NOT TARGET Eigen3::Eigen)
    add_library(Eigen3::Eigen INTERFACE IMPORTED)
    set_target_properties(Eigen3::Eigen PROPERTIES INTERFACE_INCLUDE_DIRECTORIES \"${EPCSAFT_EIGEN_INCLUDE_CMAKE}\")
endif()
set(Eigen3_VERSION 3.4.0)
set(Eigen3_FOUND TRUE)
")
    file(WRITE "${EPCSAFT_EIGEN3_CONFIG_DIR}/Eigen3ConfigVersion.cmake"
"set(PACKAGE_VERSION 3.4.0)
set(PACKAGE_VERSION_COMPATIBLE TRUE)
set(PACKAGE_VERSION_EXACT FALSE)
")
    set(Eigen3_DIR "${EPCSAFT_EIGEN3_CONFIG_DIR}" CACHE PATH "Generated Eigen3 package config for bundled includeigen")
endif()

if(EPCSAFT_USE_SYSTEM_CERES)
    unset(Ceres_BINARY_DIR CACHE)
    unset(Ceres_SOURCE_DIR CACHE)
    find_package(Ceres ${EPCSAFT_CERES_VERSION} CONFIG REQUIRED)
else()
    include(FetchContent)
    set(BUILD_TESTING OFF CACHE BOOL "" FORCE)
    set(BUILD_EXAMPLES OFF CACHE BOOL "" FORCE)
    set(BUILD_BENCHMARKS OFF CACHE BOOL "" FORCE)
    set(MINIGLOG ON CACHE BOOL "" FORCE)
    set(GFLAGS OFF CACHE BOOL "" FORCE)
    set(SUITESPARSE OFF CACHE BOOL "" FORCE)
    set(EIGENSPARSE OFF CACHE BOOL "" FORCE)
    set(LAPACK OFF CACHE BOOL "" FORCE)
    set(USE_CUDA OFF CACHE BOOL "" FORCE)
    set(SCHUR_SPECIALIZATIONS OFF CACHE BOOL "" FORCE)
    set(EPCSAFT_CERES_FETCHCONTENT_ARGS "")
    if(CMAKE_VERSION VERSION_GREATER_EQUAL 3.28)
        list(APPEND EPCSAFT_CERES_FETCHCONTENT_ARGS EXCLUDE_FROM_ALL)
    endif()
    FetchContent_Declare(
        ceres_solver
        GIT_REPOSITORY https://ceres-solver.googlesource.com/ceres-solver
        GIT_TAG ${EPCSAFT_CERES_VERSION}
        GIT_SHALLOW TRUE
        ${EPCSAFT_CERES_FETCHCONTENT_ARGS}
    )
    set(EPCSAFT_PREVIOUS_CMAKE_SKIP_INSTALL_RULES "${CMAKE_SKIP_INSTALL_RULES}")
    set(CMAKE_SKIP_INSTALL_RULES ON)
    FetchContent_MakeAvailable(ceres_solver)
    set(CMAKE_SKIP_INSTALL_RULES "${EPCSAFT_PREVIOUS_CMAKE_SKIP_INSTALL_RULES}")
    if(TARGET ceres_internal AND CMAKE_CXX_COMPILER_ID STREQUAL "GNU")
        target_compile_options(ceres_internal PRIVATE -include cstdint)
    endif()
endif()

set(EPCSAFT_CPPAD_STATUS "disabled")
set(EPCSAFT_CPPAD_GENERATED_INCLUDE_DIR "")
set(EPCSAFT_CPPAD_SOURCE_FILE "")
set(EPCSAFT_CPPAD_LIBRARY "")
if(EPCSAFT_USE_SYSTEM_CPPAD)
    find_path(EPCSAFT_CPPAD_INCLUDE_DIR NAMES cppad/cppad.hpp REQUIRED)
    find_library(EPCSAFT_CPPAD_LIBRARY NAMES cppad_lib cppad)
else()
    include(FetchContent)
    FetchContent_Declare(
        cppad
        GIT_REPOSITORY https://github.com/coin-or/CppAD.git
        GIT_TAG 20250000.3
        GIT_SHALLOW TRUE
        SOURCE_SUBDIR cmake-do-not-configure
    )
    FetchContent_MakeAvailable(cppad)
    set(EPCSAFT_CPPAD_INCLUDE_DIR "${cppad_SOURCE_DIR}/include")
    set(EPCSAFT_CPPAD_SOURCE_FILE "${cppad_SOURCE_DIR}/cppad_lib/temp_file.cpp")
endif()
if(NOT EXISTS "${EPCSAFT_CPPAD_INCLUDE_DIR}/cppad/cppad.hpp")
    message(FATAL_ERROR "EPCSAFT_ENABLE_CPPAD=ON but cppad/cppad.hpp was not found")
endif()
if(NOT EXISTS "${EPCSAFT_CPPAD_INCLUDE_DIR}/cppad/configure.hpp")
    if(NOT EXISTS "${EPCSAFT_CPPAD_INCLUDE_DIR}/cppad/configure.hpp.in")
        message(FATAL_ERROR "EPCSAFT_ENABLE_CPPAD=ON but cppad/configure.hpp is missing and no template was found")
    endif()
    set(EPCSAFT_CPPAD_GENERATED_INCLUDE_DIR "${CMAKE_CURRENT_BINARY_DIR}/generated_cppad_include")
    file(MAKE_DIRECTORY "${EPCSAFT_CPPAD_GENERATED_INCLUDE_DIR}/cppad")
    set(compiler_has_conversion_warn 0)
    set(cppad_debug_and_release_01 1)
    set(use_cplusplus_2017_ok 1)
    set(cppad_version "20250000.3")
    set(cppad_has_adolc 0)
    set(cppad_has_colpack 0)
    set(cppad_has_eigen 0)
    set(cppad_has_ipopt 0)
    set(cppad_deprecated_01 0)
    set(cppad_boostvector 0)
    set(cppad_cppadvector 0)
    set(cppad_stdvector 1)
    set(cppad_eigenvector 0)
    set(cppad_has_gettimeofday 0)
    include(CheckCXXSourceCompiles)
    check_cxx_source_compiles([=[
#include <stdlib.h>
#include <unistd.h>

int main()
{
    char pattern[] = "/tmp/fileXXXXXX";
    int fd = mkstemp(pattern);
    return fd < 0;
}
]=] EPCSAFT_CPPAD_HAS_MKSTEMP)
    if(EPCSAFT_CPPAD_HAS_MKSTEMP)
        set(cppad_has_mkstemp 1)
    else()
        set(cppad_has_mkstemp 0)
    endif()
    set(cppad_has_tmpnam_s 0)
    set(cppad_c_compiler_cmd "${CMAKE_CXX_COMPILER}")
    if(CMAKE_CXX_COMPILER_ID STREQUAL "GNU" OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
        set(cppad_c_compiler_gnu_flags 1)
    else()
        set(cppad_c_compiler_gnu_flags 0)
    endif()
    set(cppad_c_compiler_msvc_flags 0)
    set(cppad_is_same_unsigned_int_size_t 0)
    if(CMAKE_SIZEOF_VOID_P EQUAL 8)
        set(cppad_padding_block_t "")
    else()
        set(cppad_padding_block_t "void* note_used_;")
    endif()
    set(cppad_tape_addr_type "unsigned int")
    set(cppad_is_same_tape_addr_type_size_t 0)
    set(cppad_tape_id_type "unsigned int")
    set(cppad_max_num_threads 48)
    configure_file(
        "${EPCSAFT_CPPAD_INCLUDE_DIR}/cppad/configure.hpp.in"
        "${EPCSAFT_CPPAD_GENERATED_INCLUDE_DIR}/cppad/configure.hpp"
        @ONLY
    )
endif()
set(EPCSAFT_CPPAD_STATUS "enabled_available")
set(EPCSAFT_IPOPT_STATUS "disabled")

include("${EPCSAFT_PROVIDER_SDK_CMAKE_CONFIG}")
epcsaft_provider_sdk_add_provider_native(epcsaft_provider_native)

set(EPCSAFT_REGRESSION_NATIVE_ROOT "${CMAKE_CURRENT_SOURCE_DIR}/src/epcsaft_regression/native/regression")
add_library(epcsaft_regression_native OBJECT
    "${EPCSAFT_REGRESSION_NATIVE_ROOT}/ceres_regression.cpp"
)
target_include_directories(epcsaft_regression_native
    PUBLIC
        ${EPCSAFT_PROVIDER_NATIVE_INCLUDE_DIRS}
        "${CMAKE_CURRENT_SOURCE_DIR}/src/epcsaft_regression/native"
        "${EPCSAFT_REGRESSION_NATIVE_ROOT}"
        "${EPCSAFT_EIGEN_INCLUDE}"
)
target_compile_features(epcsaft_regression_native PUBLIC cxx_std_17)
set_target_properties(epcsaft_regression_native PROPERTIES POSITION_INDEPENDENT_CODE ON)
target_link_libraries(epcsaft_regression_native PUBLIC epcsaft_provider_native Ceres::ceres)
target_compile_definitions(epcsaft_regression_native PUBLIC EPCSAFT_HAS_CERES=1 EPCSAFT_HAS_REGRESSION_NATIVE=1)

pybind11_add_module(
    epcsaft_regression_native_core
    NO_EXTRAS
    "${EPCSAFT_REGRESSION_NATIVE_ROOT}/module.cpp"
)
set_target_properties(
    epcsaft_regression_native_core
    PROPERTIES
        OUTPUT_NAME "_native_core"
        LIBRARY_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/epcsaft_regression"
        RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/epcsaft_regression"
        ARCHIVE_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/epcsaft_regression"
)
target_link_libraries(epcsaft_regression_native_core PRIVATE epcsaft_provider_native epcsaft_regression_native Ceres::ceres)
target_include_directories(epcsaft_regression_native_core
    PRIVATE
        ${EPCSAFT_PROVIDER_NATIVE_INCLUDE_DIRS}
        "${CMAKE_CURRENT_SOURCE_DIR}/src/epcsaft_regression/native"
        "${EPCSAFT_REGRESSION_NATIVE_ROOT}"
        "${EPCSAFT_EIGEN_INCLUDE}"
)
target_compile_features(epcsaft_regression_native_core PRIVATE cxx_std_17)
target_compile_definitions(epcsaft_regression_native_core PRIVATE EPCSAFT_HAS_CERES=1 EPCSAFT_HAS_REGRESSION_NATIVE=1)

set(EPCSAFT_NATIVE_TARGETS epcsaft_provider_native epcsaft_regression_native epcsaft_regression_native_core)
foreach(target_name IN LISTS EPCSAFT_NATIVE_TARGETS)
    target_compile_definitions(
        ${target_name}
        PRIVATE
            EPCSAFT_CPPAD_STATUS="${EPCSAFT_CPPAD_STATUS}"
            EPCSAFT_IPOPT_STATUS="${EPCSAFT_IPOPT_STATUS}"
    )
    if(CMAKE_CXX_COMPILER_ID STREQUAL "GNU" OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
        target_compile_options(${target_name} PRIVATE -Wall -Wextra -Wpedantic)
        if(EPCSAFT_WARNINGS_AS_ERRORS)
            target_compile_options(${target_name} PRIVATE -Werror)
        endif()
    endif()
endforeach()

install(TARGETS epcsaft_regression_native_core
    LIBRARY DESTINATION epcsaft_regression
    RUNTIME DESTINATION epcsaft_regression
)
