#pragma once

#include "model/resolved_input.h"

struct NativeCorrelationJetV1 {
    double value{0.0};
    std::vector<std::string> derivative_variables;
    std::vector<double> first_derivatives;
    std::vector<double> second_derivatives_row_major;
};

NativeCorrelationJetV1 evaluate_native_correlation_v1(
    const NativeCorrelationDefinitionV1& correlation,
    const NativeDependencySignatureV1& dependency_signature,
    double temperature_K,
    const std::vector<double>& canonical_composition,
    const std::vector<std::string>& component_order,
    double organic_relative_permittivity
);
