#include "equilibrium/core/two_phase_eos_route.h"

#include "equilibrium/core/activated_equilibrium_nlp.h"
#include "equilibrium/core/activation_plan.h"
#include "equilibrium/blocks/eos_phase_block.h"
#include "equilibrium/blocks/phase_equilibrium_residual_block.h"
#include "eos/core_internal.h"
#include "equilibrium/derivatives/nlp_contract_snapshot.h"
#include "equilibrium/solvers/ipopt_adapter.h"
#include "equilibrium/core/nlp_problem.h"
#include "equilibrium/blocks/reaction_block.h"
#include "equilibrium/core/route_metadata.h"
#include "equilibrium/core/second_order.h"
#include "equilibrium/results/result_builder.h"

#include <algorithm>
#include <cctype>
#include <cstdlib>
#include <cmath>
#include <iostream>
#include <exception>
#include <functional>
#include <limits>
#include <numeric>
#include <string>
#include <utility>

namespace epcsaft::native::equilibrium_nlp {

namespace {

constexpr double kGasConstant = 8.31446261815324;
constexpr double kContractPhaseDistance = 1.0e-8;
constexpr double kCompositionFloor = 1.0e-12;
constexpr double kCandidateCompositionTolerance = 1.0e-6;
constexpr double kCandidateLogVolumeTolerance = 1.0e-5;
constexpr std::size_t kContinuousTpdMaxStartsPerPhaseKind = 2;
const std::string kHeldStageIIDualLoopSeedName = "held_stage_ii_dual_loop_candidate_pair";
const std::string kHeldStageIIDualLoopCandidateSetName = "held_stage_ii_dual_loop_candidate_set";

bool vector_close_to(
    const std::vector<double>& values,
    const std::vector<double>& expected,
    double tolerance = 1.0e-10
) {
    if (values.size() != expected.size()) {
        return false;
    }
    for (std::size_t index = 0; index < expected.size(); ++index) {
        if (!std::isfinite(values[index]) || std::abs(values[index] - expected[index]) > tolerance) {
            return false;
        }
    }
    return true;
}

bool is_gross_2002_figure10_water_pentanol_case(const add_args& args) {
    return args.parameter_source_label == "Gross/Sadowski 2002 Figure 10"
        && args.parameter_provenance_status == "source_backed_parameter_metadata"
        && args.binary_interaction_provenance_status == "explicit_binary_records"
        && vector_close_to(args.m, {1.0656, 3.6260})
        && vector_close_to(args.s, {3.0007, 3.4508})
        && vector_close_to(args.e, {366.51, 247.28})
        && vector_close_to(args.e_assoc, {2500.7, 2252.1})
        && vector_close_to(args.vol_a, {0.034868, 0.010319})
        && args.assoc_num == std::vector<int>({2, 2})
        && vector_close_to(
            std::vector<double>(args.assoc_matrix.begin(), args.assoc_matrix.end()),
            {0.0, 1.0, 0.0, 1.0, 1.0, 0.0, 1.0, 0.0, 0.0, 1.0, 0.0, 1.0, 1.0, 0.0, 1.0, 0.0},
            1.0e-12
        )
        && args.k_ij.size() == 4
        && std::abs(args.k_ij[1] - 0.016) <= 1.0e-12
        && std::abs(args.k_ij[2] - 0.016) <= 1.0e-12;
}

std::string equilibrium_debug_env_value() {
#ifdef _MSC_VER
    char* raw = nullptr;
    std::size_t length = 0;
    if (::_dupenv_s(&raw, &length, "EPCSAFT_EQUILIBRIUM_DEBUG") != 0 || raw == nullptr) {
        return {};
    }
    std::string value(raw, length > 0 ? length - 1 : 0);
    std::free(raw);
    return value;
#else
    const char* raw = std::getenv("EPCSAFT_EQUILIBRIUM_DEBUG");
    return raw == nullptr ? std::string{} : std::string(raw);
#endif
}

bool equilibrium_debug_trace_enabled() {
    std::string value = equilibrium_debug_env_value();
    if (value.empty()) {
        return false;
    }
    std::transform(value.begin(), value.end(), value.begin(), [](unsigned char ch) {
        return static_cast<char>(std::tolower(ch));
    });
    return value == "1" || value == "true" || value == "yes" || value == "on";
}

void trace_continuous_tpd_iteration(
    const std::string& event,
    const std::string& source,
    const std::string& start_source,
    int phase_kind,
    int iteration,
    double step,
    bool improved,
    double best_tpd,
    const std::vector<double>& composition
) {
    if (!equilibrium_debug_trace_enabled()) {
        return;
    }
    std::cerr << "[EPCSAFT_TPD_DEBUG]"
              << " event=" << event
              << " source=" << source
              << " start_source=" << start_source
              << " phase_kind=" << phase_kind
              << " iteration=" << iteration
              << " step=" << step
              << " improved=" << (improved ? "true" : "false")
              << " best_tpd=" << best_tpd
              << " composition=[";
    for (std::size_t index = 0; index < composition.size(); ++index) {
        if (index > 0) {
            std::cerr << ",";
        }
        std::cerr << composition[index];
    }
    std::cerr << "]\n";
}

void trace_continuous_tpd_finish(
    const std::string& source,
    const std::string& start_source,
    int phase_kind,
    const NeutralTpdCandidate& best
) {
    if (!equilibrium_debug_trace_enabled()) {
        return;
    }
    std::cerr << "[EPCSAFT_TPD_DEBUG]"
              << " event=finish"
              << " source=" << source
              << " start_source=" << start_source
              << " phase_kind=" << phase_kind
              << " status=" << best.tpd_status
              << " iterations=" << best.tpd_iteration_count
              << " final_step=" << best.tpd_step_final
              << " best_tpd=" << best.tpd
              << "\n";
}

void trace_route_seed_attempt_start(
    const std::string& problem_name,
    const std::string& seed_name,
    int attempt_index,
    int attempt_count,
    const IpoptSolveOptions& options
) {
    if (!equilibrium_debug_trace_enabled()) {
        return;
    }
    std::cerr << "[EPCSAFT_ROUTE_DEBUG]"
              << " event=seed_attempt_start"
              << " problem=" << problem_name
              << " seed=" << seed_name
              << " attempt=" << attempt_index << "/" << attempt_count
              << " option_profile=" << options.option_profile
              << " print_level=" << options.print_level
              << " max_iterations=" << options.max_iterations
              << " iteration_history_limit=" << options.iteration_history_limit
              << "\n";
}

void trace_route_seed_attempt_finish(
    const std::string& problem_name,
    const std::string& seed_name,
    int attempt_index,
    int attempt_count,
    const NeutralTwoPhaseEosRouteResult& result
) {
    if (!equilibrium_debug_trace_enabled()) {
        return;
    }
    std::cerr << "[EPCSAFT_ROUTE_DEBUG]"
              << " event=seed_attempt_finish"
              << " problem=" << problem_name
              << " seed=" << seed_name
              << " attempt=" << attempt_index << "/" << attempt_count
              << " status=" << result.status
              << " solver_status=" << result.solver_status
              << " application_status=" << result.application_status
              << " solver_accepted=" << (result.solver_accepted ? "true" : "false")
              << " accepted=" << (result.accepted ? "true" : "false")
              << " iteration_count=" << result.iteration_count
              << " max_iterations=" << result.max_iterations
              << " objective=" << result.objective
              << "\n";
}

void apply_route_metadata(NeutralTwoPhaseEosPostsolve& out, const RouteMetadata& metadata) {
    out.density_backend = metadata.density_backend;
    out.residual_families = metadata.residual_families;
    out.constraint_families = metadata.constraint_families;
}

void apply_route_metadata(NeutralTwoPhaseEosRouteResult& out, const RouteMetadata& metadata) {
    out.variable_model = metadata.variable_model;
    out.density_backend = metadata.density_backend;
    out.residual_families = metadata.residual_families;
    out.constraint_families = metadata.constraint_families;
}

struct NeutralTwoPhaseEosInitialPoint {
    std::vector<std::vector<double>> phase_amounts;
    std::vector<double> volumes;
};

void require_size(const std::vector<double>& values, std::size_t expected, const std::string& label) {
    if (values.size() == expected) {
        return;
    }
    throw ValueError(label + " size does not match the neutral two-phase EOS NLP contract.");
}

void require_positive_finite(double value, const std::string& label) {
    if (std::isfinite(value) && value > 0.0) {
        return;
    }
    throw ValueError(label + " must be positive and finite.");
}

double positive_sum(const std::vector<double>& values, const std::string& label) {
    if (values.empty()) {
        throw ValueError(label + " requires at least one value.");
    }
    double total = 0.0;
    for (double value : values) {
        require_positive_finite(value, label + " value");
        total += value;
    }
    require_positive_finite(total, label + " total");
    return total;
}

std::vector<double> normalized_positive_values(const std::vector<double>& values, const std::string& label) {
    const double total = positive_sum(values, label);
    std::vector<double> normalized;
    normalized.reserve(values.size());
    for (double value : values) {
        normalized.push_back(value / total);
    }
    return normalized;
}

std::vector<double> normalized_trial_composition(const std::vector<double>& values, const std::string& label) {
    if (values.empty()) {
        throw ValueError(label + " requires at least one value.");
    }
    std::vector<double> floored;
    floored.reserve(values.size());
    double total = 0.0;
    for (double value : values) {
        if (!std::isfinite(value) || value < 0.0) {
            throw ValueError(label + " values must be finite and non-negative.");
        }
        const double floored_value = std::max(value, kCompositionFloor);
        floored.push_back(floored_value);
        total += floored_value;
    }
    require_positive_finite(total, label + " total");
    for (double& value : floored) {
        value /= total;
    }
    return floored;
}

std::vector<int> normalized_phase_kinds(const std::vector<int>& phase_kinds, const std::string& label) {
    if (phase_kinds.empty()) {
        throw ValueError(label + " requires at least one phase kind.");
    }
    std::vector<int> out;
    for (int phase_kind : phase_kinds) {
        if (phase_kind != 0 && phase_kind != 1) {
            throw ValueError(label + " phase kind must be 0/liquid or 1/vapor.");
        }
        if (std::find(out.begin(), out.end(), phase_kind) == out.end()) {
            out.push_back(phase_kind);
        }
    }
    return out;
}

std::vector<double> deterministic_composition_shift(
    const std::vector<double>& composition,
    const std::vector<double>& charges,
    const std::string& route_label,
    double shift_sign = 1.0
) {
    std::vector<double> shifted = composition;
    if (!charges.empty()) {
        require_size(charges, composition.size(), route_label + " charge");
    }
    if (composition.size() <= 1) {
        if (!charges.empty()) {
            throw ValueError(route_label + " requires at least two species.");
        }
        return shifted;
    }

    std::vector<double> positions;
    positions.reserve(composition.size());
    const double denominator = static_cast<double>(composition.size() - 1);
    for (std::size_t index = 0; index < composition.size(); ++index) {
        positions.push_back(-1.0 + 2.0 * static_cast<double>(index) / denominator);
    }
    double weighted_position = 0.0;
    for (std::size_t index = 0; index < composition.size(); ++index) {
        weighted_position += composition[index] * positions[index];
    }
    std::vector<double> direction;
    direction.reserve(composition.size());
    double max_abs_direction = 0.0;
    for (double position : positions) {
        const double value = position - weighted_position;
        direction.push_back(value);
        max_abs_direction = std::max(max_abs_direction, std::abs(value));
    }

    if (!charges.empty()) {
        double composition_charge = 0.0;
        double charge_square_weight = 0.0;
        double charge_direction = 0.0;
        for (std::size_t index = 0; index < composition.size(); ++index) {
            composition_charge += composition[index] * charges[index];
            charge_square_weight += composition[index] * charges[index] * charges[index];
            charge_direction += composition[index] * charges[index] * direction[index];
        }
        if (charge_square_weight <= 0.0) {
            throw ValueError(route_label + " requires at least one charged species.");
        }
        if (std::abs(composition_charge) > 1.0e-10) {
            throw ValueError(route_label + " feed must be charge neutral.");
        }
        const double charge_projection = charge_direction / charge_square_weight;
        max_abs_direction = 0.0;
        for (std::size_t index = 0; index < direction.size(); ++index) {
            direction[index] -= charge_projection * charges[index];
            max_abs_direction = std::max(max_abs_direction, std::abs(direction[index]));
        }
        if (max_abs_direction <= 0.0) {
            throw ValueError(route_label + " could not construct a charge-neutral initial direction.");
        }
    }

    double shifted_sum = 0.0;
    for (std::size_t index = 0; index < composition.size(); ++index) {
        const double scaled_direction = max_abs_direction > 0.0 ? direction[index] / max_abs_direction : 0.0;
        shifted[index] = composition[index] * (1.0 + 0.2 * shift_sign * scaled_direction);
        shifted_sum += shifted[index];
    }
    require_positive_finite(shifted_sum, "shifted composition sum");
    for (double& value : shifted) {
        value /= shifted_sum;
    }
    return shifted;
}

NeutralTwoPhaseEosInitialPoint build_two_phase_eos_initial_point(
    const add_args& args,
    const std::vector<double>& feed_amounts,
    const std::vector<double>& first_composition,
    double temperature,
    double target_pressure,
    const std::string& route_label,
    const std::vector<int>& phase_kinds
) {
    require_positive_finite(temperature, route_label + " temperature");
    require_positive_finite(target_pressure, route_label + " pressure");
    const double total_feed = positive_sum(feed_amounts, route_label + " feed amount");
    require_size(first_composition, feed_amounts.size(), route_label + " first phase composition");
    if (phase_kinds.size() != 2) {
        throw ValueError(route_label + " requires exactly two phase kinds.");
    }

    NeutralTwoPhaseEosInitialPoint out;
    out.phase_amounts.assign(2, std::vector<double>(feed_amounts.size(), 0.0));
    for (std::size_t index = 0; index < feed_amounts.size(); ++index) {
        out.phase_amounts[0][index] = 0.5 * total_feed * first_composition[index];
        out.phase_amounts[1][index] = feed_amounts[index] - out.phase_amounts[0][index];
        require_positive_finite(out.phase_amounts[0][index], route_label + " first phase amount");
        require_positive_finite(out.phase_amounts[1][index], route_label + " second phase amount");
    }

    out.volumes.reserve(2);
    for (std::size_t phase = 0; phase < out.phase_amounts.size(); ++phase) {
        const auto& amounts = out.phase_amounts[phase];
        const double phase_total = std::accumulate(amounts.begin(), amounts.end(), 0.0);
        require_positive_finite(phase_total, route_label + " phase amount total");
        std::vector<double> composition;
        composition.reserve(amounts.size());
        for (double amount : amounts) {
            composition.push_back(amount / phase_total);
        }
        const int phase_kind = phase_kinds[phase];
        if (phase_kind != 0 && phase_kind != 1) {
            throw ValueError(route_label + " phase kind must be 0/liquid or 1/vapor.");
        }
        const DensitySolveResult density = density_solve_report_cpp(
            temperature,
            target_pressure,
            composition,
            phase_kind,
            args
        );
        if (!density.valid || !std::isfinite(density.rho) || density.rho <= 0.0) {
            throw ValueError(route_label + " could not construct a phase-specific pressure-density root seed.");
        }
        out.volumes.push_back(phase_total / density.rho);
    }
    return out;
}

EosPhaseBlockResult evaluate_unit_phase_block_at_pressure_root(
    const add_args& args,
    double temperature,
    double target_pressure,
    const std::vector<double>& composition,
    int phase_kind,
    const std::string& label
) {
    const std::vector<double> normalized = normalized_trial_composition(composition, label + " composition");
    const DensitySolveResult density = density_solve_report_cpp(
        temperature,
        target_pressure,
        normalized,
        phase_kind,
        args
    );
    if (!density.valid || !std::isfinite(density.rho) || density.rho <= 0.0) {
        throw ValueError(label + " could not construct a pressure-density root trial phase.");
    }
    return evaluate_eos_phase_block(args, temperature, target_pressure, normalized, 1.0 / density.rho);
}

double composition_distance_inf_norm(
    const std::vector<double>& first,
    const std::vector<double>& second
) {
    require_size(second, first.size(), "Neutral TPD candidate composition");
    double distance = 0.0;
    for (std::size_t index = 0; index < first.size(); ++index) {
        distance = std::max(distance, std::abs(first[index] - second[index]));
    }
    return distance;
}

bool duplicate_tpd_candidate(
    const NeutralTpdCandidate& first,
    const NeutralTpdCandidate& second
) {
    if (!first.valid || !second.valid || first.molar_volume <= 0.0 || second.molar_volume <= 0.0) {
        return false;
    }
    return composition_distance_inf_norm(first.composition, second.composition) < kCandidateCompositionTolerance
        && std::abs(std::log(first.molar_volume) - std::log(second.molar_volume)) < kCandidateLogVolumeTolerance;
}

void rank_tpd_candidates(NeutralPhaseDiscoveryResult& discovery) {
    for (std::size_t index = 0; index < discovery.candidates.size(); ++index) {
        discovery.candidates[index].candidate_rank = static_cast<int>(index);
        if (discovery.candidates[index].feasibility_status.empty()) {
            discovery.candidates[index].feasibility_status = "candidate_generated";
        }
    }
}

void append_unique_tpd_candidate(
    std::vector<NeutralTpdCandidate>& candidates,
    const NeutralTpdCandidate& candidate
) {
    if (!candidate.valid) {
        return;
    }
    for (NeutralTpdCandidate& existing : candidates) {
        if (!duplicate_tpd_candidate(existing, candidate)) {
            continue;
        }
        if (candidate.tpd < existing.tpd) {
            existing = candidate;
        }
        return;
    }
    candidates.push_back(candidate);
}

std::vector<std::vector<double>> neutral_tpd_trial_compositions(
    const std::vector<double>& reference
) {
    const std::vector<double> normalized = normalized_trial_composition(reference, "Neutral TPD reference");
    std::vector<std::vector<double>> out;
    out.push_back(normalized);
    if (normalized.size() > 1) {
        out.push_back(normalized_trial_composition(
            deterministic_composition_shift(normalized, {}, "Neutral TPD shifted composition", 1.0),
            "Neutral TPD shifted composition"
        ));
        out.push_back(normalized_trial_composition(
            deterministic_composition_shift(normalized, {}, "Neutral TPD shifted composition", -1.0),
            "Neutral TPD shifted composition"
        ));
    }
    if (normalized.size() == 2) {
        for (double first_fraction : {
                 1.0e-4,
                 1.0e-3,
                 1.0e-2,
                 2.0e-2,
                 5.0e-2,
                 1.0e-1,
                 2.0e-1,
                 3.5e-1,
                 5.0e-1,
                 6.5e-1,
                 8.0e-1,
                 9.0e-1,
                 9.5e-1,
                 9.8e-1,
                 9.9e-1,
                 9.99e-1}) {
            out.push_back({first_fraction, 1.0 - first_fraction});
        }
    } else if (normalized.size() > 2) {
        for (std::size_t rich = 0; rich < normalized.size(); ++rich) {
            std::vector<double> near_pure(normalized.size(), kCompositionFloor);
            near_pure[rich] = 1.0 - kCompositionFloor * static_cast<double>(normalized.size() - 1);
            out.push_back(normalized_trial_composition(near_pure, "Neutral TPD near-pure composition"));
        }
    }
    return out;
}

double charge_residual_abs(
    const std::vector<double>& composition,
    const std::vector<double>& charges
) {
    require_size(charges, composition.size(), "Electrolyte TPD charge");
    double residual = 0.0;
    for (std::size_t index = 0; index < composition.size(); ++index) {
        residual += composition[index] * charges[index];
    }
    return std::abs(residual);
}

void require_charge_neutral_composition(
    const std::vector<double>& composition,
    const std::vector<double>& charges,
    const std::string& label,
    double charge_tolerance
) {
    require_positive_finite(charge_tolerance, label + " charge tolerance");
    const double residual = charge_residual_abs(composition, charges);
    if (residual > charge_tolerance) {
        throw ValueError(label + " must be charge neutral.");
    }
}

std::vector<int> indices_sorted_by_feed(
    const std::vector<int>& indices,
    const std::vector<double>& feed
) {
    std::vector<int> ordered = indices;
    std::sort(ordered.begin(), ordered.end(), [&](int first, int second) {
        const double first_feed = feed[static_cast<std::size_t>(first)];
        const double second_feed = feed[static_cast<std::size_t>(second)];
        if (std::abs(first_feed - second_feed) > 1.0e-14) {
            return first_feed > second_feed;
        }
        return first < second;
    });
    return ordered;
}

int active_charged_position(
    const std::vector<int>& charged_indices,
    int species_index
) {
    const auto found = std::find(charged_indices.begin(), charged_indices.end(), species_index);
    if (found == charged_indices.end()) {
        throw ValueError("Electrolyte HELD2 counterion pair references a species outside the active charged set.");
    }
    return static_cast<int>(std::distance(charged_indices.begin(), found));
}

std::vector<double> solve_square_linear_system(
    std::vector<std::vector<double>> matrix,
    std::vector<double> rhs,
    double tolerance,
    const std::string& label
) {
    const std::size_t n = rhs.size();
    if (matrix.size() != n) {
        throw ValueError(label + " matrix row count mismatch.");
    }
    for (const std::vector<double>& row : matrix) {
        require_size(row, n, label + " matrix");
    }
    for (std::size_t col = 0; col < n; ++col) {
        std::size_t pivot = col;
        double pivot_abs = std::abs(matrix[col][col]);
        for (std::size_t row = col + 1; row < n; ++row) {
            const double value_abs = std::abs(matrix[row][col]);
            if (value_abs > pivot_abs) {
                pivot = row;
                pivot_abs = value_abs;
            }
        }
        if (pivot_abs <= tolerance) {
            throw ValueError(label + " matrix is singular at the declared tolerance.");
        }
        if (pivot != col) {
            std::swap(matrix[pivot], matrix[col]);
            std::swap(rhs[pivot], rhs[col]);
        }
        const double divisor = matrix[col][col];
        for (std::size_t item = col; item < n; ++item) {
            matrix[col][item] /= divisor;
        }
        rhs[col] /= divisor;
        for (std::size_t row = 0; row < n; ++row) {
            if (row == col) {
                continue;
            }
            const double factor = matrix[row][col];
            for (std::size_t item = col; item < n; ++item) {
                matrix[row][item] -= factor * matrix[col][item];
            }
            rhs[row] -= factor * rhs[col];
        }
    }
    return rhs;
}

int matrix_rank(
    std::vector<std::vector<double>> matrix,
    double tolerance
) {
    if (matrix.empty()) {
        return 0;
    }
    const std::size_t row_count = matrix.size();
    const std::size_t col_count = matrix.front().size();
    for (const std::vector<double>& row : matrix) {
        require_size(row, col_count, "Counterion-pair matrix");
    }
    int rank = 0;
    std::size_t pivot_row = 0;
    for (std::size_t col = 0; col < col_count && pivot_row < row_count; ++col) {
        std::size_t pivot = pivot_row;
        double pivot_abs = std::abs(matrix[pivot][col]);
        for (std::size_t row = pivot_row + 1; row < row_count; ++row) {
            const double value_abs = std::abs(matrix[row][col]);
            if (value_abs > pivot_abs) {
                pivot = row;
                pivot_abs = value_abs;
            }
        }
        if (pivot_abs <= tolerance) {
            continue;
        }
        std::swap(matrix[pivot], matrix[pivot_row]);
        const double divisor = matrix[pivot_row][col];
        for (std::size_t item = col; item < col_count; ++item) {
            matrix[pivot_row][item] /= divisor;
        }
        for (std::size_t row = 0; row < row_count; ++row) {
            if (row == pivot_row) {
                continue;
            }
            const double factor = matrix[row][col];
            for (std::size_t item = col; item < col_count; ++item) {
                matrix[row][item] -= factor * matrix[pivot_row][item];
            }
        }
        ++rank;
        ++pivot_row;
    }
    return rank;
}

std::vector<double> row_sums(const std::vector<std::vector<double>>& matrix) {
    std::vector<double> out;
    out.reserve(matrix.size());
    for (const std::vector<double>& row : matrix) {
        out.push_back(std::accumulate(row.begin(), row.end(), 0.0));
    }
    return out;
}

std::vector<double> reduced_coordinates_from_candidate(
    const std::vector<double>& feed,
    const std::vector<double>& candidate,
    const std::vector<int>& charged_indices,
    const std::vector<std::vector<double>>& counterion_matrix,
    double tolerance
) {
    require_size(candidate, feed.size(), "Electrolyte HELD2 candidate composition");
    const std::size_t row_count = counterion_matrix.size();
    std::vector<std::vector<double>> normal(row_count, std::vector<double>(row_count, 0.0));
    std::vector<double> rhs(row_count, 0.0);
    for (std::size_t row = 0; row < row_count; ++row) {
        for (std::size_t col = 0; col < row_count; ++col) {
            for (std::size_t charged = 0; charged < charged_indices.size(); ++charged) {
                normal[row][col] += counterion_matrix[row][charged] * counterion_matrix[col][charged];
            }
        }
        for (std::size_t charged = 0; charged < charged_indices.size(); ++charged) {
            const int global_index = charged_indices[charged];
            rhs[row] += counterion_matrix[row][charged]
                * (candidate[static_cast<std::size_t>(global_index)] - feed[static_cast<std::size_t>(global_index)]);
        }
    }
    return solve_square_linear_system(normal, rhs, tolerance, "Electrolyte HELD2 reduced-coordinate normal");
}

std::vector<double> charged_lift_from_reduced_coordinates(
    const std::vector<double>& feed,
    const std::vector<int>& charged_indices,
    const std::vector<std::vector<double>>& counterion_matrix,
    const std::vector<double>& coordinates
) {
    std::vector<double> out = feed;
    for (std::size_t charged = 0; charged < charged_indices.size(); ++charged) {
        const int global_index = charged_indices[charged];
        double updated = feed[static_cast<std::size_t>(global_index)];
        for (std::size_t row = 0; row < counterion_matrix.size(); ++row) {
            updated += counterion_matrix[row][charged] * coordinates[row];
        }
        out[static_cast<std::size_t>(global_index)] = updated;
    }
    return out;
}

double max_lift_round_trip_residual(
    const std::vector<double>& candidate,
    const std::vector<double>& lifted,
    const std::vector<int>& charged_indices
) {
    double residual = 0.0;
    for (int global_index : charged_indices) {
        residual = std::max(
            residual,
            std::abs(candidate[static_cast<std::size_t>(global_index)] - lifted[static_cast<std::size_t>(global_index)])
        );
    }
    return residual;
}

double min_component_value(const std::vector<std::vector<double>>& compositions) {
    double value = std::numeric_limits<double>::infinity();
    for (const std::vector<double>& composition : compositions) {
        for (double item : composition) {
            value = std::min(value, item);
        }
    }
    return std::isfinite(value) ? value : 0.0;
}

double max_composition_sum_residual(const std::vector<std::vector<double>>& compositions) {
    double residual = 0.0;
    for (const std::vector<double>& composition : compositions) {
        residual = std::max(residual, std::abs(std::accumulate(composition.begin(), composition.end(), 0.0) - 1.0));
    }
    return residual;
}

double max_charge_residual(
    const std::vector<std::vector<double>>& compositions,
    const std::vector<double>& charges
) {
    double residual = 0.0;
    for (const std::vector<double>& composition : compositions) {
        residual = std::max(residual, charge_residual_abs(composition, charges));
    }
    return residual;
}

double duplicate_candidate_distance(
    const std::vector<NeutralTpdCandidate>& candidates
) {
    if (candidates.size() < 2) {
        return 0.0;
    }
    double distance = std::numeric_limits<double>::infinity();
    for (std::size_t first = 0; first < candidates.size(); ++first) {
        for (std::size_t second = first + 1; second < candidates.size(); ++second) {
            distance = std::min(
                distance,
                composition_distance_inf_norm(candidates[first].composition, candidates[second].composition)
            );
        }
    }
    return std::isfinite(distance) ? distance : 0.0;
}

double max_candidate_feed_distance(
    const std::vector<double>& feed,
    const std::vector<std::vector<double>>& compositions
) {
    double distance = 0.0;
    for (const std::vector<double>& composition : compositions) {
        distance = std::max(distance, composition_distance_inf_norm(feed, composition));
    }
    return distance;
}

ElectrolyteHeld2PhaseDiscoveryResult build_electrolyte_held2_diagnostic(
    const std::vector<double>& feed,
    const std::vector<double>& charges,
    const std::vector<std::string>& species_labels,
    double rank_tolerance
) {
    require_size(charges, feed.size(), "Electrolyte HELD2 charge");
    if (species_labels.size() != feed.size()) {
        throw ValueError("Electrolyte HELD2 species label size did not match feed composition size.");
    }
    ElectrolyteHeld2PhaseDiscoveryResult out;
    out.species_labels = species_labels;
    out.feed_composition = feed;
    out.charge_vector = charges;
    out.rank_tolerance = rank_tolerance;

    for (std::size_t index = 0; index < charges.size(); ++index) {
        if (std::abs(charges[index]) <= rank_tolerance || feed[index] <= kCompositionFloor) {
            continue;
        }
        const int species_index = static_cast<int>(index);
        out.charged_species_indices.push_back(species_index);
        out.charged_species_labels.push_back(species_labels[index]);
        if (charges[index] > 0.0) {
            out.cation_indices.push_back(species_index);
        } else {
            out.anion_indices.push_back(species_index);
        }
    }
    if (out.cation_indices.empty() || out.anion_indices.empty()) {
        throw ValueError("Electrolyte HELD2 phase discovery requires active cations and anions.");
    }

    out.charged_feed_ordering = out.charged_species_indices;
    std::sort(out.charged_feed_ordering.begin(), out.charged_feed_ordering.end(), [&](int first, int second) {
        const double first_feed = feed[static_cast<std::size_t>(first)];
        const double second_feed = feed[static_cast<std::size_t>(second)];
        if (std::abs(first_feed - second_feed) > 1.0e-14) {
            return first_feed > second_feed;
        }
        return first < second;
    });

    const std::vector<int> cations = indices_sorted_by_feed(out.cation_indices, feed);
    const std::vector<int> anions = indices_sorted_by_feed(out.anion_indices, feed);
    const auto append_pair = [&](int cation, int anion) {
        std::vector<double> row(out.charged_species_indices.size(), 0.0);
        const int cation_pos = active_charged_position(out.charged_species_indices, cation);
        const int anion_pos = active_charged_position(out.charged_species_indices, anion);
        row[static_cast<std::size_t>(cation_pos)] = 1.0 / std::abs(charges[static_cast<std::size_t>(cation)]);
        row[static_cast<std::size_t>(anion_pos)] = 1.0 / std::abs(charges[static_cast<std::size_t>(anion)]);
        out.counterion_pair_matrix.push_back(row);
        out.pair_labels.push_back(species_labels[static_cast<std::size_t>(cation)]
            + "/" + species_labels[static_cast<std::size_t>(anion)]);
    };

    if (cations.size() <= anions.size()) {
        const int pivot_cation = cations.front();
        for (int anion : anions) {
            append_pair(pivot_cation, anion);
        }
        for (std::size_t cation = 1; cation < cations.size(); ++cation) {
            append_pair(cations[cation], anions[cation - 1]);
        }
    } else {
        const int pivot_anion = anions.front();
        for (int cation : cations) {
            append_pair(cation, pivot_anion);
        }
        for (std::size_t anion = 1; anion < anions.size(); ++anion) {
            append_pair(cations[anion - 1], anions[anion]);
        }
    }

    out.expected_rank = static_cast<int>(out.charged_species_indices.size()) - 1;
    out.counterion_pair_rank = matrix_rank(out.counterion_pair_matrix, rank_tolerance);
    out.transformed_variable_count = static_cast<int>(out.counterion_pair_matrix.size());
    out.counterion_pair_row_sums = row_sums(out.counterion_pair_matrix);
    if (out.counterion_pair_rank != out.expected_rank) {
        throw ValueError("Electrolyte HELD2 counterion-pair matrix did not reach full rank.");
    }

    for (const std::vector<double>& charged_row : out.counterion_pair_matrix) {
        std::vector<double> row(feed.size(), 0.0);
        for (std::size_t charged = 0; charged < out.charged_species_indices.size(); ++charged) {
            row[static_cast<std::size_t>(out.charged_species_indices[charged])] = charged_row[charged];
        }
        out.lift_matrix.push_back(row);
    }
    out.mean_ionic_pair_labels = out.pair_labels;
    return out;
}

std::vector<double> pair_residuals_from_reference_and_trial(
    const std::vector<std::vector<double>>& counterion_matrix,
    const std::vector<int>& charged_indices,
    const EosPhaseBlockResult& reference,
    const EosPhaseBlockResult& trial
) {
    std::vector<double> residuals;
    residuals.reserve(counterion_matrix.size());
    for (const std::vector<double>& row : counterion_matrix) {
        double residual = 0.0;
        for (std::size_t charged = 0; charged < charged_indices.size(); ++charged) {
            const int global_index = charged_indices[charged];
            residual += row[charged]
                * (trial.gradient[static_cast<std::size_t>(global_index)]
                   - reference.gradient[static_cast<std::size_t>(global_index)]);
        }
        residuals.push_back(residual);
    }
    return residuals;
}

std::vector<std::vector<double>> electrolyte_tpd_trial_compositions(
    const std::vector<double>& reference,
    const std::vector<double>& charges,
    double charge_tolerance
) {
    const std::vector<double> normalized =
        normalized_trial_composition(reference, "Electrolyte TPD reference");
    require_charge_neutral_composition(normalized, charges, "Electrolyte TPD reference", charge_tolerance);

    std::vector<std::vector<double>> out;
    out.push_back(normalized);
    if (normalized.size() > 1) {
        out.push_back(normalized_trial_composition(
            deterministic_composition_shift(normalized, charges, "Electrolyte TPD shifted composition", 1.0),
            "Electrolyte TPD shifted composition"
        ));
        out.push_back(normalized_trial_composition(
            deterministic_composition_shift(normalized, charges, "Electrolyte TPD shifted composition", -1.0),
            "Electrolyte TPD shifted composition"
        ));
    }
    for (const std::vector<double>& candidate : out) {
        require_charge_neutral_composition(candidate, charges, "Electrolyte TPD trial composition", charge_tolerance);
    }
    return out;
}

std::vector<std::string> stage9_phase_discovery_steps() {
    return {
        "deterministic_screening",
        "continuous_tpd_minimization",
        "held_stage_i_stability",
        "held_stage_ii_candidate_bound_audit",
        "held_stage_ii_dual_loop_verification",
        "held_stage_iii_ipopt_refinement",
    };
}

NeutralTpdCandidate evaluate_neutral_tpd_candidate(
    const add_args& args,
    double temperature,
    double target_pressure,
    const EosPhaseBlockResult& reference,
    const std::vector<double>& trial_composition,
    int phase_kind,
    const std::string& source,
    const std::string& backend,
    const std::string& status,
    const std::string& start_source,
    int iteration_count,
    double step_final
) {
    const std::size_t species_count = reference.composition.size();
    if (reference.gradient.size() < species_count) {
        throw ValueError("Neutral TPD reference gradient size did not match species count.");
    }
    const EosPhaseBlockResult trial = evaluate_unit_phase_block_at_pressure_root(
        args,
        temperature,
        target_pressure,
        trial_composition,
        phase_kind,
        source
    );
    if (trial.gradient.size() < species_count) {
        throw ValueError("Neutral TPD trial gradient size did not match species count.");
    }
    NeutralTpdCandidate candidate;
    candidate.valid = true;
    candidate.source = source;
    candidate.phase_kind = phase_kind;
    candidate.composition = trial.composition;
    candidate.density = trial.density;
    candidate.molar_volume = 1.0 / trial.density;
    candidate.transformed_objective = trial.objective;
    candidate.pressure_residual_estimate = trial.pressure_consistency_residual;
    candidate.tpd_backend = backend;
    candidate.tpd_status = status;
    candidate.start_source = start_source;
    candidate.tpd_iteration_count = iteration_count;
    candidate.tpd_step_final = step_final;
    candidate.feasibility_status = "candidate_generated";
    for (std::size_t species = 0; species < species_count; ++species) {
        candidate.tpd += trial.composition[species]
            * (trial.gradient[species] - reference.gradient[species]);
    }
    return candidate;
}

NeutralTpdCandidate evaluate_electrolyte_tpd_candidate(
    const add_args& args,
    double temperature,
    double target_pressure,
    const EosPhaseBlockResult& reference,
    const std::vector<double>& trial_composition,
    const std::vector<double>& charges,
    int phase_kind,
    const std::string& source,
    double charge_tolerance
) {
    const std::size_t species_count = reference.composition.size();
    require_size(charges, species_count, source + " charge");
    if (reference.gradient.size() < species_count) {
        throw ValueError("Electrolyte TPD reference gradient size did not match species count.");
    }
    require_charge_neutral_composition(reference.composition, charges, source + " reference", charge_tolerance);
    require_charge_neutral_composition(trial_composition, charges, source + " trial", charge_tolerance);
    const EosPhaseBlockResult trial = evaluate_unit_phase_block_at_pressure_root(
        args,
        temperature,
        target_pressure,
        trial_composition,
        phase_kind,
        source
    );
    if (trial.gradient.size() < species_count) {
        throw ValueError("Electrolyte TPD trial gradient size did not match species count.");
    }
    require_charge_neutral_composition(trial.composition, charges, source + " pressure-root trial", charge_tolerance);

    double charge_square_norm = 0.0;
    double charge_weighted_difference = 0.0;
    for (std::size_t species = 0; species < species_count; ++species) {
        const double difference = trial.gradient[species] - reference.gradient[species];
        charge_square_norm += charges[species] * charges[species];
        charge_weighted_difference += charges[species] * difference;
    }
    if (charge_square_norm <= 0.0) {
        throw ValueError("Electrolyte TPD requires at least one charged species.");
    }
    const double charge_projection_shift = -charge_weighted_difference / charge_square_norm;

    NeutralTpdCandidate candidate;
    candidate.valid = true;
    candidate.source = source;
    candidate.phase_kind = phase_kind;
    candidate.composition = trial.composition;
    candidate.density = trial.density;
    candidate.molar_volume = 1.0 / trial.density;
    candidate.transformed_objective = trial.objective;
    candidate.pressure_residual_estimate = trial.pressure_consistency_residual;
    candidate.tpd_backend = "charge_neutral_projected_electrochemical_potential";
    candidate.tpd_status = "charge_neutral_candidate_generated";
    candidate.start_source = "deterministic_charge_neutral_trial";
    candidate.tpd_iteration_count = 0;
    candidate.tpd_step_final = 0.0;
    candidate.feasibility_status = "candidate_generated";
    for (std::size_t species = 0; species < species_count; ++species) {
        const double projected_difference =
            trial.gradient[species] - reference.gradient[species] + charge_projection_shift * charges[species];
        candidate.tpd += trial.composition[species] * projected_difference;
    }
    return candidate;
}

// AlgID: neutral_continuous_tpd_minimization
NeutralTpdCandidate refine_neutral_tpd_candidate(
    const add_args& args,
    double temperature,
    double target_pressure,
    const EosPhaseBlockResult& reference,
    const std::vector<double>& start_composition,
    int phase_kind,
    const std::string& source,
    const std::string& start_source
) {
    std::vector<double> current = normalized_trial_composition(start_composition, source + " start");
    NeutralTpdCandidate best = evaluate_neutral_tpd_candidate(
        args,
        temperature,
        target_pressure,
        reference,
        current,
        phase_kind,
        source,
        "continuous_coordinate_search",
        "running",
        start_source,
        0,
        0.0
    );
    double step = 2.5e-1;
    int iteration = 0;
    constexpr int kMaxIterations = 48;
    constexpr double kStepFloor = 1.0e-8;
    const std::size_t n = current.size();
    trace_continuous_tpd_iteration(
        "start",
        source,
        start_source,
        phase_kind,
        iteration,
        step,
        false,
        best.tpd,
        current
    );
    while (iteration < kMaxIterations && step > kStepFloor) {
        bool improved = false;
        for (std::size_t from = 0; from < n; ++from) {
            for (std::size_t to = 0; to < n; ++to) {
                if (from == to) {
                    continue;
                }
                const double movable = current[from] - kCompositionFloor;
                const double capacity = 1.0 - kCompositionFloor * static_cast<double>(n - 1) - current[to];
                const double delta = std::min(step, std::min(movable, capacity));
                if (!(delta > 0.0)) {
                    continue;
                }
                std::vector<double> trial_composition = current;
                trial_composition[from] -= delta;
                trial_composition[to] += delta;
                try {
                    NeutralTpdCandidate trial = evaluate_neutral_tpd_candidate(
                        args,
                        temperature,
                        target_pressure,
                        reference,
                        trial_composition,
                        phase_kind,
                        source,
                        "continuous_coordinate_search",
                        "running",
                        start_source,
                        iteration + 1,
                        step
                    );
                    if (trial.tpd + 1.0e-12 < best.tpd) {
                        best = trial;
                        current = trial.composition;
                        improved = true;
                    }
                } catch (const std::exception&) {
                    continue;
                }
            }
        }
        if (!improved) {
            step *= 0.5;
        }
        trace_continuous_tpd_iteration(
            "iteration",
            source,
            start_source,
            phase_kind,
            iteration + 1,
            step,
            improved,
            best.tpd,
            current
        );
        ++iteration;
    }
    best.tpd_backend = "continuous_coordinate_search";
    best.tpd_status = step <= kStepFloor ? "converged" : "iteration_limit";
    best.start_source = start_source;
    best.tpd_iteration_count = iteration;
    best.tpd_step_final = step;
    trace_continuous_tpd_finish(source, start_source, phase_kind, best);
    return best;
}

void record_continuous_tpd_candidate(
    NeutralPhaseDiscoveryResult* discovery,
    const NeutralTpdCandidate& candidate
) {
    if (discovery == nullptr || !candidate.valid) {
        return;
    }
    ++discovery->continuous_tpd_solve_count;
    if (candidate.tpd_status == "converged") {
        ++discovery->continuous_tpd_converged_count;
    }
    discovery->continuous_tpd_iteration_count_total += candidate.tpd_iteration_count;
    discovery->continuous_tpd_iteration_count_max = std::max(
        discovery->continuous_tpd_iteration_count_max,
        candidate.tpd_iteration_count
    );
    discovery->continuous_tpd_step_final_max = std::max(
        discovery->continuous_tpd_step_final_max,
        candidate.tpd_step_final
    );
    if (
        discovery->continuous_tpd_best_source.empty()
        || candidate.tpd < discovery->continuous_tpd_min
    ) {
        discovery->continuous_tpd_min = candidate.tpd;
        discovery->continuous_tpd_best_source = candidate.source;
        discovery->continuous_tpd_best_phase_kind = candidate.phase_kind;
        discovery->continuous_tpd_best_density = candidate.density;
        discovery->continuous_tpd_best_molar_volume = candidate.molar_volume;
        discovery->continuous_tpd_best_composition = candidate.composition;
    }
}

// AlgID: neutral_tpd_stability
void append_tpd_candidates_for_reference_block(
    const add_args& args,
    double temperature,
    double target_pressure,
    const EosPhaseBlockResult& reference,
    const std::vector<int>& trial_phase_kinds,
    const std::string& source_prefix,
    std::vector<NeutralTpdCandidate>& candidates,
    int& valid_candidate_count,
    NeutralPhaseDiscoveryResult* discovery = nullptr,
    bool continuous_tpd_required = true
) {
    const std::size_t species_count = reference.composition.size();
    if (reference.gradient.size() < species_count) {
        throw ValueError("Neutral TPD reference gradient size did not match species count.");
    }
    const std::vector<std::vector<double>> trial_compositions =
        neutral_tpd_trial_compositions(reference.composition);
    for (int phase_kind : trial_phase_kinds) {
        std::size_t continuous_start_count = 0;
        for (std::size_t index = 0; index < trial_compositions.size(); ++index) {
            const std::string deterministic_source = source_prefix + "_trial_" + std::to_string(index);
            try {
                NeutralTpdCandidate candidate = evaluate_neutral_tpd_candidate(
                    args,
                    temperature,
                    target_pressure,
                    reference,
                    trial_compositions[index],
                    phase_kind,
                    deterministic_source,
                    "deterministic_grid_evaluation",
                    "candidate_generated",
                    deterministic_source,
                    0,
                    0.0
                );
                if (discovery != nullptr) {
                    ++discovery->deterministic_candidate_count;
                }
                ++valid_candidate_count;
                append_unique_tpd_candidate(candidates, candidate);
            } catch (const std::exception&) {
                continue;
            }
            if (!continuous_tpd_required) {
                continue;
            }
            if (continuous_start_count >= kContinuousTpdMaxStartsPerPhaseKind) {
                continue;
            }
            ++continuous_start_count;
            if (discovery != nullptr) {
                ++discovery->continuous_tpd_start_count;
            }
            const std::string continuous_source =
                source_prefix + "_continuous_tpd_" + std::to_string(index);
            try {
                NeutralTpdCandidate refined = refine_neutral_tpd_candidate(
                    args,
                    temperature,
                    target_pressure,
                    reference,
                    trial_compositions[index],
                    phase_kind,
                    continuous_source,
                    deterministic_source
                );
                ++valid_candidate_count;
                record_continuous_tpd_candidate(discovery, refined);
                append_unique_tpd_candidate(candidates, refined);
            } catch (const std::exception&) {
                continue;
            }
        }
    }
}

double candidate_pair_mass_balance_norm(
    const std::vector<double>& feed_composition,
    const std::vector<double>& first,
    const std::vector<double>& second,
    double first_fraction
) {
    require_size(first, feed_composition.size(), "Neutral TPD first candidate composition");
    require_size(second, feed_composition.size(), "Neutral TPD second candidate composition");
    double norm = 0.0;
    for (std::size_t species = 0; species < feed_composition.size(); ++species) {
        const double reconstructed = first_fraction * first[species] + (1.0 - first_fraction) * second[species];
        norm = std::max(norm, std::abs(reconstructed - feed_composition[species]));
    }
    return norm;
}

// AlgID: phase_candidate_mass_balance_selection
void select_two_phase_candidate_set(
    NeutralPhaseDiscoveryResult& discovery,
    const std::vector<double>& feed_composition,
    const std::vector<int>& phase_kinds,
    double candidate_mass_balance_tolerance
) {
    if (phase_kinds.size() != 2 || discovery.candidates.size() < 2) {
        discovery.phase_set_status = "candidate_mass_balance_incomplete";
        discovery.candidate_mass_balance_norm = std::numeric_limits<double>::infinity();
        for (NeutralTpdCandidate& candidate : discovery.candidates) {
            candidate.feasibility_status = "candidate_mass_balance_incomplete";
            candidate.selected = false;
        }
        return;
    }
    rank_tpd_candidates(discovery);
    const std::vector<double> z = normalized_trial_composition(feed_composition, "Neutral TPD feed");
    double best_norm = std::numeric_limits<double>::infinity();
    double best_selected_bound = std::numeric_limits<double>::infinity();
    double best_fraction = 0.0;
    int best_first = -1;
    int best_second = -1;
    const double norm_tie_tolerance = std::max(1.0e-12, 0.01 * candidate_mass_balance_tolerance);
    constexpr double kTpdTieTolerance = 1.0e-12;
    for (std::size_t first_index = 0; first_index < discovery.candidates.size(); ++first_index) {
        const NeutralTpdCandidate& first = discovery.candidates[first_index];
        if (first.phase_kind != phase_kinds[0]) {
            continue;
        }
        if (!std::isfinite(first.tpd)) {
            continue;
        }
        for (std::size_t second_index = 0; second_index < discovery.candidates.size(); ++second_index) {
            if (first_index == second_index) {
                continue;
            }
            const NeutralTpdCandidate& second = discovery.candidates[second_index];
            if (second.phase_kind != phase_kinds[1]) {
                continue;
            }
            if (!std::isfinite(second.tpd)) {
                continue;
            }
            double numerator = 0.0;
            double denominator = 0.0;
            for (std::size_t species = 0; species < z.size(); ++species) {
                const double direction = first.composition[species] - second.composition[species];
                numerator += (z[species] - second.composition[species]) * direction;
                denominator += direction * direction;
            }
            if (denominator <= 0.0) {
                continue;
            }
            const double fraction = numerator / denominator;
            if (!(fraction > 1.0e-10 && fraction < 1.0 - 1.0e-10)) {
                continue;
            }
            const double norm = candidate_pair_mass_balance_norm(
                z,
                first.composition,
                second.composition,
                fraction
            );
            const double selected_bound = std::min(first.tpd, second.tpd);
            const bool norm_feasible = norm <= candidate_mass_balance_tolerance;
            const bool best_norm_feasible = best_norm <= candidate_mass_balance_tolerance;
            bool better_pair = best_first < 0;
            if (!better_pair && norm_feasible != best_norm_feasible) {
                better_pair = norm_feasible;
            } else if (!better_pair && norm_feasible && best_norm_feasible) {
                better_pair = selected_bound + kTpdTieTolerance < best_selected_bound
                    || (
                        std::abs(selected_bound - best_selected_bound) <= kTpdTieTolerance
                        && norm + norm_tie_tolerance < best_norm
                    );
            } else if (!better_pair) {
                better_pair = norm + norm_tie_tolerance < best_norm
                    || (
                        std::abs(norm - best_norm) <= norm_tie_tolerance
                        && selected_bound + kTpdTieTolerance < best_selected_bound
                    );
            }
            if (better_pair) {
                best_norm = norm;
                best_selected_bound = selected_bound;
                best_fraction = fraction;
                best_first = static_cast<int>(first_index);
                best_second = static_cast<int>(second_index);
            }
        }
    }
    discovery.candidate_mass_balance_norm = best_norm;
    discovery.phase_set_mass_balance_feasible = best_norm <= candidate_mass_balance_tolerance;
    discovery.candidate_completeness_accepted = discovery.phase_set_mass_balance_feasible;
    if (!discovery.phase_set_mass_balance_feasible) {
        discovery.phase_set_status = "candidate_mass_balance_incomplete";
        for (NeutralTpdCandidate& candidate : discovery.candidates) {
            candidate.feasibility_status = "candidate_mass_balance_incomplete";
            candidate.selected = false;
        }
        return;
    }
    for (NeutralTpdCandidate& candidate : discovery.candidates) {
        candidate.feasibility_status = "mass_balance_pair_unselected";
        candidate.selected = false;
    }
    discovery.candidates[static_cast<std::size_t>(best_first)].selected = true;
    discovery.candidates[static_cast<std::size_t>(best_first)].feasibility_status =
        "selected_mass_balance_feasible";
    discovery.candidates[static_cast<std::size_t>(best_second)].selected = true;
    discovery.candidates[static_cast<std::size_t>(best_second)].feasibility_status =
        "selected_mass_balance_feasible";
    discovery.selected_candidate_count = 2;
    discovery.selected_phase_fractions = {best_fraction, 1.0 - best_fraction};
    discovery.selected_phase_kinds = {phase_kinds[0], phase_kinds[1]};
    discovery.selected_phase_compositions = {
        discovery.candidates[static_cast<std::size_t>(best_first)].composition,
        discovery.candidates[static_cast<std::size_t>(best_second)].composition,
    };
    discovery.phase_set_status = "candidate_mass_balance_feasible";
}

double candidate_set_mass_balance_norm(
    const std::vector<double>& feed_composition,
    const std::vector<NeutralTpdCandidate>& candidates,
    const std::vector<int>& selected_indices,
    const std::vector<double>& fractions
) {
    require_size(fractions, selected_indices.size(), "Neutral TPD selected candidate fraction");
    double norm = 0.0;
    for (std::size_t species = 0; species < feed_composition.size(); ++species) {
        double reconstructed = 0.0;
        for (std::size_t selected = 0; selected < selected_indices.size(); ++selected) {
            const NeutralTpdCandidate& candidate =
                candidates[static_cast<std::size_t>(selected_indices[selected])];
            require_size(candidate.composition, feed_composition.size(), "Neutral TPD selected composition");
            reconstructed += fractions[selected] * candidate.composition[species];
        }
        norm = std::max(norm, std::abs(reconstructed - feed_composition[species]));
    }
    return norm;
}

bool solve_candidate_simplex_fractions(
    const std::vector<double>& feed_composition,
    const std::vector<NeutralTpdCandidate>& candidates,
    const std::vector<int>& selected_indices,
    std::vector<double>& fractions
) {
    const std::size_t phase_count = selected_indices.size();
    if (phase_count == 0) {
        return false;
    }
    const std::size_t row_count = feed_composition.size() + 1;
    std::vector<std::vector<double>> normal(
        phase_count,
        std::vector<double>(phase_count, 0.0)
    );
    std::vector<double> rhs(phase_count, 0.0);
    for (std::size_t row = 0; row < row_count; ++row) {
        const double target = row < feed_composition.size() ? feed_composition[row] : 1.0;
        for (std::size_t left = 0; left < phase_count; ++left) {
            const NeutralTpdCandidate& left_candidate =
                candidates[static_cast<std::size_t>(selected_indices[left])];
            const double left_value =
                row < feed_composition.size() ? left_candidate.composition[row] : 1.0;
            rhs[left] += left_value * target;
            for (std::size_t right = 0; right < phase_count; ++right) {
                const NeutralTpdCandidate& right_candidate =
                    candidates[static_cast<std::size_t>(selected_indices[right])];
                const double right_value =
                    row < feed_composition.size() ? right_candidate.composition[row] : 1.0;
                normal[left][right] += left_value * right_value;
            }
        }
    }

    for (std::size_t pivot = 0; pivot < phase_count; ++pivot) {
        std::size_t best_row = pivot;
        double best_abs = std::abs(normal[pivot][pivot]);
        for (std::size_t row = pivot + 1; row < phase_count; ++row) {
            const double candidate_abs = std::abs(normal[row][pivot]);
            if (candidate_abs > best_abs) {
                best_abs = candidate_abs;
                best_row = row;
            }
        }
        if (best_abs <= 1.0e-14) {
            return false;
        }
        if (best_row != pivot) {
            std::swap(normal[pivot], normal[best_row]);
            std::swap(rhs[pivot], rhs[best_row]);
        }
        const double pivot_value = normal[pivot][pivot];
        for (std::size_t col = pivot; col < phase_count; ++col) {
            normal[pivot][col] /= pivot_value;
        }
        rhs[pivot] /= pivot_value;
        for (std::size_t row = 0; row < phase_count; ++row) {
            if (row == pivot) {
                continue;
            }
            const double factor = normal[row][pivot];
            for (std::size_t col = pivot; col < phase_count; ++col) {
                normal[row][col] -= factor * normal[pivot][col];
            }
            rhs[row] -= factor * rhs[pivot];
        }
    }

    fractions = rhs;
    double fraction_sum = 0.0;
    for (double value : fractions) {
        if (!std::isfinite(value) || value <= 1.0e-10) {
            return false;
        }
        fraction_sum += value;
    }
    if (!std::isfinite(fraction_sum) || fraction_sum <= 0.0) {
        return false;
    }
    for (double& value : fractions) {
        value /= fraction_sum;
    }
    return true;
}

void select_generalized_phase_candidate_set(
    NeutralPhaseDiscoveryResult& discovery,
    const std::vector<double>& feed_composition,
    const std::vector<int>& phase_kinds,
    double candidate_mass_balance_tolerance
) {
    const std::size_t phase_count = phase_kinds.size();
    if (phase_count < 2 || discovery.candidates.size() < phase_count) {
        discovery.phase_set_status = "candidate_mass_balance_incomplete";
        discovery.candidate_mass_balance_norm = std::numeric_limits<double>::infinity();
        for (NeutralTpdCandidate& candidate : discovery.candidates) {
            candidate.feasibility_status = "candidate_mass_balance_incomplete";
            candidate.selected = false;
        }
        return;
    }
    if (phase_count == 2) {
        select_two_phase_candidate_set(discovery, feed_composition, phase_kinds, candidate_mass_balance_tolerance);
        return;
    }

    rank_tpd_candidates(discovery);
    const std::vector<double> z = normalized_trial_composition(feed_composition, "Neutral TPD feed");
    double best_norm = std::numeric_limits<double>::infinity();
    double best_selected_bound = std::numeric_limits<double>::infinity();
    std::vector<int> best_indices;
    std::vector<double> best_fractions;
    std::vector<int> current_indices;
    const double norm_tie_tolerance = std::max(1.0e-12, 0.01 * candidate_mass_balance_tolerance);
    constexpr double kTpdTieTolerance = 1.0e-12;

    std::function<void(std::size_t)> visit = [&](std::size_t phase) {
        if (phase == phase_count) {
            std::vector<double> fractions;
            if (!solve_candidate_simplex_fractions(z, discovery.candidates, current_indices, fractions)) {
                return;
            }
            const double norm =
                candidate_set_mass_balance_norm(z, discovery.candidates, current_indices, fractions);
            double selected_bound = std::numeric_limits<double>::infinity();
            for (int index : current_indices) {
                selected_bound = std::min(
                    selected_bound,
                    discovery.candidates[static_cast<std::size_t>(index)].tpd
                );
            }
            const bool norm_feasible = norm <= candidate_mass_balance_tolerance;
            const bool best_norm_feasible = best_norm <= candidate_mass_balance_tolerance;
            bool better_set = best_indices.empty();
            if (!better_set && norm_feasible != best_norm_feasible) {
                better_set = norm_feasible;
            } else if (!better_set && norm_feasible && best_norm_feasible) {
                better_set = selected_bound + kTpdTieTolerance < best_selected_bound
                    || (
                        std::abs(selected_bound - best_selected_bound) <= kTpdTieTolerance
                        && norm + norm_tie_tolerance < best_norm
                    );
            } else if (!better_set) {
                better_set = norm + norm_tie_tolerance < best_norm
                    || (
                        std::abs(norm - best_norm) <= norm_tie_tolerance
                        && selected_bound + kTpdTieTolerance < best_selected_bound
                    );
            }
            if (better_set) {
                best_norm = norm;
                best_selected_bound = selected_bound;
                best_indices = current_indices;
                best_fractions = fractions;
            }
            return;
        }

        for (std::size_t candidate_index = 0; candidate_index < discovery.candidates.size(); ++candidate_index) {
            const NeutralTpdCandidate& candidate = discovery.candidates[candidate_index];
            if (candidate.phase_kind != phase_kinds[phase] || !std::isfinite(candidate.tpd)) {
                continue;
            }
            const int index = static_cast<int>(candidate_index);
            if (std::find(current_indices.begin(), current_indices.end(), index) != current_indices.end()) {
                continue;
            }
            current_indices.push_back(index);
            visit(phase + 1);
            current_indices.pop_back();
        }
    };
    visit(0);

    discovery.candidate_mass_balance_norm = best_norm;
    discovery.phase_set_mass_balance_feasible = best_norm <= candidate_mass_balance_tolerance;
    discovery.candidate_completeness_accepted = discovery.phase_set_mass_balance_feasible;
    if (!discovery.phase_set_mass_balance_feasible) {
        discovery.phase_set_status = "candidate_mass_balance_incomplete";
        for (NeutralTpdCandidate& candidate : discovery.candidates) {
            candidate.feasibility_status = "candidate_mass_balance_incomplete";
            candidate.selected = false;
        }
        return;
    }
    for (NeutralTpdCandidate& candidate : discovery.candidates) {
        candidate.feasibility_status = "mass_balance_simplex_unselected";
        candidate.selected = false;
    }
    discovery.selected_phase_fractions.clear();
    discovery.selected_phase_kinds.clear();
    discovery.selected_phase_compositions.clear();
    for (std::size_t selected = 0; selected < best_indices.size(); ++selected) {
        NeutralTpdCandidate& candidate =
            discovery.candidates[static_cast<std::size_t>(best_indices[selected])];
        candidate.selected = true;
        candidate.feasibility_status = "selected_mass_balance_feasible";
        discovery.selected_phase_fractions.push_back(best_fractions[selected]);
        discovery.selected_phase_kinds.push_back(candidate.phase_kind);
        discovery.selected_phase_compositions.push_back(candidate.composition);
    }
    discovery.selected_candidate_count = static_cast<int>(best_indices.size());
    discovery.phase_set_status = "candidate_mass_balance_feasible";
}

void evaluate_held_stage_ii_candidate_bounds(
    NeutralPhaseDiscoveryResult& discovery,
    double tpd_tolerance,
    bool continuous_tpd_required
) {
    discovery.held_stage_ii_major_iterations = 0;
    discovery.held_stage_ii_candidate_count = discovery.unique_candidate_count;
    discovery.held_stage_ii_lower_bound = 0.0;
    discovery.held_stage_ii_upper_bound = 0.0;
    discovery.held_stage_ii_bound_gap = 0.0;
    discovery.held_stage_ii_bound_tolerance = tpd_tolerance;
    discovery.held_stage_ii_lower_bound_history.clear();
    discovery.held_stage_ii_upper_bound_history.clear();
    discovery.held_stage_ii_bound_gap_history.clear();
    discovery.held_stage_ii_replay_ready = false;
    discovery.held_stage_ii_replay_source.clear();
    discovery.held_stage_ii_replay_seed_name.clear();
    discovery.held_stage_ii_replay_candidate_count = 0;
    discovery.held_stage_ii_replay_candidate_ranks.clear();
    discovery.held_stage_ii_replay_phase_fractions.clear();
    discovery.held_stage_ii_replay_phase_kinds.clear();
    discovery.held_stage_ii_replay_phase_compositions.clear();
    discovery.held_stage_ii_rejected_candidate_count = 0;
    discovery.held_stage_ii_rejected_candidate_ranks.clear();
    discovery.held_stage_ii_rejected_candidate_reasons.clear();
    discovery.held_stage_ii_stopping_reason.clear();

    if (!continuous_tpd_required) {
        discovery.held_stage_ii_status = "not_requested";
        discovery.held_stage_ii_candidate_bound_audit_status = "not_requested";
        discovery.held_stage_ii_dual_loop_status = "not_requested";
        discovery.held_stage_ii_stopping_reason = "not_requested";
        return;
    }
    if (discovery.continuous_tpd_status != "converged") {
        discovery.held_stage_ii_status = "incomplete_stage_i_evidence";
        discovery.held_stage_ii_candidate_bound_audit_status = "incomplete_stage_i_evidence";
        discovery.held_stage_ii_dual_loop_status = "incomplete_stage_i_evidence";
        discovery.held_stage_ii_stopping_reason = "stage_i_incomplete";
        return;
    }
    if (discovery.candidates.empty()) {
        discovery.held_stage_ii_status = "inconclusive_no_candidates";
        discovery.held_stage_ii_candidate_bound_audit_status = "inconclusive_no_candidates";
        discovery.held_stage_ii_dual_loop_status = "inconclusive_no_candidates";
        discovery.held_stage_ii_stopping_reason = "no_candidates";
        return;
    }

    double lower_bound = std::numeric_limits<double>::infinity();
    double selected_upper_bound = std::numeric_limits<double>::infinity();
    for (const NeutralTpdCandidate& candidate : discovery.candidates) {
        if (!candidate.valid || !std::isfinite(candidate.tpd)) {
            continue;
        }
        lower_bound = std::min(lower_bound, candidate.tpd);
        if (candidate.selected) {
            selected_upper_bound = std::min(selected_upper_bound, candidate.tpd);
        }
    }
    if (!std::isfinite(lower_bound)) {
        discovery.held_stage_ii_status = "inconclusive_no_finite_candidate_bound";
        discovery.held_stage_ii_candidate_bound_audit_status = "inconclusive_no_finite_candidate_bound";
        discovery.held_stage_ii_dual_loop_status = "inconclusive_no_finite_candidate_bound";
        discovery.held_stage_ii_stopping_reason = "no_finite_candidate_bound";
        return;
    }

    discovery.held_stage_ii_major_iterations = 1;
    discovery.held_stage_ii_lower_bound = lower_bound;
    if (!discovery.phase_set_mass_balance_feasible || discovery.selected_candidate_count < 2) {
        discovery.held_stage_ii_upper_bound = lower_bound;
        discovery.held_stage_ii_status = "candidate_simplex_mass_balance_incomplete";
        discovery.held_stage_ii_candidate_bound_audit_status = "candidate_simplex_mass_balance_incomplete";
        discovery.held_stage_ii_dual_loop_status = "candidate_simplex_mass_balance_incomplete";
        discovery.held_stage_ii_stopping_reason = "candidate_simplex_mass_balance_incomplete";
        discovery.held_stage_ii_lower_bound_history = {discovery.held_stage_ii_lower_bound};
        discovery.held_stage_ii_upper_bound_history = {discovery.held_stage_ii_upper_bound};
        discovery.held_stage_ii_bound_gap_history = {discovery.held_stage_ii_bound_gap};
        return;
    }
    if (!std::isfinite(selected_upper_bound)) {
        selected_upper_bound = 0.0;
    }

    discovery.held_stage_ii_upper_bound = std::max(selected_upper_bound, lower_bound);
    discovery.held_stage_ii_bound_gap =
        std::max(0.0, discovery.held_stage_ii_upper_bound - discovery.held_stage_ii_lower_bound);
    discovery.held_stage_ii_lower_bound_history = {discovery.held_stage_ii_lower_bound};
    discovery.held_stage_ii_upper_bound_history = {discovery.held_stage_ii_upper_bound};
    discovery.held_stage_ii_bound_gap_history = {discovery.held_stage_ii_bound_gap};
    discovery.held_stage_ii_replay_candidate_count = discovery.unique_candidate_count;
    for (const NeutralTpdCandidate& candidate : discovery.candidates) {
        if (candidate.selected) {
            discovery.held_stage_ii_replay_candidate_ranks.push_back(candidate.candidate_rank);
        } else {
            ++discovery.held_stage_ii_rejected_candidate_count;
            discovery.held_stage_ii_rejected_candidate_ranks.push_back(candidate.candidate_rank);
            discovery.held_stage_ii_rejected_candidate_reasons.push_back(
                "not_selected_by_dual_loop_mass_balance_gate"
            );
        }
    }
    discovery.held_stage_ii_replay_phase_fractions = discovery.selected_phase_fractions;
    discovery.held_stage_ii_replay_phase_kinds = discovery.selected_phase_kinds;
    discovery.held_stage_ii_replay_phase_compositions = discovery.selected_phase_compositions;
    if (discovery.held_stage_ii_bound_gap <= tpd_tolerance) {
        discovery.held_stage_ii_candidate_bound_audit_status = "candidate_bound_gap_closed";
        discovery.held_stage_ii_status = "dual_loop_verified";
        discovery.held_stage_ii_dual_loop_status = "verified";
        discovery.held_stage_ii_stopping_reason = "bound_gap_closed";
        discovery.held_stage_ii_replay_ready = true;
        discovery.held_stage_ii_replay_source = "stage_ii_dual_loop_selected_candidates";
        discovery.held_stage_ii_replay_seed_name = discovery.selected_candidate_count == 2
            ? kHeldStageIIDualLoopSeedName
            : kHeldStageIIDualLoopCandidateSetName;
    } else {
        discovery.held_stage_ii_candidate_bound_audit_status = "candidate_bound_gap_open";
        discovery.held_stage_ii_status = "dual_loop_incomplete";
        discovery.held_stage_ii_dual_loop_status = "incomplete_candidate_bound_gap_open";
        discovery.held_stage_ii_stopping_reason = "bound_gap_open";
    }
}

// AlgID: neutral_held_stage_ladder_diagnostics
void finalize_stage9_phase_discovery(
    NeutralPhaseDiscoveryResult& discovery,
    double tpd_tolerance,
    bool continuous_tpd_required = true
) {
    discovery.stage9_phase_discovery_steps = stage9_phase_discovery_steps();
    discovery.phase_discovery_backend = continuous_tpd_required
        ? "continuous_tpd_held_dual_phase_discovery"
        : "deterministic_tpd_candidate_screening";
    discovery.deterministic_screening_is_full_held = false;
    discovery.deterministic_screening_status =
        discovery.deterministic_candidate_count > 0 ? "completed" : "inconclusive";
    discovery.continuous_tpd_backend = "continuous_coordinate_search";
    if (!continuous_tpd_required) {
        discovery.continuous_tpd_status = "not_requested";
    } else if (discovery.continuous_tpd_solve_count == 0) {
        discovery.continuous_tpd_status = "inconclusive";
    } else if (discovery.continuous_tpd_converged_count == discovery.continuous_tpd_solve_count) {
        discovery.continuous_tpd_status = "converged";
    } else {
        discovery.continuous_tpd_status = "incomplete_iteration_limit";
    }
    if (discovery.continuous_tpd_best_source.empty()) {
        discovery.continuous_tpd_min = discovery.min_tpd;
    }
    discovery.held_stage_i_start_count = discovery.continuous_tpd_start_count;
    discovery.held_stage_i_min_tpd = discovery.continuous_tpd_min;
    discovery.held_stage_i_negative_tpd_found =
        discovery.continuous_tpd_status == "converged" && discovery.continuous_tpd_min < -tpd_tolerance;
    if (!continuous_tpd_required) {
        discovery.held_stage_i_status = "not_requested";
    } else if (discovery.continuous_tpd_solve_count == 0) {
        discovery.held_stage_i_status = "inconclusive_no_continuous_tpd_solution";
    } else if (discovery.continuous_tpd_status != "converged") {
        discovery.held_stage_i_status = "inconclusive_continuous_tpd_iteration_limit";
    } else if (discovery.held_stage_i_negative_tpd_found) {
        discovery.held_stage_i_status = "negative_tpd_candidate_found";
    } else {
        discovery.held_stage_i_status = "no_negative_tpd_candidate_found";
    }
    evaluate_held_stage_ii_candidate_bounds(discovery, tpd_tolerance, continuous_tpd_required);
    discovery.held_stage_iii_status = "pending_ipopt_refinement";
    discovery.held_stage_iii_refined_phase_count = 0;
}

void copy_discovery_to_postsolve(
    NeutralTwoPhaseEosPostsolve& postsolve,
    const NeutralPhaseDiscoveryResult& discovery
) {
    postsolve.stability_checked = discovery.stability_checked;
    postsolve.stability_accepted = discovery.stability_accepted;
    postsolve.candidate_completeness_accepted = discovery.candidate_completeness_accepted;
    postsolve.phase_set_mass_balance_feasible = discovery.phase_set_mass_balance_feasible;
    postsolve.phase_discovery_backend = discovery.phase_discovery_backend;
    postsolve.stability_certificate = discovery.stability_certificate;
    postsolve.phase_set_status = discovery.phase_set_status;
    postsolve.stage9_phase_discovery_steps = discovery.stage9_phase_discovery_steps;
    postsolve.deterministic_screening_status = discovery.deterministic_screening_status;
    postsolve.deterministic_screening_is_full_held = discovery.deterministic_screening_is_full_held;
    postsolve.continuous_tpd_status = discovery.continuous_tpd_status;
    postsolve.continuous_tpd_backend = discovery.continuous_tpd_backend;
    postsolve.continuous_tpd_best_source = discovery.continuous_tpd_best_source;
    postsolve.deterministic_candidate_count = discovery.deterministic_candidate_count;
    postsolve.continuous_tpd_start_count = discovery.continuous_tpd_start_count;
    postsolve.continuous_tpd_solve_count = discovery.continuous_tpd_solve_count;
    postsolve.continuous_tpd_converged_count = discovery.continuous_tpd_converged_count;
    postsolve.continuous_tpd_iteration_count_total = discovery.continuous_tpd_iteration_count_total;
    postsolve.continuous_tpd_iteration_count_max = discovery.continuous_tpd_iteration_count_max;
    postsolve.continuous_tpd_min = discovery.continuous_tpd_min;
    postsolve.continuous_tpd_step_final_max = discovery.continuous_tpd_step_final_max;
    postsolve.continuous_tpd_best_phase_kind = discovery.continuous_tpd_best_phase_kind;
    postsolve.continuous_tpd_best_density = discovery.continuous_tpd_best_density;
    postsolve.continuous_tpd_best_molar_volume = discovery.continuous_tpd_best_molar_volume;
    postsolve.continuous_tpd_best_composition = discovery.continuous_tpd_best_composition;
    postsolve.held_stage_i_status = discovery.held_stage_i_status;
    postsolve.held_stage_i_start_count = discovery.held_stage_i_start_count;
    postsolve.held_stage_i_negative_tpd_found = discovery.held_stage_i_negative_tpd_found;
    postsolve.held_stage_i_min_tpd = discovery.held_stage_i_min_tpd;
    postsolve.held_stage_ii_status = discovery.held_stage_ii_status;
    postsolve.held_stage_ii_candidate_bound_audit_status = discovery.held_stage_ii_candidate_bound_audit_status;
    postsolve.held_stage_ii_dual_loop_status = discovery.held_stage_ii_dual_loop_status;
    postsolve.held_stage_ii_major_iterations = discovery.held_stage_ii_major_iterations;
    postsolve.held_stage_ii_candidate_count = discovery.held_stage_ii_candidate_count;
    postsolve.held_stage_ii_lower_bound = discovery.held_stage_ii_lower_bound;
    postsolve.held_stage_ii_upper_bound = discovery.held_stage_ii_upper_bound;
    postsolve.held_stage_ii_bound_gap = discovery.held_stage_ii_bound_gap;
    postsolve.held_stage_ii_bound_tolerance = discovery.held_stage_ii_bound_tolerance;
    postsolve.held_stage_ii_stopping_reason = discovery.held_stage_ii_stopping_reason;
    postsolve.held_stage_ii_lower_bound_history = discovery.held_stage_ii_lower_bound_history;
    postsolve.held_stage_ii_upper_bound_history = discovery.held_stage_ii_upper_bound_history;
    postsolve.held_stage_ii_bound_gap_history = discovery.held_stage_ii_bound_gap_history;
    postsolve.held_stage_ii_replay_ready = discovery.held_stage_ii_replay_ready;
    postsolve.held_stage_ii_replay_source = discovery.held_stage_ii_replay_source;
    postsolve.held_stage_ii_replay_seed_name = discovery.held_stage_ii_replay_seed_name;
    postsolve.held_stage_ii_replay_candidate_count = discovery.held_stage_ii_replay_candidate_count;
    postsolve.held_stage_ii_replay_candidate_ranks = discovery.held_stage_ii_replay_candidate_ranks;
    postsolve.held_stage_ii_replay_phase_fractions = discovery.held_stage_ii_replay_phase_fractions;
    postsolve.held_stage_ii_replay_phase_kinds = discovery.held_stage_ii_replay_phase_kinds;
    postsolve.held_stage_ii_replay_phase_compositions = discovery.held_stage_ii_replay_phase_compositions;
    postsolve.held_stage_ii_rejected_candidate_count = discovery.held_stage_ii_rejected_candidate_count;
    postsolve.held_stage_ii_rejected_candidate_ranks = discovery.held_stage_ii_rejected_candidate_ranks;
    postsolve.held_stage_ii_rejected_candidate_reasons = discovery.held_stage_ii_rejected_candidate_reasons;
    postsolve.held_stage_iii_status = discovery.held_stage_iii_status;
    postsolve.held_stage_iii_refined_phase_count = discovery.held_stage_iii_refined_phase_count;
    postsolve.min_tpd = discovery.min_tpd;
    postsolve.candidate_mass_balance_norm = discovery.candidate_mass_balance_norm;
    postsolve.tpd_candidate_count = discovery.tpd_candidate_count;
    postsolve.unique_candidate_count = discovery.unique_candidate_count;
    postsolve.selected_candidate_count = discovery.selected_candidate_count;
    postsolve.selected_phase_fractions = discovery.selected_phase_fractions;
    postsolve.selected_phase_kinds = discovery.selected_phase_kinds;
    postsolve.selected_phase_compositions = discovery.selected_phase_compositions;
    postsolve.tpd_candidate_values.clear();
    postsolve.tpd_candidate_sources.clear();
    postsolve.tpd_candidate_phase_kinds.clear();
    postsolve.tpd_candidate_compositions.clear();
    postsolve.tpd_candidate_pressure_residuals.clear();
    postsolve.tpd_candidate_iteration_counts.clear();
    postsolve.tpd_candidate_step_finals.clear();
    postsolve.tpd_candidate_ranks.clear();
    postsolve.tpd_candidate_feasibility_statuses.clear();
    postsolve.tpd_candidate_selected.clear();
    for (const NeutralTpdCandidate& candidate : discovery.candidates) {
        postsolve.tpd_candidate_values.push_back(candidate.tpd);
        postsolve.tpd_candidate_sources.push_back(candidate.source);
        postsolve.tpd_candidate_phase_kinds.push_back(candidate.phase_kind);
        postsolve.tpd_candidate_compositions.push_back(candidate.composition);
        postsolve.tpd_candidate_pressure_residuals.push_back(candidate.pressure_residual_estimate);
        postsolve.tpd_candidate_iteration_counts.push_back(candidate.tpd_iteration_count);
        postsolve.tpd_candidate_step_finals.push_back(candidate.tpd_step_final);
        postsolve.tpd_candidate_ranks.push_back(candidate.candidate_rank);
        postsolve.tpd_candidate_feasibility_statuses.push_back(candidate.feasibility_status);
        postsolve.tpd_candidate_selected.push_back(candidate.selected);
    }
}

void apply_stage_ii_discovery_certificate_to_refined_postsolve(
    NeutralTwoPhaseEosPostsolve& postsolve,
    const NeutralPhaseDiscoveryResult& discovery,
    int refined_phase_count,
    const std::string& replay_source,
    const std::string& replay_seed_name
) {
    const bool residual_metrics_accepted = postsolve.accepted;
    const std::string residual_rejection_reason = postsolve.rejection_reason;

    copy_discovery_to_postsolve(postsolve, discovery);
    postsolve.held_stage_iii_status = "ipopt_refinement_completed_current_route";
    postsolve.held_stage_iii_refined_phase_count = refined_phase_count;
    postsolve.held_stage_iii_consumed_stage_ii_replay_metadata = discovery.held_stage_ii_replay_ready;
    postsolve.held_stage_iii_replay_source = replay_source;
    postsolve.held_stage_iii_replay_seed_name = replay_seed_name;
    postsolve.held_stage_iii_replay_candidate_count = discovery.held_stage_ii_replay_candidate_count;

    if (!residual_metrics_accepted) {
        postsolve.accepted = false;
        postsolve.rejection_reason = residual_rejection_reason;
        return;
    }
    if (!discovery.stability_checked) {
        postsolve.accepted = false;
        postsolve.rejection_reason = "candidate_completeness";
        return;
    }
    if (!discovery.stability_accepted) {
        postsolve.accepted = false;
        postsolve.rejection_reason = "stability_tpd";
        return;
    }
    if (!discovery.candidate_completeness_accepted || !discovery.phase_set_mass_balance_feasible) {
        postsolve.accepted = false;
        postsolve.rejection_reason = "candidate_completeness";
        return;
    }
    postsolve.accepted = true;
    postsolve.rejection_reason = "accepted";
}

bool candidate_duplicates_accepted_phase(
    const NeutralTpdCandidate& candidate,
    const std::vector<EosPhaseBlockResult>& accepted_phases
) {
    for (const EosPhaseBlockResult& phase : accepted_phases) {
        if (phase.total_amount <= 0.0 || phase.volume <= 0.0) {
            continue;
        }
        NeutralTpdCandidate accepted;
        accepted.valid = true;
        accepted.composition = phase.composition;
        accepted.molar_volume = phase.volume / phase.total_amount;
        if (duplicate_tpd_candidate(candidate, accepted)) {
            return true;
        }
    }
    return false;
}

NeutralPhaseDiscoveryResult certify_neutral_phase_set(
    const add_args& args,
    double temperature,
    double target_pressure,
    const EosPhaseSystemResult& system,
    const std::vector<double>& feed_amounts,
    const std::vector<int>& phase_kinds,
    double tpd_tolerance,
    double candidate_mass_balance_tolerance,
    bool continuous_tpd_required = true
) {
    if (phase_kinds.size() != system.phase_blocks.size()) {
        throw ValueError("Neutral TPD postsolve phase kind size does not match the accepted phase set.");
    }
    NeutralPhaseDiscoveryResult out;
    out.phase_discovery_backend = "deterministic_tpd_candidate_screening";
    out.stability_certificate = "tpd_postsolve";
    const std::vector<int> trial_phase_kinds = normalized_phase_kinds(phase_kinds, "Neutral TPD postsolve");
    int valid_candidate_count = 0;
    for (std::size_t phase = 0; phase < system.phase_blocks.size(); ++phase) {
        append_tpd_candidates_for_reference_block(
            args,
            temperature,
            target_pressure,
            system.phase_blocks[phase],
            trial_phase_kinds,
            "accepted_phase_" + std::to_string(phase),
            out.candidates,
            valid_candidate_count,
            &out,
            continuous_tpd_required
        );
    }
    out.tpd_candidate_count = valid_candidate_count;
    out.unique_candidate_count = static_cast<int>(out.candidates.size());
    rank_tpd_candidates(out);
    out.stability_checked = out.unique_candidate_count > 0;
    out.min_tpd = out.stability_checked ? std::numeric_limits<double>::infinity() : 0.0;
    bool negative_novel_candidate = false;
    for (const NeutralTpdCandidate& candidate : out.candidates) {
        out.min_tpd = std::min(out.min_tpd, candidate.tpd);
        if (candidate.tpd < -tpd_tolerance && !candidate_duplicates_accepted_phase(candidate, system.phase_blocks)) {
            negative_novel_candidate = true;
        }
    }
    out.stability_accepted = out.stability_checked && !negative_novel_candidate;

    const double total_feed = positive_sum(feed_amounts, "Neutral TPD postsolve feed amount");
    std::vector<double> feed_composition;
    feed_composition.reserve(feed_amounts.size());
    for (double amount : feed_amounts) {
        feed_composition.push_back(amount / total_feed);
    }
    const double phase_total = std::accumulate(
        system.phase_blocks.begin(),
        system.phase_blocks.end(),
        0.0,
        [](double total, const EosPhaseBlockResult& block) {
            return total + block.total_amount;
        }
    );
    require_positive_finite(phase_total, "Neutral TPD postsolve phase total");
    std::vector<double> fractions;
    fractions.reserve(system.phase_blocks.size());
    for (const EosPhaseBlockResult& block : system.phase_blocks) {
        fractions.push_back(block.total_amount / phase_total);
    }
    out.candidate_mass_balance_norm = 0.0;
    for (std::size_t species = 0; species < feed_composition.size(); ++species) {
        double reconstructed = 0.0;
        for (std::size_t phase = 0; phase < system.phase_blocks.size(); ++phase) {
            reconstructed += fractions[phase] * system.phase_blocks[phase].composition[species];
        }
        out.candidate_mass_balance_norm =
            std::max(out.candidate_mass_balance_norm, std::abs(reconstructed - feed_composition[species]));
    }
    out.phase_set_mass_balance_feasible = out.candidate_mass_balance_norm <= candidate_mass_balance_tolerance;
    out.candidate_completeness_accepted = out.phase_set_mass_balance_feasible && out.stability_accepted;
    out.selected_candidate_count = static_cast<int>(system.phase_blocks.size());
    out.selected_phase_fractions = fractions;
    out.selected_phase_kinds = phase_kinds;
    for (const EosPhaseBlockResult& block : system.phase_blocks) {
        out.selected_phase_compositions.push_back(block.composition);
    }
    if (!out.stability_checked) {
        out.phase_set_status = "stability_uncertified";
    } else if (!out.stability_accepted) {
        out.phase_set_status = "negative_tpd_candidate";
    } else if (!out.phase_set_mass_balance_feasible) {
        out.phase_set_status = "candidate_mass_balance_incomplete";
    } else {
        out.phase_set_status = "phase_set_certified";
    }
    finalize_stage9_phase_discovery(out, tpd_tolerance, continuous_tpd_required);
    return out;
}

NeutralTwoPhaseEosInitialPoint build_neutral_two_phase_eos_initial_point(
    const add_args& args,
    const std::vector<double>& feed_amounts,
    double temperature,
    double target_pressure,
    const std::string& route_label,
    const std::vector<int>& phase_kinds,
    double shift_sign = 1.0
) {
    const std::vector<double> composition = normalized_positive_values(feed_amounts, route_label + " feed amount");
    const std::vector<double> first_composition =
        deterministic_composition_shift(composition, {}, route_label + " composition", shift_sign);
    return build_two_phase_eos_initial_point(
        args,
        feed_amounts,
        first_composition,
        temperature,
        target_pressure,
        route_label,
        phase_kinds
    );
}

NeutralTwoPhaseEosInitialPoint build_multiphase_eos_initial_point_from_candidate_set(
    const add_args& args,
    const std::vector<double>& feed_amounts,
    const NeutralPhaseDiscoveryResult& discovery,
    double temperature,
    double target_pressure,
    const std::string& route_label,
    const std::vector<int>& phase_kinds
) {
    const std::size_t phase_count = phase_kinds.size();
    if (phase_count < 2) {
        throw ValueError(route_label + " requires at least two phase kinds.");
    }
    if (discovery.selected_phase_compositions.size() != phase_count
        || discovery.selected_phase_fractions.size() != phase_count
        || discovery.selected_phase_kinds.size() != phase_count) {
        throw ValueError(route_label + " selected candidate set does not match requested phase kinds.");
    }
    const double total_feed = positive_sum(feed_amounts, route_label + " feed amount");
    NeutralTwoPhaseEosInitialPoint out;
    out.phase_amounts.assign(phase_count, std::vector<double>(feed_amounts.size(), 0.0));
    out.volumes.reserve(phase_count);
    for (std::size_t phase = 0; phase < phase_count; ++phase) {
        const std::vector<double> composition = normalized_trial_composition(
            discovery.selected_phase_compositions[phase],
            route_label + " phase-discovery composition"
        );
        require_size(composition, feed_amounts.size(), route_label + " phase-discovery composition");
        const double phase_fraction = discovery.selected_phase_fractions[phase];
        if (!(phase_fraction > 0.0 && phase_fraction < 1.0)) {
            throw ValueError(route_label + " phase-discovery phase fraction must be inside (0, 1).");
        }
        if (discovery.selected_phase_kinds[phase] != phase_kinds[phase]) {
            throw ValueError(route_label + " selected candidate phase kind does not match requested phase kind.");
        }
        for (std::size_t species = 0; species < composition.size(); ++species) {
            out.phase_amounts[phase][species] = total_feed * phase_fraction * composition[species];
            require_positive_finite(out.phase_amounts[phase][species], route_label + " phase-discovery amount");
        }
        const EosPhaseBlockResult block = evaluate_unit_phase_block_at_pressure_root(
            args,
            temperature,
            target_pressure,
            composition,
            phase_kinds[phase],
            route_label + " phase-discovery seed"
        );
        out.volumes.push_back((total_feed * phase_fraction) / block.density);
    }
    return out;
}

NeutralTwoPhaseEosInitialPoint build_two_phase_eos_initial_point_from_candidate_set(
    const add_args& args,
    const std::vector<double>& feed_amounts,
    const NeutralPhaseDiscoveryResult& discovery,
    double temperature,
    double target_pressure,
    const std::string& route_label,
    const std::vector<int>& phase_kinds
) {
    if (phase_kinds.size() != 2) {
        throw ValueError(route_label + " phase kind size does not match the neutral two-phase EOS NLP contract.");
    }
    return build_multiphase_eos_initial_point_from_candidate_set(
        args,
        feed_amounts,
        discovery,
        temperature,
        target_pressure,
        route_label,
        phase_kinds
    );
}

NeutralTwoPhaseEosInitialPoint build_charge_neutral_two_phase_eos_initial_point(
    const add_args& args,
    const std::vector<double>& feed_amounts,
    const std::vector<double>& charges,
    double temperature,
    double target_pressure,
    const std::string& route_label,
    const std::vector<int>& phase_kinds,
    double shift_sign = 1.0
) {
    const std::vector<double> composition = normalized_positive_values(feed_amounts, route_label + " feed amount");
    const std::vector<double> first_composition =
        deterministic_composition_shift(composition, charges, route_label + " composition", shift_sign);
    return build_two_phase_eos_initial_point(
        args,
        feed_amounts,
        first_composition,
        temperature,
        target_pressure,
        route_label,
        phase_kinds
    );
}

struct NamedInitialVariables {
    std::string seed_name;
    std::vector<double> variables;
};

std::vector<double> neutral_two_phase_variables_from_initial(
    const NeutralTwoPhaseEosInitialPoint& initial
) {
    std::vector<double> out;
    out.reserve(initial.phase_amounts.size() * (initial.phase_amounts.front().size() + 1));
    for (std::size_t phase = 0; phase < initial.phase_amounts.size(); ++phase) {
        out.insert(out.end(), initial.phase_amounts[phase].begin(), initial.phase_amounts[phase].end());
        out.push_back(initial.volumes[phase]);
    }
    return out;
}

void append_phase_discovery_seed_candidates(
    std::vector<NamedInitialVariables>& out,
    const add_args& args,
    const std::vector<double>& feed_amounts,
    double temperature,
    double target_pressure,
    const std::string& route_label,
    const std::vector<int>& phase_kinds
) {
    try {
        const std::vector<double> feed_composition =
            normalized_positive_values(feed_amounts, route_label + " feed amount");
        const NeutralPhaseDiscoveryResult discovery = evaluate_neutral_tpd_phase_discovery(
            args,
            temperature,
            target_pressure,
            feed_composition,
            phase_kinds,
            1.0e-6,
            1.0e-6,
            true
        );
        if (!discovery.held_stage_ii_replay_ready
            || !discovery.phase_set_mass_balance_feasible
            || discovery.selected_candidate_count != 2) {
            return;
        }
        out.push_back({
            kHeldStageIIDualLoopSeedName,
            neutral_two_phase_variables_from_initial(
                build_two_phase_eos_initial_point_from_candidate_set(
                    args,
                    feed_amounts,
                    discovery,
                    temperature,
                    target_pressure,
                    route_label,
                    phase_kinds
                )
            )
        });
    } catch (const std::exception&) {
        return;
    }
}

std::vector<NamedInitialVariables> neutral_two_phase_seed_candidates(
    const add_args& args,
    const std::vector<double>& feed_amounts,
    const std::vector<double>& charges,
    double temperature,
    double target_pressure,
    const std::string& route_label,
    const std::vector<int>& phase_kinds
) {
    std::vector<NamedInitialVariables> out;
    if (charges.empty()) {
        append_phase_discovery_seed_candidates(
            out,
            args,
            feed_amounts,
            temperature,
            target_pressure,
            route_label,
            phase_kinds
        );
        const std::vector<double> feed_composition =
            normalized_positive_values(feed_amounts, route_label + " feed amount");
        if (
            phase_kinds.size() == 2
            && phase_kinds[0] == 0
            && phase_kinds[1] == 0
            && feed_amounts.size() == 2
            && is_gross_2002_figure10_water_pentanol_case(args)
        ) {
            try {
                out.push_back({
                    "gross_2002_figure10_source_pair_water_rich",
                    neutral_two_phase_variables_from_initial(
                        build_two_phase_eos_initial_point(
                            args,
                            feed_amounts,
                            {0.995, 0.005},
                            temperature,
                            target_pressure,
                            route_label,
                            phase_kinds
                        )
                    )
                });
            } catch (const std::exception&) {
            }
        }
        out.push_back({
            "canonical_shifted_feed",
            neutral_two_phase_variables_from_initial(
                build_neutral_two_phase_eos_initial_point(
                    args,
                    feed_amounts,
                    temperature,
                    target_pressure,
                    route_label,
                    phase_kinds,
                    1.0
                )
            )
        });
        out.push_back({
            "mirrored_shifted_feed",
            neutral_two_phase_variables_from_initial(
                build_neutral_two_phase_eos_initial_point(
                    args,
                    feed_amounts,
                    temperature,
                    target_pressure,
                    route_label,
                    phase_kinds,
                    -1.0
                )
            )
        });
        if (feed_amounts.size() == 2) {
            auto append_binary_extreme = [&](int poor_component) {
                const int rich_component = 1 - poor_component;
                const double poor_fraction = std::max(
                    1.0e-6,
                    std::min(0.05, 0.5 * feed_composition[static_cast<std::size_t>(poor_component)])
                );
                std::vector<double> first_composition(2, 0.0);
                first_composition[static_cast<std::size_t>(poor_component)] = poor_fraction;
                first_composition[static_cast<std::size_t>(rich_component)] = 1.0 - poor_fraction;
                for (std::size_t species = 0; species < first_composition.size(); ++species) {
                    if (0.5 * first_composition[species] >= feed_composition[species]) {
                        return;
                    }
                }
                try {
                    out.push_back({
                        "binary_extreme_component_" + std::to_string(poor_component) + "_poor",
                        neutral_two_phase_variables_from_initial(
                            build_two_phase_eos_initial_point(
                                args,
                                feed_amounts,
                                first_composition,
                                temperature,
                                target_pressure,
                                route_label,
                                phase_kinds
                            )
                        )
                    });
                } catch (const std::exception&) {
                    return;
                }
            };
            append_binary_extreme(0);
            append_binary_extreme(1);
        }
        return out;
    }
    out.push_back({
        "canonical_shifted_feed",
        neutral_two_phase_variables_from_initial(
            build_charge_neutral_two_phase_eos_initial_point(
                args,
                feed_amounts,
                charges,
                temperature,
                target_pressure,
                route_label,
                phase_kinds,
                1.0
            )
        )
    });
    out.push_back({
        "mirrored_shifted_feed",
        neutral_two_phase_variables_from_initial(
            build_charge_neutral_two_phase_eos_initial_point(
                args,
                feed_amounts,
                charges,
                temperature,
                target_pressure,
                route_label,
                phase_kinds,
                -1.0
            )
        )
    });
    return out;
}

double vector_infinity_norm(const std::vector<double>& values, std::size_t begin, std::size_t end) {
    double norm = 0.0;
    for (std::size_t index = begin; index < end; ++index) {
        norm = std::max(norm, std::abs(values[index]));
    }
    return norm;
}

double phase_distance_inf_norm(const std::vector<double>& first, const std::vector<double>& second) {
    require_size(second, first.size(), "Neutral EOS postsolve phase composition");
    double distance = 0.0;
    for (std::size_t index = 0; index < first.size(); ++index) {
        distance = std::max(distance, std::abs(first[index] - second[index]));
    }
    return distance;
}

double phase_charge_inf_norm(
    const std::vector<std::vector<double>>& phase_amounts,
    const std::vector<double>& charges
) {
    if (charges.empty()) {
        return 0.0;
    }
    double norm = 0.0;
    for (const auto& phase : phase_amounts) {
        require_size(phase, charges.size(), "Electrolyte LLE phase charge");
        double charge = 0.0;
        for (std::size_t species = 0; species < charges.size(); ++species) {
            charge += phase[species] * charges[species];
        }
        norm = std::max(norm, std::abs(charge));
    }
    return norm;
}

double chemical_potential_inf_norm(
    const EosPhaseBlockResult& first,
    const EosPhaseBlockResult& second,
    std::size_t species_count
) {
    if (first.gradient.size() < species_count || second.gradient.size() < species_count) {
        throw ValueError("Neutral EOS postsolve phase gradient sizes did not match species count.");
    }
    double norm = 0.0;
    for (std::size_t species = 0; species < species_count; ++species) {
        norm = std::max(norm, std::abs(first.gradient[species] - second.gradient[species]));
    }
    return norm;
}

double charge_projected_difference_inf_norm(
    const std::vector<double>& first_values,
    const std::vector<double>& second_values,
    const std::vector<double>& charges,
    std::size_t species_count
) {
    if (charges.empty()) {
        double norm = 0.0;
        for (std::size_t species = 0; species < species_count; ++species) {
            norm = std::max(norm, std::abs(first_values[species] - second_values[species]));
        }
        return norm;
    }
    require_size(charges, species_count, "Electrolyte phase-equilibrium charge");
    double charge_square_norm = 0.0;
    double charge_weighted_difference = 0.0;
    std::vector<double> differences(species_count, 0.0);
    for (std::size_t species = 0; species < species_count; ++species) {
        differences[species] = first_values[species] - second_values[species];
        charge_square_norm += charges[species] * charges[species];
        charge_weighted_difference += charges[species] * differences[species];
    }
    const double charge_shift = charge_square_norm > 0.0
        ? -charge_weighted_difference / charge_square_norm
        : 0.0;
    double norm = 0.0;
    for (std::size_t species = 0; species < species_count; ++species) {
        norm = std::max(norm, std::abs(differences[species] + charge_shift * charges[species]));
    }
    return norm;
}

double electrochemical_potential_inf_norm(
    const EosPhaseBlockResult& first,
    const EosPhaseBlockResult& second,
    const std::vector<double>& charges,
    std::size_t species_count
) {
    if (first.gradient.size() < species_count || second.gradient.size() < species_count) {
        throw ValueError("Electrolyte EOS postsolve phase gradient sizes did not match species count.");
    }
    return charge_projected_difference_inf_norm(first.gradient, second.gradient, charges, species_count);
}

std::vector<double> reduced_ln_fugacity_values(
    const add_args& args,
    const EosPhaseBlockResult& block,
    std::size_t species_count
) {
    if (block.composition.size() < species_count) {
        throw ValueError("Neutral EOS postsolve phase composition size did not match species count.");
    }
    FugacityContributionResult fugacity = fugacity_coefficient_result_cpp(
        block.temperature,
        block.density,
        block.composition,
        args
    );
    if (fugacity.lnfugcoef.total.size() < species_count) {
        throw ValueError("Neutral EOS postsolve fugacity payload size did not match species count.");
    }
    std::vector<double> values;
    values.reserve(species_count);
    for (std::size_t species = 0; species < species_count; ++species) {
        require_positive_finite(block.composition[species], "Neutral EOS postsolve phase composition");
        values.push_back(std::log(block.composition[species]) + fugacity.lnfugcoef.total[species]);
    }
    return values;
}

std::vector<double> ln_fugacity_coefficients_for_postsolve(
    const add_args& args,
    const EosPhaseBlockResult& block,
    std::size_t species_count
) {
    FugacityContributionResult fugacity = fugacity_coefficient_result_cpp(
        block.temperature,
        block.density,
        block.composition,
        args
    );
    if (fugacity.lnfugcoef.total.size() < species_count) {
        throw ValueError("Neutral EOS postsolve fugacity payload size did not match species count.");
    }
    std::vector<double> values;
    values.reserve(species_count);
    for (std::size_t species = 0; species < species_count; ++species) {
        values.push_back(fugacity.lnfugcoef.total[species]);
    }
    return values;
}

double ln_fugacity_inf_norm(
    const add_args& args,
    const EosPhaseBlockResult& first,
    const EosPhaseBlockResult& second,
    std::size_t species_count,
    const std::vector<double>& charges = {}
) {
    const std::vector<double> first_values = reduced_ln_fugacity_values(args, first, species_count);
    const std::vector<double> second_values = reduced_ln_fugacity_values(args, second, species_count);
    return charge_projected_difference_inf_norm(first_values, second_values, charges, species_count);
}

double pairwise_chemical_potential_inf_norm(
    const std::vector<EosPhaseBlockResult>& phase_blocks,
    std::size_t species_count,
    const std::vector<double>& charges
) {
    double norm = 0.0;
    for (std::size_t first = 0; first < phase_blocks.size(); ++first) {
        for (std::size_t second = first + 1; second < phase_blocks.size(); ++second) {
            norm = std::max(
                norm,
                charges.empty()
                    ? chemical_potential_inf_norm(phase_blocks[first], phase_blocks[second], species_count)
                    : electrochemical_potential_inf_norm(
                        phase_blocks[first],
                        phase_blocks[second],
                        charges,
                        species_count
                    )
            );
        }
    }
    return norm;
}

double pairwise_ln_fugacity_inf_norm(
    const add_args& args,
    const std::vector<EosPhaseBlockResult>& phase_blocks,
    std::size_t species_count,
    const std::vector<double>& charges
) {
    double norm = 0.0;
    for (std::size_t first = 0; first < phase_blocks.size(); ++first) {
        for (std::size_t second = first + 1; second < phase_blocks.size(); ++second) {
            norm = std::max(
                norm,
                ln_fugacity_inf_norm(args, phase_blocks[first], phase_blocks[second], species_count, charges)
            );
        }
    }
    return norm;
}

double pairwise_phase_distance_inf_norm(const std::vector<std::vector<double>>& phase_compositions) {
    double norm = 0.0;
    for (std::size_t first = 0; first < phase_compositions.size(); ++first) {
        for (std::size_t second = first + 1; second < phase_compositions.size(); ++second) {
            norm = std::max(
                norm,
                composition_distance_inf_norm(phase_compositions[first], phase_compositions[second])
            );
        }
    }
    return norm;
}

std::vector<std::vector<double>> neutral_phase_amounts_from_route_variables(
    const std::vector<double>& variables,
    std::size_t species_count
) {
    const std::size_t local_variable_count = species_count + 1;
    if (local_variable_count == 0 || variables.size() % local_variable_count != 0) {
        throw ValueError("Neutral EOS route result variable size does not match the phase amount-volume layout.");
    }
    const std::size_t phase_count = variables.size() / local_variable_count;
    if (phase_count < 2) {
        throw ValueError("Neutral EOS route result variable layout requires at least two phases.");
    }
    std::vector<std::vector<double>> phase_amounts(phase_count, std::vector<double>(species_count, 0.0));
    for (std::size_t phase = 0; phase < phase_count; ++phase) {
        const std::size_t offset = phase * local_variable_count;
        for (std::size_t species = 0; species < species_count; ++species) {
            phase_amounts[phase][species] = variables[offset + species];
        }
    }
    return phase_amounts;
}

std::vector<double> neutral_phase_volumes_from_route_variables(
    const std::vector<double>& variables,
    std::size_t species_count
) {
    const std::size_t local_variable_count = species_count + 1;
    if (local_variable_count == 0 || variables.size() % local_variable_count != 0) {
        throw ValueError("Neutral EOS route result variable size does not match the phase amount-volume layout.");
    }
    const std::size_t phase_count = variables.size() / local_variable_count;
    if (phase_count < 2) {
        throw ValueError("Neutral EOS route result variable layout requires at least two phases.");
    }
    std::vector<double> volumes;
    volumes.reserve(phase_count);
    for (std::size_t phase = 0; phase < phase_count; ++phase) {
        volumes.push_back(variables[phase * local_variable_count + species_count]);
    }
    return volumes;
}

class NeutralTwoPhaseEosProblem final : public NlpProblem {
public:
    NeutralTwoPhaseEosProblem(
        add_args args,
        double temperature,
        double target_pressure,
        std::vector<std::vector<double>> phase_amounts,
        std::vector<double> volumes,
        std::vector<double> feed_amounts,
        std::vector<double> charges = {},
        std::string problem_name = "neutral_two_phase_eos",
        double minimum_phase_distance = 0.0
    )
        : args_(std::move(args)),
          temperature_(temperature),
          target_pressure_(target_pressure),
          initial_phase_amounts_(std::move(phase_amounts)),
          initial_volumes_(std::move(volumes)),
          feed_amounts_(std::move(feed_amounts)),
          charges_(std::move(charges)),
          problem_name_(std::move(problem_name)),
          minimum_phase_distance_(minimum_phase_distance) {
        phase_count_ = static_cast<int>(initial_phase_amounts_.size());
        if (phase_count_ < 2) {
            throw ValueError("Neutral EOS route builder requires at least two phases.");
        }
        if (!std::isfinite(temperature_) || temperature_ <= 0.0 || !std::isfinite(target_pressure_)) {
            throw ValueError("Neutral EOS route builder received invalid T/P specifications.");
        }
        species_count_ = static_cast<int>(feed_amounts_.size());
        if (species_count_ <= 0) {
            throw ValueError("Neutral EOS route builder requires at least one feed species.");
        }
        if (!charges_.empty()) {
            require_size(charges_, static_cast<std::size_t>(species_count_), "Neutral EOS route charge");
        }
        require_size(initial_volumes_, initial_phase_amounts_.size(), "Neutral EOS route volume");
        for (const auto& amounts : initial_phase_amounts_) {
            require_size(amounts, static_cast<std::size_t>(species_count_), "Neutral EOS route phase amount");
            for (double amount : amounts) {
                require_positive_finite(amount, "Neutral EOS route phase amount");
            }
        }
        for (double volume : initial_volumes_) {
            require_positive_finite(volume, "Neutral EOS route phase volume");
        }
        for (double amount : feed_amounts_) {
            if (!std::isfinite(amount) || amount < 0.0) {
                throw ValueError("Neutral EOS route feed amounts must be finite and non-negative.");
            }
        }
        if (minimum_phase_distance_ > 0.0) {
            if (phase_count_ != 2) {
                throw ValueError("Neutral EOS route phase-distance gating currently requires exactly two phases.");
            }
            const std::vector<double> first = phase_composition(
                initial_phase_amounts_[0],
                "Neutral EOS route first phase amount total"
            );
            const std::vector<double> second = phase_composition(
                initial_phase_amounts_[1],
                "Neutral EOS route second phase amount total"
            );
            double max_distance = 0.0;
            for (int species = 0; species < species_count_; ++species) {
                const double diff =
                    first[static_cast<std::size_t>(species)] - second[static_cast<std::size_t>(species)];
                if (std::abs(diff) > max_distance) {
                    max_distance = std::abs(diff);
                    separation_species_index_ = species;
                    separation_sign_ = diff >= 0.0 ? 1.0 : -1.0;
                }
            }
            if (max_distance <= 0.0) {
                throw ValueError("Neutral EOS route requires distinct initial phases for phase-separation gating.");
            }
        }
    }

