#pragma once

#include "equilibrium/core/activation_plan.h"
#include "equilibrium/core/nlp_problem.h"
#include "equilibrium/core/two_phase_eos_route.h"
#include "equilibrium/core/variable_layout.h"

#include <memory>
#include <string>
#include <vector>

struct add_args;

namespace epcsaft::native::equilibrium_nlp {

class ActivatedEquilibriumNlp final : public NlpProblem {
public:
    ActivatedEquilibriumNlp(
        const add_args& args,
        epcsaft::native::equilibrium::ActivationPlan plan,
        epcsaft::native::equilibrium::VariableLayout layout
    );

    std::string name() const override;
    int variable_count() const override;
    int constraint_count() const override;
    int jacobian_nonzero_count() const override;
    NlpBounds bounds() const override;
    std::vector<double> initial_point() const override;
    double objective(const std::vector<double>& variables) const override;
    std::vector<double> objective_gradient(const std::vector<double>& variables) const override;
    std::vector<double> constraints(const std::vector<double>& variables) const override;
    NlpJacobianStructure jacobian_structure() const override;
    std::vector<double> jacobian_values(const std::vector<double>& variables) const override;
    bool has_exact_hessian() const override;
    int hessian_nonzero_count() const override;
    NlpHessianStructure hessian_structure() const override;
    std::vector<double> hessian_values(
        const std::vector<double>& variables,
        double objective_factor,
        const std::vector<double>& constraint_multipliers
    ) const override;
    std::string hessian_backend() const override;
    NlpScaling scaling() const override;
    std::map<std::string, std::string> diagnostics() const override;

    const epcsaft::native::equilibrium::ActivationPlan& plan() const;
    const epcsaft::native::equilibrium::VariableLayout& layout() const;

private:
    epcsaft::native::equilibrium::ActivationPlan plan_;
    epcsaft::native::equilibrium::VariableLayout layout_;
    std::unique_ptr<NlpProblem> delegate_;
};

}  // namespace epcsaft::native::equilibrium_nlp
