include_guard(GLOBAL)

function(
    _epcsaft_equilibrium_manifest_paths
    manifest_json
    manifest_key
    native_root
    output_variable
)
    string(JSON entry_count ERROR_VARIABLE json_error LENGTH "${manifest_json}" "${manifest_key}")
    if(json_error)
        message(FATAL_ERROR "Equilibrium native source manifest is missing '${manifest_key}': ${json_error}")
    endif()
    if(entry_count LESS 1)
        message(FATAL_ERROR "Equilibrium native source manifest '${manifest_key}' must not be empty.")
    endif()

    math(EXPR last_entry "${entry_count} - 1")
    set(absolute_paths "")
    foreach(entry_index RANGE 0 ${last_entry})
        string(JSON relative_path GET "${manifest_json}" "${manifest_key}" ${entry_index})
        if(relative_path STREQUAL "" OR IS_ABSOLUTE "${relative_path}" OR relative_path MATCHES "(^|/)\\.\\.(/|$)")
            message(FATAL_ERROR "Equilibrium native source manifest path must be a nonempty package-relative path: ${relative_path}")
        endif()
        set(absolute_path "${native_root}/${relative_path}")
        if(NOT EXISTS "${absolute_path}")
            message(FATAL_ERROR "Equilibrium native source manifest entry does not exist: ${absolute_path}")
        endif()
        if(IS_DIRECTORY "${absolute_path}")
            message(FATAL_ERROR "Equilibrium native source manifest entries must be existing files: ${absolute_path}")
        endif()
        list(APPEND absolute_paths "${absolute_path}")
    endforeach()
    set(${output_variable} "${absolute_paths}" PARENT_SCOPE)
endfunction()

function(
    epcsaft_equilibrium_load_native_source_manifest
    equilibrium_package_root
    object_sources_output
    module_sources_output
    identity_files_output
)
    set(manifest_path "${equilibrium_package_root}/cmake/equilibrium_native_sources.json")
    if(NOT EXISTS "${manifest_path}")
        message(FATAL_ERROR "Equilibrium native source manifest does not exist: ${manifest_path}")
    endif()
    file(READ "${manifest_path}" manifest_json)
    string(JSON schema_version ERROR_VARIABLE schema_error GET "${manifest_json}" schema_version)
    if(schema_error OR NOT schema_version EQUAL 1)
        message(FATAL_ERROR "Equilibrium native source manifest requires schema_version 1: ${schema_error}")
    endif()

    set(native_root "${equilibrium_package_root}/src/epcsaft_equilibrium/native/equilibrium")
    _epcsaft_equilibrium_manifest_paths(
        "${manifest_json}" object_sources "${native_root}" object_sources
    )
    _epcsaft_equilibrium_manifest_paths(
        "${manifest_json}" module_sources "${native_root}" module_sources
    )
    _epcsaft_equilibrium_manifest_paths(
        "${manifest_json}" headers "${native_root}" header_files
    )
    set(identity_files ${object_sources} ${module_sources} ${header_files})
    list(LENGTH identity_files identity_file_count)
    list(REMOVE_DUPLICATES identity_files)
    list(LENGTH identity_files unique_identity_file_count)
    if(NOT identity_file_count EQUAL unique_identity_file_count)
        message(FATAL_ERROR "Equilibrium native source manifest entries must be unique.")
    endif()

    set(${object_sources_output} "${object_sources}" PARENT_SCOPE)
    set(${module_sources_output} "${module_sources}" PARENT_SCOPE)
    set(${identity_files_output} "${identity_files}" PARENT_SCOPE)
endfunction()

