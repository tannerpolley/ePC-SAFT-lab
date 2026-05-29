cmake_minimum_required(VERSION 3.20...4.2)

if(NOT DEFINED SKBUILD_PROJECT_NAME)
    set(SKBUILD_PROJECT_NAME epcsaft)
endif()
if(NOT DEFINED SKBUILD_PROJECT_VERSION)
    file(READ "${CMAKE_CURRENT_SOURCE_DIR}/pyproject.toml" EPCSAFT_PYPROJECT_TOML)
    string(REGEX MATCH "version[ \t]*=[ \t]*\"([^\"]+)\"" EPCSAFT_VERSION_MATCH "${EPCSAFT_PYPROJECT_TOML}")
    if(NOT CMAKE_MATCH_1)
        message(FATAL_ERROR "Could not derive SKBUILD_PROJECT_VERSION from pyproject.toml")
    endif()
    set(SKBUILD_PROJECT_VERSION "${CMAKE_MATCH_1}")
endif()

project(${SKBUILD_PROJECT_NAME}
    VERSION ${SKBUILD_PROJECT_VERSION}
    LANGUAGES CXX
)

option(EPCSAFT_DEV_INPLACE "Copy the compiled extension into src/epcsaft for local development" OFF)
option(EPCSAFT_ENABLE_CERES "Enable Ceres Solver support for native regression solves" ON)
option(EPCSAFT_USE_SYSTEM_CERES "Use an installed Ceres Solver package instead of FetchContent" OFF)
option(EPCSAFT_ENABLE_CPPAD "Enable package-wide CppAD support" ON)
option(EPCSAFT_USE_SYSTEM_CPPAD "Use installed CppAD instead of FetchContent" OFF)
option(EPCSAFT_ENABLE_IPOPT "Enable native Ipopt support for production equilibrium NLP solves" ON)
option(EPCSAFT_USE_SYSTEM_IPOPT "Use an installed Ipopt package for native equilibrium NLP solves" ON)
option(
    EPCSAFT_BUILD_EQUILIBRIUM_NATIVE_MODULE
    "Build the epcsaft-equilibrium package-owned native module"
    ON
)
option(
    EPCSAFT_BUILD_REGRESSION_NATIVE_MODULE
    "Build the epcsaft-regression package-owned native module"
    ON
)
if(DEFINED EPCSAFT_BUILD_PROFILE)
    set(EPCSAFT_BUILD_PROFILE_INITIAL "${EPCSAFT_BUILD_PROFILE}")
else()
    set(EPCSAFT_BUILD_PROFILE_INITIAL "custom")
endif()
set(
    EPCSAFT_BUILD_PROFILE
    "${EPCSAFT_BUILD_PROFILE_INITIAL}"
    CACHE STRING
    "Named native dependency profile used by repo build helpers; provider forces the core-only boundary lane"
    FORCE
)
set_property(CACHE EPCSAFT_BUILD_PROFILE PROPERTY STRINGS custom fast full ipopt provider)
set(EPCSAFT_IPOPT_ROOT "" CACHE PATH "Root directory for an installed Ipopt tree with include/, lib/, and bin/")
option(EPCSAFT_WARNINGS_AS_ERRORS "Treat native warnings as errors" OFF)
option(EPCSAFT_ENABLE_SANITIZERS "Enable ASAN/UBSAN in debug builds" OFF)
set(EPCSAFT_CERES_VERSION "2.2.0")

if(EPCSAFT_BUILD_PROFILE STREQUAL "provider")
    set(EPCSAFT_ENABLE_CERES OFF CACHE BOOL "Enable Ceres Solver support for native regression solves" FORCE)
    set(EPCSAFT_ENABLE_IPOPT OFF CACHE BOOL "Enable native Ipopt support for production equilibrium NLP solves" FORCE)
    set(EPCSAFT_BUILD_EQUILIBRIUM_NATIVE_MODULE OFF CACHE BOOL "Build the epcsaft-equilibrium package-owned native module" FORCE)
    set(EPCSAFT_BUILD_REGRESSION_NATIVE_MODULE OFF CACHE BOOL "Build the epcsaft-regression package-owned native module" FORCE)
    set(EPCSAFT_USE_SYSTEM_IPOPT OFF CACHE BOOL "Use an installed Ipopt package for native equilibrium NLP solves" FORCE)
endif()