    std::string name() const override {
        return problem_name_;
    }

    int variable_count() const override {
        return phase_count() * local_variable_count();
    }

    int constraint_count() const override {
        return species_count_ + phase_count() + (charges_.empty() ? 0 : phase_count())
            + separation_constraint_count();
    }

    int jacobian_nonzero_count() const override {
        const int material_nonzeros = phase_count() * species_count_;
        const int pressure_nonzeros = phase_count() * local_variable_count();
        const int charge_nonzeros = charges_.empty() ? 0 : phase_count() * species_count_;
        const int separation_nonzeros = separation_constraint_count() > 0 ? phase_count() * species_count_ : 0;
        return material_nonzeros + pressure_nonzeros + charge_nonzeros + separation_nonzeros;
    }

    NlpBounds bounds() const override {
        NlpBounds out;
        const double total_feed = std::accumulate(feed_amounts_.begin(), feed_amounts_.end(), 0.0);
        const double amount_upper = std::max(1.0, 10.0 * total_feed);
        const double volume_upper = std::max(1.0, 1.0e6 * total_feed);
        out.variable_lower.assign(static_cast<std::size_t>(variable_count()), 1.0e-14);
        out.variable_upper.reserve(static_cast<std::size_t>(variable_count()));
        for (int phase = 0; phase < phase_count(); ++phase) {
            for (int species = 0; species < species_count_; ++species) {
                out.variable_upper.push_back(amount_upper);
            }
            out.variable_upper.push_back(volume_upper);
        }
        out.constraint_lower.assign(static_cast<std::size_t>(constraint_count()), 0.0);
        out.constraint_upper.assign(static_cast<std::size_t>(constraint_count()), 0.0);
        if (separation_constraint_count() > 0) {
            out.constraint_lower.back() = minimum_phase_distance_;
            out.constraint_upper.back() = 1.0e12;
        }
        return out;
    }

