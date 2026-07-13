#include "regression_problem.h"

#include <algorithm>
#include <array>
#include <cctype>
#include <cmath>
#include <cstdint>
#include <iomanip>
#include <limits>
#include <set>
#include <sstream>
#include <stdexcept>
#include <utility>

#include <ceres/cost_function.h>
#include <ceres/problem.h>
#include <ceres/solver.h>

namespace {

bool nonblank(const std::string& value) {
    return !value.empty() && std::any_of(value.begin(), value.end(), [](unsigned char character) {
        return !std::isspace(character);
    });
}

bool is_sha256(const std::string& value) {
    return value.size() == 64 && std::all_of(value.begin(), value.end(), [](unsigned char character) {
        return std::isxdigit(character) && !std::isupper(character);
    });
}

bool positive_finite(double value) {
    return std::isfinite(value) && value > 0.0;
}

class Sha256 final {
public:
    void update(const unsigned char* data, std::size_t length) {
        for (std::size_t index = 0; index < length; ++index) {
            block_[block_length_++] = data[index];
            bit_length_ += 8;
            if (block_length_ == block_.size()) {
                transform();
                block_length_ = 0;
            }
        }
    }

    std::string finish() {
        block_[block_length_++] = 0x80;
        if (block_length_ > 56) {
            while (block_length_ < 64) block_[block_length_++] = 0;
            transform();
            block_length_ = 0;
        }
        while (block_length_ < 56) block_[block_length_++] = 0;
        for (int shift = 56; shift >= 0; shift -= 8) {
            block_[block_length_++] = static_cast<unsigned char>((bit_length_ >> shift) & 0xffU);
        }
        transform();

        std::ostringstream output;
        output << std::hex << std::setfill('0');
        for (std::uint32_t word : state_) output << std::setw(8) << word;
        return output.str();
    }

private:
    static constexpr std::array<std::uint32_t, 64> constants_ = {
        0x428a2f98U, 0x71374491U, 0xb5c0fbcfU, 0xe9b5dba5U, 0x3956c25bU, 0x59f111f1U,
        0x923f82a4U, 0xab1c5ed5U, 0xd807aa98U, 0x12835b01U, 0x243185beU, 0x550c7dc3U,
        0x72be5d74U, 0x80deb1feU, 0x9bdc06a7U, 0xc19bf174U, 0xe49b69c1U, 0xefbe4786U,
        0x0fc19dc6U, 0x240ca1ccU, 0x2de92c6fU, 0x4a7484aaU, 0x5cb0a9dcU, 0x76f988daU,
        0x983e5152U, 0xa831c66dU, 0xb00327c8U, 0xbf597fc7U, 0xc6e00bf3U, 0xd5a79147U,
        0x06ca6351U, 0x14292967U, 0x27b70a85U, 0x2e1b2138U, 0x4d2c6dfcU, 0x53380d13U,
        0x650a7354U, 0x766a0abbU, 0x81c2c92eU, 0x92722c85U, 0xa2bfe8a1U, 0xa81a664bU,
        0xc24b8b70U, 0xc76c51a3U, 0xd192e819U, 0xd6990624U, 0xf40e3585U, 0x106aa070U,
        0x19a4c116U, 0x1e376c08U, 0x2748774cU, 0x34b0bcb5U, 0x391c0cb3U, 0x4ed8aa4aU,
        0x5b9cca4fU, 0x682e6ff3U, 0x748f82eeU, 0x78a5636fU, 0x84c87814U, 0x8cc70208U,
        0x90befffaU, 0xa4506cebU, 0xbef9a3f7U, 0xc67178f2U,
    };

    static std::uint32_t rotate_right(std::uint32_t value, unsigned int count) {
        return (value >> count) | (value << (32U - count));
    }