if(NOT EPCSAFT_ENABLE_CPPAD)
    message(FATAL_ERROR "EPCSAFT_ENABLE_CPPAD=OFF is not supported; derivative-capable package builds require CppAD.")
endif()
if(NOT EPCSAFT_BUILD_EQUILIBRIUM_NATIVE_MODULE AND EPCSAFT_ENABLE_IPOPT)
    message(FATAL_ERROR "EPCSAFT_ENABLE_IPOPT=ON requires EPCSAFT_BUILD_EQUILIBRIUM_NATIVE_MODULE=ON.")
endif()
if(NOT EPCSAFT_BUILD_REGRESSION_NATIVE_MODULE AND EPCSAFT_ENABLE_CERES)
    message(FATAL_ERROR "EPCSAFT_ENABLE_CERES=ON requires EPCSAFT_BUILD_REGRESSION_NATIVE_MODULE=ON.")
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

if(EPCSAFT_ENABLE_CERES AND NOT Eigen3_DIR)
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

if(EPCSAFT_ENABLE_CERES)
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
        if(CMAKE_VERSION VERSION_GREATER_EQUAL "3.28")
            FetchContent_Declare(
                ceres_solver
                GIT_REPOSITORY https://ceres-solver.googlesource.com/ceres-solver
                GIT_TAG ${EPCSAFT_CERES_VERSION}
                GIT_SHALLOW TRUE
                EXCLUDE_FROM_ALL
            )
            FetchContent_MakeAvailable(ceres_solver)
        else()
            FetchContent_Declare(
                ceres_solver
                GIT_REPOSITORY https://ceres-solver.googlesource.com/ceres-solver
                GIT_TAG ${EPCSAFT_CERES_VERSION}
                GIT_SHALLOW TRUE
            )
            FetchContent_GetProperties(ceres_solver)
            if(NOT ceres_solver_POPULATED)
                FetchContent_Populate(ceres_solver)
                add_subdirectory("${ceres_solver_SOURCE_DIR}" "${ceres_solver_BINARY_DIR}" EXCLUDE_FROM_ALL)
            endif()
        endif()
        if(TARGET ceres_internal AND CMAKE_CXX_COMPILER_ID STREQUAL "GNU")
            target_compile_options(ceres_internal PRIVATE -include cstdint)
        endif()
    endif()
endif()

set(EPCSAFT_IPOPT_STATUS "disabled")
set(EPCSAFT_IPOPT_TARGET "")
if(EPCSAFT_ENABLE_IPOPT)
    if(NOT EPCSAFT_USE_SYSTEM_IPOPT)
        message(FATAL_ERROR "EPCSAFT_ENABLE_IPOPT=ON requires EPCSAFT_USE_SYSTEM_IPOPT=ON; vendored Ipopt builds are not supported.")
    endif()
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
        if(WIN32 AND CMAKE_CXX_COMPILER_ID STREQUAL "GNU" AND EPCSAFT_IPOPT_LIBRARY MATCHES "\\.lib$")
            message(FATAL_ERROR "EPCSAFT_IPOPT_ROOT resolved to an MSVC import library, but the active compiler is GNU. Use an MSVC CMake toolchain or provide a MinGW-compatible Ipopt library.")
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
        message(FATAL_ERROR "EPCSAFT_ENABLE_IPOPT=ON requested, but native Ipopt was not found. Set Ipopt_DIR, EPCSAFT_IPOPT_ROOT, or provide pkg-config metadata for ipopt.")
    endif()
    set(EPCSAFT_IPOPT_STATUS "enabled_available")
endif()

if(EPCSAFT_USE_SYSTEM_CPPAD)
    set(EPCSAFT_ENABLE_CPPAD ON CACHE BOOL "Enable package-wide CppAD support" FORCE)
endif()

set(EPCSAFT_CPPAD_STATUS "disabled")
set(EPCSAFT_CPPAD_GENERATED_INCLUDE_DIR "")
set(EPCSAFT_CPPAD_SOURCE_FILE "")
set(EPCSAFT_CPPAD_LIBRARY "")
if(EPCSAFT_ENABLE_CPPAD)
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
        set(cppad_tape_addr_type "unsigned int")
        set(cppad_is_same_tape_addr_type_size_t 0)
        set(cppad_tape_id_type "unsigned int")
        set(cppad_max_num_threads 48)
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
        configure_file(
            "${EPCSAFT_CPPAD_INCLUDE_DIR}/cppad/configure.hpp.in"
            "${EPCSAFT_CPPAD_GENERATED_INCLUDE_DIR}/cppad/configure.hpp"
            @ONLY
        )
    endif()
    set(EPCSAFT_CPPAD_STATUS "enabled_available")