    std::vector<double> initial_point() const override {
        std::vector<double> out;
        out.reserve(static_cast<std::size_t>(variable_count()));
        for (std::size_t phase = 0; phase < initial_phase_amounts_.size(); ++phase) {
            out.insert(out.end(), initial_phase_amounts_[phase].begin(), initial_phase_amounts_[phase].end());
            out.push_back(initial_volumes_[phase]);
        }
        return out;
    }

    double objective(const std::vector<double>& variables) const override {
        return phase_system(variables).objective;
    }

    std::vector<double> objective_gradient(const std::vector<double>& variables) const override {
        return phase_system(variables).gradient;
    }

    std::vector<double> constraints(const std::vector<double>& variables) const override {
        std::vector<double> out = phase_system(variables).constraints;
        if (separation_constraint_count() > 0) {
            out.push_back(phase_separation(phase_amounts_from_variables(variables)));
        }
        return out;
    }

    NlpJacobianStructure jacobian_structure() const override {
        NlpJacobianStructure out;
        out.rows.reserve(static_cast<std::size_t>(jacobian_nonzero_count()));
        out.cols.reserve(static_cast<std::size_t>(jacobian_nonzero_count()));
        for (int species = 0; species < species_count_; ++species) {
            for (int phase = 0; phase < phase_count(); ++phase) {
                out.rows.push_back(species);
                out.cols.push_back(phase * local_variable_count() + species);
            }
        }
        const int pressure_row_start = species_count_;
        for (int phase = 0; phase < phase_count(); ++phase) {
            const int row = pressure_row_start + phase;
            const int phase_offset = phase * local_variable_count();
            for (int col = 0; col < local_variable_count(); ++col) {
                out.rows.push_back(row);
                out.cols.push_back(phase_offset + col);
            }
        }
        if (!charges_.empty()) {
            const int charge_row_start = pressure_row_start + phase_count();
            for (int phase = 0; phase < phase_count(); ++phase) {
                const int row = charge_row_start + phase;
                const int phase_offset = phase * local_variable_count();
                for (int species = 0; species < species_count_; ++species) {
                    out.rows.push_back(row);
                    out.cols.push_back(phase_offset + species);
                }
            }
        }
        if (separation_constraint_count() > 0) {
            const int row = constraint_count() - 1;
            for (int phase = 0; phase < phase_count(); ++phase) {
                const int phase_offset = phase * local_variable_count();
                for (int species = 0; species < species_count_; ++species) {
                    out.rows.push_back(row);
                    out.cols.push_back(phase_offset + species);
                }
            }
        }
        return out;
    }

