#include "equilibrium/core/continuation_driver.h"

#include "model/native_types.h"

#include <cmath>
#include <set>

namespace epcsaft::native::equilibrium_nlp {

namespace {

void apply_continuation_state(
    IpoptSolveOptions& options,
    const ContinuationState& state
) {
    if (state.empty()) {
        return;
    }
    options.initial_variables = state.variables;
    options.initial_bound_lower_multipliers = state.bound_lower_multipliers;
    options.initial_bound_upper_multipliers = state.bound_upper_multipliers;
    options.initial_constraint_multipliers = state.constraint_multipliers;
}

void validate_stage_spec(
    const ContinuationStageSpec& stage,
    std::set<std::string>& seen_stage_ids
) {
    if (stage.stage_id.empty()) {
        throw ValueError("Continuation stage id must be non-empty.");
    }
    if (!seen_stage_ids.insert(stage.stage_id).second) {
        throw ValueError("Continuation stage id must be unique: " + stage.stage_id + ".");
    }
    if (!std::isfinite(stage.parameter_value)) {
        throw ValueError("Continuation stage parameter value must be finite.");
    }
    if (!stage.problem_factory) {
        throw ValueError("Continuation stage requires an NLP problem factory.");
    }
}

}  // namespace

ContinuationState continuation_state_from_solve_result(const IpoptSolveResult& result) {
    return {
        result.variables,
        result.bound_lower_multipliers,
        result.bound_upper_multipliers,
        result.constraint_multipliers,
    };
}

ContinuationTraceResult run_continuation_plan(
    const std::vector<ContinuationStageSpec>& stages,
    const ContinuationState& initial_state
) {
    if (stages.empty()) {
        throw ValueError("Continuation plan requires at least one stage.");
    }

    std::set<std::string> seen_stage_ids;
    for (const ContinuationStageSpec& stage : stages) {
        validate_stage_spec(stage, seen_stage_ids);
    }

    ContinuationTraceResult result;
    ContinuationState next_state = initial_state;
    std::string next_state_source = initial_state.empty() ? "" : "external";
    bool saw_final_proof = false;

    for (const ContinuationStageSpec& stage : stages) {
        std::unique_ptr<NlpProblem> problem = stage.problem_factory();
        if (!problem) {
            throw ValueError("Continuation stage returned an empty NLP problem: " + stage.stage_id + ".");
        }

        IpoptSolveOptions options = stage.options;
        apply_continuation_state(options, next_state);

        ContinuationStageResult stage_result;
        stage_result.stage_id = stage.stage_id;
        stage_result.parameter_value = stage.parameter_value;
        stage_result.final_proof = stage.final_proof;
        stage_result.seeded_from_stage = next_state_source;
        stage_result.initial_state = next_state;
        stage_result.solve = solve_ipopt_nlp(*problem, options);
        stage_result.accepted = stage_result.solve.accepted;
        stage_result.continuation_state = continuation_state_from_solve_result(stage_result.solve);

        result.trace.push_back(stage_result);

        if (stage.final_proof) {
            saw_final_proof = true;
            result.final_stage_id = stage.stage_id;
            result.final_proof_status = stage_result.accepted ? "accepted" : "rejected";
        }

        if (!stage_result.accepted) {
            result.rejection_stage_id = stage.stage_id;
            break;
        }

        next_state = stage_result.continuation_state;
        next_state_source = stage.stage_id;
        result.continuation_state = next_state;
    }

    if (!saw_final_proof && result.rejection_stage_id.empty()) {
        result.final_proof_status = "no_final_stage";
    }
    result.accepted = result.rejection_stage_id.empty()
        && (result.final_proof_status == "accepted" || result.final_proof_status == "no_final_stage");
    return result;
}

}  // namespace epcsaft::native::equilibrium_nlp