endif()

set(EPCSAFT_NATIVE_MODEL_SOURCES
    src/epcsaft/native/model/parameter_setup.cpp
)
set(EPCSAFT_NATIVE_EOS_SOURCES
    src/epcsaft/native/eos/activity.cpp
    src/epcsaft/native/eos/chemical_potential.cpp
    src/epcsaft/native/eos/compressibility.cpp
    src/epcsaft/native/eos/density.cpp
    src/epcsaft/native/eos/derivatives/born_ssmds.cpp
    src/epcsaft/native/eos/fugacity.cpp
    src/epcsaft/native/eos/pure_neutral_parameter_derivatives.cpp
    src/epcsaft/native/eos/residual_helmholtz.cpp
    src/epcsaft/native/eos/residual_properties.cpp
    src/epcsaft/native/eos/state.cpp
    src/epcsaft/native/eos/contributions/association.cpp
    src/epcsaft/native/eos/contributions/born.cpp
    src/epcsaft/native/eos/contributions/dispersion.cpp
    src/epcsaft/native/eos/contributions/hard_chain.cpp
    src/epcsaft/native/eos/contributions/ion.cpp
)
set(EPCSAFT_NATIVE_AUTODIFF_SOURCES
    src/epcsaft/native/autodiff/cppad_smoke_checks.cpp
    src/epcsaft/native/autodiff/implicit_sensitivity.cpp
)
set(
    EPCSAFT_EQUILIBRIUM_PACKAGE_ROOT
    "${CMAKE_CURRENT_SOURCE_DIR}/packages/epcsaft-equilibrium"
    CACHE PATH
    "Monorepo package directory that owns the equilibrium extension sources"
)
set(
    EPCSAFT_REGRESSION_PACKAGE_ROOT
    "${CMAKE_CURRENT_SOURCE_DIR}/packages/epcsaft-regression"
    CACHE PATH
    "Monorepo package directory that owns the regression extension sources"
)
set(EPCSAFT_EQUILIBRIUM_EXTENSION_NATIVE_ROOT "${EPCSAFT_EQUILIBRIUM_PACKAGE_ROOT}/native")
set(EPCSAFT_REGRESSION_EXTENSION_NATIVE_ROOT "${EPCSAFT_REGRESSION_PACKAGE_ROOT}/native")
set(EPCSAFT_EQUILIBRIUM_NATIVE_ROOT "${EPCSAFT_EQUILIBRIUM_EXTENSION_NATIVE_ROOT}/equilibrium")
set(EPCSAFT_REGRESSION_NATIVE_ROOT "${EPCSAFT_REGRESSION_EXTENSION_NATIVE_ROOT}/regression")
set(EPCSAFT_EQUILIBRIUM_REGISTER_BINDINGS_SOURCE "${EPCSAFT_EQUILIBRIUM_NATIVE_ROOT}/register_bindings.cpp")
if(EPCSAFT_BUILD_EQUILIBRIUM_NATIVE_MODULE AND NOT EXISTS "${EPCSAFT_EQUILIBRIUM_REGISTER_BINDINGS_SOURCE}")
    message(
        FATAL_ERROR
        "EPCSAFT_BUILD_EQUILIBRIUM_NATIVE_MODULE requires the monorepo epcsaft-equilibrium package at "
        "${EPCSAFT_EQUILIBRIUM_PACKAGE_ROOT}."
    )
endif()
if(EPCSAFT_BUILD_REGRESSION_NATIVE_MODULE AND NOT EXISTS "${EPCSAFT_REGRESSION_NATIVE_ROOT}/ceres_regression.cpp")
    message(
        FATAL_ERROR
        "EPCSAFT_BUILD_REGRESSION_NATIVE_MODULE requires the monorepo epcsaft-regression package at "
        "${EPCSAFT_REGRESSION_PACKAGE_ROOT}."
    )