function(
    epcsaft_equilibrium_apply_native_source_identity
    target_name
    equilibrium_package_root
    provider_package_root
)
    if(NOT TARGET "${target_name}")
        message(FATAL_ERROR "Native source identity target does not exist: ${target_name}")
    endif()

    set(identity_algorithm "sha256-relative-path-content-v1")
    set(identity_scope "equilibrium-explicit-source-manifest-and-provider-manifest-driven-target-graph")
    set(
        identity_limit
        "Covers the canonical equilibrium object/module/header manifest, every listed equilibrium file, this shared CMake loader/identity helper, the provider source manifest contract, the exact manifest-listed provider target .cpp files, and the .h/.hpp header contracts reachable from manifest include roots. Root/standalone target compile definitions, include/link flags, compiler identity, generated dependency sources, and dependency binaries are outside this source receipt."
    )
    include("${provider_package_root}/native_sdk/provider_native_sdk_v1/epcsaft_provider_sdk.cmake")

    epcsaft_equilibrium_load_native_source_manifest(
        "${equilibrium_package_root}"
        equilibrium_object_sources
        equilibrium_module_sources
        equilibrium_identity_files
    )
    epcsaft_provider_sdk_load_source_manifest(
        "${provider_package_root}"
        provider_identity_sources
        provider_identity_include_dirs
    )
    set(identity_entries
        "equilibrium/cmake/EquilibriumNativeSourceIdentity.cmake|${equilibrium_package_root}/cmake/EquilibriumNativeSourceIdentity.cmake"
        "equilibrium/cmake/equilibrium_native_sources.json|${equilibrium_package_root}/cmake/equilibrium_native_sources.json"
        "provider/native_sdk/provider_native_sdk_v1/epcsaft_provider_sdk.cmake|${provider_package_root}/native_sdk/provider_native_sdk_v1/epcsaft_provider_sdk.cmake"
        "provider/native_sdk/provider_native_sdk_v1/provider_sources.json|${provider_package_root}/native_sdk/provider_native_sdk_v1/provider_sources.json"
    )
    foreach(absolute_path IN LISTS equilibrium_identity_files)
        file(RELATIVE_PATH relative_path "${equilibrium_package_root}" "${absolute_path}")
        list(
            APPEND identity_entries
            "equilibrium/${relative_path}|${absolute_path}"
        )
    endforeach()
    foreach(absolute_path IN LISTS provider_identity_sources)
        file(RELATIVE_PATH relative_path "${provider_package_root}" "${absolute_path}")
        list(
            APPEND identity_entries
            "provider/${relative_path}|${absolute_path}"
        )
    endforeach()
    set(provider_identity_headers "")
    foreach(include_dir IN LISTS provider_identity_include_dirs)
        file(
            GLOB_RECURSE include_headers
            CONFIGURE_DEPENDS
            RELATIVE "${provider_package_root}"
            "${include_dir}/*.h"
            "${include_dir}/*.hpp"
        )
        list(APPEND provider_identity_headers ${include_headers})
    endforeach()
    list(REMOVE_DUPLICATES provider_identity_headers)
    list(SORT provider_identity_headers)
    foreach(relative_path IN LISTS provider_identity_headers)
        list(
            APPEND identity_entries
            "provider/${relative_path}|${provider_package_root}/${relative_path}"
        )
    endforeach()
    list(SORT identity_entries)

    set(identity_input "")
    set(identity_dependencies "")
    foreach(identity_entry IN LISTS identity_entries)
        string(REPLACE "|" ";" identity_parts "${identity_entry}")
        list(GET identity_parts 0 logical_path)
        list(GET identity_parts 1 absolute_path)
        list(APPEND identity_dependencies "${absolute_path}")
        file(SHA256 "${absolute_path}" file_hash)
        string(APPEND identity_input "${logical_path}:${file_hash}\n")
    endforeach()
    set_property(DIRECTORY APPEND PROPERTY CMAKE_CONFIGURE_DEPENDS ${identity_dependencies})
    string(SHA256 source_identity "${identity_input}")
    list(LENGTH identity_entries source_file_count)

    set_property(
        TARGET "${target_name}"
        PROPERTY EPCSAFT_EQUILIBRIUM_NATIVE_SOURCE_IDENTITY "${source_identity}"
    )
    set_property(
        TARGET "${target_name}"
        PROPERTY EPCSAFT_EQUILIBRIUM_NATIVE_SOURCE_FILE_COUNT "${source_file_count}"
    )
    set_property(
        TARGET "${target_name}"
        PROPERTY EPCSAFT_EQUILIBRIUM_NATIVE_SOURCE_IDENTITY_ALGORITHM "${identity_algorithm}"
    )
    set_property(
        TARGET "${target_name}"
        PROPERTY EPCSAFT_EQUILIBRIUM_NATIVE_SOURCE_IDENTITY_SCOPE "${identity_scope}"
    )

    target_compile_definitions(
        "${target_name}"
        PRIVATE
            EPCSAFT_EQUILIBRIUM_NATIVE_SOURCE_IDENTITY="${source_identity}"
            EPCSAFT_EQUILIBRIUM_NATIVE_SOURCE_FILE_COUNT=${source_file_count}
            EPCSAFT_EQUILIBRIUM_NATIVE_SOURCE_IDENTITY_ALGORITHM="${identity_algorithm}"
            EPCSAFT_EQUILIBRIUM_NATIVE_SOURCE_IDENTITY_SCOPE="${identity_scope}"
            EPCSAFT_EQUILIBRIUM_NATIVE_SOURCE_IDENTITY_LIMIT="${identity_limit}"
    )
endfunction()
