cmake_minimum_required(VERSION 3.20...4.2)

if(NOT DEFINED SKBUILD_PROJECT_NAME)
    set(SKBUILD_PROJECT_NAME epcsaft)
endif()
if(NOT DEFINED SKBUILD_PROJECT_VERSION)
    file(READ "${CMAKE_CURRENT_SOURCE_DIR}/pyproject.toml" EPCSAFT_PYPROJECT_TOML)
    string(REGEX MATCH "version[ \t]*=[ \t]*\"([^\"]+)\"" EPCSAFT_VERSION_MATCH "${EPCSAFT_PYPROJECT_TOML}")
    if(NOT CMAKE_MATCH_1)
        message(FATAL_ERROR "Could not derive SKBUILD_PROJECT_VERSION from packages/epcsaft/pyproject.toml")
    endif()
    set(SKBUILD_PROJECT_VERSION "${CMAKE_MATCH_1}")
endif()

project(${SKBUILD_PROJECT_NAME}
    VERSION ${SKBUILD_PROJECT_VERSION}
    LANGUAGES CXX
)

option(EPCSAFT_ENABLE_CPPAD "Enable package-wide CppAD support" ON)
option(EPCSAFT_USE_SYSTEM_CPPAD "Use installed CppAD instead of FetchContent" OFF)
option(EPCSAFT_ENABLE_CERES "Enable Ceres Solver support for native regression solves" OFF)
option(EPCSAFT_ENABLE_IPOPT "Enable native Ipopt support for production equilibrium NLP solves" OFF)
option(EPCSAFT_USE_SYSTEM_IPOPT "Use an installed Ipopt package for native equilibrium NLP solves" OFF)
set(EPCSAFT_IPOPT_ROOT "" CACHE PATH "Root directory for an installed Ipopt tree with include/, lib/, and bin/")
option(EPCSAFT_BUILD_EQUILIBRIUM_NATIVE_MODULE "Build the epcsaft-equilibrium package-owned native module" OFF)
option(EPCSAFT_BUILD_REGRESSION_NATIVE_MODULE "Build the epcsaft-regression package-owned native module" OFF)
option(EPCSAFT_WARNINGS_AS_ERRORS "Treat native warnings as errors" OFF)

if(NOT EPCSAFT_ENABLE_CPPAD)
    message(FATAL_ERROR "EPCSAFT_ENABLE_CPPAD=OFF is invalid; derivative-capable provider builds require CppAD.")
endif()
if(EPCSAFT_ENABLE_CERES)
    message(FATAL_ERROR "Provider package builds must keep EPCSAFT_ENABLE_CERES=OFF; regression native builds belong to epcsaft-regression.")
endif()
if(EPCSAFT_ENABLE_IPOPT)
    message(FATAL_ERROR "Provider package builds must keep EPCSAFT_ENABLE_IPOPT=OFF; equilibrium native builds belong to epcsaft-equilibrium.")
endif()
if(EPCSAFT_BUILD_EQUILIBRIUM_NATIVE_MODULE)
    message(FATAL_ERROR "Provider package builds must keep EPCSAFT_BUILD_EQUILIBRIUM_NATIVE_MODULE=OFF.")
endif()
if(EPCSAFT_BUILD_REGRESSION_NATIVE_MODULE)
    message(FATAL_ERROR "Provider package builds must keep EPCSAFT_BUILD_REGRESSION_NATIVE_MODULE=OFF.")
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
set(EPCSAFT_CPPAD_INCLUDE_DIR "")
set(EPCSAFT_CPPAD_LIBRARY "")
set(EPCSAFT_CPPAD_SOURCE_FILE "")
set(EPCSAFT_CPPAD_GENERATED_INCLUDE_DIR "")
if(EPCSAFT_ENABLE_CPPAD)
    if(EPCSAFT_USE_SYSTEM_CPPAD)
        find_package(CppAD CONFIG REQUIRED)
        if(TARGET CppAD::cppad_lib)
            set(EPCSAFT_CPPAD_LIBRARY CppAD::cppad_lib)
        endif()
        get_target_property(EPCSAFT_CPPAD_INCLUDE_DIR CppAD::cppad INTERFACE_INCLUDE_DIRECTORIES)
        set(EPCSAFT_CPPAD_STATUS "enabled_available")
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
endif()

