#pragma once

#include "equilibrium/core/second_order.h"

#include <string>
#include <vector>

namespace epcsaft::native::equilibrium_nlp {

struct VariableTransformEvaluation {
    int input_variable_count = 0;
    int output_variable_count = 0;
    std::vector<double> solver_variables;
    std::vector<double> physical_variables;
    std::vector<double> jacobian_row_major;
    std::vector<double> output_hessian_tensor_row_major;
    std::string transform_policy;
    std::string backend = "analytic";
};

class VariableTransform {
public:
    virtual ~VariableTransform() = default;

    virtual std::string transform_policy() const = 0;
    virtual int input_variable_count() const = 0;
    virtual int output_variable_count() const = 0;
    virtual VariableTransformEvaluation evaluate(
        const std::vector<double>& solver_variables
    ) const = 0;

    std::vector<double> solver_to_physical(
        const std::vector<double>& solver_variables
    ) const;

    std::vector<double> dx_du(
        const std::vector<double>& solver_variables
    ) const;

    std::vector<double> d2x_du2(
        const std::vector<double>& solver_variables
    ) const;

    VariableTransformSecondOrderData second_order_data(
        const std::vector<double>& solver_variables
    ) const;
};

class IdentityVariableTransform final : public VariableTransform {
public:
    explicit IdentityVariableTransform(int variable_count);

    std::string transform_policy() const override;
    int input_variable_count() const override;
    int output_variable_count() const override;
    VariableTransformEvaluation evaluate(
        const std::vector<double>& solver_variables
    ) const override;

private:
    int variable_count_;
};

class PositiveLogVariableTransform final : public VariableTransform {
public:
    explicit PositiveLogVariableTransform(int variable_count);

    std::string transform_policy() const override;
    int input_variable_count() const override;
    int output_variable_count() const override;
    VariableTransformEvaluation evaluate(
        const std::vector<double>& solver_variables
    ) const override;

private:
    int variable_count_;
};

VariableTransformSecondOrderData variable_transform_second_order_data(
    const VariableTransformEvaluation& evaluation
);

}  // namespace epcsaft::native::equilibrium_nlp
