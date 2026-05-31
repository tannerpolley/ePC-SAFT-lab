#pragma once

#include "equilibrium/core/two_phase_eos_route.h"

namespace epcsaft::native::equilibrium_nlp {

enum class NlpContractSnapshotDetail {
    Basic,
    FullDerivativeEvidence,
};

NeutralTwoPhaseEosNlpContract make_neutral_two_phase_nlp_contract_snapshot(
    const NlpProblem& problem,
    int phase_count,
    int species_count,
    NlpContractSnapshotDetail detail
);

}  // namespace epcsaft::native::equilibrium_nlp
