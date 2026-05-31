#include "equilibrium/derivatives/nlp_contract_snapshot.h"

#include "equilibrium/core/route_metadata.h"
#include "equilibrium/core/variable_transform.h"

#include <algorithm>
#include <cmath>
#include <limits>
#include <map>

namespace epcsaft::native::equilibrium_nlp {

namespace nlp_contract_snapshot_detail {

void apply_route_metadata(NeutralTwoPhaseEosNlpContract& out, const RouteMetadata& metadata) {
    out.variable_model = metadata.variable_model;
    out.density_backend = metadata.density_backend;
    out.residual_families = metadata.residual_families;
    out.constraint_families = metadata.constraint_families;
}

void populate_domain_margins(
    NeutralTwoPhaseEosNlpContract& out,
    const NlpProblem& problem,
    const NlpBounds& bounds,
    const std::vector<double>& initial,
    const std::vector<double>& constraints,
    int species_count
) {
    out.initial_variable_lower_margin = std::numeric_limits<double>::infinity();
    out.initial_variable_upper_margin = std::numeric_limits<double>::infinity();
    out.initial_amount_lower_margin = std::numeric_limits<double>::infinity();
    out.initial_volume_lower_margin = std::numeric_limits<double>::infinity();
    for (int index = 0; index < problem.variable_count(); ++index) {
        const std::size_t i = static_cast<std::size_t>(index);
        const double lower_margin = initial[i] - bounds.variable_lower[i];
        const double upper_margin = bounds.variable_upper[i] - initial[i];
        out.initial_variable_lower_margin = std::min(out.initial_variable_lower_margin, lower_margin);
        out.initial_variable_upper_margin = std::min(out.initial_variable_upper_margin, upper_margin);
        const bool is_volume = species_count > 0 && (index % (species_count + 1)) == species_count;
        if (is_volume) {
            out.initial_volume_lower_margin = std::min(out.initial_volume_lower_margin, lower_margin);
        } else {
            out.initial_amount_lower_margin = std::min(out.initial_amount_lower_margin, lower_margin);
        }
    }
    out.initial_variable_bound_margin =
        std::min(out.initial_variable_lower_margin, out.initial_variable_upper_margin);
    out.initial_constraint_bound_violation = 0.0;
    for (int index = 0; index < problem.constraint_count(); ++index) {
        const std::size_t i = static_cast<std::size_t>(index);
        if (constraints[i] < bounds.constraint_lower[i]) {
            out.initial_constraint_bound_violation =
                std::max(out.initial_constraint_bound_violation, bounds.constraint_lower[i] - constraints[i]);
        }
        if (constraints[i] > bounds.constraint_upper[i]) {
            out.initial_constraint_bound_violation =
                std::max(out.initial_constraint_bound_violation, constraints[i] - bounds.constraint_upper[i]);
        }
    }
    if (!std::isfinite(out.initial_amount_lower_margin)) {
        out.initial_amount_lower_margin = 0.0;
    }
    if (!std::isfinite(out.initial_volume_lower_margin)) {
        out.initial_volume_lower_margin = 0.0;
    }
}

}  // namespace nlp_contract_snapshot_detail

NeutralTwoPhaseEosNlpContract make_neutral_two_phase_nlp_contract_snapshot(
    const NlpProblem& problem,
    int phase_count,
    int species_count,
    NlpContractSnapshotDetail detail
) {
    validate_nlp_problem_shape(problem);

    const std::vector<double> initial = problem.initial_point();
    const NlpBounds bounds = problem.bounds();
    const NlpJacobianStructure structure = problem.jacobian_structure();
    const std::vector<double> constraints = problem.constraints(initial);
    const std::map<std::string, std::string> diagnostics = problem.diagnostics();

    NeutralTwoPhaseEosNlpContract out;
    out.problem_name = problem.name();
    out.derivative_backend = "analytic_cppad";
    const auto activation_compiler = diagnostics.find("activation_compiler");
    out.activation_compiler =
        activation_compiler == diagnostics.end() ? "" : activation_compiler->second;
    nlp_contract_snapshot_detail::apply_route_metadata(out, route_metadata_from_diagnostics(diagnostics));
    out.phase_count = phase_count;
    out.species_count = species_count;
    out.variable_count = problem.variable_count();
    out.constraint_count = problem.constraint_count();
    out.jacobian_nonzero_count = problem.jacobian_nonzero_count();
    out.exact_hessian_available = problem.has_exact_hessian();
    out.hessian_nonzero_count = problem.hessian_nonzero_count();
    out.hessian_backend = problem.hessian_backend();
    out.initial_point = initial;
    out.variable_lower_bounds = bounds.variable_lower;
    out.variable_upper_bounds = bounds.variable_upper;
    out.constraint_lower_bounds = bounds.constraint_lower;
    out.constraint_upper_bounds = bounds.constraint_upper;
    out.objective_at_initial = problem.objective(initial);
    out.gradient_at_initial = problem.objective_gradient(initial);
    out.constraints_at_initial = constraints;
    out.jacobian_rows = structure.rows;
    out.jacobian_cols = structure.cols;
    out.jacobian_values_at_initial = problem.jacobian_values(initial);

    if (detail == NlpContractSnapshotDetail::Basic) {
        return out;
    }

    const NlpHessianStructure hessian_structure = problem.hessian_structure();
    out.hessian_rows = hessian_structure.rows;
    out.hessian_cols = hessian_structure.cols;
    if (problem.has_exact_hessian()) {
        out.hessian_values_at_initial = problem.hessian_values(
            initial,
            1.0,
            std::vector<double>(static_cast<std::size_t>(problem.constraint_count()), 0.0)
        );
    }
    const NlpScaling scaling = problem.scaling();
    out.objective_scaling = scaling.objective;
    out.variable_scaling = scaling.variables;
    out.constraint_scaling = scaling.constraints;
    const IdentityVariableTransform transform(problem.variable_count());
    const VariableTransformEvaluation transform_evaluation = transform.evaluate(initial);
    out.transform_policy = transform_evaluation.transform_policy;
    out.transform_backend = transform_evaluation.backend;
    out.transform_input_variable_count = transform_evaluation.input_variable_count;
    out.transform_output_variable_count = transform_evaluation.output_variable_count;
    out.transform_jacobian_value_count = static_cast<int>(transform_evaluation.jacobian_row_major.size());
    out.transform_hessian_value_count =
        static_cast<int>(transform_evaluation.output_hessian_tensor_row_major.size());
    nlp_contract_snapshot_detail::populate_domain_margins(
        out,
        problem,
        bounds,
        initial,
        constraints,
        species_count
    );
    return out;
}

}  // namespace epcsaft::native::equilibrium_nlp