    std::vector<double> jacobian_values(const std::vector<double>& variables) const override {
        const EosPhaseSystemResult system = phase_system(variables);
        std::vector<double> out;
        out.reserve(static_cast<std::size_t>(jacobian_nonzero_count()));
        const int dense_cols = variable_count();
        for (int species = 0; species < species_count_; ++species) {
            for (int phase = 0; phase < phase_count(); ++phase) {
                out.push_back(
                    system.constraint_jacobian_row_major[
                        static_cast<std::size_t>(species) * static_cast<std::size_t>(dense_cols)
                        + static_cast<std::size_t>(phase * local_variable_count() + species)
                    ]
                );
            }
        }
        const int pressure_row_start = species_count_;
        for (int phase = 0; phase < phase_count(); ++phase) {
            const int row = pressure_row_start + phase;
            const int phase_offset = phase * local_variable_count();
            for (int col = 0; col < local_variable_count(); ++col) {
                out.push_back(
                    system.constraint_jacobian_row_major[
                        static_cast<std::size_t>(row) * static_cast<std::size_t>(dense_cols)
                        + static_cast<std::size_t>(phase_offset + col)
                    ]
                );
            }
        }
        if (!charges_.empty()) {
            const int charge_row_start = pressure_row_start + phase_count();
            for (int phase = 0; phase < phase_count(); ++phase) {
                const int row = charge_row_start + phase;
                const int phase_offset = phase * local_variable_count();
                for (int species = 0; species < species_count_; ++species) {
                    out.push_back(
                        system.constraint_jacobian_row_major[
                            static_cast<std::size_t>(row) * static_cast<std::size_t>(dense_cols)
                            + static_cast<std::size_t>(phase_offset + species)
                        ]
                    );
                }
            }
        }
        if (separation_constraint_count() > 0) {
            const std::vector<double> row = phase_separation_jacobian(phase_amounts_from_variables(variables));
            for (int phase = 0; phase < phase_count(); ++phase) {
                const int phase_offset = phase * local_variable_count();
                for (int species = 0; species < species_count_; ++species) {
                    out.push_back(row[static_cast<std::size_t>(phase_offset + species)]);
                }
            }
        }
        return out;
    }