endif()
set(EPCSAFT_NATIVE_EQUILIBRIUM_SOURCES
    ${EPCSAFT_EQUILIBRIUM_NATIVE_ROOT}/blocks/association_block.cpp
    ${EPCSAFT_EQUILIBRIUM_NATIVE_ROOT}/blocks/electrolyte_block.cpp
    ${EPCSAFT_EQUILIBRIUM_NATIVE_ROOT}/blocks/eos_phase_block.cpp
    ${EPCSAFT_EQUILIBRIUM_NATIVE_ROOT}/blocks/gibbs_blocks.cpp
    ${EPCSAFT_EQUILIBRIUM_NATIVE_ROOT}/blocks/reaction_block.cpp
    ${EPCSAFT_EQUILIBRIUM_NATIVE_ROOT}/core/activated_equilibrium_nlp.cpp
    ${EPCSAFT_EQUILIBRIUM_NATIVE_ROOT}/core/activation_plan.cpp
    ${EPCSAFT_EQUILIBRIUM_NATIVE_ROOT}/core/helpers.cpp
    ${EPCSAFT_EQUILIBRIUM_NATIVE_ROOT}/core/nlp_problem.cpp
    ${EPCSAFT_EQUILIBRIUM_NATIVE_ROOT}/core/selector_core.cpp
    ${EPCSAFT_EQUILIBRIUM_NATIVE_ROOT}/core/second_order.cpp
    ${EPCSAFT_EQUILIBRIUM_NATIVE_ROOT}/core/two_phase_eos_route.cpp
    ${EPCSAFT_EQUILIBRIUM_NATIVE_ROOT}/core/variable_transform.cpp
    ${EPCSAFT_EQUILIBRIUM_NATIVE_ROOT}/core/variable_layout.cpp
    ${EPCSAFT_EQUILIBRIUM_NATIVE_ROOT}/results/result_builder.cpp
    ${EPCSAFT_EQUILIBRIUM_NATIVE_ROOT}/routes/derived/bubble_dew.cpp
    ${EPCSAFT_EQUILIBRIUM_NATIVE_ROOT}/solvers/ipopt_adapter.cpp
)
set(EPCSAFT_NATIVE_REGRESSION_SOURCES
    ${EPCSAFT_REGRESSION_NATIVE_ROOT}/ceres_regression.cpp
)
set(EPCSAFT_PROVIDER_NATIVE_SOURCES
    ${EPCSAFT_NATIVE_MODEL_SOURCES}
    ${EPCSAFT_NATIVE_EOS_SOURCES}
    ${EPCSAFT_NATIVE_AUTODIFF_SOURCES}
)
if(EPCSAFT_CPPAD_SOURCE_FILE)
    list(APPEND EPCSAFT_PROVIDER_NATIVE_SOURCES "${EPCSAFT_CPPAD_SOURCE_FILE}")
endif()

set(EPCSAFT_PROVIDER_NATIVE_INCLUDE_DIRS
    "${CMAKE_CURRENT_SOURCE_DIR}/src/epcsaft/native"
    "${CMAKE_CURRENT_SOURCE_DIR}/src/epcsaft/native/autodiff"
    "${CMAKE_CURRENT_SOURCE_DIR}/src/epcsaft/native/bindings"
    "${CMAKE_CURRENT_SOURCE_DIR}/src/epcsaft/native/eos"
    "${CMAKE_CURRENT_SOURCE_DIR}/src/epcsaft/native/eos/contributions"
    "${CMAKE_CURRENT_SOURCE_DIR}/src/epcsaft/native/model"
    "${CMAKE_CURRENT_SOURCE_DIR}/src/epcsaft/native/runtime"
)
set(EPCSAFT_EQUILIBRIUM_NATIVE_INCLUDE_DIRS
    ${EPCSAFT_PROVIDER_NATIVE_INCLUDE_DIRS}
    "${EPCSAFT_EQUILIBRIUM_EXTENSION_NATIVE_ROOT}"
    "${EPCSAFT_EQUILIBRIUM_NATIVE_ROOT}"
    "${EPCSAFT_EQUILIBRIUM_NATIVE_ROOT}/blocks"
    "${EPCSAFT_EQUILIBRIUM_NATIVE_ROOT}/core"
    "${EPCSAFT_EQUILIBRIUM_NATIVE_ROOT}/results"
    "${EPCSAFT_EQUILIBRIUM_NATIVE_ROOT}/routes/derived"
    "${EPCSAFT_EQUILIBRIUM_NATIVE_ROOT}/solvers"
)
set(EPCSAFT_REGRESSION_NATIVE_INCLUDE_DIRS
    ${EPCSAFT_PROVIDER_NATIVE_INCLUDE_DIRS}
    "${EPCSAFT_REGRESSION_EXTENSION_NATIVE_ROOT}"
    "${EPCSAFT_REGRESSION_NATIVE_ROOT}"
)

