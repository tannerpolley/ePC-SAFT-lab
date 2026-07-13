#pragma once

#include <memory>
#include <string>
#include <utility>
#include <vector>

#include "model/resolved_input.h"

struct NativeFittedParameter final {
    NativeFittedParameter(
        std::string key,
        std::string target_kind,
        int first_index,
        int second_index,
        double start,
        double lower,
        double upper
    );

    std::string key;
    std::string target_kind;
    int first_index;
    int second_index;
    double start;
    double lower;
    double upper;
};

struct NativeRegressionControls final {
    NativeRegressionControls(
        std::string loss,
        int max_num_iterations,
        double function_tolerance,
        double gradient_tolerance,
        double parameter_tolerance
    );

    std::string loss;
    int max_num_iterations;
    double function_tolerance;
    double gradient_tolerance;
    double parameter_tolerance;
};

struct NativeRegressionRow final {
    NativeRegressionRow(
        std::string row_id,
        std::string source_id,
        std::string source_kind,
        std::string target_family,
        std::vector<int> provider_handle_indices,
        double pressure_Pa,
        double weight,
        double residual_scale,
        double target_value,
        double model_intercept,
        std::vector<double> parameter_coefficients,
        std::string derivative_owner
    );

    std::string row_id;
    std::string source_id;
    std::string source_kind;
    std::string target_family;
    std::vector<int> provider_handle_indices;
    double pressure_Pa;
    double weight;
    double residual_scale;
    double target_value;
    double model_intercept;
    std::vector<double> parameter_coefficients;
    std::string derivative_owner;
};

struct NativeRegressionProblem final {
    NativeRegressionProblem(
        std::string dataset_id,
        std::string provider_definition_fingerprint,
        std::vector<std::shared_ptr<ProviderResolvedInputHandleV1>> provider_handles,
        std::vector<std::pair<std::string, std::string>> fixed_parameter_fingerprints,
        std::vector<NativeRegressionRow> rows,
        std::vector<NativeFittedParameter> parameters,
        NativeRegressionControls controls
    );

    std::string dataset_id;
    std::string provider_definition_fingerprint;
    std::vector<std::shared_ptr<ProviderResolvedInputHandleV1>> provider_handles;
    std::vector<std::pair<std::string, std::string>> fixed_parameter_fingerprints;
    std::vector<NativeRegressionRow> rows;
    std::vector<NativeFittedParameter> parameters;
    NativeRegressionControls controls;
    std::string problem_fingerprint;
};

struct NativeRegressionRowDiagnostic final {
    std::string row_id;
    std::string source_id;
    double raw_residual;
    double weighted_residual;
};

struct NativeRegressionEvaluation final {
    std::vector<double> parameter_values;
    std::vector<NativeRegressionRowDiagnostic> row_diagnostics;
    std::vector<double> jacobian_row_major;
    int jacobian_rows{0};
    int jacobian_cols{0};
    double objective{0.0};
    bool finite_outputs{false};
    bool derivative_complete{false};
    std::vector<std::string> derivative_column_owners;
};

struct NativeEffectiveCeresOptions final {
    int max_num_iterations{0};
    double function_tolerance{0.0};
    double gradient_tolerance{0.0};
    double parameter_tolerance{0.0};
};

struct NativeRegressionSolveResult final {
    NativeRegressionEvaluation evaluation;
    NativeEffectiveCeresOptions effective_options;
    std::string termination_type;
    bool solution_usable{false};
    bool success{false};
    int iterations{0};
    double initial_cost{0.0};
    double final_cost{0.0};
    std::string message;
};

NativeRegressionEvaluation evaluate_regression_problem(
    const NativeRegressionProblem& problem,
    const std::vector<double>& parameter_values
);

NativeRegressionSolveResult solve_regression_problem(const NativeRegressionProblem& problem);

bool regression_acceptance_from_summary(
    const std::string& termination_type,
    bool solution_usable,
    double initial_cost,
    double final_cost,
    bool finite_outputs,
    bool derivative_complete
);