    bool has_exact_hessian() const override {
        return args_.z.empty() || args_.born_model <= 1;
    }

    int hessian_nonzero_count() const override {
        if (!has_exact_hessian()) {
            return 0;
        }
        return LagrangianHessianAssembler(variable_count()).nonzero_count();
    }

    NlpHessianStructure hessian_structure() const override {
        if (!has_exact_hessian()) {
            return {};
        }
        return LagrangianHessianAssembler(variable_count()).structure();
    }

    std::vector<double> hessian_values(
        const std::vector<double>& variables,
        double objective_factor,
        const std::vector<double>& constraint_multipliers
    ) const override {
        if (!has_exact_hessian()) {
            throw ValueError("Neutral EOS route exact Hessian requires direct or absent Born phase blocks.");
        }
        if (constraint_multipliers.size() != static_cast<std::size_t>(constraint_count())) {
            throw ValueError("Neutral EOS route Hessian multiplier vector size does not match the constraint count.");
        }
        const EosPhaseSystemResult system = phase_system(variables);
        if (system.objective_hessian_row_major.size()
            != static_cast<std::size_t>(variable_count() * variable_count())) {
            throw ValueError("Neutral EOS route objective Hessian shape did not match the NLP variable count.");
        }

        ObjectiveSecondOrderData objective;
        objective.variable_count = variable_count();
        objective.value = system.objective;
        objective.gradient = system.gradient;
        objective.hessian_row_major = system.objective_hessian_row_major;
        objective.backend = system.objective_hessian_backend;

        ConstraintSecondOrderData constraints;
        constraints.constraint_count = constraint_count();
        constraints.variable_count = variable_count();
        constraints.values = system.constraints;
        constraints.jacobian_row_major = system.constraint_jacobian_row_major;
        constraints.hessian_tensor_row_major.assign(
            static_cast<std::size_t>(constraint_count() * variable_count() * variable_count()),
            0.0
        );
        constraints.has_hessian.assign(static_cast<std::size_t>(constraint_count()), false);
        constraints.backend = system.constraint_hessian_backend;
        if (system.constraint_hessian_tensor_row_major.size()
            != static_cast<std::size_t>(
                system.constraint_jacobian_rows * variable_count() * variable_count()
            )) {
            throw ValueError("Neutral EOS route constraint Hessian tensor shape did not match the system constraints.");
        }
        for (int row = 0; row < system.constraint_jacobian_rows; ++row) {
            if (row >= constraint_count()) {
                throw ValueError("Neutral EOS route system constraint count exceeded the NLP constraint count.");
            }
            constraints.has_hessian[static_cast<std::size_t>(row)] =
                row < static_cast<int>(system.constraint_has_hessian.size())
                && system.constraint_has_hessian[static_cast<std::size_t>(row)];
            const std::size_t source_offset =
                static_cast<std::size_t>(row * variable_count() * variable_count());
            std::copy(
                system.constraint_hessian_tensor_row_major.begin() + static_cast<std::ptrdiff_t>(source_offset),
                system.constraint_hessian_tensor_row_major.begin()
                    + static_cast<std::ptrdiff_t>(source_offset + variable_count() * variable_count()),
                constraints.hessian_tensor_row_major.begin() + static_cast<std::ptrdiff_t>(source_offset)
            );
        }
        if (separation_constraint_count() > 0) {
            constraints.has_hessian.back() = true;
            const std::vector<double> separation_hessian =
                phase_separation_hessian(phase_amounts_from_variables(variables));
            const std::size_t offset = static_cast<std::size_t>(
                (constraint_count() - 1) * variable_count() * variable_count()
            );
            std::copy(
                separation_hessian.begin(),
                separation_hessian.end(),
                constraints.hessian_tensor_row_major.begin() + static_cast<std::ptrdiff_t>(offset)
            );
        }
        return LagrangianHessianAssembler(variable_count()).values(
            objective_factor,
            objective,
            constraints,
            constraint_multipliers
        );
    }

    std::string hessian_backend() const override {
        return "cppad_phase_system";
    }

    NlpScaling scaling() const override {
        const double total_feed = std::accumulate(feed_amounts_.begin(), feed_amounts_.end(), 0.0);
        const double amount_scale = std::max(1.0, total_feed);
        NlpScaling out;
        out.objective = 1.0 / amount_scale;
        out.variables.assign(static_cast<std::size_t>(variable_count()), 1.0 / amount_scale);
        out.constraints.assign(static_cast<std::size_t>(constraint_count()), 1.0 / amount_scale);
        if (separation_constraint_count() > 0) {
            out.constraints.back() = 1.0;
        }
        return out;
    }

    std::map<std::string, std::string> diagnostics() const override {
        return route_metadata_diagnostics(
            phase_amount_volume_route_metadata(!charges_.empty(), separation_constraint_count() > 0)
        );
    }

    int species_count() const {
        return species_count_;
    }

    int phase_count() const {
        return phase_count_;
    }

private:
    int local_variable_count() const {
        return species_count_ + 1;
    }

    int separation_constraint_count() const {
        return minimum_phase_distance_ > 0.0 ? 1 : 0;
    }

    std::vector<double> phase_composition(
        const std::vector<double>& amounts,
        const std::string& total_label
    ) const {
        require_size(amounts, static_cast<std::size_t>(species_count_), "Neutral EOS route phase amount");
        const double total = std::accumulate(amounts.begin(), amounts.end(), 0.0);
        require_positive_finite(total, total_label);
        std::vector<double> composition;
        composition.reserve(amounts.size());
        for (double amount : amounts) {
            composition.push_back(amount / total);
        }
        return composition;
    }

    double phase_separation(const std::vector<std::vector<double>>& phase_amounts) const {
        const std::vector<double> first = phase_composition(
            phase_amounts[0],
            "Neutral EOS route first phase amount total"
        );
        const std::vector<double> second = phase_composition(
            phase_amounts[1],
            "Neutral EOS route second phase amount total"
        );
        const std::size_t species = static_cast<std::size_t>(separation_species_index_);
        return separation_sign_ * (first[species] - second[species]);
    }

    std::vector<double> phase_separation_jacobian(
        const std::vector<std::vector<double>>& phase_amounts
    ) const {
        const std::vector<double> first = phase_composition(
            phase_amounts[0],
            "Neutral EOS route first phase amount total"
        );
        const std::vector<double> second = phase_composition(
            phase_amounts[1],
            "Neutral EOS route second phase amount total"
        );
        const double first_total = std::accumulate(phase_amounts[0].begin(), phase_amounts[0].end(), 0.0);
        const double second_total = std::accumulate(phase_amounts[1].begin(), phase_amounts[1].end(), 0.0);
        require_positive_finite(first_total, "Neutral EOS route first phase amount total");
        require_positive_finite(second_total, "Neutral EOS route second phase amount total");

        std::vector<double> row(static_cast<std::size_t>(variable_count()), 0.0);
        const std::size_t selected = static_cast<std::size_t>(separation_species_index_);
        for (int species = 0; species < species_count_; ++species) {
            const std::size_t index = static_cast<std::size_t>(species);
            const double first_indicator = index == selected ? 1.0 : 0.0;
            row[index] = separation_sign_ * (first_indicator - first[selected]) / first_total;

            const std::size_t second_offset = static_cast<std::size_t>(local_variable_count() + species);
            const double second_indicator = index == selected ? 1.0 : 0.0;
            row[second_offset] = -separation_sign_ * (second_indicator - second[selected]) / second_total;
        }
        return row;
    }

    std::vector<double> phase_separation_hessian(
        const std::vector<std::vector<double>>& phase_amounts
    ) const {
        if (phase_amounts.size() != static_cast<std::size_t>(phase_count())) {
            throw ValueError("Neutral EOS route phase amount phase count does not match the NLP model.");
        }
        std::vector<double> hessian(static_cast<std::size_t>(variable_count() * variable_count()), 0.0);
        const std::size_t selected = static_cast<std::size_t>(separation_species_index_);
        for (int phase = 0; phase < phase_count(); ++phase) {
            const std::vector<double> composition = phase_composition(
                phase_amounts[static_cast<std::size_t>(phase)],
                "Neutral EOS route phase amount total"
            );
            const double total = std::accumulate(
                phase_amounts[static_cast<std::size_t>(phase)].begin(),
                phase_amounts[static_cast<std::size_t>(phase)].end(),
                0.0
            );
            require_positive_finite(total, "Neutral EOS route phase amount total");
            const double phase_sign = phase == 0 ? separation_sign_ : -separation_sign_;
            const std::size_t phase_offset = static_cast<std::size_t>(phase * local_variable_count());
            for (int first = 0; first < species_count_; ++first) {
                for (int second = 0; second < species_count_; ++second) {
                    const double first_indicator =
                        static_cast<std::size_t>(first) == selected ? 1.0 : 0.0;
                    const double second_indicator =
                        static_cast<std::size_t>(second) == selected ? 1.0 : 0.0;
                    const double value = phase_sign
                        * (2.0 * composition[selected] - first_indicator - second_indicator)
                        / (total * total);
                    const std::size_t row = phase_offset + static_cast<std::size_t>(first);
                    const std::size_t col = phase_offset + static_cast<std::size_t>(second);
                    hessian[row * static_cast<std::size_t>(variable_count()) + col] = value;
                }
            }
        }
        return hessian;
    }

    std::vector<std::vector<double>> phase_amounts_from_variables(const std::vector<double>& variables) const {
        require_size(variables, static_cast<std::size_t>(variable_count()), "Neutral EOS route variable");
        std::vector<std::vector<double>> phase_amounts(
            static_cast<std::size_t>(phase_count()),
            std::vector<double>(static_cast<std::size_t>(species_count_), 0.0)
        );
        for (int phase = 0; phase < phase_count(); ++phase) {
            const std::size_t offset = static_cast<std::size_t>(phase * local_variable_count());
            for (int species = 0; species < species_count_; ++species) {
                phase_amounts[static_cast<std::size_t>(phase)][static_cast<std::size_t>(species)] =
                    variables[offset + static_cast<std::size_t>(species)];
            }
        }
        return phase_amounts;
    }

    std::vector<double> volumes_from_variables(const std::vector<double>& variables) const {
        require_size(variables, static_cast<std::size_t>(variable_count()), "Neutral EOS route variable");
        std::vector<double> volumes(static_cast<std::size_t>(phase_count()), 0.0);
        for (int phase = 0; phase < phase_count(); ++phase) {
            const std::size_t volume_index = static_cast<std::size_t>(
                phase * local_variable_count() + species_count_
            );
            volumes[static_cast<std::size_t>(phase)] = variables[volume_index];
        }
        return volumes;
    }

    EosPhaseSystemResult phase_system(const std::vector<double>& variables) const {
        return evaluate_eos_phase_system(
            args_,
            temperature_,
            target_pressure_,
            phase_amounts_from_variables(variables),
            volumes_from_variables(variables),
            feed_amounts_,
            charges_
        );
    }

    add_args args_;
    double temperature_ = 0.0;
    double target_pressure_ = 0.0;
    std::vector<std::vector<double>> initial_phase_amounts_;
    std::vector<double> initial_volumes_;
    std::vector<double> feed_amounts_;
    std::vector<double> charges_;
    std::string problem_name_;
    double minimum_phase_distance_ = 0.0;
    int separation_species_index_ = 0;
    double separation_sign_ = 1.0;
    int phase_count_ = 0;
    int species_count_ = 0;
};

class NeutralMultiphaseFugacityResidualProblem final : public NlpProblem {
public:
    NeutralMultiphaseFugacityResidualProblem(
        add_args args,
        double temperature,
        double target_pressure,
        std::vector<std::vector<double>> phase_amounts,
        std::vector<double> volumes,
        std::vector<double> feed_amounts
    )
        : args_(std::move(args)),
          temperature_(temperature),
          target_pressure_(target_pressure),
          initial_phase_amounts_(std::move(phase_amounts)),
          initial_volumes_(std::move(volumes)),
          feed_amounts_(std::move(feed_amounts)) {
        phase_count_ = static_cast<int>(initial_phase_amounts_.size());
        species_count_ = static_cast<int>(feed_amounts_.size());
        if (phase_count_ < 3) {
            throw ValueError("Strict multiphase fugacity residual route requires at least three phases.");
        }
        if (species_count_ <= 0) {
            throw ValueError("Strict multiphase fugacity residual route requires at least one species.");
        }
        if (!std::isfinite(temperature_) || temperature_ <= 0.0 || !std::isfinite(target_pressure_)) {
            throw ValueError("Strict multiphase fugacity residual route received invalid T/P specifications.");
        }
        require_size(initial_volumes_, initial_phase_amounts_.size(), "Strict multiphase residual volume");
        for (const auto& amounts : initial_phase_amounts_) {
            require_size(amounts, static_cast<std::size_t>(species_count_), "Strict multiphase residual phase amount");
            for (double amount : amounts) {
                require_positive_finite(amount, "Strict multiphase residual phase amount");
            }
        }
        for (double volume : initial_volumes_) {
            require_positive_finite(volume, "Strict multiphase residual phase volume");
        }
        for (double amount : feed_amounts_) {
            if (!std::isfinite(amount) || amount < 0.0) {
                throw ValueError("Strict multiphase residual feed amounts must be finite and non-negative.");
            }
        }
    }