    void transform() {
        std::array<std::uint32_t, 64> schedule{};
        for (std::size_t index = 0; index < 16; ++index) {
            const std::size_t offset = index * 4;
            schedule[index] = (static_cast<std::uint32_t>(block_[offset]) << 24U)
                | (static_cast<std::uint32_t>(block_[offset + 1]) << 16U)
                | (static_cast<std::uint32_t>(block_[offset + 2]) << 8U)
                | static_cast<std::uint32_t>(block_[offset + 3]);
        }
        for (std::size_t index = 16; index < schedule.size(); ++index) {
            const std::uint32_t s0 = rotate_right(schedule[index - 15], 7U)
                ^ rotate_right(schedule[index - 15], 18U) ^ (schedule[index - 15] >> 3U);
            const std::uint32_t s1 = rotate_right(schedule[index - 2], 17U)
                ^ rotate_right(schedule[index - 2], 19U) ^ (schedule[index - 2] >> 10U);
            schedule[index] = schedule[index - 16] + s0 + schedule[index - 7] + s1;
        }

        std::uint32_t a = state_[0];
        std::uint32_t b = state_[1];
        std::uint32_t c = state_[2];
        std::uint32_t d = state_[3];
        std::uint32_t e = state_[4];
        std::uint32_t f = state_[5];
        std::uint32_t g = state_[6];
        std::uint32_t h = state_[7];
        for (std::size_t index = 0; index < schedule.size(); ++index) {
            const std::uint32_t sigma1 = rotate_right(e, 6U) ^ rotate_right(e, 11U) ^ rotate_right(e, 25U);
            const std::uint32_t choice = (e & f) ^ ((~e) & g);
            const std::uint32_t temporary1 = h + sigma1 + choice + constants_[index] + schedule[index];
            const std::uint32_t sigma0 = rotate_right(a, 2U) ^ rotate_right(a, 13U) ^ rotate_right(a, 22U);
            const std::uint32_t majority = (a & b) ^ (a & c) ^ (b & c);
            const std::uint32_t temporary2 = sigma0 + majority;
            h = g;
            g = f;
            f = e;
            e = d + temporary1;
            d = c;
            c = b;
            b = a;
            a = temporary1 + temporary2;
        }
        state_[0] += a;
        state_[1] += b;
        state_[2] += c;
        state_[3] += d;
        state_[4] += e;
        state_[5] += f;
        state_[6] += g;
        state_[7] += h;
    }