add_library(epcsaft_provider_native OBJECT ${EPCSAFT_PROVIDER_NATIVE_SOURCES})
add_library(epcsaft_native INTERFACE)

set(EPCSAFT_NATIVE_OBJECT_TARGETS
    epcsaft_provider_native
)
if(EPCSAFT_BUILD_EQUILIBRIUM_NATIVE_MODULE)
    add_library(epcsaft_equilibrium_native OBJECT ${EPCSAFT_NATIVE_EQUILIBRIUM_SOURCES})
    list(APPEND EPCSAFT_NATIVE_OBJECT_TARGETS epcsaft_equilibrium_native)
endif()
if(EPCSAFT_BUILD_REGRESSION_NATIVE_MODULE)
    add_library(epcsaft_regression_native OBJECT ${EPCSAFT_NATIVE_REGRESSION_SOURCES})
    list(APPEND EPCSAFT_NATIVE_OBJECT_TARGETS epcsaft_regression_native)
endif()
target_link_libraries(epcsaft_native INTERFACE epcsaft_provider_native)

target_include_directories(epcsaft_provider_native
    PUBLIC
        ${EPCSAFT_PROVIDER_NATIVE_INCLUDE_DIRS}
        "${EPCSAFT_EIGEN_INCLUDE}"
)
if(EPCSAFT_BUILD_EQUILIBRIUM_NATIVE_MODULE)
    target_include_directories(epcsaft_equilibrium_native
        PUBLIC
            ${EPCSAFT_EQUILIBRIUM_NATIVE_INCLUDE_DIRS}
            "${EPCSAFT_EIGEN_INCLUDE}"
    )
endif()
if(EPCSAFT_BUILD_REGRESSION_NATIVE_MODULE)
    target_include_directories(epcsaft_regression_native
        PUBLIC
            ${EPCSAFT_REGRESSION_NATIVE_INCLUDE_DIRS}
            "${EPCSAFT_EIGEN_INCLUDE}"
    )
endif()
foreach(target_name IN LISTS EPCSAFT_NATIVE_OBJECT_TARGETS)
    target_compile_features(${target_name} PUBLIC cxx_std_17)
    set_target_properties(${target_name} PROPERTIES POSITION_INDEPENDENT_CODE ON)
endforeach()

if(EPCSAFT_BUILD_EQUILIBRIUM_NATIVE_MODULE)
    target_link_libraries(epcsaft_equilibrium_native PUBLIC epcsaft_provider_native)
    if(EPCSAFT_ENABLE_IPOPT)
        target_link_libraries(epcsaft_equilibrium_native PUBLIC "${EPCSAFT_IPOPT_TARGET}")
        target_compile_definitions(epcsaft_equilibrium_native PUBLIC EPCSAFT_HAS_IPOPT=1)
    endif()
endif()
if(EPCSAFT_BUILD_REGRESSION_NATIVE_MODULE)
    target_link_libraries(epcsaft_regression_native PUBLIC epcsaft_provider_native)
    if(EPCSAFT_ENABLE_CERES)
        target_link_libraries(epcsaft_regression_native PUBLIC Ceres::ceres)
        target_compile_definitions(epcsaft_regression_native PUBLIC EPCSAFT_HAS_CERES=1)
    endif()
endif()
if(EPCSAFT_CPPAD_LIBRARY)
    target_link_libraries(epcsaft_provider_native PUBLIC "${EPCSAFT_CPPAD_LIBRARY}")
endif()

set(EPCSAFT_PYBIND_SOURCES
    src/epcsaft/native/bindings/module.cpp
)
pybind11_add_module(_core NO_EXTRAS ${EPCSAFT_PYBIND_SOURCES})
target_link_libraries(
    _core
    PRIVATE
        epcsaft_provider_native
)
target_include_directories(_core
    PRIVATE
        ${EPCSAFT_PROVIDER_NATIVE_INCLUDE_DIRS}
        "${EPCSAFT_EIGEN_INCLUDE}"
)
target_compile_features(_core PRIVATE cxx_std_17)
if(MSVC)
    set_source_files_properties(
        src/epcsaft/native/bindings/module.cpp
        PROPERTIES COMPILE_OPTIONS "/Od;/Ob0"
    )
