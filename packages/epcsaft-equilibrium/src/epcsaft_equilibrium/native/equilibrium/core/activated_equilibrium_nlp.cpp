#include "equilibrium/core/activated_equilibrium_nlp.h"

#include "equilibrium/core/chemical_equilibrium_objective.h"
#include "equilibrium/derivatives/nlp_contract_snapshot.h"
#include "model/native_types.h"

#include <algorithm>
#include <cmath>
#include <cstddef>
#include <memory>
#include <sstream>
#include <utility>

namespace epcsaft::native::equilibrium_nlp {

namespace {

std::vector<int> phase_kind_tokens(const std::vector<std::string>& phase_kinds) {
    std::vector<int> out;
    out.reserve(phase_kinds.size());
    for (const std::string& phase_kind : phase_kinds) {
        if (phase_kind == "liquid") {
            out.push_back(0);
        } else if (phase_kind == "vapor") {
            out.push_back(1);
        } else {
            throw ValueError("activation-nlp-ineligible: unsupported phase kind in activation plan.");
        }
    }
    return out;
}

void require_activated_neutral_two_phase_plan(
    const epcsaft::native::equilibrium::ActivationPlan& plan,
    const epcsaft::native::equilibrium::VariableLayout& layout
) {
    if (!((plan.family_key == "neutral_tp_flash" && plan.route == "neutral_tp_flash")
          || (plan.family_key == "neutral_lle" && plan.route == "neutral_lle"))) {
        throw ValueError("activation-nlp-ineligible: only activation-matrix neutral two-phase routes are supported.");
    }
    if (layout.family_key != plan.family_key || layout.route != plan.route) {
        throw ValueError("activation-nlp-ineligible: variable layout route does not match activation plan.");
    }
    if (layout.variable_model != plan.variable_model || layout.variable_count <= 0) {
        throw ValueError("activation-nlp-ineligible: variable layout does not match activation plan model.");
    }
}

std::unique_ptr<NlpProblem> make_delegate(
    const add_args& args,
    const epcsaft::native::equilibrium::ActivationPlan& plan
) {
    if (plan.route == "neutral_tp_flash") {
        return make_neutral_tp_flash_eos_problem(
            args,
            plan.temperature,
            plan.pressure,
            plan.feed_composition,
            "neutral_tp_flash_eos"
        );
    }
    return make_neutral_two_phase_eos_problem_from_feed(
        args,
        plan.temperature,
        plan.pressure,
        plan.feed_composition,
        phase_kind_tokens(plan.phase_kinds),
        "neutral_lle_eos",
        1.0e-8
    );
}

}  // namespace

ActivatedEquilibriumNlp::ActivatedEquilibriumNlp(
    const add_args& args,
    epcsaft::native::equilibrium::ActivationPlan plan,
    epcsaft::native::equilibrium::VariableLayout layout
)
    : plan_(std::move(plan)),
      layout_(std::move(layout)),
      delegate_(make_delegate(args, plan_)) {
    require_activated_neutral_two_phase_plan(plan_, layout_);
    if (!delegate_) {
        throw ValueError("activation-nlp-ineligible: two-phase delegate was not created.");
    }
    if (delegate_->variable_count() != layout_.variable_count) {
        throw ValueError("activation-nlp-ineligible: compiled NLP variable count does not match layout.");
    }
}

std::string ActivatedEquilibriumNlp::name() const {
    return delegate_->name();
}

int ActivatedEquilibriumNlp::variable_count() const {
    return delegate_->variable_count();
}

int ActivatedEquilibriumNlp::constraint_count() const {
    return delegate_->constraint_count();
}

int ActivatedEquilibriumNlp::jacobian_nonzero_count() const {
    return delegate_->jacobian_nonzero_count();
}

NlpBounds ActivatedEquilibriumNlp::bounds() const {
    return delegate_->bounds();
}

std::vector<double> ActivatedEquilibriumNlp::initial_point() const {
    return delegate_->initial_point();
}

double ActivatedEquilibriumNlp::objective(const std::vector<double>& variables) const {
    return delegate_->objective(variables);
}

std::vector<double> ActivatedEquilibriumNlp::objective_gradient(
    const std::vector<double>& variables
) const {
    return delegate_->objective_gradient(variables);
}

std::vector<double> ActivatedEquilibriumNlp::constraints(const std::vector<double>& variables) const {
    return delegate_->constraints(variables);
}

NlpJacobianStructure ActivatedEquilibriumNlp::jacobian_structure() const {
    return delegate_->jacobian_structure();
}

std::vector<double> ActivatedEquilibriumNlp::jacobian_values(
    const std::vector<double>& variables
) const {
    return delegate_->jacobian_values(variables);
}

bool ActivatedEquilibriumNlp::has_exact_hessian() const {
    return delegate_->has_exact_hessian();
}

int ActivatedEquilibriumNlp::hessian_nonzero_count() const {
    return delegate_->hessian_nonzero_count();
}

NlpHessianStructure ActivatedEquilibriumNlp::hessian_structure() const {
    return delegate_->hessian_structure();
}

std::vector<double> ActivatedEquilibriumNlp::hessian_values(
    const std::vector<double>& variables,
    double objective_factor,
    const std::vector<double>& constraint_multipliers
) const {
    return delegate_->hessian_values(variables, objective_factor, constraint_multipliers);
}

std::string ActivatedEquilibriumNlp::hessian_backend() const {
    return delegate_->hessian_backend();
}

NlpScaling ActivatedEquilibriumNlp::scaling() const {
    return delegate_->scaling();
}

std::map<std::string, std::string> ActivatedEquilibriumNlp::diagnostics() const {
    std::map<std::string, std::string> out = delegate_->diagnostics();
    out["activation_compiler"] = "activation_plan";
    out["activation_family"] = plan_.family_key;
    return out;
}

const epcsaft::native::equilibrium::ActivationPlan& ActivatedEquilibriumNlp::plan() const {
    return plan_;
}

const epcsaft::native::equilibrium::VariableLayout& ActivatedEquilibriumNlp::layout() const {
    return layout_;
}

NeutralTwoPhaseEosNlpContract evaluate_activated_neutral_tp_flash_nlp_contract(
    const add_args& args,
    const epcsaft::native::equilibrium::ActivationPlan& plan,
    const epcsaft::native::equilibrium::VariableLayout& layout
) {
    ActivatedEquilibriumNlp problem(args, plan, layout);
    return make_neutral_two_phase_nlp_contract_snapshot(
        problem,
        layout.phase_count,
        layout.species_count,
        NlpContractSnapshotDetail::FullDerivativeEvidence
    );
}

NeutralTwoPhaseEosNlpContract evaluate_activated_neutral_lle_nlp_contract(
    const add_args& args,
    const epcsaft::native::equilibrium::ActivationPlan& plan,
    const epcsaft::native::equilibrium::VariableLayout& layout
) {
    ActivatedEquilibriumNlp problem(args, plan, layout);
    return make_neutral_two_phase_nlp_contract_snapshot(
        problem,
        layout.phase_count,
        layout.species_count,
        NlpContractSnapshotDetail::FullDerivativeEvidence
    );
}

NeutralTwoPhaseEosNlpContract evaluate_activated_chemical_equilibrium_nlp_contract(
    const ChemicalEquilibriumNlpInput& input,
    const epcsaft::native::equilibrium::ActivationPlan& plan,
    const epcsaft::native::equilibrium::VariableLayout& layout
) {
    HomogeneousChemicalEquilibriumNlp problem(input, plan, layout);
    NeutralTwoPhaseEosNlpContract out = make_neutral_two_phase_nlp_contract_snapshot(
        problem,
        layout.phase_count,
        layout.species_count,
        NlpContractSnapshotDetail::FullDerivativeEvidence
    );
    const HomogeneousChemicalEquilibriumBlockResult block =
        problem.evaluate_physical_block(input.initial_amounts);
    out.balance_row_count = static_cast<int>(input.conservation_labels.size());
    out.reaction_count = static_cast<int>(input.reaction_labels.size());
    out.standard_mu_rt = block.standard_mu_rt;
    return out;
}

namespace {

ChemicalEquilibriumNlpInput input_with_initial_amounts(
    const ChemicalEquilibriumNlpInput& input,
    const std::vector<double>& initial_amounts
) {
    ChemicalEquilibriumNlpInput out = input;
    out.initial_amounts = initial_amounts;
    return out;
}

IpoptSolveOptions ce_stage_options(
    const IpoptSolveOptions& options,
    const std::string& option_profile
) {
    IpoptSolveOptions out = options;
    out.option_profile = option_profile;
    if (out.bound_push <= 0.0) {
        out.bound_push = 1.0e-12;
    }
    if (out.bound_frac <= 0.0) {
        out.bound_frac = 1.0e-12;
    }
    return out;
}

ContinuationStageSpec ce_homotopy_stage(
    const ChemicalEquilibriumNlpInput& base_input,
    const epcsaft::native::equilibrium::ActivationPlan& plan,
    const epcsaft::native::equilibrium::VariableLayout& layout,
    const IpoptSolveOptions& options,
    const std::string& stage_id,
    double lambda,
    bool final_proof
) {
    ContinuationStageSpec stage;
    stage.stage_id = stage_id;
    stage.parameter_value = lambda;
    stage.final_proof = final_proof;
    stage.options = ce_stage_options(options, final_proof ? "proof" : "continuation_trace");
    ChemicalEquilibriumNlpInput stage_input =
        chemical_equilibrium_input_with_log_k_lambda(base_input, lambda);
    stage.problem_factory = [stage_input, plan, layout]() {
        return std::make_unique<HomogeneousChemicalEquilibriumNlp>(stage_input, plan, layout);
    };
    return stage;
}

ContinuationStageSpec ce_activity_homotopy_stage(
    const ChemicalEquilibriumNlpInput& base_input,
    const epcsaft::native::equilibrium::ActivationPlan& plan,
    const epcsaft::native::equilibrium::VariableLayout& layout,
    const IpoptSolveOptions& options,
    const std::string& stage_id,
    double lambda,
    bool final_proof
) {
    ContinuationStageSpec stage;
    stage.stage_id = stage_id;
    stage.parameter_value = lambda;
    stage.final_proof = final_proof;
    stage.options = ce_stage_options(options, final_proof ? "proof" : "continuation_trace");
    ChemicalEquilibriumNlpInput stage_input =
        chemical_equilibrium_input_with_activity_lambda(
            chemical_equilibrium_input_with_log_k_lambda(base_input, 1.0),
            lambda
        );
    stage.problem_factory = [stage_input, plan, layout]() {
        return std::make_unique<HomogeneousChemicalEquilibriumNlp>(stage_input, plan, layout);
    };
    return stage;
}

ChemicalEquilibriumNlpResult build_ce_result_from_solve(
    const ChemicalEquilibriumNlpInput& input,
    const epcsaft::native::equilibrium::ActivationPlan& plan,
    const epcsaft::native::equilibrium::VariableLayout& layout,
    const IpoptSolveResult& solve,
    double balance_tolerance,
    double reaction_stationarity_tolerance
) {
    HomogeneousChemicalEquilibriumNlp problem(input, plan, layout);
    ChemicalEquilibriumNlpResult out;
    out.contract = evaluate_activated_chemical_equilibrium_nlp_contract(input, plan, layout);
    out.solve = solve;
    const std::vector<double>& variables = out.solve.variables.empty()
        ? problem.initial_point()
        : out.solve.variables;
    const ChemicalEquilibriumProofEvaluation proof = problem.evaluate_physical_proof(
        variables,
        balance_tolerance,
        reaction_stationarity_tolerance
    );
    out.postsolve = proof.block;
    out.balance_inf_norm = proof.balance_inf_norm;
    out.reaction_stationarity_inf_norm = proof.reaction_stationarity_inf_norm;
    out.proof_metrics = proof.proof_metrics;
    out.accepted = ipopt_solve_result_allows_postsolve(out.solve)
        && proof.thermodynamically_accepted;
    return out;
}

ChemicalEquilibriumNlpResult solve_single_ce_proof(
    const ChemicalEquilibriumNlpInput& input,
    const epcsaft::native::equilibrium::ActivationPlan& plan,
    const epcsaft::native::equilibrium::VariableLayout& layout,
    const IpoptSolveOptions& options,
    double balance_tolerance,
    double reaction_stationarity_tolerance
) {
    HomogeneousChemicalEquilibriumNlp problem(input, plan, layout);
    validate_nlp_problem_shape(problem);
    IpoptSolveOptions solve_options = ce_stage_options(options, "proof");
    if (solve_options.initial_constraint_multipliers.empty()) {
        solve_options.initial_constraint_multipliers = problem.initial_constraint_multipliers();
        solve_options.initial_bound_lower_multipliers.assign(
            static_cast<std::size_t>(problem.variable_count()),
            0.0
        );
        solve_options.initial_bound_upper_multipliers.assign(
            static_cast<std::size_t>(problem.variable_count()),
            0.0
        );
    }
    return build_ce_result_from_solve(
        input,
        plan,
        layout,
        solve_ipopt_nlp(problem, solve_options),
        balance_tolerance,
        reaction_stationarity_tolerance
    );
}

ChemicalEquilibriumNlpResult result_from_homotopy_trace(
    const ChemicalEquilibriumNlpInput& true_input,
    const epcsaft::native::equilibrium::ActivationPlan& plan,
    const epcsaft::native::equilibrium::VariableLayout& layout,
    const ContinuationTraceResult& trace,
    double balance_tolerance,
    double reaction_stationarity_tolerance
) {
    if (trace.trace.empty()) {
        ChemicalEquilibriumNlpResult out;
        out.continuation = trace;
        return out;
    }
    ChemicalEquilibriumNlpResult out = build_ce_result_from_solve(
        true_input,
        plan,
        layout,
        trace.trace.back().solve,
        balance_tolerance,
        reaction_stationarity_tolerance
    );
    out.continuation = trace;
    out.accepted = trace.accepted && out.accepted;
    return out;
}

bool trace_finished_final_lambda_one(const ContinuationTraceResult& trace) {
    if (trace.trace.empty()) {
        return false;
    }
    const ContinuationStageResult& final_stage = trace.trace.back();
    return final_stage.final_proof
        && std::abs(final_stage.parameter_value - 1.0) <= 1.0e-12
        && !final_stage.solve.variables.empty();
}

std::string activity_continuation_stage_id(double activity_lambda, int attempt_index) {
    if (std::abs(activity_lambda) <= 1.0e-12) {
        return "activity_lambda_0";
    }
    if (std::abs(activity_lambda - 0.5) <= 1.0e-12) {
        return "activity_lambda_half";
    }
    if (std::abs(activity_lambda - 1.0) <= 1.0e-12) {
        return "activity_lambda_1";
    }
    std::ostringstream stream;
    stream << "activity_lambda_" << attempt_index;
    return stream.str();
}

ContinuationTraceResult run_adaptive_eos_activity_continuation(
    const ChemicalEquilibriumNlpInput& seeded_input,
    const epcsaft::native::equilibrium::ActivationPlan& plan,
    const epcsaft::native::equilibrium::VariableLayout& layout,
    const IpoptSolveOptions& options,
    double minimum_step,
    int maximum_stage_count,
    std::vector<double>& accepted_activity_steps,
    std::vector<double>& rejected_activity_steps
) {
    ContinuationTraceResult trace;
    ContinuationState current_state;
    const HomogeneousChemicalEquilibriumNlp initial_problem(seeded_input, plan, layout);
    current_state.variables = initial_problem.initial_point();
    double current_lambda = 0.0;
    double step = 0.5;
    bool solved_initial_stage = false;

    for (int attempt = 0; attempt < maximum_stage_count; ++attempt) {
        const double target_lambda = solved_initial_stage
            ? std::min(1.0, current_lambda + step)
            : 0.0;
        const bool final_proof = std::abs(target_lambda - 1.0) <= 1.0e-12;
        ContinuationStageSpec stage = ce_activity_homotopy_stage(
            seeded_input,
            plan,
            layout,
            options,
            activity_continuation_stage_id(target_lambda, attempt),
            target_lambda,
            final_proof
        );
        ContinuationTraceResult stage_trace = run_continuation_plan({stage}, current_state);
        if (stage_trace.trace.empty()) {
            trace.final_proof_status = "rejected";
            trace.rejection_stage_id = stage.stage_id;
            break;
        }

        const ContinuationStageResult& stage_result = stage_trace.trace.back();
        trace.trace.push_back(stage_result);
        if (stage_result.final_proof) {
            trace.final_stage_id = stage_result.stage_id;
            trace.final_proof_status = stage_result.accepted ? "accepted" : "rejected";
        }

        if (stage_result.accepted) {
            accepted_activity_steps.push_back(target_lambda);
            current_state = stage_result.continuation_state;
            trace.continuation_state = current_state;
            current_lambda = target_lambda;
            solved_initial_stage = true;
            trace.rejection_stage_id.clear();
            if (final_proof) {
                break;
            }
            continue;
        }

        rejected_activity_steps.push_back(target_lambda);
        trace.rejection_stage_id = stage_result.stage_id;
        if (!solved_initial_stage) {
            break;
        }
        step *= 0.5;
        if (step < minimum_step) {
            break;
        }
        trace.rejection_stage_id.clear();
    }

    if (trace.final_proof_status == "pending") {
        trace.final_proof_status = trace.rejection_stage_id.empty() ? "no_final_stage" : "rejected";
    }
    trace.accepted = trace.rejection_stage_id.empty() && trace.final_proof_status == "accepted";
    return trace;
}

ChemicalEquilibriumNlpResult solve_eos_activity_continuation_from_seed(
    const ChemicalEquilibriumNlpInput& seeded_input,
    const epcsaft::native::equilibrium::ActivationPlan& plan,
    const epcsaft::native::equilibrium::VariableLayout& layout,
    const IpoptSolveOptions& options,
    double balance_tolerance,
    double reaction_stationarity_tolerance
) {
    ChemicalEquilibriumNlpInput true_input =
        chemical_equilibrium_input_with_activity_lambda(
            chemical_equilibrium_input_with_log_k_lambda(seeded_input, 1.0),
            1.0
        );
    constexpr double kActivityMinimumStep = 0.125;
    constexpr int kActivityMaximumStageCount = 20;
    std::vector<double> accepted_activity_steps;
    std::vector<double> rejected_activity_steps;
    ContinuationTraceResult trace = run_adaptive_eos_activity_continuation(
        seeded_input,
        plan,
        layout,
        options,
        kActivityMinimumStep,
        kActivityMaximumStageCount,
        accepted_activity_steps,
        rejected_activity_steps
    );
    ChemicalEquilibriumNlpResult out = result_from_homotopy_trace(
        true_input,
        plan,
        layout,
        trace,
        balance_tolerance,
        reaction_stationarity_tolerance
    );
    out.continuation_parameter_name = "activity_lambda";
    out.continuation_lambdas = accepted_activity_steps;
    out.activity_continuation_lambdas = accepted_activity_steps;
    out.activity_continuation_mode = "adaptive_bisection";
    out.activity_continuation_minimum_step = kActivityMinimumStep;
    out.activity_continuation_maximum_stage_count = kActivityMaximumStageCount;
    out.accepted_activity_steps = accepted_activity_steps;
    out.rejected_activity_steps = rejected_activity_steps;
    if (!out.accepted && trace_finished_final_lambda_one(trace)) {
        const HomogeneousChemicalEquilibriumNlp proof_problem(true_input, plan, layout);
        out.proof_corrector = proof_problem.correct_physical_proof(
            trace.trace.back().solve.variables,
            balance_tolerance,
            reaction_stationarity_tolerance
        );
        if (out.proof_corrector.accepted) {
            out.postsolve = out.proof_corrector.postsolve;
            out.balance_inf_norm = out.proof_corrector.balance_inf_norm;
            out.reaction_stationarity_inf_norm = out.proof_corrector.reaction_stationarity_inf_norm;
            out.proof_metrics = out.proof_corrector.proof_metrics;
            out.accepted = true;
            out.continuation.accepted = true;
            out.continuation.final_proof_status = "accepted";
        }
    }
    return out;
}

void record_seed_attempt_diagnostics(
    ChemicalEquilibriumNlpResult& result,
    bool caller_seed_attempted,
    bool caller_seed_final_proof_accepted,
    bool caller_seed_escalated,
    const std::string& caller_seed_rejection_reason = "",
    bool caller_seed_exception_observed = false,
    const std::string& caller_seed_exception_message = ""
) {
    result.caller_seed_attempted = caller_seed_attempted;
    result.caller_seed_final_proof_attempted = caller_seed_attempted;
    result.caller_seed_final_proof_accepted = caller_seed_attempted && caller_seed_final_proof_accepted;
    result.caller_seed_escalated = caller_seed_attempted && caller_seed_escalated;
    result.caller_seed_rejection_source = result.caller_seed_escalated ? "caller_initial_amounts" : "";
    result.caller_seed_rejection_reason = result.caller_seed_escalated ? caller_seed_rejection_reason : "";
    result.caller_seed_exception_observed = result.caller_seed_escalated && caller_seed_exception_observed;
    result.caller_seed_exception_message = result.caller_seed_exception_observed
        ? caller_seed_exception_message
        : "";
    result.accepted_seed_source = result.accepted ? result.seed_source : "";
    result.seed_attempt_order.clear();
    if (caller_seed_attempted) {
        result.seed_attempt_order.push_back("caller_initial_amounts");
    }
    if (!caller_seed_attempted || caller_seed_escalated) {
        result.seed_attempt_order.push_back("max_min_feasible_interior");
    }
}

}  // namespace

ChemicalEquilibriumNlpResult solve_activated_chemical_equilibrium_nlp(
    const ChemicalEquilibriumNlpInput& input,
    const epcsaft::native::equilibrium::ActivationPlan& plan,
    const epcsaft::native::equilibrium::VariableLayout& layout,
    const IpoptSolveOptions& options,
    double balance_tolerance,
    double reaction_stationarity_tolerance
) {
    if (input.eos_activity_enabled) {
        std::string caller_seed_rejection_reason;
        bool caller_seed_exception_observed = false;
        std::string caller_seed_exception_message;
        if (!input.initial_amounts.empty()) {
            try {
                ChemicalEquilibriumNlpResult out = solve_eos_activity_continuation_from_seed(
                    input,
                    plan,
                    layout,
                    options,
                    balance_tolerance,
                    reaction_stationarity_tolerance
                );
                out.source_oracle_initial_amounts = true;
                out.seed_source = "caller_initial_amounts";
                out.direct_final_proof_attempted = false;
                out.direct_final_proof_accepted = false;
                if (out.accepted) {
                    record_seed_attempt_diagnostics(out, true, true, false);
                    return out;
                }
                caller_seed_rejection_reason = "final_proof_rejected";
            } catch (const std::exception& exc) {
                caller_seed_rejection_reason = "caller_seed_exception";
                caller_seed_exception_observed = true;
                caller_seed_exception_message = exc.what();
                // A positive caller seed is only a hint; CE-owned initialization remains authoritative.
            }
        }

        FeasibleInitializationResult feasible = solve_max_min_feasible_initialization(
            chemical_equilibrium_feasible_initialization_input(input),
            ce_stage_options(options, "proof"),
            balance_tolerance
        );
        ChemicalEquilibriumNlpResult out;
        if (feasible.accepted) {
            ChemicalEquilibriumNlpInput seeded_input = input_with_initial_amounts(input, feasible.amounts);
            out = solve_eos_activity_continuation_from_seed(
                seeded_input,
                plan,
                layout,
                options,
                balance_tolerance,
                reaction_stationarity_tolerance
            );
        }
        out.source_oracle_initial_amounts = false;
        out.seed_source = "max_min_feasible_interior";
        out.feasible_initialization = feasible;
        out.direct_final_proof_attempted = false;
        out.direct_final_proof_accepted = false;
        record_seed_attempt_diagnostics(
            out,
            !input.initial_amounts.empty(),
            false,
            !input.initial_amounts.empty(),
            caller_seed_rejection_reason.empty() ? "final_proof_rejected" : caller_seed_rejection_reason,
            caller_seed_exception_observed,
            caller_seed_exception_message
        );
        return out;
    }

    bool caller_seed_attempted = false;
    bool caller_seed_final_proof_accepted = false;
    std::string caller_seed_rejection_reason;
    bool caller_seed_exception_observed = false;
    std::string caller_seed_exception_message;
    if (!input.initial_amounts.empty()) {
        caller_seed_attempted = true;
        try {
            ChemicalEquilibriumNlpInput true_input =
                chemical_equilibrium_input_with_log_k_lambda(input, 1.0);
            ChemicalEquilibriumNlpResult out = solve_single_ce_proof(
                true_input,
                plan,
                layout,
                options,
                balance_tolerance,
                reaction_stationarity_tolerance
            );
            const bool direct_proof_accepted = out.accepted;
            if (!out.accepted && !out.solve.variables.empty()) {
                const HomogeneousChemicalEquilibriumNlp proof_problem(true_input, plan, layout);
                out.proof_corrector = proof_problem.correct_physical_proof(
                    out.solve.variables,
                    balance_tolerance,
                    reaction_stationarity_tolerance
                );
                if (out.proof_corrector.accepted) {
                    out.postsolve = out.proof_corrector.postsolve;
                    out.balance_inf_norm = out.proof_corrector.balance_inf_norm;
                    out.reaction_stationarity_inf_norm = out.proof_corrector.reaction_stationarity_inf_norm;
                    out.proof_metrics = out.proof_corrector.proof_metrics;
                    out.accepted = true;
                }
            }
            out.source_oracle_initial_amounts = true;
            out.seed_source = "caller_initial_amounts";
            out.direct_final_proof_attempted = true;
            out.direct_final_proof_accepted = direct_proof_accepted;
            out.continuation.final_proof_status = out.accepted ? "accepted" : "rejected";
            out.continuation.final_stage_id = "lambda_1";
            out.continuation.accepted = out.accepted;
            out.continuation_lambdas = {1.0};
            caller_seed_final_proof_accepted = out.accepted;
            if (out.accepted) {
                record_seed_attempt_diagnostics(out, true, true, false);
                return out;
            }
            caller_seed_rejection_reason = "final_proof_rejected";
        } catch (const std::exception& exc) {
            caller_seed_final_proof_accepted = false;
            caller_seed_rejection_reason = "caller_seed_exception";
            caller_seed_exception_observed = true;
            caller_seed_exception_message = exc.what();
        }
    }

    FeasibleInitializationResult feasible = solve_max_min_feasible_initialization(
        chemical_equilibrium_feasible_initialization_input(input),
        ce_stage_options(options, "proof"),
        balance_tolerance
    );
    ChemicalEquilibriumNlpInput seeded_input = input_with_initial_amounts(input, feasible.amounts);
    ChemicalEquilibriumNlpInput true_input =
        chemical_equilibrium_input_with_log_k_lambda(seeded_input, 1.0);

    ChemicalEquilibriumNlpResult direct;
    if (feasible.accepted) {
        direct = solve_single_ce_proof(
            true_input,
            plan,
            layout,
            options,
            balance_tolerance,
            reaction_stationarity_tolerance
        );
    }
    const bool direct_proof_accepted = feasible.accepted && direct.accepted;
    if (feasible.accepted && !direct.accepted && !direct.solve.variables.empty()) {
        const HomogeneousChemicalEquilibriumNlp proof_problem(true_input, plan, layout);
        direct.proof_corrector = proof_problem.correct_physical_proof(
            direct.solve.variables,
            balance_tolerance,
            reaction_stationarity_tolerance
        );
        if (direct.proof_corrector.accepted) {
            direct.postsolve = direct.proof_corrector.postsolve;
            direct.balance_inf_norm = direct.proof_corrector.balance_inf_norm;
            direct.reaction_stationarity_inf_norm = direct.proof_corrector.reaction_stationarity_inf_norm;
            direct.proof_metrics = direct.proof_corrector.proof_metrics;
            direct.accepted = true;
        }
    }
    if (feasible.accepted && direct.accepted) {
        direct.source_oracle_initial_amounts = false;
        direct.seed_source = "max_min_feasible_interior";
        direct.feasible_initialization = feasible;
        direct.direct_final_proof_attempted = true;
        direct.direct_final_proof_accepted = direct_proof_accepted;
        direct.continuation.final_proof_status = "accepted";
        direct.continuation.final_stage_id = "lambda_1";
        direct.continuation.accepted = true;
        direct.continuation_lambdas = {1.0};
        record_seed_attempt_diagnostics(
            direct,
            caller_seed_attempted,
            caller_seed_final_proof_accepted,
            caller_seed_attempted && !caller_seed_final_proof_accepted,
            caller_seed_rejection_reason.empty() ? "final_proof_rejected" : caller_seed_rejection_reason,
            caller_seed_exception_observed,
            caller_seed_exception_message
        );
        return direct;
    }

    ContinuationTraceResult trace;
    std::vector<double> lambdas;
    if (feasible.accepted) {
        std::vector<ContinuationStageSpec> stages;
        stages.push_back(ce_homotopy_stage(seeded_input, plan, layout, options, "lambda_0", 0.0, false));
        stages.push_back(ce_homotopy_stage(seeded_input, plan, layout, options, "lambda_half", 0.5, false));
        stages.push_back(ce_homotopy_stage(seeded_input, plan, layout, options, "lambda_1", 1.0, true));
        ContinuationState initial_state;
        const HomogeneousChemicalEquilibriumNlp initial_problem(seeded_input, plan, layout);
        initial_state.variables = initial_problem.initial_point();
        trace = run_continuation_plan(stages, initial_state);
        lambdas = {0.0, 0.5, 1.0};
    }

    ChemicalEquilibriumNlpResult out = feasible.accepted
        ? result_from_homotopy_trace(
            true_input,
            plan,
            layout,
            trace,
            balance_tolerance,
            reaction_stationarity_tolerance
        )
        : ChemicalEquilibriumNlpResult{};
    out.continuation = trace;
    if (feasible.accepted
        && !out.accepted
        && !trace.trace.empty()
        && trace.final_stage_id == "lambda_1"
        && !trace.trace.back().solve.variables.empty()) {
        const HomogeneousChemicalEquilibriumNlp proof_problem(true_input, plan, layout);
        out.proof_corrector = proof_problem.correct_physical_proof(
            trace.trace.back().solve.variables,
            balance_tolerance,
            reaction_stationarity_tolerance
        );
        if (out.proof_corrector.accepted) {
            out.postsolve = out.proof_corrector.postsolve;
            out.balance_inf_norm = out.proof_corrector.balance_inf_norm;
            out.reaction_stationarity_inf_norm = out.proof_corrector.reaction_stationarity_inf_norm;
            out.proof_metrics = out.proof_corrector.proof_metrics;
            out.accepted = true;
            out.continuation.accepted = true;
            out.continuation.final_proof_status = "accepted";
        }
    }
    out.source_oracle_initial_amounts = false;
    out.seed_source = "max_min_feasible_interior";
    out.feasible_initialization = feasible;
    out.direct_final_proof_attempted = feasible.accepted;
    out.direct_final_proof_accepted = direct_proof_accepted;
    out.continuation_lambdas = lambdas;
    record_seed_attempt_diagnostics(
        out,
        caller_seed_attempted,
        caller_seed_final_proof_accepted,
        caller_seed_attempted && !caller_seed_final_proof_accepted,
        caller_seed_rejection_reason.empty() ? "final_proof_rejected" : caller_seed_rejection_reason,
        caller_seed_exception_observed,
        caller_seed_exception_message
    );
    return out;
}
}  // namespace epcsaft::native::equilibrium_nlp