    std::array<unsigned char, 64> block_{};
    std::size_t block_length_{0};
    std::uint64_t bit_length_{0};
    std::array<std::uint32_t, 8> state_{
        0x6a09e667U, 0xbb67ae85U, 0x3c6ef372U, 0xa54ff53aU,
        0x510e527fU, 0x9b05688cU, 0x1f83d9abU, 0x5be0cd19U,
    };
};

std::string sha256(const std::string& input) {
    Sha256 digest;
    digest.update(reinterpret_cast<const unsigned char*>(input.data()), input.size());
    return digest.finish();
}

std::string stable_double(double value) {
    std::ostringstream output;
    output << std::setprecision(std::numeric_limits<double>::max_digits10) << value;
    return output.str();
}

void append_string(std::ostringstream& output, const std::string& value) {
    output << value.size() << ':' << value << ';';
}

void append_double(std::ostringstream& output, double value) {
    append_string(output, stable_double(value));
}

std::string canonical_problem_record(const NativeRegressionProblem& problem) {
    std::ostringstream output;
    append_string(output, "epcsaft.regression.native-problem");
    append_string(output, "1");
    append_string(output, problem.dataset_id);
    append_string(output, problem.provider_definition_fingerprint);
    output << problem.provider_handles.size() << ';';
    for (const auto& handle : problem.provider_handles) {
        append_string(output, handle->snapshot().snapshot_fingerprint_sha256);
    }
    output << problem.fixed_parameter_fingerprints.size() << ';';
    for (const auto& [record_id, fingerprint] : problem.fixed_parameter_fingerprints) {
        append_string(output, record_id);
        append_string(output, fingerprint);
    }
    output << problem.rows.size() << ';';
    for (const NativeRegressionRow& row : problem.rows) {
        append_string(output, row.row_id);
        append_string(output, row.source_id);
        append_string(output, row.source_kind);
        append_string(output, row.target_family);
        output << row.provider_handle_indices.size() << ';';
        for (int index : row.provider_handle_indices) output << index << ';';
        append_double(output, row.pressure_Pa);
        append_double(output, row.weight);
        append_double(output, row.residual_scale);
        append_double(output, row.target_value);
        append_double(output, row.model_intercept);
        output << row.parameter_coefficients.size() << ';';
        for (double coefficient : row.parameter_coefficients) append_double(output, coefficient);
        append_string(output, row.derivative_owner);
    }
    output << problem.parameters.size() << ';';
    for (const NativeFittedParameter& parameter : problem.parameters) {
        append_string(output, parameter.key);
        append_string(output, parameter.target_kind);
        output << parameter.first_index << ';' << parameter.second_index << ';';
        append_double(output, parameter.start);
        append_double(output, parameter.lower);
        append_double(output, parameter.upper);
    }
    append_string(output, problem.controls.loss);
    output << problem.controls.max_num_iterations << ';';
    append_double(output, problem.controls.function_tolerance);
    append_double(output, problem.controls.gradient_tolerance);
    append_double(output, problem.controls.parameter_tolerance);
    return output.str();
}

const std::set<std::string>& fitted_target_kinds() {
    static const std::set<std::string> values{
        "segment_count",
        "sigma_angstrom",
        "epsilon_k_K",
        "association_energy_K",
        "association_volume",
        "born_diameter_angstrom",
        "k_ij",
        "l_ij",
        "k_hb_ij",
        "solvation_factor",
        "relative_permittivity",
    };
    return values;
}

const std::set<std::string>& source_kinds() {
    static const std::set<std::string> values{
        "literature", "user_measurement", "component_test"
    };
    return values;
}

bool is_component_test_family(const std::string& family) {
    return family == "component_test_affine" || family == "component_test_quadratic";
}

bool is_production_family(const std::string& family) {
    return family == "binary_vle"
        || family == "pure_saturation_fugacity_balance"
        || family == "pure_liquid_density_at_pressure";
}

bool is_interaction_target(const std::string& target_kind) {
    return target_kind == "k_ij" || target_kind == "l_ij" || target_kind == "k_hb_ij";
}

void validate_problem(const NativeRegressionProblem& problem) {
    if (!nonblank(problem.dataset_id)) {
        throw std::invalid_argument("native regression dataset_id must be nonblank");
    }
    if (!is_sha256(problem.provider_definition_fingerprint)) {
        throw std::invalid_argument("native regression provider definition fingerprint must be SHA-256");
    }
    if (problem.provider_handles.empty()) {
        throw std::invalid_argument("native regression problem requires provider handles");
    }
    for (const auto& handle : problem.provider_handles) {
        if (!handle) throw std::invalid_argument("native regression provider handle cannot be null");
    }
    const auto& component_order = problem.provider_handles.front()->snapshot().component_order;
    for (const auto& handle : problem.provider_handles) {
        const NativeEvaluatedInputSnapshot& snapshot = handle->snapshot();
        if (snapshot.definition_fingerprint_sha256 != problem.provider_definition_fingerprint) {
            throw std::invalid_argument("native regression provider handles must share one definition fingerprint");
        }
        if (snapshot.component_order != component_order) {
            throw std::invalid_argument("native regression provider handles must share component order");
        }
        if (!is_sha256(snapshot.snapshot_fingerprint_sha256)) {
            throw std::invalid_argument("native regression provider handle lacks a SHA-256 snapshot fingerprint");
        }
    }
    std::string previous_fixed_record_id;
    for (const auto& [record_id, fingerprint] : problem.fixed_parameter_fingerprints) {
        if (!nonblank(record_id) || !is_sha256(fingerprint)) {
            throw std::invalid_argument(
                "native regression fixed parameter fingerprints require record IDs and SHA-256 values"
            );
        }
        if (!previous_fixed_record_id.empty() && record_id <= previous_fixed_record_id) {
            throw std::invalid_argument(
                "native regression fixed parameter fingerprints must have unique sorted record IDs"
            );
        }
        previous_fixed_record_id = record_id;
    }
    if (problem.parameters.empty()) {
        throw std::invalid_argument("native regression problem requires fitted parameters");
    }
    std::set<std::string> parameter_keys;
    for (const NativeFittedParameter& parameter : problem.parameters) {
        if (!parameter_keys.insert(parameter.key).second) {
            throw std::invalid_argument("native regression fitted parameter keys must be unique");
        }
        if (parameter.first_index < 0
            || static_cast<std::size_t>(parameter.first_index) >= component_order.size()) {
            throw std::invalid_argument("native fitted parameter first component index is invalid");
        }
        if (is_interaction_target(parameter.target_kind)) {
            if (parameter.second_index < 0
                || static_cast<std::size_t>(parameter.second_index) >= component_order.size()
                || parameter.second_index == parameter.first_index) {
                throw std::invalid_argument("native fitted interaction parameter indices are invalid");
            }
        } else if (parameter.second_index != -1) {
            throw std::invalid_argument("native fitted pure parameter second index must be -1");
        }
    }
    if (problem.rows.empty()) {
        throw std::invalid_argument("native regression problem requires target rows");
    }
    std::set<std::string> row_ids;
    for (const NativeRegressionRow& row : problem.rows) {
        if (!row_ids.insert(row.row_id).second) {
            throw std::invalid_argument("native regression row IDs must be unique");
        }
        if (row.provider_handle_indices.empty()) {
            throw std::invalid_argument("native regression row requires provider handle indices");
        }
        const std::set<int> unique_handle_indices(
            row.provider_handle_indices.begin(), row.provider_handle_indices.end()
        );
        if (unique_handle_indices.size() != row.provider_handle_indices.size()) {
            throw std::invalid_argument("native regression row provider handle indices must be unique");
        }
        for (int index : row.provider_handle_indices) {
            if (index < 0 || static_cast<std::size_t>(index) >= problem.provider_handles.size()) {
                throw std::invalid_argument("native regression row provider handle index is invalid");
            }
        }
        if (is_component_test_family(row.target_family)) {
            if (row.provider_handle_indices.size() != 1) {
                throw std::invalid_argument("component-test rows require one provider handle");
            }
            if (row.source_kind != "component_test") {
                throw std::invalid_argument("component-test regression rows require component_test source identity");
            }
            if (row.parameter_coefficients.size() != problem.parameters.size()) {
                throw std::invalid_argument("component-test parameter coefficient count must match fitted parameters");
            }
            if (row.derivative_owner != "exact_component_test") {
                throw std::invalid_argument("component-test rows require the exact component-test derivative owner");
            }
        } else if (is_production_family(row.target_family)) {
            const std::size_t expected_handle_count = row.target_family == "binary_vle" ? 2 : 1;
            if (row.provider_handle_indices.size() != expected_handle_count) {
                throw std::invalid_argument("production regression row has an invalid provider handle count");
            }
            if (!row.parameter_coefficients.empty()) {
                throw std::invalid_argument("production regression rows cannot carry component-test coefficients");
            }
            if (row.derivative_owner != "pending_resolved_input_overlay") {
                throw std::invalid_argument("production regression rows require the resolved-input overlay owner");
            }
        } else {
            throw std::invalid_argument("native regression row has an unsupported target family");
        }
    }
}

std::string termination_name(ceres::TerminationType type) {
    switch (type) {
        case ceres::CONVERGENCE:
            return "CONVERGENCE";
        case ceres::NO_CONVERGENCE:
            return "NO_CONVERGENCE";
        case ceres::FAILURE:
            return "FAILURE";
        case ceres::USER_SUCCESS:
            return "USER_SUCCESS";
        case ceres::USER_FAILURE:
            return "USER_FAILURE";
    }
    throw std::invalid_argument("unknown Ceres termination type");
}

class ExactComponentTestCost final : public ceres::CostFunction {
public:
    explicit ExactComponentTestCost(const NativeRegressionProblem& problem) : problem_(problem) {
        set_num_residuals(static_cast<int>(problem.rows.size()));
        mutable_parameter_block_sizes()->push_back(static_cast<int>(problem.parameters.size()));
    }

