include_guard(GLOBAL)

get_filename_component(EPCSAFT_PROVIDER_SDK_PACKAGE_ROOT "${CMAKE_CURRENT_LIST_DIR}/../.." ABSOLUTE)
set(EPCSAFT_PROVIDER_NATIVE_ROOT "${EPCSAFT_PROVIDER_SDK_PACKAGE_ROOT}/native")

if(NOT EXISTS "${EPCSAFT_PROVIDER_NATIVE_ROOT}/bindings/module.cpp")
    message(FATAL_ERROR "Provider native SDK could not locate epcsaft provider native sources at ${EPCSAFT_PROVIDER_NATIVE_ROOT}.")
endif()

function(
    _epcsaft_provider_sdk_manifest_paths
    manifest_json
    manifest_key
    package_root
    output_variable
)
    string(JSON entry_count ERROR_VARIABLE json_error LENGTH "${manifest_json}" "${manifest_key}")
    if(json_error)
        message(FATAL_ERROR "Provider native source manifest is missing '${manifest_key}': ${json_error}")
    endif()
    if(entry_count LESS 1)
        message(FATAL_ERROR "Provider native source manifest '${manifest_key}' must not be empty.")
    endif()

    math(EXPR last_entry "${entry_count} - 1")
    set(absolute_paths "")
    set(relative_paths "")
    foreach(entry_index RANGE 0 ${last_entry})
        string(JSON relative_path GET "${manifest_json}" "${manifest_key}" ${entry_index})
        if(relative_path STREQUAL "" OR IS_ABSOLUTE "${relative_path}" OR relative_path MATCHES "(^|/)\\.\\.(/|$)")
            message(FATAL_ERROR "Provider native source manifest path must be a nonempty package-relative path: ${relative_path}")
        endif()
        set(absolute_path "${package_root}/${relative_path}")
        if(NOT EXISTS "${absolute_path}")
            message(FATAL_ERROR "Provider native source manifest entry does not exist: ${absolute_path}")
        endif()
        if(manifest_key STREQUAL "sources")
            if(IS_DIRECTORY "${absolute_path}")
                message(FATAL_ERROR "Provider native source manifest 'sources' entries must be existing files: ${absolute_path}")
            endif()
        endif()
        if(manifest_key STREQUAL "include_dirs")
            if(NOT IS_DIRECTORY "${absolute_path}")
                message(FATAL_ERROR "Provider native source manifest 'include_dirs' entries must be existing directories: ${absolute_path}")
            endif()
        endif()
        list(APPEND relative_paths "${relative_path}")
        list(APPEND absolute_paths "${absolute_path}")
    endforeach()
    list(LENGTH relative_paths relative_path_count)
    list(REMOVE_DUPLICATES relative_paths)
    list(LENGTH relative_paths unique_relative_path_count)
    if(NOT relative_path_count EQUAL unique_relative_path_count)
        message(FATAL_ERROR "Provider native source manifest '${manifest_key}' entries must be unique.")
    endif()
    set(${output_variable} "${absolute_paths}" PARENT_SCOPE)
endfunction()

function(
    epcsaft_provider_sdk_load_source_manifest
    provider_package_root
    sources_output
    include_dirs_output
)
    set(manifest_path "${provider_package_root}/native_sdk/provider_native_sdk_v1/provider_sources.json")
    if(NOT EXISTS "${manifest_path}")
        message(FATAL_ERROR "Provider native source manifest does not exist: ${manifest_path}")
    endif()
    set_property(DIRECTORY APPEND PROPERTY CMAKE_CONFIGURE_DEPENDS "${manifest_path}")
    file(READ "${manifest_path}" manifest_json)
    string(JSON contract_id ERROR_VARIABLE contract_error GET "${manifest_json}" contract_id)
    if(contract_error OR NOT contract_id STREQUAL "provider_native_sdk_v1")
        message(FATAL_ERROR "Provider native source manifest requires contract_id 'provider_native_sdk_v1': ${contract_error}")
    endif()

    _epcsaft_provider_sdk_manifest_paths(
        "${manifest_json}" sources "${provider_package_root}" provider_sources
    )
    _epcsaft_provider_sdk_manifest_paths(
        "${manifest_json}" include_dirs "${provider_package_root}" provider_include_dirs
    )

    set(${sources_output} "${provider_sources}" PARENT_SCOPE)
    set(${include_dirs_output} "${provider_include_dirs}" PARENT_SCOPE)
endfunction()

epcsaft_provider_sdk_load_source_manifest(
    "${EPCSAFT_PROVIDER_SDK_PACKAGE_ROOT}"
    EPCSAFT_PROVIDER_NATIVE_SOURCES
    EPCSAFT_PROVIDER_NATIVE_INCLUDE_DIRS
)
set(EPCSAFT_PROVIDER_NATIVE_TARGET_SOURCES ${EPCSAFT_PROVIDER_NATIVE_SOURCES})
if(DEFINED EPCSAFT_CPPAD_SOURCE_FILE AND EPCSAFT_CPPAD_SOURCE_FILE)
    list(APPEND EPCSAFT_PROVIDER_NATIVE_TARGET_SOURCES "${EPCSAFT_CPPAD_SOURCE_FILE}")
endif()

function(epcsaft_provider_sdk_add_provider_native target_name)
    if(TARGET "${target_name}")
        return()
    endif()
    if(NOT DEFINED EPCSAFT_EIGEN_INCLUDE OR NOT EXISTS "${EPCSAFT_EIGEN_INCLUDE}")
        message(FATAL_ERROR "EPCSAFT_EIGEN_INCLUDE must point at the Eigen include root before adding ${target_name}.")
    endif()

    add_library("${target_name}" OBJECT ${EPCSAFT_PROVIDER_NATIVE_TARGET_SOURCES})
    target_include_directories("${target_name}"
        PUBLIC
            ${EPCSAFT_PROVIDER_NATIVE_INCLUDE_DIRS}
            "${EPCSAFT_EIGEN_INCLUDE}"
    )
    target_compile_features("${target_name}" PUBLIC cxx_std_17)
    set_target_properties("${target_name}" PROPERTIES POSITION_INDEPENDENT_CODE ON)

    if(DEFINED EPCSAFT_CPPAD_LIBRARY AND EPCSAFT_CPPAD_LIBRARY)
        target_link_libraries("${target_name}" PUBLIC "${EPCSAFT_CPPAD_LIBRARY}")
    endif()
    if(DEFINED EPCSAFT_CPPAD_GENERATED_INCLUDE_DIR AND EPCSAFT_CPPAD_GENERATED_INCLUDE_DIR)
        target_include_directories("${target_name}" SYSTEM PUBLIC "${EPCSAFT_CPPAD_GENERATED_INCLUDE_DIR}")
    endif()
    if(DEFINED EPCSAFT_CPPAD_INCLUDE_DIR AND EPCSAFT_CPPAD_INCLUDE_DIR)
        target_include_directories("${target_name}" SYSTEM PUBLIC "${EPCSAFT_CPPAD_INCLUDE_DIR}")
        target_compile_definitions("${target_name}" PUBLIC EPCSAFT_HAS_CPPAD=1)
    endif()
endfunction()