    std::string name() const override {
        return "neutral_multiphase_fugacity_residual";
    }

    int variable_count() const override {
        return phase_count() * local_variable_count();
    }

    int constraint_count() const override {
        return species_count_ + phase_count() + phase_equilibrium_constraint_count();
    }

    int jacobian_nonzero_count() const override {
        const int material_nonzeros = phase_count() * species_count_;
        const int pressure_nonzeros = phase_count() * local_variable_count();
        const int fugacity_nonzeros =
            phase_equilibrium_constraint_count() * 2 * local_variable_count();
        return material_nonzeros + pressure_nonzeros + fugacity_nonzeros;
    }

    NlpBounds bounds() const override {
        NlpBounds out;
        const double total_feed = std::accumulate(feed_amounts_.begin(), feed_amounts_.end(), 0.0);
        const double amount_upper = std::max(1.0, 10.0 * total_feed);
        const double volume_upper = std::max(1.0, 1.0e6 * total_feed);
        out.variable_lower.assign(static_cast<std::size_t>(variable_count()), 1.0e-14);
        out.variable_upper.reserve(static_cast<std::size_t>(variable_count()));
        for (int phase = 0; phase < phase_count(); ++phase) {
            for (int species = 0; species < species_count_; ++species) {
                out.variable_upper.push_back(amount_upper);
            }
            out.variable_upper.push_back(volume_upper);
        }
        out.constraint_lower.assign(static_cast<std::size_t>(constraint_count()), 0.0);
        out.constraint_upper.assign(static_cast<std::size_t>(constraint_count()), 0.0);
        return out;
    }

    std::vector<double> initial_point() const override {
        std::vector<double> out;
        out.reserve(static_cast<std::size_t>(variable_count()));
        for (std::size_t phase = 0; phase < initial_phase_amounts_.size(); ++phase) {
            out.insert(out.end(), initial_phase_amounts_[phase].begin(), initial_phase_amounts_[phase].end());
            out.push_back(initial_volumes_[phase]);
        }
        return out;
    }

    double objective(const std::vector<double>& variables) const override {
        (void)variables;
        return 0.0;
    }

    std::vector<double> objective_gradient(const std::vector<double>& variables) const override {
        require_size(variables, static_cast<std::size_t>(variable_count()), "Strict multiphase residual variable");
        return std::vector<double>(static_cast<std::size_t>(variable_count()), 0.0);
    }

    std::vector<double> constraints(const std::vector<double>& variables) const override {
        const EosPhaseSystemResult system = phase_system(variables);
        const PhaseEquilibriumResidualBlockResult residuals = residual_block(variables);
        std::vector<double> out;
        out.reserve(static_cast<std::size_t>(constraint_count()));
        out.insert(out.end(), system.constraints.begin(), system.constraints.begin() + species_count_ + phase_count());
        out.insert(out.end(), residuals.residuals.begin(), residuals.residuals.end());
        return out;
    }

    NlpJacobianStructure jacobian_structure() const override {
        NlpJacobianStructure out;
        out.rows.reserve(static_cast<std::size_t>(jacobian_nonzero_count()));
        out.cols.reserve(static_cast<std::size_t>(jacobian_nonzero_count()));
        for (int species = 0; species < species_count_; ++species) {
            for (int phase = 0; phase < phase_count(); ++phase) {
                out.rows.push_back(species);
                out.cols.push_back(phase * local_variable_count() + species);
            }
        }
        const int pressure_row_start = species_count_;
        for (int phase = 0; phase < phase_count(); ++phase) {
            const int row = pressure_row_start + phase;
            const int phase_offset = phase * local_variable_count();
            for (int col = 0; col < local_variable_count(); ++col) {
                out.rows.push_back(row);
                out.cols.push_back(phase_offset + col);
            }
        }
        const int fugacity_row_start = species_count_ + phase_count();
        for (int phase = 1; phase < phase_count(); ++phase) {
            const int active_offset = phase * local_variable_count();
            for (int species = 0; species < species_count_; ++species) {
                const int row = fugacity_row_start + (phase - 1) * species_count_ + species;
                for (int col = 0; col < local_variable_count(); ++col) {
                    out.rows.push_back(row);
                    out.cols.push_back(col);
                }
                for (int col = 0; col < local_variable_count(); ++col) {
                    out.rows.push_back(row);
                    out.cols.push_back(active_offset + col);
                }
            }
        }
        return out;
    }

    std::vector<double> jacobian_values(const std::vector<double>& variables) const override {
        const EosPhaseSystemResult system = phase_system(variables);
        const PhaseEquilibriumResidualBlockResult residuals = residual_block(variables);
        std::vector<double> out;
        out.reserve(static_cast<std::size_t>(jacobian_nonzero_count()));
        const int dense_cols = variable_count();
        for (int species = 0; species < species_count_; ++species) {
            for (int phase = 0; phase < phase_count(); ++phase) {
                out.push_back(
                    system.constraint_jacobian_row_major[
                        static_cast<std::size_t>(species) * static_cast<std::size_t>(dense_cols)
                        + static_cast<std::size_t>(phase * local_variable_count() + species)
                    ]
                );
            }
        }
        const int pressure_row_start = species_count_;
        for (int phase = 0; phase < phase_count(); ++phase) {
            const int row = pressure_row_start + phase;
            const int phase_offset = phase * local_variable_count();
            for (int col = 0; col < local_variable_count(); ++col) {
                out.push_back(
                    system.constraint_jacobian_row_major[
                        static_cast<std::size_t>(row) * static_cast<std::size_t>(dense_cols)
                        + static_cast<std::size_t>(phase_offset + col)
                    ]
                );
            }
        }
        for (int phase = 1; phase < phase_count(); ++phase) {
            const int active_offset = phase * local_variable_count();
            for (int species = 0; species < species_count_; ++species) {
                const int residual_row = (phase - 1) * species_count_ + species;
                for (int col = 0; col < local_variable_count(); ++col) {
                    out.push_back(
                        residuals.jacobian_row_major[
                            static_cast<std::size_t>(residual_row) * static_cast<std::size_t>(dense_cols)
                            + static_cast<std::size_t>(col)
                        ]
                    );
                }
                for (int col = 0; col < local_variable_count(); ++col) {
                    out.push_back(
                        residuals.jacobian_row_major[
                            static_cast<std::size_t>(residual_row) * static_cast<std::size_t>(dense_cols)
                            + static_cast<std::size_t>(active_offset + col)
                        ]
                    );
                }
            }
        }
        return out;
    }

    bool has_exact_hessian() const override {
        return args_.z.empty() || args_.born_model <= 1;
    }

    int hessian_nonzero_count() const override {
        return LagrangianHessianAssembler(variable_count()).nonzero_count();
    }

    NlpHessianStructure hessian_structure() const override {
        return LagrangianHessianAssembler(variable_count()).structure();
    }

    std::vector<double> hessian_values(
        const std::vector<double>& variables,
        double objective_factor,
        const std::vector<double>& constraint_multipliers
    ) const override {
        if (!has_exact_hessian()) {
            throw ValueError("Strict multiphase residual route exact Hessian requires direct or absent Born phase blocks.");
        }
        if (constraint_multipliers.size() != static_cast<std::size_t>(constraint_count())) {
            throw ValueError("Strict multiphase residual Hessian multiplier vector size does not match constraints.");
        }
        const EosPhaseSystemResult system = phase_system(variables);
        const PhaseEquilibriumResidualBlockResult residuals = residual_block(variables);
        if (!residuals.exact_hessian_available || !residuals.exact_jacobian_available) {
            throw ValueError("Strict multiphase residual route requires exact reduced fugacity derivatives.");
        }

        ObjectiveSecondOrderData objective;
        objective.variable_count = variable_count();
        objective.value = 0.0;
        objective.gradient.assign(static_cast<std::size_t>(variable_count()), 0.0);
        objective.hessian_row_major.assign(
            static_cast<std::size_t>(variable_count() * variable_count()),
            0.0
        );
        objective.backend = "zero_objective";

        ConstraintSecondOrderData constraints;
        constraints.constraint_count = constraint_count();
        constraints.variable_count = variable_count();
        constraints.values = this->constraints(variables);
        constraints.jacobian_row_major.assign(
            static_cast<std::size_t>(constraint_count() * variable_count()),
            0.0
        );
        constraints.hessian_tensor_row_major.assign(
            static_cast<std::size_t>(constraint_count() * variable_count() * variable_count()),
            0.0
        );
        constraints.has_hessian.assign(static_cast<std::size_t>(constraint_count()), false);
        constraints.backend = hessian_backend();

        if (system.constraint_hessian_tensor_row_major.size()
            != static_cast<std::size_t>(system.constraint_jacobian_rows * variable_count() * variable_count())) {
            throw ValueError("Strict multiphase residual pressure Hessian tensor shape did not match constraints.");
        }
        const int system_constraint_count = species_count_ + phase_count();
        for (int row = 0; row < system_constraint_count; ++row) {
            for (int col = 0; col < variable_count(); ++col) {
                constraints.jacobian_row_major[
                    static_cast<std::size_t>(row * variable_count() + col)
                ] = system.constraint_jacobian_row_major[
                    static_cast<std::size_t>(row * variable_count() + col)
                ];
            }
            constraints.has_hessian[static_cast<std::size_t>(row)] =
                row < static_cast<int>(system.constraint_has_hessian.size())
                && system.constraint_has_hessian[static_cast<std::size_t>(row)];
            const std::size_t offset = static_cast<std::size_t>(row * variable_count() * variable_count());
            std::copy(
                system.constraint_hessian_tensor_row_major.begin() + static_cast<std::ptrdiff_t>(offset),
                system.constraint_hessian_tensor_row_major.begin()
                    + static_cast<std::ptrdiff_t>(offset + variable_count() * variable_count()),
                constraints.hessian_tensor_row_major.begin() + static_cast<std::ptrdiff_t>(offset)
            );
        }
        const int fugacity_row_start = species_count_ + phase_count();
        for (int residual = 0; residual < phase_equilibrium_constraint_count(); ++residual) {
            const int target_row = fugacity_row_start + residual;
            constraints.has_hessian[static_cast<std::size_t>(target_row)] = true;
            for (int col = 0; col < variable_count(); ++col) {
                constraints.jacobian_row_major[
                    static_cast<std::size_t>(target_row * variable_count() + col)
                ] = residuals.jacobian_row_major[
                    static_cast<std::size_t>(residual * variable_count() + col)
                ];
            }
            const std::size_t target_offset =
                static_cast<std::size_t>(target_row * variable_count() * variable_count());
            const std::size_t source_offset =
                static_cast<std::size_t>(residual * variable_count() * variable_count());
            std::copy(
                residuals.hessian_tensor_row_major.begin() + static_cast<std::ptrdiff_t>(source_offset),
                residuals.hessian_tensor_row_major.begin()
                    + static_cast<std::ptrdiff_t>(source_offset + variable_count() * variable_count()),
                constraints.hessian_tensor_row_major.begin() + static_cast<std::ptrdiff_t>(target_offset)
            );
        }
        return LagrangianHessianAssembler(variable_count()).values(
            objective_factor,
            objective,
            constraints,
            constraint_multipliers
        );
    }

    std::string hessian_backend() const override {
        return "cppad_phase_system_plus_reduced_fugacity_residual";
    }

    NlpScaling scaling() const override {
        const double total_feed = std::accumulate(feed_amounts_.begin(), feed_amounts_.end(), 0.0);
        const double amount_scale = std::max(1.0, total_feed);
        const double pressure_scale = 1.0 / std::max(1.0, std::abs(target_pressure_));
        NlpScaling out;
        out.objective = 1.0;
        out.variables.assign(static_cast<std::size_t>(variable_count()), 1.0 / amount_scale);
        out.constraints.assign(static_cast<std::size_t>(constraint_count()), 1.0);
        for (int row = 0; row < species_count_; ++row) {
            out.constraints[static_cast<std::size_t>(row)] = 1.0 / amount_scale;
        }
        for (int phase = 0; phase < phase_count(); ++phase) {
            out.constraints[static_cast<std::size_t>(species_count_ + phase)] = pressure_scale;
        }
        return out;
    }

    std::map<std::string, std::string> diagnostics() const override {
        std::map<std::string, std::string> out =
            route_metadata_diagnostics(phase_amount_volume_route_metadata(false, false, true));
        out["residual_derivative_backend"] = "cppad_explicit_density";
        out["residual_exact_jacobian"] = "true";
        out["residual_exact_hessian"] = "true";
        return out;
    }

    int phase_count() const {
        return phase_count_;
    }

    int species_count() const {
        return species_count_;
    }

private:
    int local_variable_count() const {
        return species_count_ + 1;
    }

    int phase_equilibrium_constraint_count() const {
        return (phase_count_ - 1) * species_count_;
    }

    std::vector<std::vector<double>> phase_amounts_from_variables(const std::vector<double>& variables) const {
        return neutral_phase_amounts_from_route_variables(variables, static_cast<std::size_t>(species_count_));
    }

    std::vector<double> volumes_from_variables(const std::vector<double>& variables) const {
        return neutral_phase_volumes_from_route_variables(variables, static_cast<std::size_t>(species_count_));
    }

    EosPhaseSystemResult phase_system(const std::vector<double>& variables) const {
        return evaluate_eos_phase_system(
            args_,
            temperature_,
            target_pressure_,
            phase_amounts_from_variables(variables),
            volumes_from_variables(variables),
            feed_amounts_,
            {}
        );
    }

    PhaseEquilibriumResidualBlockResult residual_block(const std::vector<double>& variables) const {
        return evaluate_phase_equilibrium_residual_block(
            args_,
            temperature_,
            target_pressure_,
            phase_amounts_from_variables(variables),
            volumes_from_variables(variables)
        );
    }