    bool Evaluate(
        double const* const* parameters,
        double* residuals,
        double** jacobians
    ) const override {
        const std::size_t parameter_count = problem_.parameters.size();
        std::vector<double> values(parameters[0], parameters[0] + parameter_count);
        const NativeRegressionEvaluation evaluation = evaluate_regression_problem(problem_, values);
        for (std::size_t row = 0; row < problem_.rows.size(); ++row) {
            residuals[row] = evaluation.row_diagnostics[row].weighted_residual;
        }
        if (jacobians != nullptr && jacobians[0] != nullptr) {
            std::copy(
                evaluation.jacobian_row_major.begin(),
                evaluation.jacobian_row_major.end(),
                jacobians[0]
            );
        }
        return evaluation.finite_outputs && evaluation.derivative_complete;
    }

private:
    const NativeRegressionProblem& problem_;
};

}  // namespace

NativeFittedParameter::NativeFittedParameter(
    std::string key_value,
    std::string target_kind_value,
    int first_index_value,
    int second_index_value,
    double start_value,
    double lower_value,
    double upper_value
) :
    key(std::move(key_value)),
    target_kind(std::move(target_kind_value)),
    first_index(first_index_value),
    second_index(second_index_value),
    start(start_value),
    lower(lower_value),
    upper(upper_value) {
    if (!nonblank(key)) throw std::invalid_argument("native fitted parameter key must be nonblank");
    if (fitted_target_kinds().count(target_kind) == 0) {
        throw std::invalid_argument("native fitted parameter target kind is unsupported");
    }
    if (!std::isfinite(start) || !std::isfinite(lower) || !std::isfinite(upper)) {
        throw std::invalid_argument("native fitted parameter values must be finite");
    }
    if (!(lower < upper)) {
        throw std::invalid_argument("native fitted parameter lower bound must be below upper bound");
    }
    if (start < lower || start > upper) {
        throw std::invalid_argument("native fitted parameter start must lie within bounds");
    }
}