endif()

set(EPCSAFT_NATIVE_TARGETS
    ${EPCSAFT_NATIVE_OBJECT_TARGETS}
    _core
)

if(EPCSAFT_BUILD_EQUILIBRIUM_NATIVE_MODULE)
    pybind11_add_module(
        epcsaft_equilibrium_native_core
        NO_EXTRAS
        "${EPCSAFT_EQUILIBRIUM_NATIVE_ROOT}/module.cpp"
        "${EPCSAFT_EQUILIBRIUM_REGISTER_BINDINGS_SOURCE}"
    )
    set_target_properties(
        epcsaft_equilibrium_native_core
        PROPERTIES
            OUTPUT_NAME "_native_core"
            LIBRARY_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/epcsaft_equilibrium"
            RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/epcsaft_equilibrium"
    )
    target_link_libraries(
        epcsaft_equilibrium_native_core
        PRIVATE
            epcsaft_provider_native
            epcsaft_equilibrium_native
    )
    target_include_directories(epcsaft_equilibrium_native_core
        PRIVATE
            ${EPCSAFT_EQUILIBRIUM_NATIVE_INCLUDE_DIRS}
            "${EPCSAFT_EIGEN_INCLUDE}"
    )
    target_compile_features(epcsaft_equilibrium_native_core PRIVATE cxx_std_17)
    if(EPCSAFT_ENABLE_IPOPT)
        target_compile_definitions(epcsaft_equilibrium_native_core PRIVATE EPCSAFT_HAS_IPOPT=1)
    endif()
    list(APPEND EPCSAFT_NATIVE_TARGETS epcsaft_equilibrium_native_core)
    if(MSVC)
        set_source_files_properties(
            "${EPCSAFT_EQUILIBRIUM_NATIVE_ROOT}/module.cpp"
            "${EPCSAFT_EQUILIBRIUM_REGISTER_BINDINGS_SOURCE}"
            PROPERTIES COMPILE_OPTIONS "/Od;/Ob0"
        )
    endif()
endif()

if(EPCSAFT_BUILD_REGRESSION_NATIVE_MODULE)
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
    )
    target_link_libraries(
        epcsaft_regression_native_core
        PRIVATE
            epcsaft_provider_native
            epcsaft_regression_native
    )
    target_include_directories(epcsaft_regression_native_core
        PRIVATE
            ${EPCSAFT_REGRESSION_NATIVE_INCLUDE_DIRS}
            "${EPCSAFT_EIGEN_INCLUDE}"
    )
    target_compile_features(epcsaft_regression_native_core PRIVATE cxx_std_17)
    if(EPCSAFT_ENABLE_CERES)
        target_link_libraries(epcsaft_regression_native_core PRIVATE Ceres::ceres)
        target_compile_definitions(epcsaft_regression_native_core PRIVATE EPCSAFT_HAS_CERES=1 EPCSAFT_HAS_REGRESSION_NATIVE=1)
    endif()
    list(APPEND EPCSAFT_NATIVE_TARGETS epcsaft_regression_native_core)
    if(MSVC)
        set_source_files_properties(
            "${EPCSAFT_REGRESSION_NATIVE_ROOT}/module.cpp"
            PROPERTIES COMPILE_OPTIONS "/Od;/Ob0"
        )
    endif()
endif()

foreach(target_name IN LISTS EPCSAFT_NATIVE_TARGETS)
    target_compile_definitions(
        ${target_name}
        PRIVATE
            EPCSAFT_CPPAD_STATUS="${EPCSAFT_CPPAD_STATUS}"
            EPCSAFT_IPOPT_STATUS="${EPCSAFT_IPOPT_STATUS}"
    )
    if(EPCSAFT_ENABLE_CPPAD)
        if(EPCSAFT_CPPAD_GENERATED_INCLUDE_DIR)
            target_include_directories(${target_name} SYSTEM PRIVATE "${EPCSAFT_CPPAD_GENERATED_INCLUDE_DIR}")
        endif()
        target_include_directories(${target_name} SYSTEM PRIVATE "${EPCSAFT_CPPAD_INCLUDE_DIR}")
        target_compile_definitions(${target_name} PRIVATE EPCSAFT_HAS_CPPAD=1)
    endif()
endforeach()

