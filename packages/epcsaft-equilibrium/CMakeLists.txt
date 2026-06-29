cmake_minimum_required(VERSION 3.20...4.2)

if(NOT DEFINED SKBUILD_PROJECT_NAME)
    set(SKBUILD_PROJECT_NAME epcsaft_equilibrium)
endif()
if(NOT DEFINED SKBUILD_PROJECT_VERSION)
    file(READ "${CMAKE_CURRENT_SOURCE_DIR}/pyproject.toml" EPCSAFT_EQUILIBRIUM_PYPROJECT_TOML)
    string(REGEX MATCH "version[ \t]*=[ \t]*\"([^\"]+)\"" EPCSAFT_EQUILIBRIUM_VERSION_MATCH "${EPCSAFT_EQUILIBRIUM_PYPROJECT_TOML}")
    if(NOT CMAKE_MATCH_1)
        message(FATAL_ERROR "Could not derive SKBUILD_PROJECT_VERSION from packages/epcsaft-equilibrium/pyproject.toml")
    endif()
    set(SKBUILD_PROJECT_VERSION "${CMAKE_MATCH_1}")
endif()

project(${SKBUILD_PROJECT_NAME}
    VERSION ${SKBUILD_PROJECT_VERSION}
    LANGUAGES CXX
)

option(EPCSAFT_ENABLE_CPPAD "Enable package-wide CppAD support" ON)
option(EPCSAFT_USE_SYSTEM_CPPAD "Use installed CppAD instead of FetchContent" OFF)
option(EPCSAFT_ENABLE_IPOPT "Enable native Ipopt support for production equilibrium NLP solves" ON)
option(EPCSAFT_USE_SYSTEM_IPOPT "Use an installed Ipopt package for native equilibrium NLP solves" ON)
option(EPCSAFT_BUILD_EXTENSION_NATIVE "Build the epcsaft-equilibrium package-owned native module" ON)
set(EPCSAFT_IPOPT_ROOT "" CACHE PATH "Root directory for an installed Ipopt tree with include/, lib/, and bin/")
set(EPCSAFT_PROVIDER_SDK_CMAKE_CONFIG "" CACHE FILEPATH "Path to epcsaft provider_native_sdk_v1 CMake config")
option(EPCSAFT_WARNINGS_AS_ERRORS "Treat native warnings as errors" OFF)

if(NOT EPCSAFT_BUILD_EXTENSION_NATIVE)
    message(STATUS "Configuring epcsaft-equilibrium editable package without native module build.")
    return()
endif()

if(NOT EPCSAFT_ENABLE_CPPAD)
    message(FATAL_ERROR "EPCSAFT_ENABLE_CPPAD=OFF is invalid; extension native builds require CppAD.")
endif()
if(NOT EPCSAFT_ENABLE_IPOPT)
    message(FATAL_ERROR "EPCSAFT_ENABLE_IPOPT=OFF is invalid for production epcsaft-equilibrium package builds.")