NativeRegressionControls::NativeRegressionControls(
    std::string loss_value,
    int max_num_iterations_value,
    double function_tolerance_value,
    double gradient_tolerance_value,
    double parameter_tolerance_value
) :
    loss(std::move(loss_value)),
    max_num_iterations(max_num_iterations_value),
    function_tolerance(function_tolerance_value),
    gradient_tolerance(gradient_tolerance_value),
    parameter_tolerance(parameter_tolerance_value) {
    if (loss != "linear") throw std::invalid_argument("native regression loss must be linear");
    if (max_num_iterations <= 0) {
        throw std::invalid_argument("native regression max_num_iterations must be positive");
    }
    if (!positive_finite(function_tolerance)
        || !positive_finite(gradient_tolerance)
        || !positive_finite(parameter_tolerance)) {
        throw std::invalid_argument("native regression tolerances must be finite and positive");
    }
}

NativeRegressionRow::NativeRegressionRow(
    std::string row_id_value,
    std::string source_id_value,
    std::string source_kind_value,
    std::string target_family_value,
    std::vector<int> provider_handle_indices_value,
    double pressure_Pa_value,
    double weight_value,
    double residual_scale_value,
    double target_value_value,
    double model_intercept_value,
    std::vector<double> parameter_coefficients_value,
    std::string derivative_owner_value
) :
    row_id(std::move(row_id_value)),
    source_id(std::move(source_id_value)),
    source_kind(std::move(source_kind_value)),
    target_family(std::move(target_family_value)),
    provider_handle_indices(std::move(provider_handle_indices_value)),
    pressure_Pa(pressure_Pa_value),
    weight(weight_value),
    residual_scale(residual_scale_value),
    target_value(target_value_value),
    model_intercept(model_intercept_value),
    parameter_coefficients(std::move(parameter_coefficients_value)),
    derivative_owner(std::move(derivative_owner_value)) {
    if (!nonblank(row_id) || !nonblank(source_id)) {
        throw std::invalid_argument("native regression row and source IDs must be nonblank");
    }
    if (source_kinds().count(source_kind) == 0) {
        throw std::invalid_argument("native regression row source kind is unsupported");
    }
    if (!positive_finite(pressure_Pa) || !positive_finite(weight) || !positive_finite(residual_scale)) {
        throw std::invalid_argument(
            "native regression row pressure, weight, and residual scale must be finite and positive"
        );
    }
    if (!std::isfinite(target_value) || !std::isfinite(model_intercept)
        || std::any_of(parameter_coefficients.begin(), parameter_coefficients.end(), [](double value) {
            return !std::isfinite(value);
        })) {
        throw std::invalid_argument("native regression row numerical fields must be finite");
    }
    if (!nonblank(derivative_owner)) {
        throw std::invalid_argument("native regression row derivative owner must be nonblank");
    }
}