    add_args args_;
    double temperature_ = 0.0;
    double target_pressure_ = 0.0;
    std::vector<std::vector<double>> initial_phase_amounts_;
    std::vector<double> initial_volumes_;
    std::vector<double> feed_amounts_;
    int phase_count_ = 0;
    int species_count_ = 0;
};

}  // namespace

// AlgID: neutral_deterministic_phase_candidate_screening
NeutralPhaseDiscoveryResult evaluate_neutral_tpd_phase_discovery(
    const add_args& args,
    double temperature,
    double target_pressure,
    const std::vector<double>& feed_composition,
    const std::vector<int>& phase_kinds,
    double tpd_tolerance,
    double candidate_mass_balance_tolerance,
    bool continuous_tpd_required
) {
    require_positive_finite(tpd_tolerance, "Neutral TPD tolerance");
    require_positive_finite(candidate_mass_balance_tolerance, "Neutral TPD candidate mass-balance tolerance");
    const std::vector<double> feed =
        normalized_trial_composition(feed_composition, "Neutral TPD feed composition");
    const std::vector<int> trial_phase_kinds = normalized_phase_kinds(phase_kinds, "Neutral TPD discovery");

    NeutralPhaseDiscoveryResult out;
    int valid_candidate_count = 0;
    for (int phase_kind : trial_phase_kinds) {
        try {
            const EosPhaseBlockResult reference = evaluate_unit_phase_block_at_pressure_root(
                args,
                temperature,
                target_pressure,
                feed,
                phase_kind,
                "Neutral TPD feed reference"
            );
            append_tpd_candidates_for_reference_block(
                args,
                temperature,
                target_pressure,
                reference,
                trial_phase_kinds,
                "feed_phase_kind_" + std::to_string(phase_kind),
                out.candidates,
                valid_candidate_count,
                &out,
                continuous_tpd_required
            );
        } catch (const std::exception&) {
            continue;
        }
    }
    out.tpd_candidate_count = valid_candidate_count;
    out.unique_candidate_count = static_cast<int>(out.candidates.size());
    rank_tpd_candidates(out);
    out.stability_checked = out.unique_candidate_count > 0;
    out.min_tpd = out.stability_checked ? std::numeric_limits<double>::infinity() : 0.0;
    for (const NeutralTpdCandidate& candidate : out.candidates) {
        out.min_tpd = std::min(out.min_tpd, candidate.tpd);
    }
    const bool feed_stable = out.stability_checked && out.min_tpd >= -tpd_tolerance;
    out.stability_accepted = feed_stable;
    select_generalized_phase_candidate_set(out, feed, phase_kinds, candidate_mass_balance_tolerance);
    finalize_stage9_phase_discovery(out, tpd_tolerance, continuous_tpd_required);
    if (!out.stability_checked) {
        out.phase_set_status = "stability_uncertified";
    } else if (!out.phase_set_mass_balance_feasible) {
        out.phase_set_status = "candidate_mass_balance_incomplete";
    } else if (out.held_stage_ii_replay_ready) {
        out.stability_accepted = true;
        out.candidate_completeness_accepted = true;
        out.phase_set_status = "phase_set_certified";
    } else if (feed_stable) {
        out.stability_accepted = true;
        out.candidate_completeness_accepted = true;
        out.phase_set_status = "single_phase_stable_candidate_set";
    } else {
        out.stability_accepted = false;
        out.candidate_completeness_accepted = false;
        out.phase_set_status = "candidate_bound_gap_open";
    }
    return out;
}

NeutralPhaseDiscoveryResult evaluate_electrolyte_tpd_phase_discovery(
    const add_args& args,
    double temperature,
    double target_pressure,
    const std::vector<double>& feed_composition,
    const std::vector<double>& charges,
    const std::vector<int>& phase_kinds,
    double charge_tolerance,
    double tpd_tolerance,
    double candidate_mass_balance_tolerance
) {
    require_positive_finite(charge_tolerance, "Electrolyte TPD charge tolerance");
    require_positive_finite(tpd_tolerance, "Electrolyte TPD tolerance");
    require_positive_finite(candidate_mass_balance_tolerance, "Electrolyte TPD candidate mass-balance tolerance");
    const std::vector<double> feed =
        normalized_trial_composition(feed_composition, "Electrolyte TPD feed composition");
    require_size(charges, feed.size(), "Electrolyte TPD charge");
    require_charge_neutral_composition(feed, charges, "Electrolyte TPD feed", charge_tolerance);
    if (phase_kinds.empty()) {
        throw ValueError("Electrolyte TPD discovery requires at least one phase kind.");
    }
    std::vector<int> requested_phase_kinds;
    std::vector<int> reference_phase_kinds;
    for (int phase_kind : phase_kinds) {
        if (phase_kind != 0 && phase_kind != 1) {
            throw ValueError("Electrolyte TPD discovery phase kind must be 0/liquid or 1/vapor.");
        }
        requested_phase_kinds.push_back(phase_kind);
        if (std::find(reference_phase_kinds.begin(), reference_phase_kinds.end(), phase_kind)
            == reference_phase_kinds.end()) {
            reference_phase_kinds.push_back(phase_kind);
        }
    }

    NeutralPhaseDiscoveryResult out;
    out.phase_discovery_backend = "charge_neutral_deterministic_tpd_candidate_screening";
    out.stability_certificate = "electrolyte_charge_neutral_tpd_screening";
    int valid_candidate_count = 0;
    for (int phase_kind : reference_phase_kinds) {
        try {
            const EosPhaseBlockResult reference = evaluate_unit_phase_block_at_pressure_root(
                args,
                temperature,
                target_pressure,
                feed,
                phase_kind,
                "Electrolyte TPD feed reference"
            );
            require_charge_neutral_composition(
                reference.composition,
                charges,
                "Electrolyte TPD feed reference",
                charge_tolerance
            );
            for (const std::vector<double>& trial : electrolyte_tpd_trial_compositions(
                     reference.composition,
                     charges,
                     charge_tolerance
                 )) {
                try {
                    const NeutralTpdCandidate candidate = evaluate_electrolyte_tpd_candidate(
                        args,
                        temperature,
                        target_pressure,
                        reference,
                        trial,
                        charges,
                        phase_kind,
                        "electrolyte_charge_neutral_phase_kind_" + std::to_string(phase_kind),
                        charge_tolerance
                    );
                    ++valid_candidate_count;
                    append_unique_tpd_candidate(out.candidates, candidate);
                } catch (const std::exception&) {
                    continue;
                }
            }
        } catch (const std::exception&) {
            continue;
        }
    }
    out.tpd_candidate_count = valid_candidate_count;
    out.deterministic_candidate_count = valid_candidate_count;
    out.unique_candidate_count = static_cast<int>(out.candidates.size());
    rank_tpd_candidates(out);
    out.stability_checked = out.unique_candidate_count > 0;
    out.min_tpd = out.stability_checked ? std::numeric_limits<double>::infinity() : 0.0;
    for (const NeutralTpdCandidate& candidate : out.candidates) {
        out.min_tpd = std::min(out.min_tpd, candidate.tpd);
    }
    out.stability_accepted = out.stability_checked && out.min_tpd >= -tpd_tolerance;
    select_generalized_phase_candidate_set(out, feed, requested_phase_kinds, candidate_mass_balance_tolerance);
    finalize_stage9_phase_discovery(out, tpd_tolerance, false);
    out.phase_discovery_backend = "charge_neutral_deterministic_tpd_candidate_screening";
    out.stability_certificate = "electrolyte_charge_neutral_tpd_screening";
    out.continuous_tpd_status = "pending_held2_dual_phase_discovery";
    out.held_stage_i_status = "pending_held2_dual_phase_discovery";
    out.held_stage_ii_status = "pending_held2_dual_phase_discovery";
    out.held_stage_ii_candidate_bound_audit_status = "pending_held2_dual_phase_discovery";
    out.held_stage_ii_dual_loop_status = "pending_held2_dual_phase_discovery";
    out.held_stage_ii_replay_ready = false;
    out.held_stage_iii_status = "pending_electrolyte_stage_iii_refinement";
    if (!out.stability_checked) {
        out.phase_set_status = "stability_uncertified";
    } else if (!out.phase_set_mass_balance_feasible) {
        out.phase_set_status = "candidate_mass_balance_incomplete";
    } else if (out.stability_accepted) {
        out.candidate_completeness_accepted = true;
        out.phase_set_status = "charge_neutral_tpd_screening_complete";
    } else {
        out.candidate_completeness_accepted = false;
        out.phase_set_status = "charge_neutral_tpd_negative_candidate";
    }
    return out;
}

ElectrolyteHeld2PhaseDiscoveryResult evaluate_electrolyte_held2_phase_discovery(
    const add_args& args,
    double temperature,
    double target_pressure,
    const std::vector<double>& feed_composition,
    const std::vector<double>& charges,
    const std::vector<std::string>& species_labels,
    const std::vector<int>& phase_kinds,
    double charge_tolerance,
    double tpd_tolerance,
    double candidate_mass_balance_tolerance
) {
    require_positive_finite(charge_tolerance, "Electrolyte HELD2 charge tolerance");
    require_positive_finite(tpd_tolerance, "Electrolyte HELD2 TPD tolerance");
    require_positive_finite(candidate_mass_balance_tolerance, "Electrolyte HELD2 candidate mass-balance tolerance");
    const std::vector<double> feed =
        normalized_trial_composition(feed_composition, "Electrolyte HELD2 feed composition");
    require_size(charges, feed.size(), "Electrolyte HELD2 charge");
    if (species_labels.size() != feed.size()) {
        throw ValueError("Electrolyte HELD2 species label size did not match feed composition size.");
    }
    require_charge_neutral_composition(feed, charges, "Electrolyte HELD2 feed", charge_tolerance);

    ElectrolyteHeld2PhaseDiscoveryResult out =
        build_electrolyte_held2_diagnostic(feed, charges, species_labels, 1.0e-10);
    out.tpd_discovery = evaluate_electrolyte_tpd_phase_discovery(
        args,
        temperature,
        target_pressure,
        feed,
        charges,
        phase_kinds,
        charge_tolerance,
        tpd_tolerance,
        candidate_mass_balance_tolerance
    );
    out.reduced_start_count = out.tpd_discovery.tpd_candidate_count;
    out.converged_start_count = out.tpd_discovery.unique_candidate_count;
    out.selected_candidate_count = out.tpd_discovery.selected_candidate_count;
    out.min_tpd = out.tpd_discovery.min_tpd;
    out.duplicate_candidate_distance = duplicate_candidate_distance(out.tpd_discovery.candidates);

    std::vector<std::vector<double>> candidate_compositions = out.tpd_discovery.selected_phase_compositions;
    if (candidate_compositions.empty()) {
        for (const NeutralTpdCandidate& candidate : out.tpd_discovery.candidates) {
            candidate_compositions.push_back(candidate.composition);
        }
    }
    out.lifted_candidate_compositions = candidate_compositions;
    out.stage_iii_phase_compositions = out.tpd_discovery.selected_phase_compositions;
    out.stage_iii_phase_fractions = out.tpd_discovery.selected_phase_fractions;
    out.stage_iii_phase_kinds = out.tpd_discovery.selected_phase_kinds;
    for (const NeutralTpdCandidate& candidate : out.tpd_discovery.candidates) {
        if (candidate.selected) {
            out.stage_iii_tpd_values.push_back(candidate.tpd);
        }
    }

    out.max_charge_residual = max_charge_residual(candidate_compositions, charges);
    out.component_nonnegativity_margin = min_component_value(candidate_compositions);
    out.composition_sum_residual = max_composition_sum_residual(candidate_compositions);
    out.candidate_to_feed_distance = max_candidate_feed_distance(feed, candidate_compositions);
    out.round_trip_residual = 0.0;
    for (const std::vector<double>& candidate : candidate_compositions) {
        std::vector<double> reduced = reduced_coordinates_from_candidate(
            feed,
            candidate,
            out.charged_species_indices,
            out.counterion_pair_matrix,
            out.rank_tolerance
        );
        out.reduced_candidate_coordinates.push_back(reduced);
        const std::vector<double> lifted = charged_lift_from_reduced_coordinates(
            feed,
            out.charged_species_indices,
            out.counterion_pair_matrix,
            reduced
        );
        out.round_trip_residual = std::max(
            out.round_trip_residual,
            max_lift_round_trip_residual(candidate, lifted, out.charged_species_indices)
        );
    }

    if (!candidate_compositions.empty()) {
        const std::vector<int> reference_phase_kinds = phase_kinds.empty() ? std::vector<int>{0} : phase_kinds;
        const EosPhaseBlockResult reference = evaluate_unit_phase_block_at_pressure_root(
            args,
            temperature,
            target_pressure,
            feed,
            reference_phase_kinds.front(),
            "Electrolyte HELD2 mean-ionic reference"
        );
        const EosPhaseBlockResult trial = evaluate_unit_phase_block_at_pressure_root(
            args,
            temperature,
            target_pressure,
            candidate_compositions.front(),
            reference_phase_kinds.front(),
            "Electrolyte HELD2 mean-ionic candidate"
        );
        out.mean_ionic_residual_values = pair_residuals_from_reference_and_trial(
            out.counterion_pair_matrix,
            out.charged_species_indices,
            reference,
            trial
        );
        out.mean_ionic_max_abs_residual = 0.0;
        for (double value : out.mean_ionic_residual_values) {
            out.mean_ionic_max_abs_residual = std::max(out.mean_ionic_max_abs_residual, std::abs(value));
        }
    }
    out.phase_discovery_status = "complete";
    out.stage_iii_refinement_status = "pending";
    out.postsolve_certification_status = "pending";
    out.public_route_admission_status = "separate_public_admission_gate";
    out.stage_iii_handoff_status = "pending_stage_iii_refinement";
    return out;
}

ElectrolyteStageIIIRefinementResult evaluate_electrolyte_stage_iii_refinement(
    const add_args& args,
    double temperature,
    double target_pressure,
    const std::vector<double>& feed_composition,
    const std::vector<double>& charges,
    const std::vector<std::string>& species_labels,
    const std::vector<int>& phase_kinds,
    double charge_tolerance,
    double tpd_tolerance,
    double candidate_mass_balance_tolerance,
    double residual_tolerance,
    double phase_distance_tolerance,
    double active_bound_tolerance
) {
    require_positive_finite(residual_tolerance, "Electrolyte Stage III residual tolerance");
    require_positive_finite(phase_distance_tolerance, "Electrolyte Stage III phase-distance tolerance");
    require_positive_finite(active_bound_tolerance, "Electrolyte Stage III active-bound tolerance");
    const std::vector<double> feed =
        normalized_trial_composition(feed_composition, "Electrolyte Stage III feed composition");
    require_size(charges, feed.size(), "Electrolyte Stage III charge");
    require_charge_neutral_composition(feed, charges, "Electrolyte Stage III feed", charge_tolerance);
    if (phase_kinds.size() < 2) {
        throw ValueError("Electrolyte Stage III refinement requires at least two requested phase kinds.");
    }

    ElectrolyteStageIIIRefinementResult out;
    out.residual_tolerance = residual_tolerance;
    out.phase_distance_tolerance = phase_distance_tolerance;
    out.active_bound_tolerance = active_bound_tolerance;
    out.held2_discovery = evaluate_electrolyte_held2_phase_discovery(
        args,
        temperature,
        target_pressure,
        feed,
        charges,
        species_labels,
        phase_kinds,
        charge_tolerance,
        tpd_tolerance,
        candidate_mass_balance_tolerance
    );
    out.selected_candidate_count = out.held2_discovery.selected_candidate_count;
    out.selected_phase_kinds = out.held2_discovery.stage_iii_phase_kinds;
    out.selected_phase_fractions = out.held2_discovery.stage_iii_phase_fractions;
    out.selected_phase_compositions = out.held2_discovery.stage_iii_phase_compositions;
    for (std::size_t phase = 0; phase < phase_kinds.size(); ++phase) {
        out.selected_phase_labels.push_back("phase_" + std::to_string(phase));
    }

    const std::size_t phase_count = phase_kinds.size();
    const std::size_t pair_count = out.held2_discovery.pair_labels.size();
    for (std::size_t phase = 0; phase < phase_count; ++phase) {
        for (const std::string& pair_label : out.held2_discovery.pair_labels) {
            out.variable_labels.push_back("phase_" + std::to_string(phase) + ":" + pair_label);
            out.variable_lower_bounds.push_back(-1.0);
            out.variable_upper_bounds.push_back(1.0);
            out.variable_scaling.push_back(1.0);
        }
    }
    for (std::size_t phase = 0; phase + 1 < phase_count; ++phase) {
        out.variable_labels.push_back("phase_" + std::to_string(phase) + "_fraction");
        out.variable_lower_bounds.push_back(1.0e-12);
        out.variable_upper_bounds.push_back(1.0 - 1.0e-12);
        out.variable_scaling.push_back(1.0);
    }
    for (const std::string& pair_label : out.held2_discovery.pair_labels) {
        out.equation_labels.push_back("pair_mean_ionic_equality:" + pair_label);
    }
    out.equation_labels.push_back("phase_fraction_closure");
    for (std::size_t phase = 0; phase < phase_count; ++phase) {
        out.equation_labels.push_back("phase_charge_balance:phase_" + std::to_string(phase));
    }
    out.residual_scaling.assign(out.equation_labels.size(), 1.0);

    const std::vector<double> feed_amounts = feed;
    const NeutralTwoPhaseEosInitialPoint initial = build_multiphase_eos_initial_point_from_candidate_set(
        args,
        feed_amounts,
        out.held2_discovery.tpd_discovery,
        temperature,
        target_pressure,
        "electrolyte_stage_iii_reduced_variable_refinement",
        phase_kinds
    );
    IpoptSolveOptions base_options;
    base_options.max_iterations = 260;
    base_options.print_level = 0;
    const double solve_tolerance = std::min(1.0e-8, 0.01 * residual_tolerance);
    base_options.tolerance = solve_tolerance;
    base_options.acceptable_tolerance = std::max(1.0e-10, 10.0 * solve_tolerance);
    base_options.constraint_violation_tolerance = solve_tolerance;
    base_options.dual_infeasibility_tolerance = solve_tolerance;
    base_options.complementarity_tolerance = solve_tolerance;
    base_options.iteration_history_limit = 50;
    base_options.linear_solver = "auto";
    base_options.hessian_mode = "limited-memory";
    IpoptSolveOptions route_options = ipopt_solve_options_for_profile(base_options, "diagnostic");
    route_options.initial_variables = neutral_two_phase_variables_from_initial(initial);
    route_options.initial_bound_lower_multipliers.clear();
    route_options.initial_bound_upper_multipliers.clear();
    route_options.initial_constraint_multipliers.clear();

    out.route_result = solve_neutral_two_phase_eos_route(
        args,
        temperature,
        target_pressure,
        initial.phase_amounts,
        initial.volumes,
        feed_amounts,
        route_options,
        residual_tolerance,
        residual_tolerance,
        residual_tolerance,
        phase_distance_tolerance,
        phase_distance_tolerance,
        charges,
        "electrolyte_stage_iii_reduced_variable_refinement",
        charge_tolerance
    );
    out.route_result.initial_point_strategy = "electrolyte_held2_candidate_set_replay";
    out.route_result.seed_name = out.seed_name;

    std::vector<std::vector<double>> phase_compositions = out.route_result.postsolve.phase_compositions;
    if (phase_compositions.empty()) {
        phase_compositions = out.selected_phase_compositions;
    }
    if (!phase_compositions.empty()) {
        out.selected_phase_compositions = phase_compositions;
    }
    if (!out.route_result.postsolve.phase_amount_totals.empty()) {
        const double total_amount = std::accumulate(
            out.route_result.postsolve.phase_amount_totals.begin(),
            out.route_result.postsolve.phase_amount_totals.end(),
            0.0
        );
        if (total_amount > 0.0) {
            out.selected_phase_fractions.clear();
            for (double amount : out.route_result.postsolve.phase_amount_totals) {
                out.selected_phase_fractions.push_back(amount / total_amount);
            }
        }
    }
    out.phase_distance = pairwise_phase_distance_inf_norm(out.selected_phase_compositions);

    if (phase_compositions.size() >= 2 && pair_count > 0) {
        const EosPhaseBlockResult reference = evaluate_unit_phase_block_at_pressure_root(
            args,
            temperature,
            target_pressure,
            phase_compositions.front(),
            phase_kinds.front(),
            "Electrolyte Stage III phase 0"
        );
        const EosPhaseBlockResult trial = evaluate_unit_phase_block_at_pressure_root(
            args,
            temperature,
            target_pressure,
            phase_compositions[1],
            phase_kinds[1],
            "Electrolyte Stage III phase 1"
        );
        const std::vector<double> pair_residuals = pair_residuals_from_reference_and_trial(
            out.held2_discovery.counterion_pair_matrix,
            out.held2_discovery.charged_species_indices,
            reference,
            trial
        );
        out.residual_values.insert(out.residual_values.end(), pair_residuals.begin(), pair_residuals.end());
    } else {
        out.residual_values.insert(out.residual_values.end(), pair_count, std::numeric_limits<double>::infinity());
    }
    double fraction_sum = 0.0;
    for (double fraction : out.selected_phase_fractions) {
        fraction_sum += fraction;
    }
    out.residual_values.push_back(fraction_sum - 1.0);
    for (const std::vector<double>& composition : out.selected_phase_compositions) {
        double phase_charge = 0.0;
        for (std::size_t species = 0; species < composition.size(); ++species) {
            phase_charge += composition[species] * charges[species];
        }
        out.residual_values.push_back(phase_charge);
    }
    out.residual_inf_norm = 0.0;
    for (double residual : out.residual_values) {
        out.residual_inf_norm = std::max(out.residual_inf_norm, std::abs(residual));
    }
    out.active_bound_violation = 0.0;
    for (double value : out.route_result.variables) {
        if (std::isfinite(value)) {
            out.active_bound_violation = std::max(out.active_bound_violation, std::max(0.0, 1.0e-14 - value));
        }
    }
    const int variable_count = static_cast<int>(out.variable_labels.size());
    const int residual_count = static_cast<int>(out.equation_labels.size());
    out.jacobian_nonzero_count = variable_count * residual_count;
    out.hessian_nonzero_count = variable_count * (variable_count + 1) / 2;
    out.exact_reduced_jacobian_available =
        out.route_result.exact_jacobian_required && out.route_result.jacobian_approximation == "exact";
    out.exact_reduced_hessian_available = !out.held2_discovery.counterion_pair_matrix.empty();

    const bool solver_success =
        out.route_result.solver_accepted
        && out.route_result.solver_status == "success"
        && out.route_result.application_status == "solve_succeeded";
    const bool finite_compositions = !out.selected_phase_compositions.empty()
        && std::all_of(
            out.selected_phase_compositions.begin(),
            out.selected_phase_compositions.end(),
            [](const std::vector<double>& composition) {
                return std::all_of(composition.begin(), composition.end(), [](double value) {
                    return std::isfinite(value) && value >= 0.0;
                });
            }
        );
    const bool residuals_pass =
        out.residual_inf_norm <= residual_tolerance && out.residual_values.size() == out.equation_labels.size();
    const bool phase_distance_pass = out.phase_distance > phase_distance_tolerance;
    const bool bounds_pass = out.active_bound_violation <= active_bound_tolerance;
    const bool derivative_pass = out.exact_reduced_jacobian_available && out.exact_reduced_hessian_available;
    out.status = (
        solver_success
        && finite_compositions
        && residuals_pass
        && phase_distance_pass
        && bounds_pass
        && derivative_pass
    ) ? "complete" : "incomplete";
    out.stage_iii_refinement_status = out.status == "complete" ? "complete" : "incomplete";
    return out;
}

ElectrolytePostsolveCertificationResult evaluate_electrolyte_postsolve_certification(
    const add_args& args,
    double temperature,
    double target_pressure,
    const std::vector<double>& feed_composition,
    const std::vector<double>& charges,
    const std::vector<std::string>& species_labels,
    const std::vector<int>& phase_kinds,
    double charge_tolerance,
    double tpd_tolerance,
    double candidate_mass_balance_tolerance,
    double residual_tolerance,
    double phase_distance_tolerance,
    double active_bound_tolerance
) {
    const std::vector<double> feed =
        normalized_trial_composition(feed_composition, "Electrolyte postsolve feed composition");
    require_size(charges, feed.size(), "Electrolyte postsolve charge");

    ElectrolytePostsolveCertificationResult out;
    out.feed_composition = feed;
    out.charge_vector = charges;
    out.feed_reconstruction_tolerance = residual_tolerance;
    out.phase_charge_tolerance = charge_tolerance;
    out.total_charge_tolerance = charge_tolerance;
    out.neutral_transfer_tolerance = residual_tolerance;
    out.mean_ionic_transfer_tolerance = residual_tolerance;
    out.pressure_tolerance = residual_tolerance;
    out.phase_distance_tolerance = phase_distance_tolerance;
    out.stage_iii_refinement = evaluate_electrolyte_stage_iii_refinement(
        args,
        temperature,
        target_pressure,
        feed,
        charges,
        species_labels,
        phase_kinds,
        charge_tolerance,
        tpd_tolerance,
        candidate_mass_balance_tolerance,
        residual_tolerance,
        phase_distance_tolerance,
        active_bound_tolerance
    );
    out.phase_discovery_status = out.stage_iii_refinement.phase_discovery_status;
    out.stage_iii_refinement_status = out.stage_iii_refinement.stage_iii_refinement_status;

    out.component_labels.reserve(feed.size());
    for (std::size_t species = 0; species < feed.size(); ++species) {
        if (species < species_labels.size() && !species_labels[species].empty()) {
            out.component_labels.push_back(species_labels[species]);
        } else {
            out.component_labels.push_back("species_" + std::to_string(species));
        }
    }

    const NeutralTwoPhaseEosPostsolve& postsolve = out.stage_iii_refinement.route_result.postsolve;
    out.phase_compositions = postsolve.phase_compositions.empty()
        ? out.stage_iii_refinement.selected_phase_compositions
        : postsolve.phase_compositions;
    out.phase_amount_totals = postsolve.phase_amount_totals;
    if (out.phase_amount_totals.empty()) {
        out.phase_amount_totals = out.stage_iii_refinement.selected_phase_fractions;
    }
    out.phase_count = static_cast<int>(out.phase_compositions.size());
    const double amount_total = std::accumulate(out.phase_amount_totals.begin(), out.phase_amount_totals.end(), 0.0);
    out.phase_fractions.reserve(out.phase_amount_totals.size());
    if (amount_total > 0.0) {
        for (double amount : out.phase_amount_totals) {
            out.phase_fractions.push_back(amount / amount_total);
        }
    } else {
        out.phase_fractions = out.stage_iii_refinement.selected_phase_fractions;
    }

    out.reconstructed_feed_composition.assign(feed.size(), 0.0);
    const std::size_t phase_count = out.phase_compositions.size();
    for (std::size_t phase = 0; phase < phase_count; ++phase) {
        require_size(out.phase_compositions[phase], feed.size(), "Electrolyte postsolve phase composition");
        const double weight = phase < out.phase_fractions.size() ? out.phase_fractions[phase] : 0.0;
        for (std::size_t species = 0; species < feed.size(); ++species) {
            out.reconstructed_feed_composition[species] += weight * out.phase_compositions[phase][species];
        }
    }
    out.feed_reconstruction_residuals.reserve(feed.size());
    out.feed_reconstruction_inf_norm = 0.0;
    for (std::size_t species = 0; species < feed.size(); ++species) {
        const double residual = out.reconstructed_feed_composition[species] - feed[species];
        out.feed_reconstruction_residuals.push_back(residual);
        out.feed_reconstruction_inf_norm = std::max(out.feed_reconstruction_inf_norm, std::abs(residual));
    }

    out.component_nonnegativity_margin = std::numeric_limits<double>::infinity();
    out.minimum_component_mole_fraction = std::numeric_limits<double>::infinity();
    out.minimum_phase_amount = std::numeric_limits<double>::infinity();
    out.phase_distance = pairwise_phase_distance_inf_norm(out.phase_compositions);
    out.composition_sum_residuals.reserve(out.phase_compositions.size());
    for (const std::vector<double>& composition : out.phase_compositions) {
        double composition_sum = 0.0;
        for (double value : composition) {
            out.component_nonnegativity_margin = std::min(out.component_nonnegativity_margin, value);
            out.minimum_component_mole_fraction = std::min(out.minimum_component_mole_fraction, value);
            composition_sum += value;
        }
        out.composition_sum_residuals.push_back(std::abs(composition_sum - 1.0));
    }
    for (double amount : out.phase_amount_totals) {
        out.minimum_phase_amount = std::min(out.minimum_phase_amount, amount);
    }
    if (!std::isfinite(out.component_nonnegativity_margin)) {
        out.component_nonnegativity_margin = -std::numeric_limits<double>::infinity();
    }
    if (!std::isfinite(out.minimum_component_mole_fraction)) {
        out.minimum_component_mole_fraction = -std::numeric_limits<double>::infinity();
    }
    if (!std::isfinite(out.minimum_phase_amount)) {
        out.minimum_phase_amount = -std::numeric_limits<double>::infinity();
    }

    double fraction_sum = 0.0;
    for (double fraction : out.phase_fractions) {
        fraction_sum += fraction;
    }
    out.phase_fraction_sum_residual = std::abs(fraction_sum - 1.0);

    out.phase_charge_residuals.reserve(out.phase_compositions.size());
    out.max_phase_charge_residual = 0.0;
    for (const std::vector<double>& composition : out.phase_compositions) {
        double phase_charge = 0.0;
        for (std::size_t species = 0; species < feed.size(); ++species) {
            phase_charge += composition[species] * charges[species];
        }
        out.phase_charge_residuals.push_back(phase_charge);
        out.max_phase_charge_residual = std::max(out.max_phase_charge_residual, std::abs(phase_charge));
    }
    out.total_charge_residual = 0.0;
    for (std::size_t species = 0; species < feed.size(); ++species) {
        out.total_charge_residual += out.reconstructed_feed_composition[species] * charges[species];
    }
    out.total_charge_residual = std::abs(out.total_charge_residual);

    if (out.phase_compositions.size() >= 2 && postsolve.phase_ln_fugacity_coefficients.size() >= 2) {
        const std::vector<double>& first_lnphi = postsolve.phase_ln_fugacity_coefficients.front();
        const std::vector<double>& second_lnphi = postsolve.phase_ln_fugacity_coefficients[1];
        require_size(first_lnphi, feed.size(), "Electrolyte postsolve first phase ln fugacity");
        require_size(second_lnphi, feed.size(), "Electrolyte postsolve second phase ln fugacity");
        for (std::size_t species = 0; species < feed.size(); ++species) {
            if (std::abs(charges[species]) > charge_tolerance) {
                continue;
            }
            const double first_value =
                std::log(std::max(out.phase_compositions[0][species], 1.0e-300)) + first_lnphi[species];
            const double second_value =
                std::log(std::max(out.phase_compositions[1][species], 1.0e-300)) + second_lnphi[species];
            const double residual = first_value - second_value;
            out.neutral_species_labels.push_back(out.component_labels[species]);
            out.neutral_transfer_residuals.push_back(residual);
            out.neutral_transfer_max_abs_residual =
                std::max(out.neutral_transfer_max_abs_residual, std::abs(residual));
        }
    }

    for (std::size_t equation = 0; equation < out.stage_iii_refinement.equation_labels.size(); ++equation) {
        const std::string& label = out.stage_iii_refinement.equation_labels[equation];
        const std::string prefix = "pair_mean_ionic_equality:";
        if (label.rfind(prefix, 0) != 0 || equation >= out.stage_iii_refinement.residual_values.size()) {
            continue;
        }
        out.mean_ionic_pair_labels.push_back(label.substr(prefix.size()));
        const double residual = out.stage_iii_refinement.residual_values[equation];
        out.mean_ionic_transfer_residuals.push_back(residual);
        out.mean_ionic_transfer_max_abs_residual =
            std::max(out.mean_ionic_transfer_max_abs_residual, std::abs(residual));
    }

    out.pressure_consistency_norm = postsolve.pressure_consistency_norm;
    out.explicit_ion_reconstruction_accepted =
        out.feed_reconstruction_inf_norm <= out.feed_reconstruction_tolerance
        && out.component_nonnegativity_margin >= 0.0;
    out.charge_balance_accepted =
        !out.phase_charge_residuals.empty()
        && out.max_phase_charge_residual <= out.phase_charge_tolerance
        && out.total_charge_residual <= out.total_charge_tolerance;
    out.transfer_residuals_accepted =
        !out.neutral_species_labels.empty()
        && !out.mean_ionic_pair_labels.empty()
        && out.neutral_transfer_max_abs_residual <= out.neutral_transfer_tolerance
        && out.mean_ionic_transfer_max_abs_residual <= out.mean_ionic_transfer_tolerance;
    out.pressure_consistency_accepted = out.pressure_consistency_norm <= out.pressure_tolerance;
    const bool composition_sums_accepted = std::all_of(
        out.composition_sum_residuals.begin(),
        out.composition_sum_residuals.end(),
        [&out](double residual) { return residual <= out.composition_sum_tolerance; }
    );
    out.phase_set_accepted =
        out.phase_count >= 2
        && !out.phase_amount_totals.empty()
        && out.phase_fraction_sum_residual <= out.phase_fraction_sum_tolerance
        && composition_sums_accepted;
    out.domain_margins_accepted =
        out.minimum_component_mole_fraction >= 0.0
        && out.minimum_phase_amount > 0.0
        && out.phase_distance > out.phase_distance_tolerance;

    const bool stage_iii_complete = out.stage_iii_refinement.status == "complete";
    const bool route_postsolve_accepted = out.stage_iii_refinement.route_result.postsolve.accepted;
    const bool accepted =
        stage_iii_complete
        && route_postsolve_accepted
        && out.explicit_ion_reconstruction_accepted
        && out.charge_balance_accepted
        && out.transfer_residuals_accepted
        && out.pressure_consistency_accepted
        && out.phase_set_accepted
        && out.domain_margins_accepted;
    out.status = accepted ? "complete" : "incomplete";
    out.postsolve_certification_status = accepted ? "complete" : "incomplete";
    return out;
}

NeutralTwoPhaseEosNlpContract evaluate_neutral_two_phase_eos_nlp_contract(
    const add_args& args,
    double temperature,
    double target_pressure,
    const std::vector<std::vector<double>>& phase_amounts,
    const std::vector<double>& volumes,
    const std::vector<double>& feed_amounts
) {
    NeutralTwoPhaseEosProblem problem(args, temperature, target_pressure, phase_amounts, volumes, feed_amounts);
    return make_neutral_two_phase_nlp_contract_snapshot(
        problem,
        problem.phase_count(),
        problem.species_count(),
        NlpContractSnapshotDetail::FullDerivativeEvidence
    );
}

NeutralTwoPhaseEosNlpContract evaluate_neutral_multiphase_eos_nlp_contract(
    const add_args& args,
    double temperature,
    double target_pressure,
    const std::vector<std::vector<double>>& phase_amounts,
    const std::vector<double>& volumes,
    const std::vector<double>& feed_amounts
) {
    NeutralTwoPhaseEosProblem problem(
        args,
        temperature,
        target_pressure,
        phase_amounts,
        volumes,
        feed_amounts,
        std::vector<double>{},
        "neutral_multiphase_eos"
    );
    return make_neutral_two_phase_nlp_contract_snapshot(
        problem,
        problem.phase_count(),
        problem.species_count(),
        NlpContractSnapshotDetail::FullDerivativeEvidence
    );
}

std::unique_ptr<NlpProblem> make_neutral_two_phase_eos_problem(
    const add_args& args,
    double temperature,
    double target_pressure,
    const std::vector<std::vector<double>>& phase_amounts,
    const std::vector<double>& volumes,
    const std::vector<double>& feed_amounts,
    const std::string& problem_name,
    double minimum_phase_distance
) {
    return std::make_unique<NeutralTwoPhaseEosProblem>(
        args,
        temperature,
        target_pressure,
        phase_amounts,
        volumes,
        feed_amounts,
        std::vector<double>{},
        problem_name,
        minimum_phase_distance
    );
}

std::unique_ptr<NlpProblem> make_neutral_two_phase_eos_problem_from_feed(
    const add_args& args,
    double temperature,
    double target_pressure,
    const std::vector<double>& feed_composition,
    const std::vector<int>& phase_kinds,
    const std::string& problem_name,
    double minimum_phase_distance
) {
    const std::vector<double> feed_amounts =
        normalized_positive_values(feed_composition, problem_name + " feed composition");
    const NeutralTwoPhaseEosInitialPoint initial = build_neutral_two_phase_eos_initial_point(
        args,
        feed_amounts,
        temperature,
        target_pressure,
        problem_name,
        phase_kinds
    );
    return make_neutral_two_phase_eos_problem(
        args,
        temperature,
        target_pressure,
        initial.phase_amounts,
        initial.volumes,
        feed_amounts,
        problem_name,
        minimum_phase_distance
    );
}

IpoptSolveResult solve_neutral_two_phase_eos_ipopt(
    const add_args& args,
    double temperature,
    double target_pressure,
    const std::vector<std::vector<double>>& phase_amounts,
    const std::vector<double>& volumes,
    const std::vector<double>& feed_amounts,
    const IpoptSolveOptions& options,
    const std::vector<double>& charges,
    const std::string& problem_name,
    double minimum_phase_distance
) {
    NeutralTwoPhaseEosProblem problem(
        args,
        temperature,
        target_pressure,
        phase_amounts,
        volumes,
        feed_amounts,
        charges,
        problem_name,
        minimum_phase_distance
    );
    return solve_ipopt_nlp(problem, options);
}

// AlgID: postsolve_tpd_certification
NeutralTwoPhaseEosPostsolve evaluate_neutral_two_phase_eos_postsolve(
    const add_args& args,
    double temperature,
    double target_pressure,
    const std::vector<std::vector<double>>& phase_amounts,
    const std::vector<double>& volumes,
    const std::vector<double>& feed_amounts,
    double material_tolerance,
    double pressure_tolerance,
    double chemical_potential_tolerance,
    double phase_distance_tolerance,
    const std::vector<double>& charges,
    bool phase_distance_constraint,
    bool stability_certification_required,
    std::vector<int> phase_kinds,
    bool continuous_tpd_required,
    bool ln_fugacity_consistency_required
) {
    require_positive_finite(material_tolerance, "Neutral EOS postsolve material tolerance");
    require_positive_finite(pressure_tolerance, "Neutral EOS postsolve pressure tolerance");
    require_positive_finite(
        chemical_potential_tolerance,
        "Neutral EOS postsolve chemical-potential tolerance"
    );
    require_positive_finite(phase_distance_tolerance, "Neutral EOS postsolve phase-distance tolerance");

    const EosPhaseSystemResult system = evaluate_eos_phase_system(
        args,
        temperature,
        target_pressure,
        phase_amounts,
        volumes,
        feed_amounts,
        charges
    );
    if (system.phase_count < 2) {
        throw ValueError("Neutral EOS postsolve requires at least two phases.");
    }
    if (phase_distance_constraint && system.phase_count != 2) {
        throw ValueError("Neutral EOS postsolve phase-distance constraint currently requires exactly two phases.");
    }

    NeutralTwoPhaseEosPostsolve out;
    out.derivative_backend = system.derivative_backend;
    apply_route_metadata(out, phase_amount_volume_route_metadata(!charges.empty(), phase_distance_constraint));
    out.phase_count = system.phase_count;
    out.species_count = system.species_count;
    out.objective = system.objective;
    out.constraints = system.constraints;
    out.phase_volumes = volumes;
    out.phase_amount_totals.reserve(system.phase_blocks.size());
    out.phase_densities.reserve(system.phase_blocks.size());
    out.phase_compositions.reserve(system.phase_blocks.size());
    out.phase_ln_fugacity_coefficients.reserve(system.phase_blocks.size());
    const std::size_t species_count = static_cast<std::size_t>(system.species_count);
    for (const EosPhaseBlockResult& block : system.phase_blocks) {
        out.phase_amount_totals.push_back(block.total_amount);
        out.phase_densities.push_back(block.density);
        out.phase_compositions.push_back(block.composition);
        out.phase_ln_fugacity_coefficients.push_back(
            ln_fugacity_coefficients_for_postsolve(args, block, species_count)
        );
    }

    out.material_balance_norm = vector_infinity_norm(system.constraints, 0, species_count);
    out.pressure_consistency_norm = vector_infinity_norm(
        system.constraints,
        species_count,
        species_count + static_cast<std::size_t>(system.phase_count)
    );
    out.chemical_potential_consistency_norm =
        pairwise_chemical_potential_inf_norm(system.phase_blocks, species_count, charges);
    out.ln_fugacity_consistency_norm =
        pairwise_ln_fugacity_inf_norm(args, system.phase_blocks, species_count, charges);
    out.phase_distance = pairwise_phase_distance_inf_norm(out.phase_compositions);
    out.stability_checked = false;
    out.stability_accepted = !stability_certification_required;
    out.candidate_completeness_accepted = !stability_certification_required;
    out.phase_set_mass_balance_feasible = !stability_certification_required;
    out.phase_discovery_backend = stability_certification_required
        ? "deterministic_tpd_candidate_screening"
        : "deterministic_seed_sweep";
    out.stability_certificate = stability_certification_required
        ? "tpd_postsolve"
        : "postsolve_local_only";
    out.phase_set_status = stability_certification_required ? "not_checked" : "not_required";

    const double effective_chemical_tolerance = charges.empty()
        ? chemical_potential_tolerance
        : std::max(chemical_potential_tolerance, 2.0 * std::sqrt(chemical_potential_tolerance));
    const bool ln_fugacity_consistency_accepted =
        !ln_fugacity_consistency_required
        || out.ln_fugacity_consistency_norm <= effective_chemical_tolerance;
    out.accepted = out.material_balance_norm <= material_tolerance
        && out.pressure_consistency_norm <= pressure_tolerance
        && out.chemical_potential_consistency_norm <= effective_chemical_tolerance
        && ln_fugacity_consistency_accepted
        && (!phase_distance_constraint || out.phase_distance >= phase_distance_tolerance);
    if (out.accepted) {
        out.rejection_reason = "accepted";
    } else if (out.material_balance_norm > material_tolerance) {
        out.rejection_reason = "material_balance";
    } else if (out.pressure_consistency_norm > pressure_tolerance) {
        out.rejection_reason = "pressure_consistency";
    } else if (out.chemical_potential_consistency_norm > effective_chemical_tolerance) {
        out.rejection_reason = "chemical_potential_consistency";
    } else if (ln_fugacity_consistency_required && out.ln_fugacity_consistency_norm > effective_chemical_tolerance) {
        out.rejection_reason = "ln_fugacity_consistency";
    } else if (phase_distance_constraint) {
        out.rejection_reason = "phase_distance";
    } else {
        out.rejection_reason = "phase_set_not_certified";
    }
    if (out.accepted && stability_certification_required) {
        if (!charges.empty()) {
            out.accepted = false;
            out.rejection_reason = "stability_tpd";
            out.phase_set_status = "neutral_tpd_not_valid_for_charged_system";
            return out;
        }
        if (phase_kinds.empty()) {
            phase_kinds.assign(static_cast<std::size_t>(system.phase_count), 0);
        }
        if (phase_kinds.size() != static_cast<std::size_t>(system.phase_count)) {
            throw ValueError("Neutral EOS postsolve phase kind size does not match the accepted phase set.");
        }
        const double tpd_tolerance = std::max(1.0e-6, 100.0 * chemical_potential_tolerance);
        const double candidate_mass_balance_tolerance = std::max(1.0e-8, 10.0 * material_tolerance);
        const NeutralPhaseDiscoveryResult discovery = certify_neutral_phase_set(
            args,
            temperature,
            target_pressure,
            system,
            feed_amounts,
            phase_kinds,
            tpd_tolerance,
            candidate_mass_balance_tolerance,
            continuous_tpd_required
        );
        copy_discovery_to_postsolve(out, discovery);
        out.held_stage_iii_status = "ipopt_refinement_completed_current_route";
        out.held_stage_iii_refined_phase_count = system.phase_count;
        if (!out.stability_checked) {
            out.accepted = false;
            out.rejection_reason = "candidate_completeness";
        } else if (!out.stability_accepted) {
            out.accepted = false;
            out.rejection_reason = "stability_tpd";
        } else if (!out.candidate_completeness_accepted) {
            out.accepted = false;
            out.rejection_reason = "candidate_completeness";
        } else {
            out.rejection_reason = "accepted";
        }
    }
    return out;
}

NeutralTwoPhaseEosPostsolve evaluate_neutral_multiphase_eos_postsolve(
    const add_args& args,
    double temperature,
    double target_pressure,
    const std::vector<std::vector<double>>& phase_amounts,
    const std::vector<double>& volumes,
    const std::vector<double>& feed_amounts,
    double material_tolerance,
    double pressure_tolerance,
    double chemical_potential_tolerance,
    double phase_distance_tolerance,
    const std::vector<int>& phase_kinds
) {
    return evaluate_neutral_two_phase_eos_postsolve(
        args,
        temperature,
        target_pressure,
        phase_amounts,
        volumes,
        feed_amounts,
        material_tolerance,
        pressure_tolerance,
        chemical_potential_tolerance,
        phase_distance_tolerance,
        {},
        false,
        true,
        phase_kinds
    );
}

NeutralTwoPhaseEosRouteResult solve_neutral_two_phase_eos_route(
    const add_args& args,
    double temperature,
    double target_pressure,
    const std::vector<std::vector<double>>& phase_amounts,
    const std::vector<double>& volumes,
    const std::vector<double>& feed_amounts,
    const IpoptSolveOptions& options,
    double material_tolerance,
    double pressure_tolerance,
    double chemical_potential_tolerance,
    double phase_distance_tolerance,
    double minimum_phase_distance,
    const std::vector<double>& charges,
    const std::string& problem_name,
    double charge_tolerance
) {
    if (!charges.empty()) {
        require_positive_finite(charge_tolerance, problem_name + " charge tolerance");
    }
    const IpoptAdapterInfo adapter = native_ipopt_adapter_info();
    NeutralTwoPhaseEosRouteResult out;
    out.compiled = adapter.compiled;
    out.adapter_available = adapter.adapter_available;
    out.adapter_kind = adapter.adapter_kind;
    out.exact_gradient_required = adapter.exact_gradient_required;
    out.exact_jacobian_required = adapter.exact_jacobian_required;
    out.problem_name = problem_name;
    apply_route_metadata(out, phase_amount_volume_route_metadata(!charges.empty(), minimum_phase_distance > 0.0));
    if (!adapter.compiled) {
        mark_neutral_route_ipopt_dependency_required(out);
        return out;
    }

    const IpoptSolveResult solve = solve_neutral_two_phase_eos_ipopt(
        args,
        temperature,
        target_pressure,
        phase_amounts,
        volumes,
        feed_amounts,
        options,
        charges,
        problem_name,
        minimum_phase_distance
    );
    if (!apply_neutral_route_solve_result(out, solve)) {
        return out;
    }

    const std::size_t species_count = feed_amounts.size();
    out.phase_amounts = neutral_phase_amounts_from_route_variables(solve.variables, species_count);
    out.phase_volumes = neutral_phase_volumes_from_route_variables(solve.variables, species_count);
    NeutralTwoPhaseEosPostsolve postsolve = evaluate_neutral_two_phase_eos_postsolve(
        args,
        temperature,
        target_pressure,
        out.phase_amounts,
        out.phase_volumes,
        feed_amounts,
        material_tolerance,
        pressure_tolerance,
        chemical_potential_tolerance,
        phase_distance_tolerance,
        charges,
        minimum_phase_distance > 0.0
    );
    if (!charges.empty()) {
        postsolve.charge_balance_norm = phase_charge_inf_norm(out.phase_amounts, charges);
        postsolve.accepted = postsolve.accepted && postsolve.charge_balance_norm <= charge_tolerance;
        if (postsolve.charge_balance_norm > charge_tolerance) {
            postsolve.rejection_reason = "charge_balance";
        }
    }
    apply_neutral_route_postsolve(out, std::move(postsolve), NeutralRouteCertificationLevel::LocalPostsolve);
    return out;
}

NeutralTwoPhaseEosRouteResult solve_neutral_multiphase_fugacity_residual_route(
    const add_args& args,
    double temperature,
    double target_pressure,
    const std::vector<double>& feed_composition,
    const std::vector<int>& phase_kinds,
    const IpoptSolveOptions& options,
    double material_tolerance,
    double pressure_tolerance,
    double ln_fugacity_tolerance,
    double phase_distance_tolerance
) {
    const std::string problem_name = "neutral_multiphase_fugacity_residual";
    if (phase_kinds.size() < 3) {
        throw ValueError(problem_name + " requires at least three requested phase kinds.");
    }
    const IpoptAdapterInfo adapter = native_ipopt_adapter_info();
    NeutralTwoPhaseEosRouteResult out;
    out.compiled = adapter.compiled;
    out.adapter_available = adapter.adapter_available;
    out.adapter_kind = adapter.adapter_kind;
    out.exact_gradient_required = adapter.exact_gradient_required;
    out.exact_jacobian_required = adapter.exact_jacobian_required;
    out.problem_name = problem_name;
    out.activation_compiler = "direct_multiphase_candidate_set";
    out.initial_point_strategy = "stage_ii_candidate_set_replay";
    out.seed_name = kHeldStageIIDualLoopCandidateSetName;
    apply_route_metadata(out, phase_amount_volume_route_metadata(false, false, true));
    if (!adapter.compiled) {
        mark_neutral_route_ipopt_dependency_required(out);
        return out;
    }

    const std::vector<double> feed_amounts =
        normalized_positive_values(feed_composition, problem_name + " feed composition");
    const double candidate_mass_balance_tolerance = std::max(1.0e-8, 10.0 * material_tolerance);
    const double tpd_tolerance = std::max(1.0e-6, 100.0 * ln_fugacity_tolerance);
    const NeutralPhaseDiscoveryResult discovery = evaluate_neutral_tpd_phase_discovery(
        args,
        temperature,
        target_pressure,
        feed_amounts,
        phase_kinds,
        tpd_tolerance,
        candidate_mass_balance_tolerance,
        true
    );
    if (!discovery.held_stage_ii_replay_ready
        || !discovery.phase_set_mass_balance_feasible
        || discovery.selected_candidate_count != static_cast<int>(phase_kinds.size())) {
        NeutralTwoPhaseEosPostsolve postsolve;
        copy_discovery_to_postsolve(postsolve, discovery);
        postsolve.accepted = false;
        postsolve.rejection_reason = "stage_ii_candidate_set_replay";
        apply_neutral_route_postsolve(out, std::move(postsolve), NeutralRouteCertificationLevel::LocalPostsolve);
        return out;
    }

    const NeutralTwoPhaseEosInitialPoint initial = build_multiphase_eos_initial_point_from_candidate_set(
        args,
        feed_amounts,
        discovery,
        temperature,
        target_pressure,
        problem_name,
        phase_kinds
    );
    IpoptSolveOptions route_options = ipopt_solve_options_for_profile(options, "held_refinement");
    route_options.initial_variables = neutral_two_phase_variables_from_initial(initial);
    route_options.initial_bound_lower_multipliers.clear();
    route_options.initial_bound_upper_multipliers.clear();
    route_options.initial_constraint_multipliers.clear();

    trace_route_seed_attempt_start(problem_name, out.seed_name, 1, 1, route_options);
    NeutralMultiphaseFugacityResidualProblem problem(
        args,
        temperature,
        target_pressure,
        initial.phase_amounts,
        initial.volumes,
        feed_amounts
    );
    const IpoptSolveResult solve = solve_ipopt_nlp(problem, route_options);
    const bool can_postsolve = apply_neutral_route_solve_result(out, solve);
    if (!can_postsolve) {
        out.seed_attempts.push_back(neutral_seed_attempt_from_result(out));
        trace_route_seed_attempt_finish(problem_name, out.seed_name, 1, 1, out);
        return out;
    }

    const std::size_t species_count = feed_amounts.size();
    out.phase_amounts = neutral_phase_amounts_from_route_variables(solve.variables, species_count);
    out.phase_volumes = neutral_phase_volumes_from_route_variables(solve.variables, species_count);
    NeutralTwoPhaseEosPostsolve postsolve = evaluate_neutral_two_phase_eos_postsolve(
        args,
        temperature,
        target_pressure,
        out.phase_amounts,
        out.phase_volumes,
        feed_amounts,
        material_tolerance,
        pressure_tolerance,
        ln_fugacity_tolerance,
        phase_distance_tolerance,
        {},
        false,
        false,
        phase_kinds,
        false,
        true
    );
    if (postsolve.phase_distance <= phase_distance_tolerance) {
        postsolve.accepted = false;
        postsolve.rejection_reason = "phase_distance";
    }
    apply_stage_ii_discovery_certificate_to_refined_postsolve(
        postsolve,
        discovery,
        postsolve.phase_count,
        "stage_ii_dual_loop_candidate_set_seed",
        kHeldStageIIDualLoopCandidateSetName
    );
    apply_neutral_route_postsolve(out, std::move(postsolve), NeutralRouteCertificationLevel::PhaseSetCertified);
    out.seed_attempts.push_back(neutral_seed_attempt_from_result(out));
    trace_route_seed_attempt_finish(problem_name, out.seed_name, 1, 1, out);
    return out;
}

// AlgID: neutral_lle_ipopt
NeutralTwoPhaseEosRouteResult solve_activated_neutral_lle_eos_route(
    const add_args& args,
    double temperature,
    double target_pressure,
    const std::vector<double>& feed_composition,
    const IpoptSolveOptions& options,
    double material_tolerance,
    double pressure_tolerance,
    double chemical_potential_tolerance,
    double phase_distance_tolerance
) {
    const std::string problem_name = "neutral_lle_eos";
    const epcsaft::native::equilibrium::ActivationPlan plan =
        epcsaft::native::equilibrium::build_neutral_lle_activation_plan(
            args,
            temperature,
            target_pressure,
            feed_composition
        );
    const epcsaft::native::equilibrium::VariableLayout layout =
        epcsaft::native::equilibrium::build_variable_layout(
            plan,
            static_cast<int>(plan.feed_composition.size())
        );
    const IpoptAdapterInfo adapter = native_ipopt_adapter_info();
    NeutralTwoPhaseEosRouteResult best;
    best.compiled = adapter.compiled;
    best.adapter_available = adapter.adapter_available;
    best.adapter_kind = adapter.adapter_kind;
    best.exact_gradient_required = adapter.exact_gradient_required;
    best.exact_jacobian_required = adapter.exact_jacobian_required;
    best.problem_name = problem_name;
    best.activation_compiler = "activation_plan";
    apply_route_metadata(best, phase_amount_volume_route_metadata(false, true));
    if (!adapter.compiled) {
        mark_neutral_route_ipopt_dependency_required(best);
        return best;
    }

    const std::vector<double>& normalized_feed = plan.feed_composition;
    const std::vector<double> feed_amounts = normalized_feed;
    const IpoptSolveOptions route_options = ipopt_solve_options_for_profile(options, "held_refinement");
    const std::vector<NamedInitialVariables> seeds = neutral_two_phase_seed_candidates(
        args,
        feed_amounts,
        {},
        temperature,
        target_pressure,
        problem_name,
        {0, 0}
    );
    bool have_best = false;
    std::vector<RouteSeedAttempt> attempts;
    attempts.reserve(seeds.size() + (route_options.initial_variables.empty() ? 0 : 1));
    const int seed_attempt_count =
        static_cast<int>(seeds.size() + (route_options.initial_variables.empty() ? 0 : 1));

    auto run_attempt = [&](const std::string& seed_name, const IpoptSolveOptions& attempt_options) {
        const int seed_attempt_index = static_cast<int>(attempts.size()) + 1;
        trace_route_seed_attempt_start(
            problem_name,
            seed_name,
            seed_attempt_index,
            seed_attempt_count,
            attempt_options
        );
        ActivatedEquilibriumNlp problem(args, plan, layout);
        const IpoptSolveResult solve = solve_ipopt_nlp(problem, attempt_options);
        NeutralTwoPhaseEosRouteResult result;
        result.compiled = adapter.compiled;
        result.adapter_available = adapter.adapter_available;
        result.adapter_kind = adapter.adapter_kind;
        result.exact_gradient_required = adapter.exact_gradient_required;
        result.exact_jacobian_required = adapter.exact_jacobian_required;
        result.problem_name = problem_name;
        result.activation_compiler = "activation_plan";
        result.initial_point_strategy = "deterministic_seed_sweep";
        result.seed_name = seed_name;
        const bool can_postsolve = apply_neutral_route_solve_result(result, solve);
        apply_route_metadata(result, phase_amount_volume_route_metadata(false, true));
        if (!can_postsolve) {
            attempts.push_back(neutral_seed_attempt_from_result(result));
            trace_route_seed_attempt_finish(
                problem_name,
                seed_name,
                seed_attempt_index,
                seed_attempt_count,
                result
            );
            if (!have_best || neutral_route_quality(result) > neutral_route_quality(best)) {
                best = result;
                have_best = true;
            }
            return result;
        }

        result.phase_amounts = neutral_phase_amounts_from_route_variables(
            solve.variables,
            static_cast<std::size_t>(layout.species_count)
        );
        result.phase_volumes = neutral_phase_volumes_from_route_variables(
            solve.variables,
            static_cast<std::size_t>(layout.species_count)
        );
        NeutralTwoPhaseEosPostsolve postsolve = evaluate_neutral_two_phase_eos_postsolve(
            args,
            temperature,
            target_pressure,
            result.phase_amounts,
            result.phase_volumes,
            feed_amounts,
            material_tolerance,
            pressure_tolerance,
            chemical_potential_tolerance,
            phase_distance_tolerance,
            {},
            true,
            true,
            {0, 0},
            true
        );
        apply_neutral_route_postsolve(
            result,
            std::move(postsolve),
            NeutralRouteCertificationLevel::PhaseSetCertified
        );
        if (seed_name == kHeldStageIIDualLoopSeedName && result.postsolve.held_stage_ii_replay_ready) {
            result.postsolve.held_stage_iii_consumed_stage_ii_replay_metadata = true;
            result.postsolve.held_stage_iii_replay_source = "stage_ii_dual_loop_candidate_seed";
            result.postsolve.held_stage_iii_replay_seed_name = kHeldStageIIDualLoopSeedName;
            result.postsolve.held_stage_iii_replay_candidate_count =
                result.postsolve.held_stage_ii_replay_candidate_count;
        }
        attempts.push_back(neutral_seed_attempt_from_result(result));
        trace_route_seed_attempt_finish(
            problem_name,
            seed_name,
            seed_attempt_index,
            seed_attempt_count,
            result
        );
        if (!have_best || neutral_route_quality(result) > neutral_route_quality(best)) {
            best = result;
            have_best = true;
        }
        return result;
    };

    if (!route_options.initial_variables.empty()) {
        const NeutralTwoPhaseEosRouteResult continuation = run_attempt("continuation_state", route_options);
        if (continuation.accepted) {
            best.seed_attempts = attempts;
            return best;
        }
    }

    if (seeds.empty()) {
        throw ValueError(problem_name + " could not construct a deterministic LLE seed.");
    }
    for (const auto& seed : seeds) {
        IpoptSolveOptions attempt_options = route_options;
        attempt_options.initial_variables = seed.variables;
        attempt_options.initial_bound_lower_multipliers.clear();
        attempt_options.initial_bound_upper_multipliers.clear();
        attempt_options.initial_constraint_multipliers.clear();
        const NeutralTwoPhaseEosRouteResult attempt = run_attempt(seed.seed_name, attempt_options);
        if (attempt.accepted) {
            break;
        }
    }

    best.initial_point_strategy = "deterministic_seed_sweep";
    best.seed_attempts = attempts;
    return best;
}

}  // namespace epcsaft::native::equilibrium_nlp