set(EPCSAFT_PROVIDER_SOURCE_ROOT "${CMAKE_CURRENT_SOURCE_DIR}/src/epcsaft")
set(EPCSAFT_PROVIDER_NATIVE_ROOT "${EPCSAFT_PROVIDER_SOURCE_ROOT}/native")
set(EPCSAFT_PROVIDER_NATIVE_SOURCES
    ${EPCSAFT_PROVIDER_NATIVE_ROOT}/model/parameter_setup.cpp
    ${EPCSAFT_PROVIDER_NATIVE_ROOT}/eos/activity.cpp
    ${EPCSAFT_PROVIDER_NATIVE_ROOT}/eos/chemical_potential.cpp
    ${EPCSAFT_PROVIDER_NATIVE_ROOT}/eos/compressibility.cpp
    ${EPCSAFT_PROVIDER_NATIVE_ROOT}/eos/density.cpp
    ${EPCSAFT_PROVIDER_NATIVE_ROOT}/eos/derivatives/born_ssmds.cpp
    ${EPCSAFT_PROVIDER_NATIVE_ROOT}/eos/fugacity.cpp
    ${EPCSAFT_PROVIDER_NATIVE_ROOT}/eos/pure_neutral_parameter_derivatives.cpp
    ${EPCSAFT_PROVIDER_NATIVE_ROOT}/eos/residual_helmholtz.cpp
    ${EPCSAFT_PROVIDER_NATIVE_ROOT}/eos/residual_properties.cpp
    ${EPCSAFT_PROVIDER_NATIVE_ROOT}/eos/state.cpp
    ${EPCSAFT_PROVIDER_NATIVE_ROOT}/eos/contributions/association.cpp
    ${EPCSAFT_PROVIDER_NATIVE_ROOT}/eos/contributions/born.cpp
    ${EPCSAFT_PROVIDER_NATIVE_ROOT}/eos/contributions/dispersion.cpp
    ${EPCSAFT_PROVIDER_NATIVE_ROOT}/eos/contributions/hard_chain.cpp
    ${EPCSAFT_PROVIDER_NATIVE_ROOT}/eos/contributions/ion.cpp
    ${EPCSAFT_PROVIDER_NATIVE_ROOT}/autodiff/cppad_smoke_checks.cpp
    ${EPCSAFT_PROVIDER_NATIVE_ROOT}/autodiff/implicit_sensitivity.cpp
)
if(EPCSAFT_CPPAD_SOURCE_FILE)
    list(APPEND EPCSAFT_PROVIDER_NATIVE_SOURCES "${EPCSAFT_CPPAD_SOURCE_FILE}")
endif()

set(EPCSAFT_PROVIDER_NATIVE_INCLUDE_DIRS
    "${EPCSAFT_PROVIDER_NATIVE_ROOT}"
    "${EPCSAFT_PROVIDER_NATIVE_ROOT}/autodiff"
    "${EPCSAFT_PROVIDER_NATIVE_ROOT}/bindings"
    "${EPCSAFT_PROVIDER_NATIVE_ROOT}/eos"
    "${EPCSAFT_PROVIDER_NATIVE_ROOT}/eos/contributions"
    "${EPCSAFT_PROVIDER_NATIVE_ROOT}/model"
)

add_library(epcsaft_provider_native OBJECT ${EPCSAFT_PROVIDER_NATIVE_SOURCES})
target_include_directories(epcsaft_provider_native
    PUBLIC
        ${EPCSAFT_PROVIDER_NATIVE_INCLUDE_DIRS}
        "${EPCSAFT_EIGEN_INCLUDE}"
)
target_compile_features(epcsaft_provider_native PUBLIC cxx_std_17)
set_target_properties(epcsaft_provider_native PROPERTIES POSITION_INDEPENDENT_CODE ON)
if(EPCSAFT_CPPAD_LIBRARY)
    target_link_libraries(epcsaft_provider_native PUBLIC "${EPCSAFT_CPPAD_LIBRARY}")
endif()

pybind11_add_module(_core NO_EXTRAS "${EPCSAFT_PROVIDER_NATIVE_ROOT}/bindings/module.cpp")
target_link_libraries(_core PRIVATE epcsaft_provider_native)
target_include_directories(_core
    PRIVATE
        ${EPCSAFT_PROVIDER_NATIVE_INCLUDE_DIRS}
        "${EPCSAFT_EIGEN_INCLUDE}"
)
target_compile_features(_core PRIVATE cxx_std_17)
if(MSVC)
    set_source_files_properties(
        "${EPCSAFT_PROVIDER_NATIVE_ROOT}/bindings/module.cpp"
        PROPERTIES COMPILE_OPTIONS "/Od;/Ob0"
    )
endif()

set(EPCSAFT_NATIVE_TARGETS epcsaft_provider_native _core)
foreach(target_name IN LISTS EPCSAFT_NATIVE_TARGETS)
    target_compile_definitions(
        ${target_name}
        PRIVATE
            EPCSAFT_CPPAD_STATUS="${EPCSAFT_CPPAD_STATUS}"
            EPCSAFT_IPOPT_STATUS="disabled"
    )
    if(EPCSAFT_ENABLE_CPPAD)
        if(EPCSAFT_CPPAD_GENERATED_INCLUDE_DIR)
            target_include_directories(${target_name} SYSTEM PRIVATE "${EPCSAFT_CPPAD_GENERATED_INCLUDE_DIR}")
        endif()
        target_include_directories(${target_name} SYSTEM PRIVATE "${EPCSAFT_CPPAD_INCLUDE_DIR}")
        target_compile_definitions(${target_name} PRIVATE EPCSAFT_HAS_CPPAD=1)
    endif()
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

if(WIN32 AND CMAKE_CXX_COMPILER_ID STREQUAL "GNU")
    target_compile_options(epcsaft_provider_native PRIVATE -Wa,-mbig-obj)
    target_compile_options(_core PRIVATE -Wa,-mbig-obj)
    target_link_options(_core PRIVATE -static -static-libgcc -static-libstdc++)
endif()

install(TARGETS _core
    LIBRARY DESTINATION epcsaft
    RUNTIME DESTINATION epcsaft
)