endif()
if(NOT EPCSAFT_USE_SYSTEM_IPOPT)
    message(FATAL_ERROR "EPCSAFT_USE_SYSTEM_IPOPT=OFF is invalid; vendored Ipopt builds are not supported.")
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
    set(cppad_has_mkstemp 0)
    set(cppad_has_tmpnam_s 0)
    set(cppad_c_compiler_cmd "${CMAKE_CXX_COMPILER}")
    if(CMAKE_CXX_COMPILER_ID STREQUAL "GNU" OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
        set(cppad_c_compiler_gnu_flags 1)
    else()
        set(cppad_c_compiler_gnu_flags 0)
    endif()
    if(MSVC)
        set(cppad_c_compiler_msvc_flags 1)
    else()
        set(cppad_c_compiler_msvc_flags 0)
    endif()
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

set(EPCSAFT_IPOPT_TARGET "")
if(EPCSAFT_IPOPT_ROOT)
    file(TO_CMAKE_PATH "${EPCSAFT_IPOPT_ROOT}" EPCSAFT_IPOPT_ROOT_CMAKE)
    find_path(EPCSAFT_IPOPT_INCLUDE_DIR
        NAMES coin-or/IpIpoptApplication.hpp IpIpoptApplication.hpp
        PATHS
            "${EPCSAFT_IPOPT_ROOT_CMAKE}/include"
            "${EPCSAFT_IPOPT_ROOT_CMAKE}/include/coin-or"
            "${EPCSAFT_IPOPT_ROOT_CMAKE}/include/coin"
        NO_DEFAULT_PATH
    )
    find_library(EPCSAFT_IPOPT_LIBRARY
        NAMES ipopt ipopt-3 libipopt
        PATHS "${EPCSAFT_IPOPT_ROOT_CMAKE}/lib"
        NO_DEFAULT_PATH
    )
    if(NOT EPCSAFT_IPOPT_INCLUDE_DIR OR NOT EPCSAFT_IPOPT_LIBRARY)
        message(FATAL_ERROR "EPCSAFT_IPOPT_ROOT must contain a usable Ipopt include/ and lib/ tree: ${EPCSAFT_IPOPT_ROOT}")
    endif()
    add_library(EPCSAFT::Ipopt UNKNOWN IMPORTED)
    set_target_properties(EPCSAFT::Ipopt PROPERTIES
        IMPORTED_LOCATION "${EPCSAFT_IPOPT_LIBRARY}"
        INTERFACE_INCLUDE_DIRECTORIES "${EPCSAFT_IPOPT_INCLUDE_DIR}"
    )
    set(EPCSAFT_IPOPT_TARGET EPCSAFT::Ipopt)
else()
    find_package(Ipopt CONFIG QUIET)
    if(TARGET Ipopt::ipopt)
        set(EPCSAFT_IPOPT_TARGET Ipopt::ipopt)
    elseif(TARGET Ipopt::Ipopt)
        set(EPCSAFT_IPOPT_TARGET Ipopt::Ipopt)
    else()
        find_package(PkgConfig QUIET)
        if(PkgConfig_FOUND)
            pkg_check_modules(EPCSAFT_IPOPT_PC QUIET IMPORTED_TARGET ipopt)
        endif()
        if(TARGET PkgConfig::EPCSAFT_IPOPT_PC)
            set(EPCSAFT_IPOPT_TARGET PkgConfig::EPCSAFT_IPOPT_PC)
        endif()
    endif()
endif()
if(NOT EPCSAFT_IPOPT_TARGET)
    message(FATAL_ERROR "Production epcsaft-equilibrium package builds require Ipopt. Set EPCSAFT_IPOPT_ROOT or Ipopt_DIR.")
endif()
set(EPCSAFT_IPOPT_STATUS "enabled_available")

include("${EPCSAFT_PROVIDER_SDK_CMAKE_CONFIG}")
epcsaft_provider_sdk_add_provider_native(epcsaft_provider_native)

set(EPCSAFT_EQUILIBRIUM_NATIVE_ROOT "${CMAKE_CURRENT_SOURCE_DIR}/src/epcsaft_equilibrium/native/equilibrium")
set(EPCSAFT_NATIVE_EQUILIBRIUM_SOURCES
    "${EPCSAFT_EQUILIBRIUM_NATIVE_ROOT}/blocks/association_block.cpp"
    "${EPCSAFT_EQUILIBRIUM_NATIVE_ROOT}/blocks/chemical_equilibrium_block.cpp"
    "${EPCSAFT_EQUILIBRIUM_NATIVE_ROOT}/blocks/electrolyte_block.cpp"
    "${EPCSAFT_EQUILIBRIUM_NATIVE_ROOT}/blocks/eos_phase_block.cpp"
    "${EPCSAFT_EQUILIBRIUM_NATIVE_ROOT}/blocks/gibbs_blocks.cpp"
    "${EPCSAFT_EQUILIBRIUM_NATIVE_ROOT}/blocks/phase_equilibrium_residual_block.cpp"
    "${EPCSAFT_EQUILIBRIUM_NATIVE_ROOT}/blocks/reaction_block.cpp"
    "${EPCSAFT_EQUILIBRIUM_NATIVE_ROOT}/blocks/saturation_block.cpp"
    "${EPCSAFT_EQUILIBRIUM_NATIVE_ROOT}/core/activated_equilibrium_nlp.cpp"
    "${EPCSAFT_EQUILIBRIUM_NATIVE_ROOT}/core/activation_plan.cpp"
    "${EPCSAFT_EQUILIBRIUM_NATIVE_ROOT}/core/chemical_equilibrium_nlp.cpp"
    "${EPCSAFT_EQUILIBRIUM_NATIVE_ROOT}/core/chemical_equilibrium_objective.cpp"
    "${EPCSAFT_EQUILIBRIUM_NATIVE_ROOT}/core/continuation_driver.cpp"
    "${EPCSAFT_EQUILIBRIUM_NATIVE_ROOT}/core/feasible_initialization.cpp"
    "${EPCSAFT_EQUILIBRIUM_NATIVE_ROOT}/core/helpers.cpp"
    "${EPCSAFT_EQUILIBRIUM_NATIVE_ROOT}/core/nlp_problem.cpp"
    "${EPCSAFT_EQUILIBRIUM_NATIVE_ROOT}/core/selector_core.cpp"
    "${EPCSAFT_EQUILIBRIUM_NATIVE_ROOT}/core/second_order.cpp"
    "${EPCSAFT_EQUILIBRIUM_NATIVE_ROOT}/core/two_phase_eos_route.cpp"
    "${EPCSAFT_EQUILIBRIUM_NATIVE_ROOT}/core/variable_transform.cpp"
    "${EPCSAFT_EQUILIBRIUM_NATIVE_ROOT}/core/variable_layout.cpp"
    "${EPCSAFT_EQUILIBRIUM_NATIVE_ROOT}/derivatives/nlp_contract_snapshot.cpp"
    "${EPCSAFT_EQUILIBRIUM_NATIVE_ROOT}/derivatives/phase_block_derivatives.cpp"
    "${EPCSAFT_EQUILIBRIUM_NATIVE_ROOT}/derivatives/phase_system_derivatives.cpp"
    "${EPCSAFT_EQUILIBRIUM_NATIVE_ROOT}/derivatives/route_second_order.cpp"
    "${EPCSAFT_EQUILIBRIUM_NATIVE_ROOT}/results/result_builder.cpp"
    "${EPCSAFT_EQUILIBRIUM_NATIVE_ROOT}/routes/derived/bubble_dew.cpp"
    "${EPCSAFT_EQUILIBRIUM_NATIVE_ROOT}/solvers/ipopt_adapter.cpp"
)
set(EPCSAFT_EQUILIBRIUM_NATIVE_INCLUDE_DIRS
    ${EPCSAFT_PROVIDER_NATIVE_INCLUDE_DIRS}
    "${CMAKE_CURRENT_SOURCE_DIR}/src/epcsaft_equilibrium/native"
    "${EPCSAFT_EQUILIBRIUM_NATIVE_ROOT}"
    "${EPCSAFT_EQUILIBRIUM_NATIVE_ROOT}/blocks"
    "${EPCSAFT_EQUILIBRIUM_NATIVE_ROOT}/core"
    "${EPCSAFT_EQUILIBRIUM_NATIVE_ROOT}/derivatives"
    "${EPCSAFT_EQUILIBRIUM_NATIVE_ROOT}/results"
    "${EPCSAFT_EQUILIBRIUM_NATIVE_ROOT}/routes/derived"
    "${EPCSAFT_EQUILIBRIUM_NATIVE_ROOT}/solvers"
)

add_library(epcsaft_equilibrium_native OBJECT ${EPCSAFT_NATIVE_EQUILIBRIUM_SOURCES})
target_include_directories(epcsaft_equilibrium_native
    PUBLIC
        ${EPCSAFT_EQUILIBRIUM_NATIVE_INCLUDE_DIRS}
        "${EPCSAFT_EIGEN_INCLUDE}"
)
target_compile_features(epcsaft_equilibrium_native PUBLIC cxx_std_17)
set_target_properties(epcsaft_equilibrium_native PROPERTIES POSITION_INDEPENDENT_CODE ON)
target_link_libraries(epcsaft_equilibrium_native PUBLIC epcsaft_provider_native "${EPCSAFT_IPOPT_TARGET}")
target_compile_definitions(epcsaft_equilibrium_native PUBLIC EPCSAFT_HAS_IPOPT=1)

pybind11_add_module(
    epcsaft_equilibrium_native_core
    NO_EXTRAS
    "${EPCSAFT_EQUILIBRIUM_NATIVE_ROOT}/module.cpp"
    "${EPCSAFT_EQUILIBRIUM_NATIVE_ROOT}/register_bindings.cpp"
)
set_target_properties(
    epcsaft_equilibrium_native_core
    PROPERTIES
        OUTPUT_NAME "_native_core"
        LIBRARY_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/epcsaft_equilibrium"
        RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/epcsaft_equilibrium"
        ARCHIVE_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/epcsaft_equilibrium"
)
target_link_libraries(epcsaft_equilibrium_native_core PRIVATE epcsaft_provider_native epcsaft_equilibrium_native "${EPCSAFT_IPOPT_TARGET}")
target_include_directories(epcsaft_equilibrium_native_core
    PRIVATE
        ${EPCSAFT_EQUILIBRIUM_NATIVE_INCLUDE_DIRS}
        "${EPCSAFT_EIGEN_INCLUDE}"
)
target_compile_features(epcsaft_equilibrium_native_core PRIVATE cxx_std_17)
target_compile_definitions(epcsaft_equilibrium_native_core PRIVATE EPCSAFT_HAS_IPOPT=1)

set(EPCSAFT_NATIVE_TARGETS epcsaft_provider_native epcsaft_equilibrium_native epcsaft_equilibrium_native_core)
foreach(target_name IN LISTS EPCSAFT_NATIVE_TARGETS)
    target_compile_definitions(
        ${target_name}
        PRIVATE
            EPCSAFT_CPPAD_STATUS="${EPCSAFT_CPPAD_STATUS}"
            EPCSAFT_IPOPT_STATUS="${EPCSAFT_IPOPT_STATUS}"
    )
    if(MSVC)
        target_compile_options(${target_name} PRIVATE /W4 /wd4551)
        if(EPCSAFT_WARNINGS_AS_ERRORS)
            target_compile_options(${target_name} PRIVATE /WX)
        endif()
    elseif(CMAKE_CXX_COMPILER_ID STREQUAL "GNU" OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
        target_compile_options(${target_name} PRIVATE -Wall -Wextra -Wpedantic)
        if(EPCSAFT_WARNINGS_AS_ERRORS)
            target_compile_options(${target_name} PRIVATE -Werror)
        endif()
    endif()
endforeach()

install(TARGETS epcsaft_equilibrium_native_core
    LIBRARY DESTINATION epcsaft_equilibrium
    RUNTIME DESTINATION epcsaft_equilibrium
)
if(WIN32 AND EPCSAFT_IPOPT_ROOT)
    file(TO_CMAKE_PATH "${EPCSAFT_IPOPT_ROOT}/bin" EPCSAFT_IPOPT_BIN_DIR)
    if(NOT IS_DIRECTORY "${EPCSAFT_IPOPT_BIN_DIR}")
        message(FATAL_ERROR "EPCSAFT_IPOPT_ROOT did not provide runtime DLLs under bin/: ${EPCSAFT_IPOPT_ROOT}")
    endif()
    install(CODE "
        set(_epcsaft_module \"$<TARGET_FILE:epcsaft_equilibrium_native_core>\")
        set(_epcsaft_ipopt_bin \"${EPCSAFT_IPOPT_BIN_DIR}\")
        if(POLICY CMP0207)
            cmake_policy(SET CMP0207 NEW)
        endif()
        file(GET_RUNTIME_DEPENDENCIES
            MODULES \"\${_epcsaft_module}\"
            DIRECTORIES \"\${_epcsaft_ipopt_bin}\"
            RESOLVED_DEPENDENCIES_VAR _epcsaft_resolved_runtime_deps
            UNRESOLVED_DEPENDENCIES_VAR _epcsaft_unresolved_runtime_deps
            POST_EXCLUDE_REGEXES
                [[.*[\\\\/]System32[\\\\/].*]]
                [[.*[\\\\/]Windows[\\\\/].*]]
                [[.*[\\\\/]python[0-9]+[.]dll$]]
                [[.*[\\\\/]Python[0-9]+[.]dll$]]
        )
        if(_epcsaft_unresolved_runtime_deps)
            list(FILTER _epcsaft_unresolved_runtime_deps EXCLUDE REGEX [[^[Pp]ython[0-9]+[.]dll$]])
        endif()
        if(_epcsaft_unresolved_runtime_deps)
            message(FATAL_ERROR \"Unresolved epcsaft-equilibrium runtime dependencies: \${_epcsaft_unresolved_runtime_deps}\")
        endif()
        set(_epcsaft_runtime_payload \"\")
        foreach(_dependency IN LISTS _epcsaft_resolved_runtime_deps)
            get_filename_component(_dependency_dir \"\${_dependency}\" DIRECTORY)
            file(TO_CMAKE_PATH \"\${_dependency_dir}\" _dependency_dir_cmake)
            if(_dependency_dir_cmake STREQUAL _epcsaft_ipopt_bin)
                list(APPEND _epcsaft_runtime_payload \"\${_dependency}\")
            endif()
        endforeach()
        if(_epcsaft_runtime_payload)
            list(REMOVE_DUPLICATES _epcsaft_runtime_payload)
            file(INSTALL DESTINATION \"\${CMAKE_INSTALL_PREFIX}/epcsaft_equilibrium\" TYPE FILE FILES \${_epcsaft_runtime_payload})
            list(LENGTH _epcsaft_runtime_payload _epcsaft_runtime_payload_count)
            message(STATUS \"Installed audited Ipopt runtime dependency payload: \${_epcsaft_runtime_payload_count} DLLs\")
        else()
            message(STATUS \"No Ipopt runtime DLL payload was required from \${_epcsaft_ipopt_bin}\")
        endif()
    ")
endif()
