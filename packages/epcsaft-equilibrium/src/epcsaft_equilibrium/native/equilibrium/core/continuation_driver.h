#pragma once

#include "equilibrium/solvers/ipopt_adapter.h"

#include <functional>
#include <memory>
#include <string>
#include <vector>

namespace epcsaft::native::equilibrium_nlp {

struct ContinuationState {
    std::vector<double> variables;
    std::vector<double> bound_lower_multipliers;
    std::vector<double> bound_upper_multipliers;
    std::vector<double> constraint_multipliers;

    bool empty() const {
        return variables.empty()
            && bound_lower_multipliers.empty()
            && bound_upper_multipliers.empty()
            && constraint_multipliers.empty();
    }
};

using ContinuationProblemFactory = std::function<std::unique_ptr<NlpProblem>()>;

struct ContinuationStageSpec {
    std::string stage_id;
    double parameter_value = 0.0;
    bool final_proof = false;
    IpoptSolveOptions options;
    ContinuationProblemFactory problem_factory;
};

struct ContinuationStageResult {
    std::string stage_id;
    double parameter_value = 0.0;
    bool final_proof = false;
    bool accepted = false;
    std::string acceptance_status = "rejected";
    std::string seeded_from_stage;
    ContinuationState initial_state;
    IpoptSolveResult solve;
    ContinuationState continuation_state;
};

struct ContinuationTraceResult {
    bool accepted = false;
    std::string final_proof_status = "pending";
    std::string final_stage_id;
    std::string rejection_stage_id;
    std::vector<ContinuationStageResult> trace;
    ContinuationState continuation_state;
};

ContinuationState continuation_state_from_solve_result(const IpoptSolveResult& result);

ContinuationTraceResult run_continuation_plan(
    const std::vector<ContinuationStageSpec>& stages,
    const ContinuationState& initial_state = {}
);

}  // namespace epcsaft::native::equilibrium_nlp
