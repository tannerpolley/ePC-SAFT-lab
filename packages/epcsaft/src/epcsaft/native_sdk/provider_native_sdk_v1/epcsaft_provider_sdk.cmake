include_guard(GLOBAL)

get_filename_component(EPCSAFT_PROVIDER_SDK_PACKAGE_ROOT "${CMAKE_CURRENT_LIST_DIR}/../.." ABSOLUTE)
set(EPCSAFT_PROVIDER_NATIVE_ROOT "${EPCSAFT_PROVIDER_SDK_PACKAGE_ROOT}/native")

if(NOT EXISTS "${EPCSAFT_PROVIDER_NATIVE_ROOT}/bindings/module.cpp")
    message(FATAL_ERROR "Provider native SDK could not locate epcsaft provider native sources at ${EPCSAFT_PROVIDER_NATIVE_ROOT}.")
endif()

set(EPCSAFT_PROVIDER_NATIVE_SOURCES
    "${EPCSAFT_PROVIDER_NATIVE_ROOT}/model/parameter_setup.cpp"
    "${EPCSAFT_PROVIDER_NATIVE_ROOT}/eos/properties/activity.cpp"
    "${EPCSAFT_PROVIDER_NATIVE_ROOT}/eos/properties/chemical_potential.cpp"
    "${EPCSAFT_PROVIDER_NATIVE_ROOT}/eos/properties/compressibility.cpp"
    "${EPCSAFT_PROVIDER_NATIVE_ROOT}/eos/properties/density.cpp"
    "${EPCSAFT_PROVIDER_NATIVE_ROOT}/eos/properties/fugacity.cpp"
    "${EPCSAFT_PROVIDER_NATIVE_ROOT}/eos/properties/pure_neutral_parameter_derivatives.cpp"
    "${EPCSAFT_PROVIDER_NATIVE_ROOT}/eos/properties/residual_association_sensitivities.cpp"
    "${EPCSAFT_PROVIDER_NATIVE_ROOT}/eos/properties/residual_helmholtz.cpp"
    "${EPCSAFT_PROVIDER_NATIVE_ROOT}/eos/properties/residual_parameter_phase_derivatives.cpp"
    "${EPCSAFT_PROVIDER_NATIVE_ROOT}/eos/properties/residual_phase_derivatives.cpp"
    "${EPCSAFT_PROVIDER_NATIVE_ROOT}/eos/properties/residual_property_derivatives.cpp"
    "${EPCSAFT_PROVIDER_NATIVE_ROOT}/eos/properties/residual_properties.cpp"
    "${EPCSAFT_PROVIDER_NATIVE_ROOT}/eos/state.cpp"
    "${EPCSAFT_PROVIDER_NATIVE_ROOT}/eos/contributions/association.cpp"
    "${EPCSAFT_PROVIDER_NATIVE_ROOT}/eos/contributions/born.cpp"
    "${EPCSAFT_PROVIDER_NATIVE_ROOT}/eos/contributions/dispersion.cpp"
    "${EPCSAFT_PROVIDER_NATIVE_ROOT}/eos/contributions/hard_chain.cpp"
    "${EPCSAFT_PROVIDER_NATIVE_ROOT}/eos/contributions/ion.cpp"
    "${EPCSAFT_PROVIDER_NATIVE_ROOT}/autodiff/cppad_smoke_checks.cpp"
    "${EPCSAFT_PROVIDER_NATIVE_ROOT}/autodiff/implicit_sensitivity.cpp"
)
if(DEFINED EPCSAFT_CPPAD_SOURCE_FILE AND EPCSAFT_CPPAD_SOURCE_FILE)
    list(APPEND EPCSAFT_PROVIDER_NATIVE_SOURCES "${EPCSAFT_CPPAD_SOURCE_FILE}")
endif()

set(EPCSAFT_PROVIDER_NATIVE_INCLUDE_DIRS
    "${EPCSAFT_PROVIDER_NATIVE_ROOT}"
    "${EPCSAFT_PROVIDER_NATIVE_ROOT}/autodiff"
    "${EPCSAFT_PROVIDER_NATIVE_ROOT}/bindings"
    "${EPCSAFT_PROVIDER_NATIVE_ROOT}/eos"
    "${EPCSAFT_PROVIDER_NATIVE_ROOT}/eos/contributions"
    "${EPCSAFT_PROVIDER_NATIVE_ROOT}/model"
    "${EPCSAFT_PROVIDER_NATIVE_ROOT}/runtime"
)

function(epcsaft_provider_sdk_add_provider_native target_name)
    if(TARGET "${target_name}")
        return()
    endif()
    if(NOT DEFINED EPCSAFT_EIGEN_INCLUDE OR NOT EXISTS "${EPCSAFT_EIGEN_INCLUDE}")
        message(FATAL_ERROR "EPCSAFT_EIGEN_INCLUDE must point at the Eigen include root before adding ${target_name}.")
    endif()

    add_library("${target_name}" OBJECT ${EPCSAFT_PROVIDER_NATIVE_SOURCES})
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
