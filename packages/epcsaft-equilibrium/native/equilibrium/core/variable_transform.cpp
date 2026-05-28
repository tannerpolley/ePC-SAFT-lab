#include "equilibrium/core/variable_transform.h"

#include "model/native_types.h"

#include <cmath>
#include <cstddef>
#include <sstream>

namespace epcsaft::native::equilibrium_nlp {

namespace {

void require_positive_count(int value, const std::string& label) {
    if (value > 0) {
        return;
    }
    throw ValueError(label + " must be positive.");
}

void require_size(const std::vector<double>& values, std::size_t expected, const std::string& label) {
    if (values.size() == expected) {
        return;
    }
    std::ostringstream msg;
    msg << label << " has size " << values.size() << " but expected " << expected << ".";
    throw ValueError(msg.str());
}

void require_finite(double value, const std::string& label) {
    if (std::isfinite(value)) {
        return;
    }
    throw ValueError(label + " must be finite.");
}

void require_finite_values(const std::vector<double>& values, const std::string& label) {
    for (double value : values) {
        require_finite(value, label);
    }
}

void validate_evaluation_shape(const VariableTransformEvaluation& evaluation) {
    require_positive_count(evaluation.input_variable_count, "VariableTransform input variable count");
    require_positive_count(evaluation.output_variable_count, "VariableTransform output variable count");
    const std::size_t input = static_cast<std::size_t>(evaluation.input_variable_count);
    const std::size_t output = static_cast<std::size_t>(evaluation.output_variable_count);
    require_size(evaluation.solver_variables, input, "VariableTransform solver variable vector");
    require_size(evaluation.physical_variables, output, "VariableTransform physical variable vector");
    require_size(evaluation.jacobian_row_major, output * input, "VariableTransform Jacobian");
    require_size(
        evaluation.output_hessian_tensor_row_major,
        output * input * input,
        "VariableTransform output Hessian tensor"
    );
    require_finite_values(evaluation.solver_variables, "VariableTransform solver variable vector");
    require_finite_values(evaluation.physical_variables, "VariableTransform physical variable vector");
    require_finite_values(evaluation.jacobian_row_major, "VariableTransform Jacobian");
    require_finite_values(evaluation.output_hessian_tensor_row_major, "VariableTransform output Hessian tensor");
}

}  // namespace

std::vector<double> VariableTransform::solver_to_physical(
    const std::vector<double>& solver_variables
) const {
    return evaluate(solver_variables).physical_variables;
}

std::vector<double> VariableTransform::dx_du(
    const std::vector<double>& solver_variables
) const {
    return evaluate(solver_variables).jacobian_row_major;
}

std::vector<double> VariableTransform::d2x_du2(
    const std::vector<double>& solver_variables
) const {
    return evaluate(solver_variables).output_hessian_tensor_row_major;
}

VariableTransformSecondOrderData VariableTransform::second_order_data(
    const std::vector<double>& solver_variables
) const {
    return variable_transform_second_order_data(evaluate(solver_variables));
}

IdentityVariableTransform::IdentityVariableTransform(int variable_count)
    : variable_count_(variable_count) {
    require_positive_count(variable_count_, "identity VariableTransform variable count");
}

std::string IdentityVariableTransform::transform_policy() const {
    return "identity_physical_coordinates";
}

int IdentityVariableTransform::input_variable_count() const {
    return variable_count_;
}

int IdentityVariableTransform::output_variable_count() const {
    return variable_count_;
}

VariableTransformEvaluation IdentityVariableTransform::evaluate(
    const std::vector<double>& solver_variables
) const {
    require_size(
        solver_variables,
        static_cast<std::size_t>(variable_count_),
        "identity VariableTransform solver variable vector"
    );
    require_finite_values(solver_variables, "identity VariableTransform solver variable vector");

    const std::size_t n = static_cast<std::size_t>(variable_count_);
    VariableTransformEvaluation out;
    out.input_variable_count = variable_count_;
    out.output_variable_count = variable_count_;
    out.solver_variables = solver_variables;
    out.physical_variables = solver_variables;
    out.jacobian_row_major.assign(n * n, 0.0);
    out.output_hessian_tensor_row_major.assign(n * n * n, 0.0);
    out.transform_policy = transform_policy();
    out.backend = "analytic_identity";
    for (std::size_t index = 0; index < n; ++index) {
        out.jacobian_row_major[index * n + index] = 1.0;
    }
    validate_evaluation_shape(out);
    return out;
}

PositiveLogVariableTransform::PositiveLogVariableTransform(int variable_count)
    : variable_count_(variable_count) {
    require_positive_count(variable_count_, "positive-log VariableTransform variable count");
}

std::string PositiveLogVariableTransform::transform_policy() const {
    return "positive_log_coordinates";
}

int PositiveLogVariableTransform::input_variable_count() const {
    return variable_count_;
}

int PositiveLogVariableTransform::output_variable_count() const {
    return variable_count_;
}

VariableTransformEvaluation PositiveLogVariableTransform::evaluate(
    const std::vector<double>& solver_variables
) const {
    require_size(
        solver_variables,
        static_cast<std::size_t>(variable_count_),
        "positive-log VariableTransform solver variable vector"
    );
    require_finite_values(solver_variables, "positive-log VariableTransform solver variable vector");

    const std::size_t n = static_cast<std::size_t>(variable_count_);
    VariableTransformEvaluation out;
    out.input_variable_count = variable_count_;
    out.output_variable_count = variable_count_;
    out.solver_variables = solver_variables;
    out.physical_variables.assign(n, 0.0);
    out.jacobian_row_major.assign(n * n, 0.0);
    out.output_hessian_tensor_row_major.assign(n * n * n, 0.0);
    out.transform_policy = transform_policy();
    out.backend = "analytic_positive_log";
    for (std::size_t index = 0; index < n; ++index) {
        const double physical = std::exp(solver_variables[index]);
        require_finite(physical, "positive-log VariableTransform physical variable");
        out.physical_variables[index] = physical;
        out.jacobian_row_major[index * n + index] = physical;
        out.output_hessian_tensor_row_major[index * n * n + index * n + index] = physical;
    }
    validate_evaluation_shape(out);
    return out;
}

VariableTransformSecondOrderData variable_transform_second_order_data(
    const VariableTransformEvaluation& evaluation
) {
    validate_evaluation_shape(evaluation);

    VariableTransformSecondOrderData out;
    out.input_variable_count = evaluation.input_variable_count;
    out.output_variable_count = evaluation.output_variable_count;
    out.jacobian_row_major = evaluation.jacobian_row_major;
    out.output_hessian_tensor_row_major = evaluation.output_hessian_tensor_row_major;
    out.backend = evaluation.backend;
    return out;
}

}  // namespace epcsaft::native::equilibrium_nlp