foreach(target_name IN LISTS EPCSAFT_NATIVE_TARGETS)
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
        if(EPCSAFT_ENABLE_SANITIZERS AND CMAKE_BUILD_TYPE MATCHES "Debug")
            target_compile_options(${target_name} PRIVATE -fsanitize=address,undefined -fno-omit-frame-pointer)
        endif()
    endif()
endforeach()

if(EPCSAFT_ENABLE_SANITIZERS AND CMAKE_BUILD_TYPE MATCHES "Debug")
    target_link_options(_core PRIVATE -fsanitize=address,undefined)
    if(EPCSAFT_BUILD_EQUILIBRIUM_NATIVE_MODULE)
        target_link_options(epcsaft_equilibrium_native_core PRIVATE -fsanitize=address,undefined)
    endif()
    if(EPCSAFT_BUILD_REGRESSION_NATIVE_MODULE)
        target_link_options(epcsaft_regression_native_core PRIVATE -fsanitize=address,undefined)
    endif()
endif()

if(EPCSAFT_ENABLE_SANITIZERS AND MSVC)
    message(WARNING "EPCSAFT_ENABLE_SANITIZERS is currently only configured for GNU/Clang debug builds.")
endif()

if(WIN32 AND CMAKE_CXX_COMPILER_ID STREQUAL "GNU")
    foreach(target_name IN LISTS EPCSAFT_NATIVE_OBJECT_TARGETS)
        target_compile_options(${target_name} PRIVATE -Wa,-mbig-obj)
    endforeach()
    target_compile_options(_core PRIVATE -Wa,-mbig-obj)
    target_link_options(_core PRIVATE -static -static-libgcc -static-libstdc++)
endif()

install(TARGETS _core
    LIBRARY DESTINATION epcsaft
    RUNTIME DESTINATION epcsaft
)
if(EPCSAFT_BUILD_EQUILIBRIUM_NATIVE_MODULE)
    install(TARGETS epcsaft_equilibrium_native_core
        LIBRARY DESTINATION epcsaft_equilibrium
        RUNTIME DESTINATION epcsaft_equilibrium
    )
endif()
if(EPCSAFT_BUILD_REGRESSION_NATIVE_MODULE)
    install(TARGETS epcsaft_regression_native_core
        LIBRARY DESTINATION epcsaft_regression
        RUNTIME DESTINATION epcsaft_regression
    )
endif()

if(EPCSAFT_DEV_INPLACE)
    add_custom_command(TARGET _core POST_BUILD
        COMMAND ${CMAKE_COMMAND} -E make_directory "${CMAKE_CURRENT_SOURCE_DIR}/src/epcsaft"
        COMMAND ${CMAKE_COMMAND} -E copy_if_different
            "$<TARGET_FILE:_core>"
            "${CMAKE_CURRENT_SOURCE_DIR}/src/epcsaft/$<TARGET_FILE_NAME:_core>"
        VERBATIM
    )
    if(EPCSAFT_BUILD_EQUILIBRIUM_NATIVE_MODULE)
        add_custom_command(TARGET epcsaft_equilibrium_native_core POST_BUILD
            COMMAND ${CMAKE_COMMAND} -E make_directory "${CMAKE_CURRENT_SOURCE_DIR}/packages/epcsaft-equilibrium/src/epcsaft_equilibrium"
            COMMAND ${CMAKE_COMMAND} -E copy_if_different
                "$<TARGET_FILE:epcsaft_equilibrium_native_core>"
                "${CMAKE_CURRENT_SOURCE_DIR}/packages/epcsaft-equilibrium/src/epcsaft_equilibrium/$<TARGET_FILE_NAME:epcsaft_equilibrium_native_core>"
            VERBATIM
        )
    endif()
    if(EPCSAFT_BUILD_REGRESSION_NATIVE_MODULE)
        add_custom_command(TARGET epcsaft_regression_native_core POST_BUILD
            COMMAND ${CMAKE_COMMAND} -E make_directory "${CMAKE_CURRENT_SOURCE_DIR}/packages/epcsaft-regression/src/epcsaft_regression"
            COMMAND ${CMAKE_COMMAND} -E copy_if_different
                "$<TARGET_FILE:epcsaft_regression_native_core>"
                "${CMAKE_CURRENT_SOURCE_DIR}/packages/epcsaft-regression/src/epcsaft_regression/$<TARGET_FILE_NAME:epcsaft_regression_native_core>"
            VERBATIM
        )
    endif()
endif()