NativeRegressionProblem::NativeRegressionProblem(
    std::string dataset_id_value,
    std::string provider_definition_fingerprint_value,
    std::vector<std::shared_ptr<ProviderResolvedInputHandleV1>> provider_handles_value,
    std::vector<std::pair<std::string, std::string>> fixed_parameter_fingerprints_value,
    std::vector<NativeRegressionRow> rows_value,
    std::vector<NativeFittedParameter> parameters_value,
    NativeRegressionControls controls_value
) :
    dataset_id(std::move(dataset_id_value)),
    provider_definition_fingerprint(std::move(provider_definition_fingerprint_value)),
    provider_handles(std::move(provider_handles_value)),
    fixed_parameter_fingerprints(std::move(fixed_parameter_fingerprints_value)),
    rows(std::move(rows_value)),
    parameters(std::move(parameters_value)),
    controls(std::move(controls_value)) {
    validate_problem(*this);
    problem_fingerprint = sha256(canonical_problem_record(*this));
}

NativeRegressionEvaluation evaluate_regression_problem(
    const NativeRegressionProblem& problem,
    const std::vector<double>& parameter_values
) {
    if (parameter_values.size() != problem.parameters.size()) {
        throw std::invalid_argument("native regression parameter vector size does not match the problem");
    }
    if (std::any_of(parameter_values.begin(), parameter_values.end(), [](double value) {
        return !std::isfinite(value);
    })) {
        throw std::invalid_argument("native regression parameter values must be finite");
    }

    NativeRegressionEvaluation result;
    result.parameter_values = parameter_values;
    result.jacobian_rows = static_cast<int>(problem.rows.size());
    result.jacobian_cols = static_cast<int>(problem.parameters.size());
    result.jacobian_row_major.assign(problem.rows.size() * problem.parameters.size(), 0.0);
    result.derivative_complete = true;
    result.derivative_column_owners.assign(problem.parameters.size(), "exact_component_test");
    result.row_diagnostics.reserve(problem.rows.size());

    double sum_of_squares = 0.0;
    for (std::size_t row_index = 0; row_index < problem.rows.size(); ++row_index) {
        const NativeRegressionRow& row = problem.rows[row_index];
        if (!is_component_test_family(row.target_family)) {
            throw std::runtime_error(
                "production regression rows require the resolved-input overlay adapter"
            );
        }
        double model_value = row.model_intercept;
        for (std::size_t column = 0; column < problem.parameters.size(); ++column) {
            const double theta = parameter_values[column];
            const double coefficient = row.parameter_coefficients[column];
            const double basis = row.target_family == "component_test_quadratic"
                ? theta * theta
                : theta;
            const double derivative = row.target_family == "component_test_quadratic"
                ? 2.0 * coefficient * theta
                : coefficient;
            model_value += coefficient * basis;
            result.jacobian_row_major[row_index * problem.parameters.size() + column]
                = std::sqrt(row.weight) * derivative / row.residual_scale;
        }
        const double raw_residual = model_value - row.target_value;
        const double weighted_residual = std::sqrt(row.weight) * raw_residual / row.residual_scale;
        result.row_diagnostics.push_back(
            {row.row_id, row.source_id, raw_residual, weighted_residual}
        );
        sum_of_squares += weighted_residual * weighted_residual;
        result.derivative_complete = result.derivative_complete
            && row.derivative_owner == "exact_component_test";
    }
    result.objective = 0.5 * sum_of_squares;
    result.finite_outputs = std::isfinite(result.objective)
        && std::all_of(
            result.jacobian_row_major.begin(),
            result.jacobian_row_major.end(),
            [](double value) { return std::isfinite(value); }
        )
        && std::all_of(
            result.row_diagnostics.begin(),
            result.row_diagnostics.end(),
            [](const NativeRegressionRowDiagnostic& row) {
                return std::isfinite(row.raw_residual) && std::isfinite(row.weighted_residual);
            }
        );
    return result;
}

bool regression_acceptance_from_summary(
    const std::string& termination_type,
    bool solution_usable,
    double initial_cost,
    double final_cost,
    bool finite_outputs,
    bool derivative_complete
) {
    const bool accepted_termination = termination_type == "CONVERGENCE"
        || termination_type == "USER_SUCCESS";
    return accepted_termination
        && solution_usable
        && std::isfinite(initial_cost)
        && std::isfinite(final_cost)
        && finite_outputs
        && derivative_complete;
}

NativeRegressionSolveResult solve_regression_problem(const NativeRegressionProblem& problem) {
    std::vector<double> parameter_values;
    parameter_values.reserve(problem.parameters.size());
    for (const NativeFittedParameter& parameter : problem.parameters) {
        parameter_values.push_back(parameter.start);
    }
    evaluate_regression_problem(problem, parameter_values);

    ceres::Problem ceres_problem;
    auto* cost = new ExactComponentTestCost(problem);
    ceres_problem.AddResidualBlock(cost, nullptr, parameter_values.data());
    for (std::size_t index = 0; index < problem.parameters.size(); ++index) {
        ceres_problem.SetParameterLowerBound(
            parameter_values.data(),
            static_cast<int>(index),
            problem.parameters[index].lower
        );
        ceres_problem.SetParameterUpperBound(
            parameter_values.data(),
            static_cast<int>(index),
            problem.parameters[index].upper
        );
    }

    ceres::Solver::Options options;
    options.max_num_iterations = problem.controls.max_num_iterations;
    options.function_tolerance = problem.controls.function_tolerance;
    options.gradient_tolerance = problem.controls.gradient_tolerance;
    options.parameter_tolerance = problem.controls.parameter_tolerance;
    options.linear_solver_type = ceres::DENSE_QR;
    options.num_threads = 1;
    options.minimizer_progress_to_stdout = false;

    NativeRegressionSolveResult result;
    result.effective_options = {
        options.max_num_iterations,
        options.function_tolerance,
        options.gradient_tolerance,
        options.parameter_tolerance,
    };
    ceres::Solver::Summary summary;
    ceres::Solve(options, &ceres_problem, &summary);

    result.evaluation = evaluate_regression_problem(problem, parameter_values);
    result.termination_type = termination_name(summary.termination_type);
    result.solution_usable = summary.IsSolutionUsable();
    result.iterations = static_cast<int>(summary.iterations.size());
    result.initial_cost = summary.initial_cost;
    result.final_cost = summary.final_cost;
    result.message = summary.BriefReport();
    const bool finite_outputs = result.evaluation.finite_outputs
        && std::isfinite(result.initial_cost)
        && std::isfinite(result.final_cost);
    result.success = regression_acceptance_from_summary(
        result.termination_type,
        result.solution_usable,
        result.initial_cost,
        result.final_cost,
        finite_outputs,
        result.evaluation.derivative_complete
    );
    return result;
}
