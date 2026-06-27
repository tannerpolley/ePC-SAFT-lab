#include "equilibrium/core/two_phase_eos_route.h"

#include "equilibrium/blocks/eos_phase_block.h"
#include "equilibrium/core/activated_equilibrium_nlp.h"
#include "equilibrium/core/activation_plan.h"
#include "eos/core_internal.h"
#include "equilibrium/derivatives/nlp_contract_snapshot.h"
#include "equilibrium/derivatives/phase_block_derivatives.h"
#include "equilibrium/derivatives/route_second_order.h"
#include "equilibrium/core/nlp_problem.h"
#include "equilibrium/core/route_metadata.h"
#include "equilibrium/core/second_order.h"
#include "equilibrium/core/variable_transform.h"
#include "equilibrium/core/variable_layout.h"
#include "equilibrium/results/result_builder.h"

#include <algorithm>
#include <cmath>
#include <memory>
#include <numeric>
#include <utility>

namespace epcsaft::native::equilibrium_nlp {
namespace {

constexpr double kInitialPressure = 1.0e5;
constexpr double kInitialTemperature = 300.0;
constexpr double kGasConstant = 8.31446261815324;
constexpr double kPressureConstraintScaleFloor = 1.0e5;
constexpr double kBoundaryVolatilityKAlpha = 2.2;
constexpr double kTwoPhaseFlashFeedBasis = 2.0;
constexpr double kSeparatedLiquidDensity = 8000.0;
constexpr double kMinimumLiquidVolume = 1.0e-6;
constexpr double kMaximumLiquidVolume = 5.0e-4;
constexpr double kMinimumVaporVolume = 1.0e-3;
constexpr double kMaximumVaporVolume = 1.0e6;
constexpr double kMinimumPhaseVolumeGap = 1.0e-7;
constexpr double kMinimumPressure = 1.0;
constexpr double kMaximumPressure = 1.0e9;
constexpr double kPureSaturationMinimumVaporVolume = 1.0e-6;
constexpr double kPureSaturationMaximumVaporVolume = 1.0e8;
constexpr double kPureSaturationMinimumPressure = 1.0e-6;
constexpr double kPureSaturationMinimumPhaseVolumeGap = 1.0e-6;
constexpr double kPureSaturationMinimumReducedDensitySeparation = 1.0e-2;
constexpr const char* kNeutralCloudTemperatureProblemName = "neutral_cloud_t_eos";

void symmetrize_local_square_matrix(std::vector<double>& values, int dimension) {
    for (int first = 0; first < dimension; ++first) {
        for (int second = first + 1; second < dimension; ++second) {
            const std::size_t first_index = static_cast<std::size_t>(first * dimension + second);
            const std::size_t second_index = static_cast<std::size_t>(second * dimension + first);
            const double symmetric_value = 0.5 * (values[first_index] + values[second_index]);
            values[first_index] = symmetric_value;
            values[second_index] = symmetric_value;
        }
    }
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

enum class DensitySeedMode {
    PhasePressureRoot,
    SeparatedPhaseRole,
};

bool temperature_route_is_cloud_shadow(const std::string& problem_name) {
    return problem_name == kNeutralCloudTemperatureProblemName;
}

double fixed_pressure_temperature_phase1_minimum_volume(const std::string& problem_name) {
    return temperature_route_is_cloud_shadow(problem_name) ? kMinimumLiquidVolume : kMinimumVaporVolume;
}

double fixed_pressure_temperature_phase1_maximum_volume(const std::string& problem_name) {
    return temperature_route_is_cloud_shadow(problem_name) ? kMaximumLiquidVolume : kMaximumVaporVolume;
}

double fixed_pressure_temperature_minimum_phase_volume_gap(const std::string& problem_name) {
    return temperature_route_is_cloud_shadow(problem_name) ? -kMaximumLiquidVolume : kMinimumPhaseVolumeGap;
}

void require_size(const std::vector<double>& values, std::size_t expected, const std::string& label) {
    if (values.size() == expected) {
        return;
    }
    throw ValueError(label + " size does not match the fixed-temperature pressure route.");
}

void require_positive_finite(double value, const std::string& label) {
    if (std::isfinite(value) && value > 0.0) {
        return;
    }
    throw ValueError(label + " must be positive and finite.");
}

double pressure_constraint_scale(double reference_pressure) {
    return 1.0 / std::max(kPressureConstraintScaleFloor, std::abs(reference_pressure));
}

void apply_pressure_constraint_scaling(
    NlpScaling& scaling,
    int pressure_row_start,
    int phase_count,
    double reference_pressure
) {
    const double scale = pressure_constraint_scale(reference_pressure);
    for (int phase = 0; phase < phase_count; ++phase) {
        scaling.constraints[static_cast<std::size_t>(pressure_row_start + phase)] = scale;
    }
}

std::vector<double> normalized_positive_values(const std::vector<double>& values, const std::string& label) {
    if (values.empty()) {
        throw ValueError(label + " requires at least one value.");
    }
    double total = 0.0;
    for (double value : values) {
        require_positive_finite(value, label + " value");
        total += value;
    }
    require_positive_finite(total, label + " total");
    std::vector<double> normalized;
    normalized.reserve(values.size());
    for (double value : values) {
        normalized.push_back(value / total);
    }
    return normalized;
}

std::vector<double> shifted_composition(const std::vector<double>& composition, double shift_sign = 1.0) {
    if (composition.empty()) {
        return {};
    }
    if (composition.size() == 1) {
        return {composition.front()};
    }
    const double triangular_sum = 0.5 * static_cast<double>(composition.size() * (composition.size() + 1));
    std::vector<double> shifted;
    shifted.reserve(composition.size());
    for (std::size_t index = 0; index < composition.size(); ++index) {
        const double triangular = static_cast<double>(index + 1) / triangular_sum;
        shifted.push_back(
            0.8 * composition[index]
            + 0.2 * (shift_sign > 0.0 ? triangular : (1.0 - triangular + 1.0 / triangular_sum))
        );
    }
    return normalized_positive_values(shifted, "shifted composition");
}

std::vector<double> charge_neutral_shifted_composition(
    const std::vector<double>& composition,
    const std::vector<double>& charges,
    const std::string& label,
    double shift_sign = 1.0
) {
    require_size(charges, composition.size(), label + " charge");
    if (composition.size() <= 1) {
        throw ValueError(label + " requires at least two species.");
    }
    double composition_charge = 0.0;
    double charge_square_weight = 0.0;
    for (std::size_t index = 0; index < composition.size(); ++index) {
        if (!std::isfinite(charges[index])) {
            throw ValueError(label + " charge values must be finite.");
        }
        composition_charge += composition[index] * charges[index];
        charge_square_weight += composition[index] * charges[index] * charges[index];
    }
    if (charge_square_weight <= 0.0) {
        throw ValueError(label + " requires at least one charged species.");
    }
    if (std::abs(composition_charge) > 1.0e-10) {
        throw ValueError(label + " fixed composition must be charge neutral.");
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
    double charge_direction = 0.0;
    for (std::size_t index = 0; index < composition.size(); ++index) {
        const double value = positions[index] - weighted_position;
        direction.push_back(value);
        charge_direction += composition[index] * charges[index] * value;
    }
    const double charge_projection = charge_direction / charge_square_weight;
    double max_abs_direction = 0.0;
    for (std::size_t index = 0; index < direction.size(); ++index) {
        direction[index] -= charge_projection * charges[index];
        max_abs_direction = std::max(max_abs_direction, std::abs(direction[index]));
    }
    if (max_abs_direction <= 0.0) {
        throw ValueError(label + " could not construct a charge-neutral initial direction.");
    }

    std::vector<double> shifted;
    shifted.reserve(composition.size());
    double shifted_sum = 0.0;
    for (std::size_t index = 0; index < composition.size(); ++index) {
        const double value =
            composition[index] * (1.0 + 0.2 * shift_sign * direction[index] / max_abs_direction);
        require_positive_finite(value, label + " shifted composition");
        shifted.push_back(value);
        shifted_sum += value;
    }
    require_positive_finite(shifted_sum, label + " shifted composition sum");
    for (double& value : shifted) {
        value /= shifted_sum;
    }
    return shifted;
}

int phase_kind_from_index(int phase, const std::string& problem_name) {
    if (phase == 0) {
        return 0;
    }
    if (phase == 1) {
        if (temperature_route_is_cloud_shadow(problem_name)) {
            return 0;
        }
        return 1;
    }
    throw ValueError(problem_name + " phase index is out of range for density-root seeding.");
}

double phase_density_root_seed(
    const add_args& args,
    double temperature,
    double pressure,
    const std::vector<double>& composition,
    int phase,
    const std::string& problem_name
) {
    const DensitySolveResult density = density_solve_report_cpp(
        temperature,
        pressure,
        composition,
        phase_kind_from_index(phase, problem_name),
        args
    );
    if (!density.valid || !std::isfinite(density.rho) || density.rho <= 0.0) {
        throw ValueError(problem_name + " could not construct a phase-specific pressure-density root seed.");
    }
    return density.rho;
}

double separated_phase_role_density_seed(double temperature, double pressure, int phase, const std::string& problem_name) {
    if (phase == 0) {
        return kSeparatedLiquidDensity;
    }
    if (phase == 1) {
        if (temperature_route_is_cloud_shadow(problem_name)) {
            return kSeparatedLiquidDensity;
        }
        return std::max(pressure / (kGasConstant * temperature), 1.0e-12);
    }
    throw ValueError(problem_name + " phase index is out of range for separated density seeding.");
}

bool fixed_temperature_pressure_seed_satisfies_volume_bounds(
    const std::vector<double>& variables,
    int species_count,
    double minimum_liquid_volume = kMinimumLiquidVolume,
    double maximum_liquid_volume = kMaximumLiquidVolume,
    double minimum_vapor_volume = kMinimumVaporVolume,
    double maximum_vapor_volume = kMaximumVaporVolume,
    double minimum_phase_volume_gap = kMinimumPhaseVolumeGap
) {
    const int local_variable_count = species_count + 1;
    if (variables.size() != static_cast<std::size_t>(2 * local_variable_count + 1)) {
        return false;
    }
    const double liquid_volume = variables[static_cast<std::size_t>(species_count)];
    const double vapor_volume = variables[static_cast<std::size_t>(local_variable_count + species_count)];
    return liquid_volume >= minimum_liquid_volume
        && liquid_volume <= maximum_liquid_volume
        && vapor_volume >= minimum_vapor_volume
        && vapor_volume <= maximum_vapor_volume
        && vapor_volume - liquid_volume >= minimum_phase_volume_gap;
}

bool fixed_temperature_pressure_flash_seed_satisfies_volume_bounds(
    const std::vector<double>& variables,
    int species_count
) {
    const int local_variable_count = species_count + 1;
    if (variables.size() != static_cast<std::size_t>(2 * local_variable_count)) {
        return false;
    }
    const double liquid_volume = variables[static_cast<std::size_t>(species_count)];
    const double vapor_volume = variables[static_cast<std::size_t>(local_variable_count + species_count)];
    return liquid_volume >= kMinimumLiquidVolume
        && liquid_volume <= kMaximumLiquidVolume
        && vapor_volume >= kMinimumVaporVolume
        && vapor_volume <= kMaximumVaporVolume
        && vapor_volume - liquid_volume >= kMinimumPhaseVolumeGap;
}

std::vector<double> log_positive_variables(
    const std::vector<double>& physical_variables,
    const std::string& label
) {
    std::vector<double> out;
    out.reserve(physical_variables.size());
    for (double value : physical_variables) {
        require_positive_finite(value, label);
        out.push_back(std::log(value));
    }
    return out;
}

std::vector<double> lower_dense_to_symmetric_matrix(
    const NlpHessianStructure& structure,
    const std::vector<double>& values,
    int variable_count,
    const std::string& label
) {
    if (structure.rows.size() != values.size() || structure.cols.size() != values.size()) {
        throw ValueError(label + " Hessian structure/value size mismatch.");
    }
    std::vector<double> dense(static_cast<std::size_t>(variable_count * variable_count), 0.0);
    for (std::size_t index = 0; index < values.size(); ++index) {
        const int row = structure.rows[index];
        const int col = structure.cols[index];
        if (row < 0 || row >= variable_count || col < 0 || col >= variable_count) {
            throw ValueError(label + " Hessian structure index is out of range.");
        }
        dense[static_cast<std::size_t>(row * variable_count + col)] = values[index];
        dense[static_cast<std::size_t>(col * variable_count + row)] = values[index];
    }
    return dense;
}

class PositiveLogNlpProblem final : public NlpProblem {
public:
    explicit PositiveLogNlpProblem(std::unique_ptr<NlpProblem> delegate)
        : delegate_(std::move(delegate)) {
        if (!delegate_) {
            throw ValueError("positive-log NLP wrapper requires a delegate problem.");
        }
    }

    std::string name() const override {
        return delegate_->name();
    }

    int variable_count() const override {
        return delegate_->variable_count();
    }

    int constraint_count() const override {
        return delegate_->constraint_count();
    }

    int jacobian_nonzero_count() const override {
        return delegate_->jacobian_nonzero_count();
    }

    NlpBounds bounds() const override {
        NlpBounds physical = delegate_->bounds();
        require_size(physical.variable_lower, static_cast<std::size_t>(variable_count()), name() + " lower bound");
        require_size(physical.variable_upper, static_cast<std::size_t>(variable_count()), name() + " upper bound");
        for (double& value : physical.variable_lower) {
            require_positive_finite(value, name() + " positive-log lower bound");
            value = std::log(value);
        }
        for (double& value : physical.variable_upper) {
            require_positive_finite(value, name() + " positive-log upper bound");
            value = std::log(value);
        }
        return physical;
    }

    std::vector<double> initial_point() const override {
        return solver_variables_from_physical(delegate_->initial_point());
    }

    double objective(const std::vector<double>& variables) const override {
        return delegate_->objective(physical_variables_from_solver(variables));
    }

    std::vector<double> objective_gradient(const std::vector<double>& variables) const override {
        const std::vector<double> physical = physical_variables_from_solver(variables);
        const std::vector<double> physical_gradient = delegate_->objective_gradient(physical);
        require_size(
            physical_gradient,
            static_cast<std::size_t>(variable_count()),
            name() + " physical objective gradient"
        );
        std::vector<double> out(static_cast<std::size_t>(variable_count()), 0.0);
        for (int col = 0; col < variable_count(); ++col) {
            out[static_cast<std::size_t>(col)] =
                physical_gradient[static_cast<std::size_t>(col)] * physical[static_cast<std::size_t>(col)];
        }
        return out;
    }

    std::vector<double> constraints(const std::vector<double>& variables) const override {
        return delegate_->constraints(physical_variables_from_solver(variables));
    }

    NlpJacobianStructure jacobian_structure() const override {
        return delegate_->jacobian_structure();
    }

    std::vector<double> jacobian_values(const std::vector<double>& variables) const override {
        const std::vector<double> physical = physical_variables_from_solver(variables);
        const NlpJacobianStructure structure = delegate_->jacobian_structure();
        std::vector<double> values = delegate_->jacobian_values(physical);
        if (values.size() != structure.cols.size()) {
            throw ValueError(name() + " positive-log Jacobian structure/value size mismatch.");
        }
        for (std::size_t index = 0; index < values.size(); ++index) {
            const int col = structure.cols[index];
            if (col < 0 || col >= variable_count()) {
                throw ValueError(name() + " positive-log Jacobian column is out of range.");
            }
            values[index] *= physical[static_cast<std::size_t>(col)];
        }
        return values;
    }

    bool has_exact_hessian() const override {
        return delegate_->has_exact_hessian();
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
        const std::vector<double> physical = physical_variables_from_solver(variables);
        const std::vector<double> physical_hessian_values =
            delegate_->hessian_values(physical, objective_factor, constraint_multipliers);
        const std::vector<double> physical_hessian = lower_dense_to_symmetric_matrix(
            delegate_->hessian_structure(),
            physical_hessian_values,
            variable_count(),
            name() + " positive-log delegate"
        );

        std::vector<double> lagrangian_gradient = delegate_->objective_gradient(physical);
        require_size(
            lagrangian_gradient,
            static_cast<std::size_t>(variable_count()),
            name() + " physical Lagrangian objective gradient"
        );
        for (double& value : lagrangian_gradient) {
            value *= objective_factor;
        }

        const NlpJacobianStructure jacobian_structure = delegate_->jacobian_structure();
        const std::vector<double> jacobian = delegate_->jacobian_values(physical);
        if (jacobian.size() != jacobian_structure.rows.size()
            || jacobian.size() != jacobian_structure.cols.size()) {
            throw ValueError(name() + " positive-log Lagrangian Jacobian structure/value size mismatch.");
        }
        require_size(
            constraint_multipliers,
            static_cast<std::size_t>(constraint_count()),
            name() + " positive-log constraint multiplier"
        );
        for (std::size_t index = 0; index < jacobian.size(); ++index) {
            const int row = jacobian_structure.rows[index];
            const int col = jacobian_structure.cols[index];
            if (row < 0 || row >= constraint_count() || col < 0 || col >= variable_count()) {
                throw ValueError(name() + " positive-log Lagrangian Jacobian index is out of range.");
            }
            lagrangian_gradient[static_cast<std::size_t>(col)] +=
                constraint_multipliers[static_cast<std::size_t>(row)] * jacobian[index];
        }

        const int n = variable_count();
        std::vector<double> transformed(static_cast<std::size_t>(n * n), 0.0);
        for (int first = 0; first < n; ++first) {
            for (int second = 0; second < n; ++second) {
                transformed[static_cast<std::size_t>(first * n + second)] =
                    physical[static_cast<std::size_t>(first)]
                    * physical_hessian[static_cast<std::size_t>(first * n + second)]
                    * physical[static_cast<std::size_t>(second)];
            }
            transformed[static_cast<std::size_t>(first * n + first)] +=
                lagrangian_gradient[static_cast<std::size_t>(first)]
                * physical[static_cast<std::size_t>(first)];
        }
        symmetrize_local_square_matrix(transformed, n);
        return lower_triangle_values(transformed, n);
    }

    std::string hessian_backend() const override {
        return delegate_->hessian_backend() + "_through_analytic_positive_log";
    }

    NlpScaling scaling() const override {
        NlpScaling out = delegate_->scaling();
        out.variables.assign(static_cast<std::size_t>(variable_count()), 1.0);
        return out;
    }

    std::map<std::string, std::string> diagnostics() const override {
        std::map<std::string, std::string> out = delegate_->diagnostics();
        out["variable_transform"] = "positive_log_coordinates";
        out["variable_model"] = "positive_log_amount_volume_temperature";
        return out;
    }

    std::vector<double> physical_variables_from_solver(
        const std::vector<double>& solver_variables
    ) const {
        return PositiveLogVariableTransform(variable_count()).solver_to_physical(solver_variables);
    }

    std::vector<double> solver_variables_from_physical(
        const std::vector<double>& physical_variables
    ) const {
        return log_positive_variables(physical_variables, name() + " positive-log physical variable");
    }

private:
    std::unique_ptr<NlpProblem> delegate_;
};

struct NamedInitialVariables {
    std::string seed_name;
    std::vector<double> variables;
};

std::vector<double> build_pressure_route_initial_variables(
    const add_args& args,
    const std::vector<double>& fixed_composition,
    int fixed_phase_index,
    double temperature,
    const std::vector<double>& charges,
    const std::string& problem_name,
    double shift_sign,
    DensitySeedMode density_seed_mode,
    double seed_pressure
) {
    require_positive_finite(seed_pressure, problem_name + " pressure seed");
    const std::vector<double> shifted = charges.empty()
        ? shifted_composition(fixed_composition, shift_sign)
        : charge_neutral_shifted_composition(
            fixed_composition,
            charges,
            problem_name + " shifted composition",
            shift_sign
        );
    std::vector<double> out;
    out.reserve(2 * (fixed_composition.size() + 1) + 1);
    for (int phase = 0; phase < 2; ++phase) {
        const std::vector<double>& composition = phase == fixed_phase_index ? fixed_composition : shifted;
        out.insert(out.end(), composition.begin(), composition.end());
        const double density = density_seed_mode == DensitySeedMode::PhasePressureRoot
            ? phase_density_root_seed(args, temperature, seed_pressure, composition, phase, problem_name)
            : separated_phase_role_density_seed(temperature, seed_pressure, phase, problem_name);
        out.push_back(1.0 / density);
    }
    out.push_back(seed_pressure);
    return out;
}

std::vector<double> build_temperature_route_initial_variables(
    const add_args& args,
    const std::vector<double>& fixed_composition,
    int fixed_phase_index,
    double target_pressure,
    const std::vector<double>& charges,
    const std::string& problem_name,
    double shift_sign,
    DensitySeedMode density_seed_mode
) {
    const std::vector<double> shifted = charges.empty()
        ? shifted_composition(fixed_composition, shift_sign)
        : charge_neutral_shifted_composition(
            fixed_composition,
            charges,
            problem_name + " shifted composition",
            shift_sign
        );
    std::vector<double> out;
    out.reserve(2 * (fixed_composition.size() + 1) + 1);
    for (int phase = 0; phase < 2; ++phase) {
        const std::vector<double>& composition = phase == fixed_phase_index ? fixed_composition : shifted;
        out.insert(out.end(), composition.begin(), composition.end());
        const double density = density_seed_mode == DensitySeedMode::PhasePressureRoot
            ? phase_density_root_seed(args, kInitialTemperature, target_pressure, composition, phase, problem_name)
            : separated_phase_role_density_seed(kInitialTemperature, target_pressure, phase, problem_name);
        out.push_back(1.0 / density);
    }
    out.push_back(kInitialTemperature);
    return out;
}

double rachford_rice_value(
    const std::vector<double>& feed_composition,
    const std::vector<double>& k_values,
    double vapor_fraction
) {
    double value = 0.0;
    for (std::size_t index = 0; index < feed_composition.size(); ++index) {
        const double k_minus_one = k_values[index] - 1.0;
        const double denominator = 1.0 + vapor_fraction * k_minus_one;
        require_positive_finite(denominator, "Rachford-Rice denominator");
        value += feed_composition[index] * k_minus_one / denominator;
    }
    return value;
}

double solve_rachford_rice_vapor_fraction(
    const std::vector<double>& feed_composition,
    const std::vector<double>& k_values,
    const std::string& problem_name
) {
    require_size(k_values, feed_composition.size(), problem_name + " K-value");
    const double f0 = rachford_rice_value(feed_composition, k_values, 0.0);
    const double f1 = rachford_rice_value(feed_composition, k_values, 1.0);
    if (!(f0 > 0.0 && f1 < 0.0)) {
        throw ValueError(problem_name + " K-values do not bracket a two-phase flash split.");
    }
    double lower = 0.0;
    double upper = 1.0;
    for (int iteration = 0; iteration < 80; ++iteration) {
        const double mid = 0.5 * (lower + upper);
        if (rachford_rice_value(feed_composition, k_values, mid) > 0.0) {
            lower = mid;
        } else {
            upper = mid;
        }
    }
    return 0.5 * (lower + upper);
}

std::vector<double> volatility_ranked_k_values(
    const add_args& args,
    const std::vector<double>& feed_composition,
    const std::string& problem_name,
    double alpha
) {
    if (feed_composition.size() <= 1) {
        throw ValueError(problem_name + " flash seed requires at least two species.");
    }
    std::vector<double> scores;
    scores.reserve(feed_composition.size());
    if (args.m.size() == feed_composition.size()) {
        double mean_m = 0.0;
        for (double value : args.m) {
            mean_m += value;
        }
        mean_m /= static_cast<double>(args.m.size());
        double span = 0.0;
        for (double value : args.m) {
            span = std::max(span, std::abs(value - mean_m));
        }
        if (span > 0.0) {
            for (double value : args.m) {
                scores.push_back((mean_m - value) / span);
            }
        }
    }
    if (scores.empty()) {
        const double denominator = static_cast<double>(feed_composition.size() - 1);
        for (std::size_t index = 0; index < feed_composition.size(); ++index) {
            scores.push_back(1.0 - 2.0 * static_cast<double>(index) / denominator);
        }
    }

    std::vector<double> k_values;
    k_values.reserve(feed_composition.size());
    for (double score : scores) {
        k_values.push_back(std::exp(alpha * score));
    }
    return k_values;
}

std::vector<double> boundary_partner_composition_from_k_values(
    const add_args& args,
    const std::vector<double>& fixed_composition,
    int fixed_phase_index,
    const std::string& problem_name,
    double alpha
) {
    const std::vector<double> k_values = volatility_ranked_k_values(
        args,
        fixed_composition,
        problem_name,
        alpha
    );
    std::vector<double> partner;
    partner.reserve(fixed_composition.size());
    for (std::size_t index = 0; index < fixed_composition.size(); ++index) {
        const double k_value = k_values[index];
        require_positive_finite(k_value, problem_name + " boundary K-value");
        partner.push_back(
            fixed_phase_index == 0
                ? fixed_composition[index] * k_value
                : fixed_composition[index] / k_value
        );
    }
    return normalized_positive_values(partner, problem_name + " boundary K-value partner composition");
}

std::vector<double> build_pressure_route_initial_variables_with_partner(
    const add_args& args,
    const std::vector<double>& fixed_composition,
    const std::vector<double>& partner_composition,
    int fixed_phase_index,
    double temperature,
    const std::string& problem_name,
    DensitySeedMode density_seed_mode
) {
    require_size(partner_composition, fixed_composition.size(), problem_name + " boundary partner composition");
    std::vector<double> out;
    out.reserve(2 * (fixed_composition.size() + 1) + 1);
    for (int phase = 0; phase < 2; ++phase) {
        const std::vector<double>& composition = phase == fixed_phase_index ? fixed_composition : partner_composition;
        out.insert(out.end(), composition.begin(), composition.end());
        const double density = density_seed_mode == DensitySeedMode::PhasePressureRoot
            ? phase_density_root_seed(args, temperature, kInitialPressure, composition, phase, problem_name)
            : separated_phase_role_density_seed(temperature, kInitialPressure, phase, problem_name);
        out.push_back(1.0 / density);
    }
    out.push_back(kInitialPressure);
    return out;
}

std::vector<double> build_temperature_route_initial_variables_with_partner(
    const add_args& args,
    const std::vector<double>& fixed_composition,
    const std::vector<double>& partner_composition,
    int fixed_phase_index,
    double target_pressure,
    const std::string& problem_name,
    DensitySeedMode density_seed_mode
) {
    require_size(partner_composition, fixed_composition.size(), problem_name + " boundary partner composition");
    std::vector<double> out;
    out.reserve(2 * (fixed_composition.size() + 1) + 1);
    for (int phase = 0; phase < 2; ++phase) {
        const std::vector<double>& composition = phase == fixed_phase_index ? fixed_composition : partner_composition;
        out.insert(out.end(), composition.begin(), composition.end());
        const double density = density_seed_mode == DensitySeedMode::PhasePressureRoot
            ? phase_density_root_seed(args, kInitialTemperature, target_pressure, composition, phase, problem_name)
            : separated_phase_role_density_seed(kInitialTemperature, target_pressure, phase, problem_name);
        out.push_back(1.0 / density);
    }
    out.push_back(kInitialTemperature);
    return out;
}

std::vector<double> build_flash_route_initial_variables(
    const add_args& args,
    const std::vector<double>& feed_composition,
    const std::vector<double>& liquid_composition,
    const std::vector<double>& vapor_composition,
    double vapor_fraction,
    double temperature,
    double target_pressure,
    const std::string& problem_name,
    DensitySeedMode density_seed_mode = DensitySeedMode::PhasePressureRoot
) {
    require_size(liquid_composition, feed_composition.size(), problem_name + " flash liquid composition");
    require_size(vapor_composition, feed_composition.size(), problem_name + " flash vapor composition");
    if (!(vapor_fraction > 0.0 && vapor_fraction < 1.0)) {
        throw ValueError(problem_name + " flash vapor fraction must be inside (0, 1).");
    }
    std::vector<double> out;
    out.reserve(2 * (feed_composition.size() + 1));
    const double liquid_fraction = 1.0 - vapor_fraction;
    for (int phase = 0; phase < 2; ++phase) {
        const double phase_fraction = phase == 0 ? liquid_fraction : vapor_fraction;
        const std::vector<double>& composition = phase == 0 ? liquid_composition : vapor_composition;
        for (double value : composition) {
            require_positive_finite(value, problem_name + " flash phase composition");
            out.push_back(kTwoPhaseFlashFeedBasis * phase_fraction * value);
        }
        const double density = density_seed_mode == DensitySeedMode::PhasePressureRoot
            ? phase_density_root_seed(args, temperature, target_pressure, composition, phase, problem_name)
            : separated_phase_role_density_seed(temperature, target_pressure, phase, problem_name);
        out.push_back(kTwoPhaseFlashFeedBasis * phase_fraction / density);
    }
    return out;
}

std::vector<double> build_flash_route_initial_variables_from_k_values(
    const add_args& args,
    const std::vector<double>& feed_composition,
    const std::vector<double>& k_values,
    double temperature,
    double target_pressure,
    const std::string& problem_name
) {
    const double vapor_fraction = solve_rachford_rice_vapor_fraction(feed_composition, k_values, problem_name);
    std::vector<double> liquid;
    std::vector<double> vapor;
    liquid.reserve(feed_composition.size());
    vapor.reserve(feed_composition.size());
    for (std::size_t index = 0; index < feed_composition.size(); ++index) {
        const double denominator = 1.0 + vapor_fraction * (k_values[index] - 1.0);
        require_positive_finite(denominator, problem_name + " flash split denominator");
        const double liquid_value = feed_composition[index] / denominator;
        const double vapor_value = k_values[index] * liquid_value;
        liquid.push_back(liquid_value);
        vapor.push_back(vapor_value);
    }
    return build_flash_route_initial_variables(
        args,
        feed_composition,
        liquid,
        vapor,
        vapor_fraction,
        temperature,
        target_pressure,
        problem_name
    );
}

std::vector<double> build_shifted_flash_route_initial_variables(
    const add_args& args,
    const std::vector<double>& feed_composition,
    double temperature,
    double target_pressure,
    const std::string& problem_name,
    double shift_sign,
    DensitySeedMode density_seed_mode
) {
    constexpr double vapor_fraction = 0.5;
    const std::vector<double> first = shifted_composition(feed_composition, shift_sign);
    std::vector<double> second;
    second.reserve(feed_composition.size());
    for (std::size_t index = 0; index < feed_composition.size(); ++index) {
        const double value = (feed_composition[index] - (1.0 - vapor_fraction) * first[index]) / vapor_fraction;
        require_positive_finite(value, problem_name + " shifted flash partner composition");
        second.push_back(value);
    }
    const std::vector<double>& liquid = shift_sign < 0.0 ? second : first;
    const std::vector<double>& vapor = shift_sign < 0.0 ? first : second;
    return build_flash_route_initial_variables(
        args,
        feed_composition,
        liquid,
        vapor,
        vapor_fraction,
        temperature,
        target_pressure,
        problem_name,
        density_seed_mode
    );
}

std::vector<double> pure_saturation_pressure_seed_values() {
    return {
        1.0e-2,
        1.0e-1,
        1.0,
        1.0e1,
        1.0e2,
        1.0e3,
        1.0e4,
        1.0e5,
        1.0e6,
        3.0e6,
        1.0e7,
    };
}

std::vector<NamedInitialVariables> pressure_route_seed_candidates(
    const add_args& args,
    const std::vector<double>& fixed_composition,
    int fixed_phase_index,
    double temperature,
    const std::vector<double>& charges,
    const std::string& problem_name
) {
    std::vector<NamedInitialVariables> out;
    const bool pure_saturation_route =
        problem_name == "single_component_vle_eos" && fixed_composition.size() == 1 && charges.empty();
    const double minimum_vapor_volume =
        pure_saturation_route ? kPureSaturationMinimumVaporVolume : kMinimumVaporVolume;
    const double maximum_vapor_volume =
        pure_saturation_route ? kPureSaturationMaximumVaporVolume : kMaximumVaporVolume;
    const double minimum_phase_volume_gap =
        pure_saturation_route ? kPureSaturationMinimumPhaseVolumeGap : kMinimumPhaseVolumeGap;
    auto append_if_feasible = [&](std::string seed_name, std::vector<double> variables) {
        if (fixed_temperature_pressure_seed_satisfies_volume_bounds(
                variables,
                static_cast<int>(fixed_composition.size()),
                kMinimumLiquidVolume,
                kMaximumLiquidVolume,
                minimum_vapor_volume,
                maximum_vapor_volume,
                minimum_phase_volume_gap
            )) {
            out.push_back({std::move(seed_name), std::move(variables)});
        }
    };
    auto append_density_root_seed = [&](std::string seed_name, double seed_pressure, double shift_sign) {
        try {
            append_if_feasible(
                std::move(seed_name),
                build_pressure_route_initial_variables(
                    args,
                    fixed_composition,
                    fixed_phase_index,
                    temperature,
                    charges,
                    problem_name,
                    shift_sign,
                    DensitySeedMode::PhasePressureRoot,
                    seed_pressure
                )
            );
        } catch (const std::exception&) {
        }
    };
    auto append_separated_phase_seed = [&](std::string seed_name, double seed_pressure, double shift_sign) {
        append_if_feasible(
            std::move(seed_name),
            build_pressure_route_initial_variables(
                args,
                fixed_composition,
                fixed_phase_index,
                temperature,
                charges,
                problem_name,
                shift_sign,
                DensitySeedMode::SeparatedPhaseRole,
                seed_pressure
            )
        );
    };
    if (charges.empty()) {
        if (pure_saturation_route) {
            int seed_index = 0;
            for (double seed_pressure : pure_saturation_pressure_seed_values()) {
                append_density_root_seed(
                    "pressure_density_root_" + std::to_string(seed_index),
                    seed_pressure,
                    1.0
                );
                append_density_root_seed(
                    "mirrored_pressure_density_root_" + std::to_string(seed_index),
                    seed_pressure,
                    -1.0
                );
                append_separated_phase_seed(
                    "separated_pressure_role_" + std::to_string(seed_index),
                    seed_pressure,
                    1.0
                );
                append_separated_phase_seed(
                    "mirrored_separated_pressure_role_" + std::to_string(seed_index),
                    seed_pressure,
                    -1.0
                );
                ++seed_index;
            }
        } else {
            append_density_root_seed("canonical_phase_density_root", kInitialPressure, 1.0);
            append_density_root_seed("mirrored_phase_density_root", kInitialPressure, -1.0);
        }
        if (fixed_composition.size() > 1) {
            const std::vector<double> partner = boundary_partner_composition_from_k_values(
                args,
                fixed_composition,
                fixed_phase_index,
                problem_name,
                kBoundaryVolatilityKAlpha
            );
            append_if_feasible(
                "volatility_k_partner_density_root",
                build_pressure_route_initial_variables_with_partner(
                    args,
                    fixed_composition,
                    partner,
                    fixed_phase_index,
                    temperature,
                    problem_name,
                    DensitySeedMode::PhasePressureRoot
                )
            );
        }
    }
    out.push_back({
        "canonical_shifted_partner_phase",
        build_pressure_route_initial_variables(
            args,
            fixed_composition,
            fixed_phase_index,
            temperature,
            charges,
            problem_name,
            1.0,
            DensitySeedMode::SeparatedPhaseRole,
            kInitialPressure
        )
    });
    out.push_back({
        "mirrored_shifted_partner_phase",
        build_pressure_route_initial_variables(
            args,
            fixed_composition,
            fixed_phase_index,
            temperature,
            charges,
            problem_name,
            -1.0,
            DensitySeedMode::SeparatedPhaseRole,
            kInitialPressure
        )
    });
    return out;
}

std::vector<NamedInitialVariables> temperature_route_seed_candidates(
    const add_args& args,
    const std::vector<double>& fixed_composition,
    int fixed_phase_index,
    double target_pressure,
    const std::vector<double>& charges,
    const std::string& problem_name
) {
    std::vector<NamedInitialVariables> out;
    const double minimum_phase1_volume = fixed_pressure_temperature_phase1_minimum_volume(problem_name);
    const double maximum_phase1_volume = fixed_pressure_temperature_phase1_maximum_volume(problem_name);
    const double minimum_phase_volume_gap = fixed_pressure_temperature_minimum_phase_volume_gap(problem_name);
    auto append_if_feasible = [&](std::string seed_name, std::vector<double> variables) {
        if (fixed_temperature_pressure_seed_satisfies_volume_bounds(
                variables,
                static_cast<int>(fixed_composition.size()),
                kMinimumLiquidVolume,
                kMaximumLiquidVolume,
                minimum_phase1_volume,
                maximum_phase1_volume,
                minimum_phase_volume_gap
            )) {
            out.push_back({std::move(seed_name), std::move(variables)});
        }
    };
    append_if_feasible(
        "canonical_phase_density_root",
        build_temperature_route_initial_variables(
            args,
            fixed_composition,
            fixed_phase_index,
            target_pressure,
            charges,
            problem_name,
            1.0,
            DensitySeedMode::PhasePressureRoot
        )
    );
    append_if_feasible(
        "mirrored_phase_density_root",
        build_temperature_route_initial_variables(
            args,
            fixed_composition,
            fixed_phase_index,
            target_pressure,
            charges,
            problem_name,
            -1.0,
            DensitySeedMode::PhasePressureRoot
        )
    );
    if (charges.empty()) {
        const std::vector<double> partner = boundary_partner_composition_from_k_values(
            args,
            fixed_composition,
            fixed_phase_index,
            problem_name,
            kBoundaryVolatilityKAlpha
        );
        append_if_feasible(
            "volatility_k_partner_density_root",
            build_temperature_route_initial_variables_with_partner(
                args,
                fixed_composition,
                partner,
                fixed_phase_index,
                target_pressure,
                problem_name,
                DensitySeedMode::PhasePressureRoot
            )
        );
    }
    out.push_back({
        "canonical_shifted_partner_phase",
        build_temperature_route_initial_variables(
            args,
            fixed_composition,
            fixed_phase_index,
            target_pressure,
            charges,
            problem_name,
            1.0,
            DensitySeedMode::SeparatedPhaseRole
        )
    });
    out.push_back({
        "mirrored_shifted_partner_phase",
        build_temperature_route_initial_variables(
            args,
            fixed_composition,
            fixed_phase_index,
            target_pressure,
            charges,
            problem_name,
            -1.0,
            DensitySeedMode::SeparatedPhaseRole
        )
    });
    return out;
}

std::vector<NamedInitialVariables> flash_route_seed_candidates(
    const add_args& args,
    const std::vector<double>& feed_composition,
    double temperature,
    double target_pressure,
    const std::string& problem_name
) {
    std::vector<NamedInitialVariables> out;
    auto append_if_feasible = [&](std::string seed_name, std::vector<double> variables) {
        if (fixed_temperature_pressure_flash_seed_satisfies_volume_bounds(
                variables,
                static_cast<int>(feed_composition.size())
            )) {
            out.push_back({std::move(seed_name), std::move(variables)});
        }
    };
    try {
        const NeutralPhaseDiscoveryResult discovery = evaluate_neutral_tpd_phase_discovery(
            args,
            temperature,
            target_pressure,
            feed_composition,
            {0, 1},
            1.0e-6,
            1.0e-6,
            false
        );
        if (discovery.phase_set_mass_balance_feasible
            && discovery.selected_phase_compositions.size() == 2
            && discovery.selected_phase_fractions.size() == 2) {
            append_if_feasible(
                "deterministic_tpd_candidate_pair",
                build_flash_route_initial_variables(
                    args,
                    feed_composition,
                    discovery.selected_phase_compositions[0],
                    discovery.selected_phase_compositions[1],
                    discovery.selected_phase_fractions[1],
                    temperature,
                    target_pressure,
                    problem_name
                )
            );
        }
    } catch (const std::exception&) {
    }
    for (double alpha : {1.5, 2.0, 2.5, 3.0}) {
        try {
            append_if_feasible(
                "volatility_ranked_rr_alpha_" + std::to_string(static_cast<int>(10.0 * alpha)),
                build_flash_route_initial_variables_from_k_values(
                    args,
                    feed_composition,
                    volatility_ranked_k_values(args, feed_composition, problem_name, alpha),
                    temperature,
                    target_pressure,
                    problem_name
                )
            );
        } catch (const std::exception&) {
        }
    }
    try {
        append_if_feasible(
            "canonical_shifted_feed_density_root",
            build_shifted_flash_route_initial_variables(
                args,
                feed_composition,
                temperature,
                target_pressure,
                problem_name,
                1.0,
                DensitySeedMode::PhasePressureRoot
            )
        );
    } catch (const std::exception&) {
    }
    try {
        append_if_feasible(
            "mirrored_shifted_feed_density_root",
            build_shifted_flash_route_initial_variables(
                args,
                feed_composition,
                temperature,
                target_pressure,
                problem_name,
                -1.0,
                DensitySeedMode::PhasePressureRoot
            )
        );
    } catch (const std::exception&) {
    }
    try {
        append_if_feasible(
            "canonical_shifted_feed_phase_role",
            build_shifted_flash_route_initial_variables(
                args,
                feed_composition,
                temperature,
                target_pressure,
                problem_name,
                1.0,
                DensitySeedMode::SeparatedPhaseRole
            )
        );
    } catch (const std::exception&) {
    }
    try {
        append_if_feasible(
            "mirrored_shifted_feed_phase_role",
            build_shifted_flash_route_initial_variables(
                args,
                feed_composition,
                temperature,
                target_pressure,
                problem_name,
                -1.0,
                DensitySeedMode::SeparatedPhaseRole
            )
        );
    } catch (const std::exception&) {
    }
    return out;
}

std::vector<std::vector<double>> pressure_route_phase_amounts(
    const std::vector<double>& variables,
    int species_count
) {
    const int local_variable_count = species_count + 1;
    require_size(
        variables,
        static_cast<std::size_t>(2 * local_variable_count + 1),
        "fixed-temperature pressure route variable"
    );
    std::vector<std::vector<double>> phase_amounts(2, std::vector<double>(static_cast<std::size_t>(species_count)));
    for (int phase = 0; phase < 2; ++phase) {
        const int offset = phase * local_variable_count;
        for (int species = 0; species < species_count; ++species) {
            phase_amounts[static_cast<std::size_t>(phase)][static_cast<std::size_t>(species)] =
                variables[static_cast<std::size_t>(offset + species)];
        }
    }
    return phase_amounts;
}

std::vector<double> pressure_route_phase_volumes(const std::vector<double>& variables, int species_count) {
    const int local_variable_count = species_count + 1;
    require_size(
        variables,
        static_cast<std::size_t>(2 * local_variable_count + 1),
        "fixed-temperature pressure route variable"
    );
    return {
        variables[static_cast<std::size_t>(species_count)],
        variables[static_cast<std::size_t>(local_variable_count + species_count)]
    };
}

std::vector<std::vector<double>> flash_route_phase_amounts(
    const std::vector<double>& variables,
    int species_count
) {
    const int local_variable_count = species_count + 1;
    require_size(
        variables,
        static_cast<std::size_t>(2 * local_variable_count),
        "fixed-temperature pressure flash variable"
    );
    std::vector<std::vector<double>> phase_amounts(2, std::vector<double>(static_cast<std::size_t>(species_count)));
    for (int phase = 0; phase < 2; ++phase) {
        const int offset = phase * local_variable_count;
        for (int species = 0; species < species_count; ++species) {
            phase_amounts[static_cast<std::size_t>(phase)][static_cast<std::size_t>(species)] =
                variables[static_cast<std::size_t>(offset + species)];
        }
    }
    return phase_amounts;
}

std::vector<double> flash_route_phase_volumes(const std::vector<double>& variables, int species_count) {
    const int local_variable_count = species_count + 1;
    require_size(
        variables,
        static_cast<std::size_t>(2 * local_variable_count),
        "fixed-temperature pressure flash variable"
    );
    return {
        variables[static_cast<std::size_t>(species_count)],
        variables[static_cast<std::size_t>(local_variable_count + species_count)]
    };
}

std::vector<double> summed_feed_amounts(const std::vector<std::vector<double>>& phase_amounts, int species_count) {
    std::vector<double> feed_amounts(static_cast<std::size_t>(species_count), 0.0);
    for (const auto& phase : phase_amounts) {
        require_size(phase, static_cast<std::size_t>(species_count), "fixed-temperature pressure phase amount");
        for (int species = 0; species < species_count; ++species) {
            feed_amounts[static_cast<std::size_t>(species)] += phase[static_cast<std::size_t>(species)];
        }
    }
    return feed_amounts;
}

double fixed_composition_norm(
    const std::vector<std::vector<double>>& phase_amounts,
    int fixed_phase_index,
    const std::vector<double>& fixed_composition
) {
    const auto& fixed_amounts = phase_amounts[static_cast<std::size_t>(fixed_phase_index)];
    const double total = std::accumulate(fixed_amounts.begin(), fixed_amounts.end(), 0.0);
    require_positive_finite(total, "fixed-temperature pressure fixed-phase amount total");
    double norm = 0.0;
    for (std::size_t species = 0; species < fixed_composition.size(); ++species) {
        norm = std::max(norm, std::abs(fixed_amounts[species] / total - fixed_composition[species]));
    }
    return norm;
}

double phase_total_norm(const std::vector<std::vector<double>>& phase_amounts) {
    double norm = 0.0;
    for (const auto& phase : phase_amounts) {
        const double total = std::accumulate(phase.begin(), phase.end(), 0.0);
        norm = std::max(norm, std::abs(total - 1.0));
    }
    return norm;
}

double phase_charge_norm(
    const std::vector<std::vector<double>>& phase_amounts,
    const std::vector<double>& charges
) {
    if (charges.empty()) {
        return 0.0;
    }
    double norm = 0.0;
    for (const auto& phase : phase_amounts) {
        require_size(phase, charges.size(), "fixed-temperature pressure charge-balance phase amount");
        double phase_charge = 0.0;
        for (std::size_t species = 0; species < charges.size(); ++species) {
            phase_charge += phase[species] * charges[species];
        }
        norm = std::max(norm, std::abs(phase_charge));
    }
    return norm;
}

bool route_has_active_association_sites(const add_args& args) {
    for (int sites : args.assoc_num) {
        if (sites > 0) {
            return true;
        }
    }
    return false;
}

bool route_close_to(double actual, double expected, double tolerance = 1.0e-10) {
    return std::isfinite(actual) && std::abs(actual - expected) <= tolerance;
}

bool route_vector_close_to(
    const std::vector<double>& values,
    const std::vector<double>& expected,
    double tolerance = 1.0e-10
) {
    if (values.size() != expected.size()) {
        return false;
    }
    for (std::size_t index = 0; index < expected.size(); ++index) {
        if (!route_close_to(values[index], expected[index], tolerance)) {
            return false;
        }
    }
    return true;
}

bool route_contains_text(const std::vector<std::string>& values, const std::string& expected) {
    return std::find(values.begin(), values.end(), expected) != values.end();
}

bool route_all_zero_or_empty(const std::vector<double>& values) {
    return std::all_of(values.begin(), values.end(), [](double value) {
        return std::isfinite(value) && std::abs(value) <= 1.0e-12;
    });
}

bool route_has_gross_2002_associating_vle_case(
    const add_args& args,
    const char* source_label,
    const std::vector<double>& expected_m,
    const std::vector<double>& expected_s,
    const std::vector<double>& expected_e,
    const std::vector<double>& expected_e_assoc,
    const std::vector<double>& expected_vol_a,
    const std::vector<int>& expected_assoc_num,
    const std::vector<double>& expected_assoc_matrix,
    const std::vector<double>& expected_kij
) {
    if (args.parameter_source_label != source_label) {
        return false;
    }
    if (args.parameter_provenance_status != "source_backed_parameter_metadata"
        || args.binary_interaction_provenance_status != "explicit_binary_records") {
        return false;
    }
    if (
        !route_contains_text(args.parameter_provenance_fields, "source")
        || !route_contains_text(args.parameter_provenance_fields, "paper")
        || !route_contains_text(args.parameter_provenance_fields, "table")
        || !route_contains_text(args.parameter_provenance_fields, "figure")
        || !route_contains_text(args.parameter_provenance_fields, "source_path")
    ) {
        return false;
    }
    if (!route_vector_close_to(args.m, expected_m)
        || !route_vector_close_to(args.s, expected_s)
        || !route_vector_close_to(args.e, expected_e)
        || !route_vector_close_to(args.e_assoc, expected_e_assoc)
        || !route_vector_close_to(args.vol_a, expected_vol_a)
        || args.assoc_num != expected_assoc_num
        || !route_vector_close_to(
            std::vector<double>(args.assoc_matrix.begin(), args.assoc_matrix.end()),
            expected_assoc_matrix,
            1.0e-12
        )) {
        return false;
    }
    if (args.k_ij.size() != 4
        || !route_close_to(args.k_ij[0], 0.0, 1.0e-12)
        || !route_close_to(args.k_ij[1], expected_kij[1], 1.0e-12)
        || !route_close_to(args.k_ij[2], expected_kij[2], 1.0e-12)
        || !route_close_to(args.k_ij[3], 0.0, 1.0e-12)) {
        return false;
    }
    const bool zero_or_empty_fsolv = route_all_zero_or_empty(args.f_solv)
        || route_vector_close_to(args.f_solv, {1.0, 1.0}, 1.0e-12);
    return route_all_zero_or_empty(args.z)
        && route_all_zero_or_empty(args.k_hb)
        && route_all_zero_or_empty(args.l_ij)
        && route_all_zero_or_empty(args.d_born)
        && zero_or_empty_fsolv;
}

bool route_has_gross_2002_associating_vle_proof(const add_args& args) {
    return route_has_gross_2002_associating_vle_case(
               args,
               "Gross/Sadowski 2002 Figure 2",
               {1.5255, 2.2616},
               {3.2300, 3.7574},
               {188.90, 216.53},
               {2899.5, 0.0},
               {0.035176, 0.0},
               {2, 0},
               {0.0, 1.0, 1.0, 0.0},
               {0.0, 0.05, 0.05, 0.0}
           )
        || route_has_gross_2002_associating_vle_case(
            args,
            "Gross/Sadowski 2002 Figure 3",
            {2.9997, 3.0799},
            {3.2522, 3.7974},
            {233.40, 287.35},
            {2276.8, 0.0},
            {0.015268, 0.0},
            {2, 0},
            {0.0, 1.0, 1.0, 0.0},
            {0.0, 0.023, 0.023, 0.0}
        )
        || route_has_gross_2002_associating_vle_case(
            args,
            "Gross/Sadowski 2002 Figure 4",
            {3.6260, 2.4653},
            {3.4508, 3.6478},
            {247.28, 287.35},
            {2252.1, 0.0},
            {0.010319, 0.0},
            {2, 0},
            {0.0, 1.0, 1.0, 0.0},
            {0.0, 0.0135, 0.0135, 0.0}
        )
        || route_has_gross_2002_associating_vle_case(
               args,
               "Gross/Sadowski 2002 Figure 5",
               {2.9997, 2.4653},
               {3.2522, 3.6478},
               {233.40, 287.35},
               {2276.8, 0.0},
               {0.015268, 0.0},
               {2, 0},
               {0.0, 1.0, 1.0, 0.0},
               {0.0, 0.020, 0.020, 0.0}
           )
        || route_has_gross_2002_associating_vle_case(
            args,
            "Gross/Sadowski 2002 Figure 5",
            {3.0929, 2.4653},
            {3.2085, 3.6478},
            {208.42, 287.35},
            {2253.9, 0.0},
            {0.024675, 0.0},
            {2, 0},
            {0.0, 1.0, 1.0, 0.0},
            {0.0, 0.021, 0.021, 0.0}
        )
        || route_has_gross_2002_associating_vle_case(
            args,
            "Gross/Sadowski 2002 Figure 6",
            {2.7515, 2.3316},
            {3.6139, 3.7086},
            {259.59, 222.88},
            {2544.6, 0.0},
            {0.006692, 0.0},
            {2, 0},
            {0.0, 1.0, 1.0, 0.0},
            {0.0, 0.015, 0.015, 0.0}
        )
        || route_has_gross_2002_associating_vle_case(
            args,
            "Gross/Sadowski 2002 Figure 7",
            {2.3827, 2.3316},
            {3.1771, 3.7086},
            {198.24, 222.88},
            {2653.4, 0.0},
            {0.032384, 0.0},
            {2, 0},
            {0.0, 1.0, 1.0, 0.0},
            {0.0, 0.028, 0.028, 0.0}
        )
        || route_has_gross_2002_associating_vle_case(
            args,
            "Gross/Sadowski 2002 Figure 8",
            {1.5255, 2.5303},
            {3.2300, 3.8499},
            {188.90, 278.11},
            {2899.5, 0.0},
            {0.035176, 0.0},
            {2, 0},
            {0.0, 1.0, 1.0, 0.0},
            {0.0, 0.051, 0.051, 0.0}
        )
        || route_has_gross_2002_associating_vle_case(
            args,
            "Gross/Sadowski 2002 Figure 9",
            {1.5255, 4.3555},
            {3.2300, 3.7145},
            {188.90, 262.74},
            {2899.5, 2754.8},
            {0.035176, 0.002197},
            {2, 2},
            {0.0, 1.0, 0.0, 1.0, 1.0, 0.0, 1.0, 0.0, 0.0, 1.0, 0.0, 1.0, 1.0, 0.0, 1.0, 0.0},
            {0.0, 0.020, 0.020, 0.0}
        )
        || route_has_gross_2002_associating_vle_case(
            args,
            "Gross/Sadowski 2002 Figure 10",
            {1.0656, 3.6260},
            {3.0007, 3.4508},
            {366.51, 247.28},
            {2500.7, 2252.1},
            {0.034868, 0.010319},
            {2, 2},
            {0.0, 1.0, 0.0, 1.0, 1.0, 0.0, 1.0, 0.0, 0.0, 1.0, 0.0, 1.0, 1.0, 0.0, 1.0, 0.0},
            {0.0, 0.016, 0.016, 0.0}
        );
}

bool route_supports_exact_phase_derivatives(const add_args& args, const std::string& problem_name) {
    if (problem_name == "electrolyte_bubble_t_eos") {
        return true;
    }
    if (!(args.z.empty() || args.born_model <= 1)) {
        return false;
    }
    if (!route_has_active_association_sites(args)) {
        return true;
    }
    if (
        (problem_name == "neutral_bubble_p_eos" || problem_name == "neutral_dew_p_eos")
        && route_has_gross_2002_associating_vle_proof(args)
    ) {
        return true;
    }
    return problem_name == "single_component_vle_eos" && args.m.size() == 1;
}

class NeutralFixedTemperaturePressureProblem final : public NlpProblem {
public:
    NeutralFixedTemperaturePressureProblem(
        add_args args,
        double temperature,
        std::vector<double> fixed_composition,
        int fixed_phase_index,
        std::string problem_name,
        std::vector<double> charges = {},
        double charge_constraint_tolerance = 0.0,
        double initial_pressure = kInitialPressure
    )
        : args_(std::move(args)),
          temperature_(temperature),
          fixed_composition_(normalized_positive_values(fixed_composition, problem_name + " composition")),
          fixed_phase_index_(fixed_phase_index),
          problem_name_(std::move(problem_name)),
          charges_(std::move(charges)),
          charge_constraint_tolerance_(charge_constraint_tolerance),
          initial_pressure_(initial_pressure) {
        require_positive_finite(temperature_, problem_name_ + " temperature");
        require_positive_finite(initial_pressure_, problem_name_ + " initial pressure");
        if (!std::isfinite(charge_constraint_tolerance_) || charge_constraint_tolerance_ < 0.0) {
            throw ValueError(problem_name_ + " charge constraint tolerance must be finite and non-negative.");
        }
        if (fixed_phase_index_ < 0 || fixed_phase_index_ >= phase_count()) {
            throw ValueError(problem_name_ + " fixed phase index is out of range.");
        }
        species_count_ = static_cast<int>(fixed_composition_.size());
        minimum_vapor_volume_ = kMinimumLiquidVolume;
        if (!charges_.empty()) {
            charge_neutral_shifted_composition(
                fixed_composition_,
                charges_,
                problem_name_ + " fixed composition"
            );
        }
        if (problem_name_ == "single_component_vle_eos" && species_count_ == 1 && charges_.empty()) {
            minimum_vapor_volume_ = kPureSaturationMinimumVaporVolume;
            maximum_vapor_volume_ = kPureSaturationMaximumVaporVolume;
            minimum_pressure_ = kPureSaturationMinimumPressure;
            minimum_phase_volume_gap_ = kPureSaturationMinimumPhaseVolumeGap;
        }
    }

    std::string name() const override {
        return problem_name_;
    }

    int variable_count() const override {
        return phase_count() * local_variable_count() + 1;
    }

    int constraint_count() const override {
        return composition_constraint_count() + 2 * phase_count() + species_count_ + 1
            + charge_constraint_count();
    }

    int jacobian_nonzero_count() const override {
        const int composition_nonzeros = composition_constraint_count() * species_count_;
        const int phase_total_nonzeros = phase_count() * species_count_;
        int charge_nonzeros = 0;
        for (double charge : charges_) {
            if (charge != 0.0) {
                charge_nonzeros += phase_count();
            }
        }
        const int pressure_nonzeros = phase_count() * (local_variable_count() + 1);
        const int chemical_nonzeros = species_count_ * phase_count() * local_variable_count();
        const int gap_nonzeros = 2;
        return composition_nonzeros + phase_total_nonzeros + charge_nonzeros + pressure_nonzeros + chemical_nonzeros
            + gap_nonzeros;
    }

    NlpBounds bounds() const override {
        NlpBounds out;
        out.variable_lower.reserve(static_cast<std::size_t>(variable_count()));
        out.variable_upper.reserve(static_cast<std::size_t>(variable_count()));
        for (int phase = 0; phase < phase_count(); ++phase) {
            for (int species = 0; species < species_count_; ++species) {
                out.variable_lower.push_back(1.0e-14);
                out.variable_upper.push_back(10.0);
            }
            if (phase == liquid_phase_index()) {
                out.variable_lower.push_back(minimum_liquid_volume_);
                out.variable_upper.push_back(maximum_liquid_volume_);
            } else if (phase == vapor_phase_index()) {
                out.variable_lower.push_back(minimum_vapor_volume_);
                out.variable_upper.push_back(maximum_vapor_volume_);
            } else {
                throw ValueError(problem_name_ + " phase role is out of range.");
            }
        }
        out.variable_lower.push_back(minimum_pressure_);
        out.variable_upper.push_back(maximum_pressure_);
        out.constraint_lower.assign(static_cast<std::size_t>(constraint_count()), 0.0);
        out.constraint_upper.assign(static_cast<std::size_t>(constraint_count()), 0.0);
        if (charge_constraint_count() > 0 && charge_constraint_tolerance_ > 0.0) {
            const int charge_row_start = composition_constraint_count() + phase_count();
            for (int phase = 0; phase < charge_constraint_count(); ++phase) {
                out.constraint_lower[static_cast<std::size_t>(charge_row_start + phase)] =
                    -charge_constraint_tolerance_;
                out.constraint_upper[static_cast<std::size_t>(charge_row_start + phase)] =
                    charge_constraint_tolerance_;
            }
        }
        out.constraint_lower.back() = minimum_phase_volume_gap_;
        out.constraint_upper.back() = 1.0e12;
        return out;
    }

    std::vector<double> initial_point() const override {
        if (charges_.empty()) {
            const std::vector<double> root = build_pressure_route_initial_variables(
                args_,
                fixed_composition_,
                fixed_phase_index_,
                temperature_,
                charges_,
                problem_name_,
                1.0,
                DensitySeedMode::PhasePressureRoot,
                initial_pressure_
            );
            if (fixed_temperature_pressure_seed_satisfies_volume_bounds(
                    root,
                    species_count_,
                    minimum_liquid_volume_,
                    maximum_liquid_volume_,
                    minimum_vapor_volume_,
                    maximum_vapor_volume_,
                    minimum_phase_volume_gap_
                )) {
                return root;
            }
        }
        return build_pressure_route_initial_variables(
            args_,
            fixed_composition_,
            fixed_phase_index_,
            temperature_,
            charges_,
            problem_name_,
            1.0,
            DensitySeedMode::SeparatedPhaseRole,
            initial_pressure_
        );
    }

    double objective(const std::vector<double>& variables) const override {
        double value = 0.0;
        for (const EosPhaseBlockResult& block : phase_blocks(variables)) {
            value += block.objective;
        }
        return value;
    }

    std::vector<double> objective_gradient(const std::vector<double>& variables) const override {
        std::vector<double> out;
        out.reserve(static_cast<std::size_t>(variable_count()));
        double pressure_derivative = 0.0;
        for (const EosPhaseBlockResult& block : phase_blocks(variables)) {
            out.insert(out.end(), block.gradient.begin(), block.gradient.end());
            pressure_derivative += block.volume / block.gas_constant_temperature;
        }
        out.push_back(pressure_derivative);
        return out;
    }

    std::vector<double> constraints(const std::vector<double>& variables) const override {
        const auto amounts = pressure_route_phase_amounts(variables, species_count_);
        std::vector<double> out(static_cast<std::size_t>(constraint_count()), 0.0);
        int row = 0;
        const auto& fixed_amounts = amounts[static_cast<std::size_t>(fixed_phase_index_)];
        const double fixed_total = std::accumulate(fixed_amounts.begin(), fixed_amounts.end(), 0.0);
        for (int species = 0; species < composition_constraint_count(); ++species) {
            out[static_cast<std::size_t>(row++)] =
                fixed_amounts[static_cast<std::size_t>(species)]
                - fixed_composition_[static_cast<std::size_t>(species)] * fixed_total;
        }
        for (int phase = 0; phase < phase_count(); ++phase) {
            const auto& phase_amounts = amounts[static_cast<std::size_t>(phase)];
            out[static_cast<std::size_t>(row++)] =
                std::accumulate(phase_amounts.begin(), phase_amounts.end(), 0.0) - 1.0;
        }
        for (int phase = 0; phase < charge_constraint_count(); ++phase) {
            const auto& phase_amounts = amounts[static_cast<std::size_t>(phase)];
            double phase_charge = 0.0;
            for (int species = 0; species < species_count_; ++species) {
                phase_charge += phase_amounts[static_cast<std::size_t>(species)]
                    * charges_[static_cast<std::size_t>(species)];
            }
            out[static_cast<std::size_t>(row++)] = phase_charge;
        }
        const auto blocks = phase_blocks(variables);
        for (const EosPhaseBlockResult& block : blocks) {
            out[static_cast<std::size_t>(row++)] = block.pressure_consistency_residual;
        }
        for (int species = 0; species < species_count_; ++species) {
            out[static_cast<std::size_t>(row++)] =
                blocks[0].gradient[static_cast<std::size_t>(species)]
                - blocks[1].gradient[static_cast<std::size_t>(species)];
        }
        out[static_cast<std::size_t>(row++)] =
            variables[static_cast<std::size_t>(vapor_volume_col())]
            - variables[static_cast<std::size_t>(liquid_volume_col())];
        return out;
    }

    NlpJacobianStructure jacobian_structure() const override {
        NlpJacobianStructure out;
        out.rows.reserve(static_cast<std::size_t>(jacobian_nonzero_count()));
        out.cols.reserve(static_cast<std::size_t>(jacobian_nonzero_count()));
        int row = 0;
        for (int species = 0; species < composition_constraint_count(); ++species) {
            for (int col = 0; col < species_count_; ++col) {
                out.rows.push_back(row);
                out.cols.push_back(fixed_col(col));
            }
            ++row;
        }
        for (int phase = 0; phase < phase_count(); ++phase) {
            const int offset = phase * local_variable_count();
            for (int species = 0; species < species_count_; ++species) {
                out.rows.push_back(row);
                out.cols.push_back(offset + species);
            }
            ++row;
        }
        for (int phase = 0; phase < charge_constraint_count(); ++phase) {
            const int offset = phase * local_variable_count();
            for (int species = 0; species < species_count_; ++species) {
                if (charges_[static_cast<std::size_t>(species)] == 0.0) {
                    continue;
                }
                out.rows.push_back(row);
                out.cols.push_back(offset + species);
            }
            ++row;
        }
        for (int phase = 0; phase < phase_count(); ++phase) {
            const int offset = phase * local_variable_count();
            for (int col = 0; col < local_variable_count(); ++col) {
                out.rows.push_back(row);
                out.cols.push_back(offset + col);
            }
            out.rows.push_back(row);
            out.cols.push_back(variable_count() - 1);
            ++row;
        }
        for (int species = 0; species < species_count_; ++species) {
            for (int phase = 0; phase < phase_count(); ++phase) {
                const int offset = phase * local_variable_count();
                for (int col = 0; col < local_variable_count(); ++col) {
                    out.rows.push_back(row);
                    out.cols.push_back(offset + col);
                }
            }
            ++row;
        }
        out.rows.push_back(row);
        out.cols.push_back(liquid_volume_col());
        out.rows.push_back(row);
        out.cols.push_back(vapor_volume_col());
        return out;
    }

    std::vector<double> jacobian_values(const std::vector<double>& variables) const override {
        const auto blocks = phase_blocks(variables);
        std::vector<double> out;
        out.reserve(static_cast<std::size_t>(jacobian_nonzero_count()));
        int row = 0;
        for (int species = 0; species < composition_constraint_count(); ++species) {
            for (int col = 0; col < species_count_; ++col) {
                out.push_back((col == species ? 1.0 : 0.0) - fixed_composition_[static_cast<std::size_t>(species)]);
            }
            ++row;
        }
        for (int phase = 0; phase < phase_count(); ++phase) {
            for (int species = 0; species < species_count_; ++species) {
                out.push_back(1.0);
            }
            ++row;
        }
        for (int phase = 0; phase < charge_constraint_count(); ++phase) {
            for (int species = 0; species < species_count_; ++species) {
                const double charge = charges_[static_cast<std::size_t>(species)];
                if (charge == 0.0) {
                    continue;
                }
                out.push_back(charge);
            }
            ++row;
        }
        for (int phase = 0; phase < phase_count(); ++phase) {
            const EosPhaseBlockResult& block = blocks[static_cast<std::size_t>(phase)];
            if (block.pressure_jacobian_row_major.size() != static_cast<std::size_t>(local_variable_count())) {
                throw ValueError(problem_name_ + " pressure Jacobian size did not match variables.");
            }
            for (int col = 0; col < local_variable_count(); ++col) {
                out.push_back(block.pressure_jacobian_row_major[static_cast<std::size_t>(col)]);
            }
            out.push_back(-1.0);
            ++row;
        }
        for (int species = 0; species < species_count_; ++species) {
            for (int phase = 0; phase < phase_count(); ++phase) {
                const EosPhaseBlockResult& block = blocks[static_cast<std::size_t>(phase)];
                if (block.objective_curvature_rows != local_variable_count()
                    || block.objective_curvature_cols != local_variable_count()
                    || block.objective_curvature_row_major.size()
                        != static_cast<std::size_t>(local_variable_count() * local_variable_count())) {
                    throw ValueError(problem_name_ + " chemical-potential Jacobian size did not match variables.");
                }
                for (int col = 0; col < local_variable_count(); ++col) {
                    out.push_back((phase == 0 ? 1.0 : -1.0) * block.objective_curvature_row_major[
                            static_cast<std::size_t>(species * local_variable_count() + col)
                        ]);
                }
            }
            ++row;
        }
        out.push_back(-1.0);
        out.push_back(1.0);
        return out;
    }

    bool has_exact_hessian() const override {
        return route_supports_exact_phase_derivatives(args_, problem_name_);
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
            throw ValueError(problem_name_ + " exact Hessian requires direct non-associating phase derivatives.");
        }
        if (constraint_multipliers.size() != static_cast<std::size_t>(constraint_count())) {
            throw ValueError(problem_name_ + " Hessian multiplier vector size does not match the constraint count.");
        }

        const auto blocks = phase_blocks(variables);
        const int n = variable_count();
        ObjectiveSecondOrderData objective;
        objective.variable_count = n;
        objective.value = 0.0;
        objective.gradient.assign(static_cast<std::size_t>(n), 0.0);
        objective.hessian_row_major.assign(static_cast<std::size_t>(n * n), 0.0);
        objective.backend = "cppad_phase_pressure_route";
        const int pressure_col = n - 1;
        for (int phase = 0; phase < phase_count(); ++phase) {
            const EosPhaseBlockResult& block = blocks[static_cast<std::size_t>(phase)];
            require_square_block(
                block.objective_curvature_row_major,
                local_variable_count(),
                problem_name_ + " objective Hessian block"
            );
            require_third_derivative_tensor(
                block.objective_third_derivative_tensor_row_major,
                local_variable_count(),
                problem_name_ + " objective third-derivative tensor"
            );
            const std::vector<int> phase_indices =
                fixed_temperature_global_indices(phase, local_variable_count());
            objective.value += block.objective;
            for (int local = 0; local < local_variable_count(); ++local) {
                objective.gradient[static_cast<std::size_t>(phase_indices[static_cast<std::size_t>(local)])] =
                    block.gradient[static_cast<std::size_t>(local)];
            }
            objective.gradient[static_cast<std::size_t>(pressure_col)] +=
                block.volume / block.gas_constant_temperature;
            add_local_hessian_to_dense(
                objective.hessian_row_major,
                n,
                phase_indices,
                block.objective_curvature_row_major,
                1.0,
                problem_name_ + " objective Hessian block"
            );
            const int phase_volume_col = phase * local_variable_count() + species_count_;
            const double pressure_volume_cross = 1.0 / block.gas_constant_temperature;
            objective.hessian_row_major[
                static_cast<std::size_t>(phase_volume_col * n + pressure_col)
            ] += pressure_volume_cross;
            objective.hessian_row_major[
                static_cast<std::size_t>(pressure_col * n + phase_volume_col)
            ] += pressure_volume_cross;
        }

        ConstraintSecondOrderData constraints_data;
        constraints_data.constraint_count = constraint_count();
        constraints_data.variable_count = n;
        constraints_data.values = this->constraints(variables);
        constraints_data.hessian_tensor_row_major.assign(
            static_cast<std::size_t>(constraint_count() * n * n),
            0.0
        );
        constraints_data.has_hessian.assign(static_cast<std::size_t>(constraint_count()), false);
        constraints_data.backend = "cppad_phase_pressure_route";

        const int pressure_row_start =
            composition_constraint_count() + phase_count() + charge_constraint_count();
        for (int phase = 0; phase < phase_count(); ++phase) {
            const EosPhaseBlockResult& block = blocks[static_cast<std::size_t>(phase)];
            require_square_block(
                block.pressure_hessian_row_major,
                local_variable_count(),
                problem_name_ + " pressure Hessian block"
            );
            const int constraint_row = pressure_row_start + phase;
            constraints_data.has_hessian[static_cast<std::size_t>(constraint_row)] = true;
            add_local_hessian_to_constraint_tensor(
                constraints_data.hessian_tensor_row_major,
                constraint_row,
                n,
                fixed_temperature_global_indices(phase, local_variable_count()),
                block.pressure_hessian_row_major,
                1.0,
                problem_name_ + " pressure Hessian block"
            );
        }

        const int chemical_row_start = pressure_row_start + phase_count();
        for (int species = 0; species < species_count_; ++species) {
            const int constraint_row = chemical_row_start + species;
            constraints_data.has_hessian[static_cast<std::size_t>(constraint_row)] = true;
            for (int phase = 0; phase < phase_count(); ++phase) {
                const EosPhaseBlockResult& block = blocks[static_cast<std::size_t>(phase)];
                const std::vector<double> chemical_hessian = third_derivative_slice(
                    block.objective_third_derivative_tensor_row_major,
                    species,
                    local_variable_count(),
                    problem_name_ + " chemical-potential Hessian block"
                );
                add_local_hessian_to_constraint_tensor(
                    constraints_data.hessian_tensor_row_major,
                    constraint_row,
                    n,
                    fixed_temperature_global_indices(phase, local_variable_count()),
                    chemical_hessian,
                    phase == 0 ? 1.0 : -1.0,
                    problem_name_ + " chemical-potential Hessian block"
                );
            }
        }

        return LagrangianHessianAssembler(n).values(
            objective_factor,
            objective,
            constraints_data,
            constraint_multipliers
        );
    }

    std::string hessian_backend() const override {
        return "cppad_phase_pressure_route";
    }

    NlpScaling scaling() const override {
        NlpScaling out;
        out.objective = 1.0;
        out.variables.assign(static_cast<std::size_t>(variable_count()), 1.0);
        out.variables.back() = pressure_constraint_scale(initial_pressure_);
        out.constraints.assign(static_cast<std::size_t>(constraint_count()), 1.0);
        apply_pressure_constraint_scaling(
            out,
            composition_constraint_count() + phase_count() + charge_constraint_count(),
            phase_count(),
            initial_pressure_
        );
        return out;
    }

    std::map<std::string, std::string> diagnostics() const override {
        return route_metadata_diagnostics(fixed_temperature_pressure_route_metadata(!charges_.empty()));
    }

    int species_count() const {
        return species_count_;
    }

    int phase_count() const {
        return 2;
    }

private:
    int local_variable_count() const {
        return species_count_ + 1;
    }

    int composition_constraint_count() const {
        return std::max(0, species_count_ - 1);
    }

    int charge_constraint_count() const {
        return charges_.empty() ? 0 : phase_count();
    }

    int fixed_col(int species) const {
        return fixed_phase_index_ * local_variable_count() + species;
    }

    int liquid_phase_index() const {
        return 0;
    }

    int vapor_phase_index() const {
        return 1;
    }

    int liquid_volume_col() const {
        return liquid_phase_index() * local_variable_count() + species_count_;
    }

    int vapor_volume_col() const {
        return vapor_phase_index() * local_variable_count() + species_count_;
    }

    std::vector<EosPhaseBlockResult> phase_blocks(const std::vector<double>& variables) const {
        require_size(variables, static_cast<std::size_t>(variable_count()), problem_name_ + " variable");
        const double pressure = variables.back();
        require_positive_finite(pressure, problem_name_ + " pressure");
        const auto amounts = pressure_route_phase_amounts(variables, species_count_);
        const auto volumes = pressure_route_phase_volumes(variables, species_count_);
        std::vector<EosPhaseBlockResult> blocks;
        blocks.reserve(static_cast<std::size_t>(phase_count()));
        for (int phase = 0; phase < phase_count(); ++phase) {
            blocks.push_back(
                evaluate_eos_phase_block(
                    args_,
                    temperature_,
                    pressure,
                    amounts[static_cast<std::size_t>(phase)],
                    volumes[static_cast<std::size_t>(phase)]
                )
            );
        }
        return blocks;
    }

    add_args args_;
    double temperature_ = 0.0;
    double initial_pressure_ = 1.0e5;
    double minimum_liquid_volume_ = kMinimumLiquidVolume;
    double maximum_liquid_volume_ = kMaximumLiquidVolume;
    double minimum_vapor_volume_ = kMinimumVaporVolume;
    double maximum_vapor_volume_ = kMaximumVaporVolume;
    double minimum_phase_volume_gap_ = kMinimumPhaseVolumeGap;
    double minimum_pressure_ = kMinimumPressure;
    double maximum_pressure_ = kMaximumPressure;
    std::vector<double> fixed_composition_;
    int fixed_phase_index_ = 0;
    std::string problem_name_;
    std::vector<double> charges_;
    double charge_constraint_tolerance_ = 0.0;
    int species_count_ = 0;
};

class NeutralFixedPressureTemperatureProblem final : public NlpProblem {
public:
    NeutralFixedPressureTemperatureProblem(
        add_args args,
        double target_pressure,
        std::vector<double> fixed_composition,
        int fixed_phase_index,
        std::string problem_name,
        std::vector<double> charges = {},
        double charge_constraint_tolerance = 0.0
    )
        : args_(std::move(args)),
          target_pressure_(target_pressure),
          fixed_composition_(normalized_positive_values(fixed_composition, problem_name + " composition")),
          fixed_phase_index_(fixed_phase_index),
          problem_name_(std::move(problem_name)),
          charges_(std::move(charges)),
          charge_constraint_tolerance_(charge_constraint_tolerance) {
        require_positive_finite(target_pressure_, problem_name_ + " pressure");
        if (!std::isfinite(charge_constraint_tolerance_) || charge_constraint_tolerance_ < 0.0) {
            throw ValueError(problem_name_ + " charge constraint tolerance must be finite and non-negative.");
        }
        if (fixed_phase_index_ < 0 || fixed_phase_index_ >= phase_count()) {
            throw ValueError(problem_name_ + " fixed phase index is out of range.");
        }
        minimum_vapor_volume_ = fixed_pressure_temperature_phase1_minimum_volume(problem_name_);
        maximum_vapor_volume_ = fixed_pressure_temperature_phase1_maximum_volume(problem_name_);
        minimum_phase_volume_gap_ = fixed_pressure_temperature_minimum_phase_volume_gap(problem_name_);
        species_count_ = static_cast<int>(fixed_composition_.size());
        if (!charges_.empty()) {
            minimum_temperature_ = 250.0;
            maximum_temperature_ = 650.0;
            require_size(charges_, fixed_composition_.size(), problem_name_ + " charge vector");
            double fixed_charge = 0.0;
            std::vector<int> cation_indices;
            std::vector<int> anion_indices;
            for (int species = 0; species < species_count_; ++species) {
                fixed_charge += fixed_composition_[static_cast<std::size_t>(species)]
                    * charges_[static_cast<std::size_t>(species)];
                const double charge = charges_[static_cast<std::size_t>(species)];
                if (std::abs(charge) <= 1.0e-12) {
                    neutral_species_indices_.push_back(species);
                } else if (charge > 0.0) {
                    cation_indices.push_back(species);
                } else {
                    anion_indices.push_back(species);
                }
            }
            if (std::abs(fixed_charge) > std::max(1.0e-14, charge_constraint_tolerance_)) {
                throw ValueError(problem_name_ + " fixed composition must be charge neutral.");
            }
            if (cation_indices.empty() || anion_indices.empty()) {
                throw ValueError(problem_name_ + " requires active cations and anions.");
            }
            auto sort_by_fixed_composition = [&](std::vector<int>& indices) {
                std::sort(indices.begin(), indices.end(), [&](int first, int second) {
                    const double first_value = fixed_composition_[static_cast<std::size_t>(first)];
                    const double second_value = fixed_composition_[static_cast<std::size_t>(second)];
                    if (std::abs(first_value - second_value) > 1.0e-14) {
                        return first_value > second_value;
                    }
                    return first < second;
                });
            };
            sort_by_fixed_composition(cation_indices);
            sort_by_fixed_composition(anion_indices);
            auto append_pair = [&](int cation, int anion) {
                std::vector<std::pair<int, double>> row;
                row.push_back({cation, 1.0 / std::abs(charges_[static_cast<std::size_t>(cation)])});
                row.push_back({anion, 1.0 / std::abs(charges_[static_cast<std::size_t>(anion)])});
                transfer_weights_.push_back(std::move(row));
            };
            for (int species : neutral_species_indices_) {
                transfer_weights_.push_back({{species, 1.0}});
            }
            if (cation_indices.size() <= anion_indices.size()) {
                const int pivot_cation = cation_indices.front();
                for (int anion : anion_indices) {
                    append_pair(pivot_cation, anion);
                }
                for (std::size_t cation = 1; cation < cation_indices.size(); ++cation) {
                    append_pair(cation_indices[cation], anion_indices[cation - 1]);
                }
            } else {
                const int pivot_anion = anion_indices.front();
                for (int cation : cation_indices) {
                    append_pair(cation, pivot_anion);
                }
                for (std::size_t anion = 1; anion < anion_indices.size(); ++anion) {
                    append_pair(cation_indices[anion - 1], anion_indices[anion]);
                }
            }
        }
    }

    std::string name() const override {
        return problem_name_;
    }

    int variable_count() const override {
        return phase_count() * local_variable_count() + 1;
    }

    int constraint_count() const override {
        if (electrolyte_boundary_mode()) {
            return composition_constraint_count()
                + phase_count()
                + charge_constraint_count();
        }
        return composition_constraint_count()
            + phase_count()
            + charge_constraint_count()
            + phase_count()
            + transfer_constraint_count()
            + 1;
    }

    int jacobian_nonzero_count() const override {
        const int composition_nonzeros = composition_constraint_count() * species_count_;
        const int phase_total_nonzeros = phase_count() * species_count_;
        int charge_nonzeros = 0;
        for (double charge : charges_) {
            if (charge != 0.0) {
                charge_nonzeros += charge_constraint_count();
            }
        }
        const int pressure_nonzeros = electrolyte_boundary_mode() ? 0 : phase_count() * (local_variable_count() + 1);
        const int chemical_nonzeros = electrolyte_boundary_mode()
            ? 0
            : transfer_constraint_count() * (phase_count() * local_variable_count() + 1);
        const int gap_nonzeros = electrolyte_boundary_mode() ? 0 : 2;
        return composition_nonzeros
            + phase_total_nonzeros
            + charge_nonzeros
            + pressure_nonzeros
            + chemical_nonzeros
            + gap_nonzeros;
    }

    NlpBounds bounds() const override {
        NlpBounds out;
        out.variable_lower.reserve(static_cast<std::size_t>(variable_count()));
        out.variable_upper.reserve(static_cast<std::size_t>(variable_count()));
        for (int phase = 0; phase < phase_count(); ++phase) {
            for (int species = 0; species < species_count_; ++species) {
                out.variable_lower.push_back(1.0e-14);
                out.variable_upper.push_back(10.0);
            }
            if (phase == liquid_phase_index()) {
                out.variable_lower.push_back(minimum_liquid_volume_);
                out.variable_upper.push_back(maximum_liquid_volume_);
            } else if (phase == vapor_phase_index()) {
                out.variable_lower.push_back(minimum_vapor_volume_);
                out.variable_upper.push_back(maximum_vapor_volume_);
            } else {
                throw ValueError(problem_name_ + " phase role is out of range.");
            }
        }
        out.variable_lower.push_back(minimum_temperature_);
        out.variable_upper.push_back(maximum_temperature_);
        out.constraint_lower.assign(static_cast<std::size_t>(constraint_count()), 0.0);
        out.constraint_upper.assign(static_cast<std::size_t>(constraint_count()), 0.0);
        if (!electrolyte_boundary_mode()) {
            out.constraint_lower.back() = minimum_phase_volume_gap_;
            out.constraint_upper.back() = 1.0e12;
        }
        return out;
    }

    std::vector<double> initial_point() const override {
        const std::vector<double> root = build_temperature_route_initial_variables(
            args_,
            fixed_composition_,
            fixed_phase_index_,
            target_pressure_,
            charges_,
            problem_name_,
            1.0,
            DensitySeedMode::PhasePressureRoot
        );
        if (fixed_temperature_pressure_seed_satisfies_volume_bounds(
                root,
                species_count_,
                minimum_liquid_volume_,
                maximum_liquid_volume_,
                minimum_vapor_volume_,
                maximum_vapor_volume_,
                minimum_phase_volume_gap_
            )) {
            return root;
        }
        return build_temperature_route_initial_variables(
            args_,
            fixed_composition_,
            fixed_phase_index_,
            target_pressure_,
            charges_,
            problem_name_,
            1.0,
            DensitySeedMode::SeparatedPhaseRole
        );
    }

    double objective(const std::vector<double>& variables) const override {
        if (electrolyte_boundary_mode()) {
            return electrolyte_boundary_objective_second_order(variables).value;
        }
        double value = 0.0;
        for (const TemperatureRoutePhaseBlock& block : phase_blocks(variables)) {
            value += block.block.objective;
        }
        return value;
    }

    std::vector<double> objective_gradient(const std::vector<double>& variables) const override {
        if (electrolyte_boundary_mode()) {
            return electrolyte_boundary_objective_second_order(variables).gradient;
        }
        std::vector<double> out;
        out.reserve(static_cast<std::size_t>(variable_count()));
        double temperature_derivative = 0.0;
        for (const TemperatureRoutePhaseBlock& block : phase_blocks(variables)) {
            out.insert(out.end(), block.gradient.begin(), block.gradient.end() - 1);
            temperature_derivative += block.gradient.back();
        }
        out.push_back(temperature_derivative);
        return out;
    }

    std::vector<double> constraints(const std::vector<double>& variables) const override {
        const auto amounts = pressure_route_phase_amounts(variables, species_count_);
        std::vector<double> out(static_cast<std::size_t>(constraint_count()), 0.0);
        int row = 0;
        const auto& fixed_amounts = amounts[static_cast<std::size_t>(fixed_phase_index_)];
        const double fixed_total = std::accumulate(fixed_amounts.begin(), fixed_amounts.end(), 0.0);
        for (int species = 0; species < composition_constraint_count(); ++species) {
            out[static_cast<std::size_t>(row++)] =
                fixed_amounts[static_cast<std::size_t>(species)]
                - fixed_composition_[static_cast<std::size_t>(species)] * fixed_total;
        }
        for (int phase = 0; phase < phase_count(); ++phase) {
            const auto& phase_amounts = amounts[static_cast<std::size_t>(phase)];
            out[static_cast<std::size_t>(row++)] =
                std::accumulate(phase_amounts.begin(), phase_amounts.end(), 0.0) - 1.0;
        }
        for (int row_index = 0; row_index < charge_constraint_count(); ++row_index) {
            const auto& phase_amounts =
                amounts[static_cast<std::size_t>(charge_constraint_phase_index(row_index))];
            double phase_charge = 0.0;
            for (int species = 0; species < species_count_; ++species) {
                phase_charge += phase_amounts[static_cast<std::size_t>(species)]
                    * charges_[static_cast<std::size_t>(species)];
            }
            out[static_cast<std::size_t>(row++)] = phase_charge;
        }
        if (electrolyte_boundary_mode()) {
            return out;
        }
        const auto blocks = phase_blocks(variables);
        for (const TemperatureRoutePhaseBlock& block : blocks) {
            out[static_cast<std::size_t>(row++)] = block.block.pressure_consistency_residual;
        }
        for (const auto& weights : transfer_weights_for_route()) {
            double residual = 0.0;
            for (const auto& [species, weight] : weights) {
                residual += weight * (
                    blocks[0].gradient[static_cast<std::size_t>(species)]
                    - blocks[1].gradient[static_cast<std::size_t>(species)]
                );
            }
            out[static_cast<std::size_t>(row++)] = residual;
        }
        if (!electrolyte_boundary_mode()) {
            out[static_cast<std::size_t>(row++)] =
                variables[static_cast<std::size_t>(vapor_volume_col())]
                - variables[static_cast<std::size_t>(liquid_volume_col())];
        }
        return out;
    }

    NlpJacobianStructure jacobian_structure() const override {
        NlpJacobianStructure out;
        out.rows.reserve(static_cast<std::size_t>(jacobian_nonzero_count()));
        out.cols.reserve(static_cast<std::size_t>(jacobian_nonzero_count()));
        int row = 0;
        for (int species = 0; species < composition_constraint_count(); ++species) {
            for (int col = 0; col < species_count_; ++col) {
                out.rows.push_back(row);
                out.cols.push_back(fixed_col(col));
            }
            ++row;
        }
        for (int phase = 0; phase < phase_count(); ++phase) {
            const int offset = phase * local_variable_count();
            for (int species = 0; species < species_count_; ++species) {
                out.rows.push_back(row);
                out.cols.push_back(offset + species);
            }
            ++row;
        }
        for (int row_index = 0; row_index < charge_constraint_count(); ++row_index) {
            const int offset = charge_constraint_phase_index(row_index) * local_variable_count();
            for (int species = 0; species < species_count_; ++species) {
                if (charges_[static_cast<std::size_t>(species)] == 0.0) {
                    continue;
                }
                out.rows.push_back(row);
                out.cols.push_back(offset + species);
            }
            ++row;
        }
        if (electrolyte_boundary_mode()) {
            return out;
        }
        for (int phase = 0; phase < phase_count(); ++phase) {
            const int offset = phase * local_variable_count();
            for (int col = 0; col < local_variable_count(); ++col) {
                out.rows.push_back(row);
                out.cols.push_back(offset + col);
            }
            out.rows.push_back(row);
            out.cols.push_back(temperature_col());
            ++row;
        }
        for (int transfer = 0; transfer < transfer_constraint_count(); ++transfer) {
            for (int phase = 0; phase < phase_count(); ++phase) {
                const int offset = phase * local_variable_count();
                for (int col = 0; col < local_variable_count(); ++col) {
                    out.rows.push_back(row);
                    out.cols.push_back(offset + col);
                }
            }
            out.rows.push_back(row);
            out.cols.push_back(temperature_col());
            ++row;
        }
        if (!electrolyte_boundary_mode()) {
            out.rows.push_back(row);
            out.cols.push_back(liquid_volume_col());
            out.rows.push_back(row);
            out.cols.push_back(vapor_volume_col());
        }
        return out;
    }

    std::vector<double> jacobian_values(const std::vector<double>& variables) const override {
        const auto blocks = phase_blocks(variables);
        std::vector<double> out;
        out.reserve(static_cast<std::size_t>(jacobian_nonzero_count()));
        int row = 0;
        for (int species = 0; species < composition_constraint_count(); ++species) {
            for (int col = 0; col < species_count_; ++col) {
                out.push_back((col == species ? 1.0 : 0.0) - fixed_composition_[static_cast<std::size_t>(species)]);
            }
            ++row;
        }
        for (int phase = 0; phase < phase_count(); ++phase) {
            for (int species = 0; species < species_count_; ++species) {
                out.push_back(1.0);
            }
            ++row;
        }
        for (int row_index = 0; row_index < charge_constraint_count(); ++row_index) {
            for (int species = 0; species < species_count_; ++species) {
                const double charge = charges_[static_cast<std::size_t>(species)];
                if (charge == 0.0) {
                    continue;
                }
                out.push_back(charge);
            }
            ++row;
        }
        if (electrolyte_boundary_mode()) {
            return out;
        }
        for (int phase = 0; phase < phase_count(); ++phase) {
            const TemperatureRoutePhaseBlock& block = blocks[static_cast<std::size_t>(phase)];
            for (int col = 0; col < local_variable_count(); ++col) {
                out.push_back(block.pressure_jacobian_row_major[static_cast<std::size_t>(col)]);
            }
            out.push_back(block.pressure_jacobian_row_major.back());
            ++row;
        }
        for (const auto& weights : transfer_weights_for_route()) {
            double temperature_value = 0.0;
            for (int phase = 0; phase < phase_count(); ++phase) {
                const TemperatureRoutePhaseBlock& block = blocks[static_cast<std::size_t>(phase)];
                const int block_variable_count = local_variable_count() + 1;
                for (int col = 0; col < local_variable_count(); ++col) {
                    double value = 0.0;
                    for (const auto& [species, weight] : weights) {
                        value += weight * (phase == 0 ? 1.0 : -1.0) * block.objective_hessian_row_major[
                                static_cast<std::size_t>(species * block_variable_count + col)
                            ];
                    }
                    out.push_back(value);
                }
                for (const auto& [species, weight] : weights) {
                    temperature_value += weight * (phase == 0 ? 1.0 : -1.0)
                        * block.objective_hessian_row_major[
                            static_cast<std::size_t>(species * block_variable_count + block_variable_count - 1)
                        ];
                }
            }
            out.push_back(temperature_value);
            ++row;
        }
        if (!electrolyte_boundary_mode()) {
            out.push_back(-1.0);
            out.push_back(1.0);
        }
        return out;
    }

    bool has_exact_hessian() const override {
        return route_supports_exact_phase_derivatives(args_, problem_name_);
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
            throw ValueError(problem_name_ + " exact Hessian requires direct non-associating phase derivatives.");
        }
        if (constraint_multipliers.size() != static_cast<std::size_t>(constraint_count())) {
            throw ValueError(problem_name_ + " Hessian multiplier vector size does not match the constraint count.");
        }

        const auto blocks = phase_blocks(variables);
        const int n = variable_count();
        const int block_variable_count = local_variable_count() + 1;
        if (electrolyte_boundary_mode()) {
            const ObjectiveSecondOrderData boundary_objective =
                electrolyte_boundary_objective_second_order(variables);
            ConstraintSecondOrderData constraints_data;
            constraints_data.constraint_count = constraint_count();
            constraints_data.variable_count = n;
            constraints_data.values = this->constraints(variables);
            constraints_data.hessian_tensor_row_major.assign(
                static_cast<std::size_t>(constraint_count() * n * n),
                0.0
            );
            constraints_data.has_hessian.assign(static_cast<std::size_t>(constraint_count()), false);
            constraints_data.backend = "linear_electrolyte_boundary_hard_constraints";
            return LagrangianHessianAssembler(n).values(
                objective_factor,
                boundary_objective,
                constraints_data,
                constraint_multipliers
            );
        }
        ObjectiveSecondOrderData objective;
        objective.variable_count = n;
        objective.value = 0.0;
        objective.gradient.assign(static_cast<std::size_t>(n), 0.0);
        objective.hessian_row_major.assign(static_cast<std::size_t>(n * n), 0.0);
        objective.backend = "cppad_phase_temperature_route";
        for (int phase = 0; phase < phase_count(); ++phase) {
            const TemperatureRoutePhaseBlock& block = blocks[static_cast<std::size_t>(phase)];
            require_square_block(
                block.objective_hessian_row_major,
                block_variable_count,
                problem_name_ + " objective Hessian block"
            );
            require_third_derivative_tensor(
                block.objective_third_derivative_tensor_row_major,
                block_variable_count,
                problem_name_ + " objective third-derivative tensor"
            );
            const std::vector<int> phase_indices =
                fixed_pressure_global_indices(phase, local_variable_count(), temperature_col());
            objective.value += block.block.objective;
            for (int local = 0; local < block_variable_count; ++local) {
                objective.gradient[static_cast<std::size_t>(phase_indices[static_cast<std::size_t>(local)])] +=
                    block.gradient[static_cast<std::size_t>(local)];
            }
            add_local_hessian_to_dense(
                objective.hessian_row_major,
                n,
                phase_indices,
                block.objective_hessian_row_major,
                1.0,
                problem_name_ + " objective Hessian block"
            );
        }
        ConstraintSecondOrderData constraints_data;
        constraints_data.constraint_count = constraint_count();
        constraints_data.variable_count = n;
        constraints_data.values = this->constraints(variables);
        constraints_data.hessian_tensor_row_major.assign(
            static_cast<std::size_t>(constraint_count() * n * n),
            0.0
        );
        constraints_data.has_hessian.assign(static_cast<std::size_t>(constraint_count()), false);
        constraints_data.backend = "cppad_phase_temperature_route";

        const int pressure_row_start =
            composition_constraint_count() + phase_count() + charge_constraint_count();
        for (int phase = 0; phase < phase_count(); ++phase) {
            const TemperatureRoutePhaseBlock& block = blocks[static_cast<std::size_t>(phase)];
            require_square_block(
                block.pressure_hessian_row_major,
                block_variable_count,
                problem_name_ + " pressure Hessian block"
            );
            const int constraint_row = pressure_row_start + phase;
            constraints_data.has_hessian[static_cast<std::size_t>(constraint_row)] = true;
            add_local_hessian_to_constraint_tensor(
                constraints_data.hessian_tensor_row_major,
                constraint_row,
                n,
                fixed_pressure_global_indices(phase, local_variable_count(), temperature_col()),
                block.pressure_hessian_row_major,
                1.0,
                problem_name_ + " pressure Hessian block"
            );
        }

        const int chemical_row_start = pressure_row_start + phase_count();
        const auto transfer_weights = transfer_weights_for_route();
        for (int transfer = 0; transfer < static_cast<int>(transfer_weights.size()); ++transfer) {
            const int constraint_row = chemical_row_start + transfer;
            constraints_data.has_hessian[static_cast<std::size_t>(constraint_row)] = true;
            for (int phase = 0; phase < phase_count(); ++phase) {
                const TemperatureRoutePhaseBlock& block = blocks[static_cast<std::size_t>(phase)];
                std::vector<double> chemical_hessian(
                    static_cast<std::size_t>(block_variable_count * block_variable_count),
                    0.0
                );
                for (const auto& [species, weight] : transfer_weights[static_cast<std::size_t>(transfer)]) {
                    const std::vector<double> slice = third_derivative_slice(
                        block.objective_third_derivative_tensor_row_major,
                        species,
                        block_variable_count,
                        problem_name_ + " chemical-potential Hessian block"
                    );
                    for (std::size_t index = 0; index < chemical_hessian.size(); ++index) {
                        chemical_hessian[index] += weight * slice[index];
                    }
                }
                for (int first = 0; first < block_variable_count; ++first) {
                    for (int second = first + 1; second < block_variable_count; ++second) {
                        const std::size_t first_index =
                            static_cast<std::size_t>(first * block_variable_count + second);
                        const std::size_t second_index =
                            static_cast<std::size_t>(second * block_variable_count + first);
                        const double symmetric_value =
                            0.5 * (chemical_hessian[first_index] + chemical_hessian[second_index]);
                        chemical_hessian[first_index] = symmetric_value;
                        chemical_hessian[second_index] = symmetric_value;
                    }
                }
                add_local_hessian_to_constraint_tensor(
                    constraints_data.hessian_tensor_row_major,
                    constraint_row,
                    n,
                    fixed_pressure_global_indices(phase, local_variable_count(), temperature_col()),
                    chemical_hessian,
                    phase == 0 ? 1.0 : -1.0,
                    problem_name_ + " chemical-potential Hessian block"
                );
            }
        }

        return LagrangianHessianAssembler(n).values(
            objective_factor,
            objective,
            constraints_data,
            constraint_multipliers
        );
    }

    std::string hessian_backend() const override {
        return "cppad_phase_temperature_route";
    }

    NlpScaling scaling() const override {
        NlpScaling out;
        out.objective = 1.0;
        out.variables.assign(static_cast<std::size_t>(variable_count()), 1.0);
        out.variables.back() = 1.0e-2;
        out.constraints.assign(static_cast<std::size_t>(constraint_count()), 1.0);
        if (!electrolyte_boundary_mode()) {
            apply_pressure_constraint_scaling(
                out,
                composition_constraint_count() + phase_count() + charge_constraint_count(),
                phase_count(),
                target_pressure_
            );
        }
        return out;
    }

    std::map<std::string, std::string> diagnostics() const override {
        return route_metadata_diagnostics(fixed_pressure_temperature_route_metadata(!charges_.empty()));
    }

    int species_count() const {
        return species_count_;
    }

    int phase_count() const {
        return 2;
    }

private:
    int local_variable_count() const {
        return species_count_ + 1;
    }

    int composition_constraint_count() const {
        return std::max(0, species_count_ - 1);
    }

    int charge_constraint_count() const {
        return charges_.empty() ? 0 : 1;
    }

    int fixed_col(int species) const {
        return fixed_phase_index_ * local_variable_count() + species;
    }

    int liquid_phase_index() const {
        return 0;
    }

    int vapor_phase_index() const {
        return 1;
    }

    int liquid_volume_col() const {
        return liquid_phase_index() * local_variable_count() + species_count_;
    }

    int vapor_volume_col() const {
        return vapor_phase_index() * local_variable_count() + species_count_;
    }

    int temperature_col() const {
        return variable_count() - 1;
    }

    bool electrolyte_boundary_mode() const {
        return !charges_.empty();
    }

    int charge_constraint_phase_index(int row_index) const {
        if (!electrolyte_boundary_mode() || row_index != 0) {
            throw ValueError(problem_name_ + " charge constraint row is out of range.");
        }
        return fixed_phase_index_ == liquid_phase_index() ? vapor_phase_index() : liquid_phase_index();
    }

    int transfer_constraint_count() const {
        return electrolyte_boundary_mode() ? static_cast<int>(transfer_weights_.size()) : species_count_;
    }

    const std::vector<std::vector<std::pair<int, double>>>& transfer_weights_for_route() const {
        if (electrolyte_boundary_mode()) {
            return transfer_weights_;
        }
        if (neutral_transfer_weights_.empty()) {
            for (int species = 0; species < species_count_; ++species) {
                neutral_transfer_weights_.push_back({{species, 1.0}});
            }
        }
        return neutral_transfer_weights_;
    }

    ResidualSecondOrderData electrolyte_boundary_residual_second_order(
        const std::vector<double>& variables
    ) const {
        const auto blocks = phase_blocks(variables);
        const int n = variable_count();
        const int block_variable_count = local_variable_count() + 1;
        const auto transfer_weights = transfer_weights_for_route();
        const int pressure_count = phase_count();
        const int residual_count = pressure_count + static_cast<int>(transfer_weights.size());
        ResidualSecondOrderData out;
        out.residual_count = residual_count;
        out.variable_count = n;
        out.backend = "cppad_phase_temperature_projected_electrolyte_boundary";
        out.residuals.assign(static_cast<std::size_t>(residual_count), 0.0);
        out.jacobian_row_major.assign(static_cast<std::size_t>(residual_count * n), 0.0);
        out.residual_hessian_tensor_row_major.assign(
            static_cast<std::size_t>(residual_count * n * n),
            0.0
        );

        const double pressure_scale = 1.0 / std::max(1.0, 1.0e-3 * std::abs(target_pressure_));
        for (int phase = 0; phase < phase_count(); ++phase) {
            const TemperatureRoutePhaseBlock& block = blocks[static_cast<std::size_t>(phase)];
            const std::vector<int> phase_indices =
                fixed_pressure_global_indices(phase, local_variable_count(), temperature_col());
            out.residuals[static_cast<std::size_t>(phase)] =
                pressure_scale * block.block.pressure_consistency_residual;
            for (int local = 0; local < block_variable_count; ++local) {
                out.jacobian_row_major[
                    static_cast<std::size_t>(phase * n + phase_indices[static_cast<std::size_t>(local)])
                ] = pressure_scale * block.pressure_jacobian_row_major[static_cast<std::size_t>(local)];
            }
            std::vector<double> pressure_hessian = block.pressure_hessian_row_major;
            symmetrize_local_square_matrix(pressure_hessian, block_variable_count);
            add_local_hessian_to_constraint_tensor(
                out.residual_hessian_tensor_row_major,
                phase,
                n,
                phase_indices,
                pressure_hessian,
                pressure_scale,
                problem_name_ + " pressure residual Hessian block"
            );
        }

        for (int transfer = 0; transfer < static_cast<int>(transfer_weights.size()); ++transfer) {
            const int row = pressure_count + transfer;
            for (int phase = 0; phase < phase_count(); ++phase) {
                const TemperatureRoutePhaseBlock& block = blocks[static_cast<std::size_t>(phase)];
                const int phase_sign = phase == 0 ? 1 : -1;
                const std::vector<int> phase_indices =
                    fixed_pressure_global_indices(phase, local_variable_count(), temperature_col());
                std::vector<double> transfer_hessian(
                    static_cast<std::size_t>(block_variable_count * block_variable_count),
                    0.0
                );
                for (const auto& [species, weight] : transfer_weights[static_cast<std::size_t>(transfer)]) {
                    out.residuals[static_cast<std::size_t>(row)] += weight * static_cast<double>(phase_sign)
                        * block.gradient[static_cast<std::size_t>(species)];
                    for (int local = 0; local < block_variable_count; ++local) {
                        out.jacobian_row_major[
                            static_cast<std::size_t>(
                                row * n + phase_indices[static_cast<std::size_t>(local)]
                            )
                        ] += weight * static_cast<double>(phase_sign) * block.objective_hessian_row_major[
                            static_cast<std::size_t>(species * block_variable_count + local)
                        ];
                    }
                    const std::vector<double> slice = third_derivative_slice(
                        block.objective_third_derivative_tensor_row_major,
                        species,
                        block_variable_count,
                        problem_name_ + " projected transfer Hessian block"
                    );
                    for (std::size_t index = 0; index < transfer_hessian.size(); ++index) {
                        transfer_hessian[index] += weight * static_cast<double>(phase_sign) * slice[index];
                    }
                }
                symmetrize_local_square_matrix(transfer_hessian, block_variable_count);
                add_local_hessian_to_constraint_tensor(
                    out.residual_hessian_tensor_row_major,
                    row,
                    n,
                    phase_indices,
                    transfer_hessian,
                    1.0,
                    problem_name_ + " projected transfer Hessian block"
                );
            }
        }
        return out;
    }

    ObjectiveSecondOrderData electrolyte_boundary_objective_second_order(
        const std::vector<double>& variables
    ) const {
        return residual_quadratic_objective_second_order(
            electrolyte_boundary_residual_second_order(variables)
        );
    }

    std::vector<TemperatureRoutePhaseBlock> phase_blocks(const std::vector<double>& variables) const {
        require_size(variables, static_cast<std::size_t>(variable_count()), problem_name_ + " variable");
        const double temperature = variables.back();
        require_positive_finite(temperature, problem_name_ + " temperature");
        const auto amounts = pressure_route_phase_amounts(variables, species_count_);
        const auto volumes = pressure_route_phase_volumes(variables, species_count_);
        std::vector<TemperatureRoutePhaseBlock> blocks;
        blocks.reserve(static_cast<std::size_t>(phase_count()));
        for (int phase = 0; phase < phase_count(); ++phase) {
            blocks.push_back(
                evaluate_temperature_route_phase_block(
                    args_,
                    temperature,
                    target_pressure_,
                    amounts[static_cast<std::size_t>(phase)],
                    volumes[static_cast<std::size_t>(phase)]
                )
            );
        }
        return blocks;
    }

    add_args args_;
    double target_pressure_ = 0.0;
    double initial_temperature_ = 300.0;
    double minimum_temperature_ = 1.0;
    double maximum_temperature_ = 2000.0;
    double minimum_liquid_volume_ = kMinimumLiquidVolume;
    double maximum_liquid_volume_ = kMaximumLiquidVolume;
    double minimum_vapor_volume_ = kMinimumVaporVolume;
    double maximum_vapor_volume_ = kMaximumVaporVolume;
    double minimum_phase_volume_gap_ = kMinimumPhaseVolumeGap;
    std::vector<double> fixed_composition_;
    int fixed_phase_index_ = 0;
    std::string problem_name_;
    std::vector<double> charges_;
    double charge_constraint_tolerance_ = 0.0;
    std::vector<int> neutral_species_indices_;
    std::vector<std::vector<std::pair<int, double>>> transfer_weights_;
    mutable std::vector<std::vector<std::pair<int, double>>> neutral_transfer_weights_;
    int species_count_ = 0;
};

class NeutralFixedTemperaturePressureFlashProblem final : public NlpProblem {
public:
    NeutralFixedTemperaturePressureFlashProblem(
        add_args args,
        double temperature,
        double target_pressure,
        std::vector<double> feed_composition,
        std::string problem_name
    )
        : args_(std::move(args)),
          temperature_(temperature),
          target_pressure_(target_pressure),
          feed_composition_(normalized_positive_values(feed_composition, problem_name + " feed composition")),
          problem_name_(std::move(problem_name)) {
        require_positive_finite(temperature_, problem_name_ + " temperature");
        require_positive_finite(target_pressure_, problem_name_ + " pressure");
        species_count_ = static_cast<int>(feed_composition_.size());
    }

    std::string name() const override {
        return problem_name_;
    }

    int variable_count() const override {
        return phase_count() * local_variable_count();
    }

    int constraint_count() const override {
        return species_count_ + phase_count() + species_count_ + 1;
    }

    int jacobian_nonzero_count() const override {
        const int material_nonzeros = phase_count() * species_count_;
        const int pressure_nonzeros = phase_count() * local_variable_count();
        const int chemical_nonzeros = species_count_ * phase_count() * local_variable_count();
        const int gap_nonzeros = 2;
        return material_nonzeros + pressure_nonzeros + chemical_nonzeros + gap_nonzeros;
    }

    NlpBounds bounds() const override {
        NlpBounds out;
        out.variable_lower.reserve(static_cast<std::size_t>(variable_count()));
        out.variable_upper.reserve(static_cast<std::size_t>(variable_count()));
        for (int phase = 0; phase < phase_count(); ++phase) {
            for (int species = 0; species < species_count_; ++species) {
                out.variable_lower.push_back(1.0e-14);
                out.variable_upper.push_back(10.0);
            }
            if (phase == liquid_phase_index()) {
                out.variable_lower.push_back(minimum_liquid_volume_);
                out.variable_upper.push_back(maximum_liquid_volume_);
            } else if (phase == vapor_phase_index()) {
                out.variable_lower.push_back(minimum_vapor_volume_);
                out.variable_upper.push_back(maximum_vapor_volume_);
            } else {
                throw ValueError(problem_name_ + " phase role is out of range.");
            }
        }
        out.constraint_lower.assign(static_cast<std::size_t>(constraint_count()), 0.0);
        out.constraint_upper.assign(static_cast<std::size_t>(constraint_count()), 0.0);
        out.constraint_lower.back() = minimum_phase_volume_gap_;
        out.constraint_upper.back() = 1.0e12;
        return out;
    }

    std::vector<double> initial_point() const override {
        const std::vector<NamedInitialVariables> seeds = flash_route_seed_candidates(
            args_,
            feed_composition_,
            temperature_,
            target_pressure_,
            problem_name_
        );
        if (seeds.empty()) {
            throw ValueError(problem_name_ + " could not construct a deterministic flash seed.");
        }
        return seeds.front().variables;
    }

    double objective(const std::vector<double>& variables) const override {
        double value = 0.0;
        for (const EosPhaseBlockResult& block : phase_blocks(variables)) {
            value += block.objective;
        }
        return value;
    }

    std::vector<double> objective_gradient(const std::vector<double>& variables) const override {
        std::vector<double> out;
        out.reserve(static_cast<std::size_t>(variable_count()));
        for (const EosPhaseBlockResult& block : phase_blocks(variables)) {
            out.insert(out.end(), block.gradient.begin(), block.gradient.end());
        }
        return out;
    }

    std::vector<double> constraints(const std::vector<double>& variables) const override {
        const auto amounts = flash_route_phase_amounts(variables, species_count_);
        const auto blocks = phase_blocks(variables);
        std::vector<double> out(static_cast<std::size_t>(constraint_count()), 0.0);
        int row = 0;
        for (int species = 0; species < species_count_; ++species) {
            out[static_cast<std::size_t>(row++)] =
                amounts[0][static_cast<std::size_t>(species)]
                + amounts[1][static_cast<std::size_t>(species)]
                - kTwoPhaseFlashFeedBasis * feed_composition_[static_cast<std::size_t>(species)];
        }
        for (const EosPhaseBlockResult& block : blocks) {
            out[static_cast<std::size_t>(row++)] = block.pressure_consistency_residual;
        }
        for (int species = 0; species < species_count_; ++species) {
            out[static_cast<std::size_t>(row++)] =
                blocks[0].gradient[static_cast<std::size_t>(species)]
                - blocks[1].gradient[static_cast<std::size_t>(species)];
        }
        out[static_cast<std::size_t>(row++)] =
            variables[static_cast<std::size_t>(vapor_volume_col())]
            - variables[static_cast<std::size_t>(liquid_volume_col())];
        return out;
    }

    NlpJacobianStructure jacobian_structure() const override {
        NlpJacobianStructure out;
        out.rows.reserve(static_cast<std::size_t>(jacobian_nonzero_count()));
        out.cols.reserve(static_cast<std::size_t>(jacobian_nonzero_count()));
        int row = 0;
        for (int species = 0; species < species_count_; ++species) {
            for (int phase = 0; phase < phase_count(); ++phase) {
                out.rows.push_back(row);
                out.cols.push_back(phase * local_variable_count() + species);
            }
            ++row;
        }
        for (int phase = 0; phase < phase_count(); ++phase) {
            const int offset = phase * local_variable_count();
            for (int col = 0; col < local_variable_count(); ++col) {
                out.rows.push_back(row);
                out.cols.push_back(offset + col);
            }
            ++row;
        }
        for (int species = 0; species < species_count_; ++species) {
            for (int phase = 0; phase < phase_count(); ++phase) {
                const int offset = phase * local_variable_count();
                for (int col = 0; col < local_variable_count(); ++col) {
                    out.rows.push_back(row);
                    out.cols.push_back(offset + col);
                }
            }
            ++row;
        }
        out.rows.push_back(row);
        out.cols.push_back(liquid_volume_col());
        out.rows.push_back(row);
        out.cols.push_back(vapor_volume_col());
        return out;
    }

    std::vector<double> jacobian_values(const std::vector<double>& variables) const override {
        const auto blocks = phase_blocks(variables);
        std::vector<double> out;
        out.reserve(static_cast<std::size_t>(jacobian_nonzero_count()));
        int row = 0;
        for (int species = 0; species < species_count_; ++species) {
            for (int phase = 0; phase < phase_count(); ++phase) {
                out.push_back(1.0);
            }
            ++row;
        }
        for (int phase = 0; phase < phase_count(); ++phase) {
            const EosPhaseBlockResult& block = blocks[static_cast<std::size_t>(phase)];
            if (block.pressure_jacobian_row_major.size() != static_cast<std::size_t>(local_variable_count())) {
                throw ValueError(problem_name_ + " pressure Jacobian size did not match variables.");
            }
            for (int col = 0; col < local_variable_count(); ++col) {
                out.push_back(block.pressure_jacobian_row_major[static_cast<std::size_t>(col)]);
            }
            ++row;
        }
        for (int species = 0; species < species_count_; ++species) {
            for (int phase = 0; phase < phase_count(); ++phase) {
                const EosPhaseBlockResult& block = blocks[static_cast<std::size_t>(phase)];
                if (block.objective_curvature_rows != local_variable_count()
                    || block.objective_curvature_cols != local_variable_count()
                    || block.objective_curvature_row_major.size()
                        != static_cast<std::size_t>(local_variable_count() * local_variable_count())) {
                    throw ValueError(problem_name_ + " chemical-potential Jacobian size did not match variables.");
                }
                for (int col = 0; col < local_variable_count(); ++col) {
                    out.push_back((phase == 0 ? 1.0 : -1.0) * block.objective_curvature_row_major[
                            static_cast<std::size_t>(species * local_variable_count() + col)
                        ]);
                }
            }
            ++row;
        }
        out.push_back(-1.0);
        out.push_back(1.0);
        return out;
    }

    bool has_exact_hessian() const override {
        return route_supports_exact_phase_derivatives(args_, problem_name_);
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
            throw ValueError(problem_name_ + " exact Hessian requires direct non-associating phase derivatives.");
        }
        if (constraint_multipliers.size() != static_cast<std::size_t>(constraint_count())) {
            throw ValueError(problem_name_ + " Hessian multiplier vector size does not match the constraint count.");
        }

        const auto blocks = phase_blocks(variables);
        const int n = variable_count();
        ObjectiveSecondOrderData objective;
        objective.variable_count = n;
        objective.value = 0.0;
        objective.gradient.assign(static_cast<std::size_t>(n), 0.0);
        objective.hessian_row_major.assign(static_cast<std::size_t>(n * n), 0.0);
        objective.backend = "cppad_phase_flash_route";
        for (int phase = 0; phase < phase_count(); ++phase) {
            const EosPhaseBlockResult& block = blocks[static_cast<std::size_t>(phase)];
            require_square_block(
                block.objective_curvature_row_major,
                local_variable_count(),
                problem_name_ + " objective Hessian block"
            );
            require_third_derivative_tensor(
                block.objective_third_derivative_tensor_row_major,
                local_variable_count(),
                problem_name_ + " objective third-derivative tensor"
            );
            const std::vector<int> phase_indices = fixed_temperature_global_indices(phase, local_variable_count());
            objective.value += block.objective;
            for (int local = 0; local < local_variable_count(); ++local) {
                objective.gradient[static_cast<std::size_t>(phase_indices[static_cast<std::size_t>(local)])] =
                    block.gradient[static_cast<std::size_t>(local)];
            }
            add_local_hessian_to_dense(
                objective.hessian_row_major,
                n,
                phase_indices,
                block.objective_curvature_row_major,
                1.0,
                problem_name_ + " objective Hessian block"
            );
        }

        ConstraintSecondOrderData constraints_data;
        constraints_data.constraint_count = constraint_count();
        constraints_data.variable_count = n;
        constraints_data.values = this->constraints(variables);
        constraints_data.hessian_tensor_row_major.assign(
            static_cast<std::size_t>(constraint_count() * n * n),
            0.0
        );
        constraints_data.has_hessian.assign(static_cast<std::size_t>(constraint_count()), false);
        constraints_data.backend = "cppad_phase_flash_route";

        const int pressure_row_start = species_count_;
        for (int phase = 0; phase < phase_count(); ++phase) {
            const EosPhaseBlockResult& block = blocks[static_cast<std::size_t>(phase)];
            require_square_block(
                block.pressure_hessian_row_major,
                local_variable_count(),
                problem_name_ + " pressure Hessian block"
            );
            const int constraint_row = pressure_row_start + phase;
            constraints_data.has_hessian[static_cast<std::size_t>(constraint_row)] = true;
            add_local_hessian_to_constraint_tensor(
                constraints_data.hessian_tensor_row_major,
                constraint_row,
                n,
                fixed_temperature_global_indices(phase, local_variable_count()),
                block.pressure_hessian_row_major,
                1.0,
                problem_name_ + " pressure Hessian block"
            );
        }

        const int chemical_row_start = pressure_row_start + phase_count();
        for (int species = 0; species < species_count_; ++species) {
            const int constraint_row = chemical_row_start + species;
            constraints_data.has_hessian[static_cast<std::size_t>(constraint_row)] = true;
            for (int phase = 0; phase < phase_count(); ++phase) {
                const EosPhaseBlockResult& block = blocks[static_cast<std::size_t>(phase)];
                const std::vector<double> chemical_hessian = third_derivative_slice(
                    block.objective_third_derivative_tensor_row_major,
                    species,
                    local_variable_count(),
                    problem_name_ + " chemical-potential Hessian block"
                );
                add_local_hessian_to_constraint_tensor(
                    constraints_data.hessian_tensor_row_major,
                    constraint_row,
                    n,
                    fixed_temperature_global_indices(phase, local_variable_count()),
                    chemical_hessian,
                    phase == 0 ? 1.0 : -1.0,
                    problem_name_ + " chemical-potential Hessian block"
                );
            }
        }

        return LagrangianHessianAssembler(n).values(
            objective_factor,
            objective,
            constraints_data,
            constraint_multipliers
        );
    }

    std::string hessian_backend() const override {
        return "cppad_phase_flash_route";
    }

    NlpScaling scaling() const override {
        NlpScaling out;
        out.objective = 1.0;
        out.variables.assign(static_cast<std::size_t>(variable_count()), 1.0);
        out.constraints.assign(static_cast<std::size_t>(constraint_count()), 1.0);
        return out;
    }

    std::map<std::string, std::string> diagnostics() const override {
        return route_metadata_diagnostics(fixed_temperature_pressure_flash_route_metadata());
    }

    int species_count() const {
        return species_count_;
    }

    int phase_count() const {
        return 2;
    }

    std::vector<double> feed_amounts() const {
        std::vector<double> out;
        out.reserve(feed_composition_.size());
        for (double value : feed_composition_) {
            out.push_back(kTwoPhaseFlashFeedBasis * value);
        }
        return out;
    }

private:
    int local_variable_count() const {
        return species_count_ + 1;
    }

    int liquid_phase_index() const {
        return 0;
    }

    int vapor_phase_index() const {
        return 1;
    }

    int liquid_volume_col() const {
        return liquid_phase_index() * local_variable_count() + species_count_;
    }

    int vapor_volume_col() const {
        return vapor_phase_index() * local_variable_count() + species_count_;
    }

    std::vector<EosPhaseBlockResult> phase_blocks(const std::vector<double>& variables) const {
        require_size(variables, static_cast<std::size_t>(variable_count()), problem_name_ + " variable");
        const auto amounts = flash_route_phase_amounts(variables, species_count_);
        const auto volumes = flash_route_phase_volumes(variables, species_count_);
        std::vector<EosPhaseBlockResult> blocks;
        blocks.reserve(static_cast<std::size_t>(phase_count()));
        for (int phase = 0; phase < phase_count(); ++phase) {
            blocks.push_back(
                evaluate_eos_phase_block(
                    args_,
                    temperature_,
                    target_pressure_,
                    amounts[static_cast<std::size_t>(phase)],
                    volumes[static_cast<std::size_t>(phase)]
                )
            );
        }
        return blocks;
    }

    add_args args_;
    double temperature_ = 0.0;
    double target_pressure_ = 0.0;
    double minimum_liquid_volume_ = kMinimumLiquidVolume;
    double maximum_liquid_volume_ = kMaximumLiquidVolume;
    double minimum_vapor_volume_ = kMinimumVaporVolume;
    double maximum_vapor_volume_ = kMaximumVaporVolume;
    double minimum_phase_volume_gap_ = kMinimumPhaseVolumeGap;
    std::vector<double> feed_composition_;
    std::string problem_name_;
    int species_count_ = 0;
};

NeutralTwoPhaseEosNlpContract make_contract(const NlpProblem& problem, int phase_count, int species_count) {
    return make_neutral_two_phase_nlp_contract_snapshot(
        problem,
        phase_count,
        species_count,
        NlpContractSnapshotDetail::Basic
    );
}

NeutralTwoPhaseEosPostsolve fixed_temperature_pressure_postsolve(
    const add_args& args,
    double temperature,
    double pressure,
    const std::vector<std::vector<double>>& phase_amounts,
    const std::vector<double>& volumes,
    int fixed_phase_index,
    const std::vector<double>& fixed_composition,
    const std::vector<double>& charges,
    double phase_total_tolerance,
    double pressure_tolerance,
    double charge_tolerance,
    double chemical_potential_tolerance,
    double phase_distance_tolerance,
    const std::string& problem_name
) {
    const bool pure_density_distance_route =
        problem_name == "single_component_vle_eos" && fixed_composition.size() == 1 && charges.empty();
    NeutralTwoPhaseEosPostsolve out = evaluate_neutral_two_phase_eos_postsolve(
        args,
        temperature,
        pressure,
        phase_amounts,
        volumes,
        summed_feed_amounts(phase_amounts, static_cast<int>(fixed_composition.size())),
        phase_total_tolerance,
        pressure_tolerance,
        chemical_potential_tolerance,
        phase_distance_tolerance,
        {},
        false,
        false,
        {},
        false,
        !pure_density_distance_route
    );
    apply_route_metadata(out, fixed_temperature_pressure_route_metadata(!charges.empty()));
    out.fixed_composition_norm = fixed_composition_norm(phase_amounts, fixed_phase_index, fixed_composition);
    out.phase_amount_total_norm = phase_total_norm(phase_amounts);
    out.charge_balance_norm = phase_charge_norm(phase_amounts, charges);
    const bool pure_density_distance_postsolve =
        pure_density_distance_route && out.phase_densities.size() == 2;
    const bool local_postsolve_accepted = out.accepted;
    if (pure_density_distance_postsolve) {
        const double first_density = out.phase_densities[0];
        const double second_density = out.phase_densities[1];
        const double density_scale = std::max(1.0, std::max(std::abs(first_density), std::abs(second_density)));
        out.phase_distance = std::abs(first_density - second_density) / density_scale;
    }
    const double effective_phase_distance_tolerance = pure_density_distance_route
        ? std::max(phase_distance_tolerance, kPureSaturationMinimumReducedDensitySeparation)
        : phase_distance_tolerance;
    const bool pure_density_distance_rejected =
        pure_density_distance_postsolve && out.phase_distance < effective_phase_distance_tolerance;
    out.accepted = out.accepted
        && out.fixed_composition_norm <= phase_total_tolerance
        && out.phase_amount_total_norm <= phase_total_tolerance
        && (charges.empty() || out.charge_balance_norm <= charge_tolerance)
        && !pure_density_distance_rejected;
    if (!charges.empty() && out.charge_balance_norm > charge_tolerance) {
        out.rejection_reason = "charge_balance";
    } else if (!out.accepted && out.phase_amount_total_norm > phase_total_tolerance) {
        out.rejection_reason = "phase_amount_total";
    } else if (!out.accepted && out.fixed_composition_norm > phase_total_tolerance) {
        out.rejection_reason = "fixed_composition";
    } else if (local_postsolve_accepted && pure_density_distance_rejected) {
        out.rejection_reason = "phase_distance";
    }
    return out;
}

NeutralTwoPhaseEosPostsolve fixed_temperature_pressure_flash_postsolve(
    const add_args& args,
    double temperature,
    double pressure,
    const std::vector<std::vector<double>>& phase_amounts,
    const std::vector<double>& volumes,
    const std::vector<double>& feed_amounts,
    double material_tolerance,
    double pressure_tolerance,
    double chemical_potential_tolerance,
    double phase_distance_tolerance,
    bool stability_certification_required = false
) {
    NeutralTwoPhaseEosPostsolve out = evaluate_neutral_two_phase_eos_postsolve(
        args,
        temperature,
        pressure,
        phase_amounts,
        volumes,
        feed_amounts,
        material_tolerance,
        pressure_tolerance,
        chemical_potential_tolerance,
        phase_distance_tolerance,
        {},
        false,
        stability_certification_required,
        {0, 1}
    );
    apply_route_metadata(out, fixed_temperature_pressure_flash_route_metadata());
    return out;
}

// AlgID: bubble_dew_ipopt
NeutralTwoPhaseEosRouteResult solve_pressure_route(
    const add_args& args,
    double temperature,
    const std::vector<double>& fixed_composition,
    int fixed_phase_index,
    const std::string& problem_name,
    const std::vector<double>& charges,
    const IpoptSolveOptions& options,
    double phase_total_tolerance,
    double pressure_tolerance,
    double charge_tolerance,
    double chemical_potential_tolerance,
    double phase_distance_tolerance
) {
    const IpoptAdapterInfo adapter = native_ipopt_adapter_info();
    NeutralTwoPhaseEosRouteResult best;
    best.compiled = adapter.compiled;
    best.adapter_available = adapter.adapter_available;
    best.adapter_kind = adapter.adapter_kind;
    best.exact_gradient_required = adapter.exact_gradient_required;
    best.exact_jacobian_required = adapter.exact_jacobian_required;
    best.problem_name = problem_name;
    apply_route_metadata(best, fixed_temperature_pressure_route_metadata(!charges.empty()));
    if (!adapter.compiled) {
        mark_neutral_route_ipopt_dependency_required(best);
        return best;
    }

    const std::vector<double> normalized_composition =
        normalized_positive_values(fixed_composition, problem_name + " composition");
    const std::vector<NamedInitialVariables> seeds = pressure_route_seed_candidates(
        args,
        normalized_composition,
        fixed_phase_index,
        temperature,
        charges,
        problem_name
    );
    bool have_best = false;
    std::vector<RouteSeedAttempt> attempts;
    attempts.reserve(seeds.size() + (options.initial_variables.empty() ? 0 : 1));

    auto run_attempt = [&](const std::string& seed_name, const IpoptSolveOptions& attempt_options) {
        NeutralFixedTemperaturePressureProblem problem(
            args,
            temperature,
            normalized_composition,
            fixed_phase_index,
            problem_name,
            charges,
            charge_tolerance,
            attempt_options.initial_variables.empty() ? kInitialPressure : attempt_options.initial_variables.back()
        );
        const IpoptSolveResult solve = solve_ipopt_nlp(problem, attempt_options);
        NeutralTwoPhaseEosRouteResult result;
        result.compiled = adapter.compiled;
        result.adapter_available = adapter.adapter_available;
        result.adapter_kind = adapter.adapter_kind;
        result.exact_gradient_required = adapter.exact_gradient_required;
        result.exact_jacobian_required = adapter.exact_jacobian_required;
        result.problem_name = problem_name;
        result.initial_point_strategy = "deterministic_seed_sweep";
        result.seed_name = seed_name;
        const bool can_postsolve = apply_neutral_route_solve_result(result, solve);
        if (!can_postsolve) {
            attempts.push_back(neutral_seed_attempt_from_result(result));
            if (!have_best || neutral_boundary_route_quality(result) > neutral_boundary_route_quality(best)) {
                best = result;
                have_best = true;
            }
            return result;
        }

        const int species_count = problem.species_count();
        result.phase_amounts = pressure_route_phase_amounts(solve.variables, species_count);
        result.phase_volumes = pressure_route_phase_volumes(solve.variables, species_count);
        NeutralTwoPhaseEosPostsolve postsolve = fixed_temperature_pressure_postsolve(
            args,
            temperature,
            solve.variables.back(),
            result.phase_amounts,
            result.phase_volumes,
            fixed_phase_index,
            normalized_composition,
            charges,
            phase_total_tolerance,
            pressure_tolerance,
            charge_tolerance,
            chemical_potential_tolerance,
            phase_distance_tolerance,
            problem_name
        );
        apply_neutral_route_postsolve(
            result,
            std::move(postsolve),
            NeutralRouteCertificationLevel::LocalPostsolve
        );
        attempts.push_back(neutral_seed_attempt_from_result(result));
        if (!have_best || neutral_boundary_route_quality(result) > neutral_boundary_route_quality(best)) {
            best = result;
            have_best = true;
        }
        return result;
    };

    if (!options.initial_variables.empty()) {
        const NeutralTwoPhaseEosRouteResult continuation = run_attempt("continuation_state", options);
        if (neutral_route_strict_ipopt_success(continuation)) {
            best.seed_attempts = attempts;
            return best;
        }
    }

    for (const auto& seed : seeds) {
        IpoptSolveOptions attempt_options = options;
        attempt_options.initial_variables = seed.variables;
        attempt_options.initial_bound_lower_multipliers.clear();
        attempt_options.initial_bound_upper_multipliers.clear();
        attempt_options.initial_constraint_multipliers.clear();
        const NeutralTwoPhaseEosRouteResult attempt = run_attempt(seed.seed_name, attempt_options);
        if (neutral_route_strict_ipopt_success(attempt)) {
            break;
        }
    }

    best.initial_point_strategy = "deterministic_seed_sweep";
    best.seed_attempts = attempts;
    return best;
}

// AlgID: bubble_dew_ipopt
NeutralTwoPhaseEosRouteResult solve_temperature_route(
    const add_args& args,
    double target_pressure,
    const std::vector<double>& fixed_composition,
    int fixed_phase_index,
    const std::string& problem_name,
    const std::vector<double>& charges,
    const IpoptSolveOptions& options,
    double phase_total_tolerance,
    double pressure_tolerance,
    double charge_tolerance,
    double chemical_potential_tolerance,
    double phase_distance_tolerance
) {
    const IpoptAdapterInfo adapter = native_ipopt_adapter_info();
    NeutralTwoPhaseEosRouteResult best;
    best.compiled = adapter.compiled;
    best.adapter_available = adapter.adapter_available;
    best.adapter_kind = adapter.adapter_kind;
    best.exact_gradient_required = adapter.exact_gradient_required;
    best.exact_jacobian_required = adapter.exact_jacobian_required;
    best.problem_name = problem_name;
    apply_route_metadata(best, fixed_pressure_temperature_route_metadata(!charges.empty()));
    if (!adapter.compiled) {
        mark_neutral_route_ipopt_dependency_required(best);
        return best;
    }

    const std::vector<double> normalized_composition =
        normalized_positive_values(fixed_composition, problem_name + " composition");
    const std::vector<NamedInitialVariables> seeds = temperature_route_seed_candidates(
        args,
        normalized_composition,
        fixed_phase_index,
        target_pressure,
        charges,
        problem_name
    );
    bool have_best = false;
    std::vector<RouteSeedAttempt> attempts;
    attempts.reserve(seeds.size() + (options.initial_variables.empty() ? 0 : 1));

    auto run_attempt = [&](const std::string& seed_name, const IpoptSolveOptions& attempt_options) {
        auto physical_problem = std::make_unique<NeutralFixedPressureTemperatureProblem>(
            args,
            target_pressure,
            normalized_composition,
            fixed_phase_index,
            problem_name,
            charges,
            charge_tolerance
        );
        const int species_count = physical_problem->species_count();
        const bool transformed_electrolyte_temperature_route = !charges.empty();
        std::unique_ptr<NlpProblem> problem;
        if (transformed_electrolyte_temperature_route) {
            problem = std::make_unique<PositiveLogNlpProblem>(std::move(physical_problem));
        } else {
            problem = std::move(physical_problem);
        }
        validate_nlp_problem_shape(*problem);
        IpoptSolveOptions route_options = attempt_options;
        if (transformed_electrolyte_temperature_route && !route_options.initial_variables.empty()) {
            route_options.initial_variables = log_positive_variables(
                route_options.initial_variables,
                problem_name + " electrolyte temperature-route initial variable"
            );
        }
        IpoptSolveResult solve = solve_ipopt_nlp(*problem, route_options);
        if (transformed_electrolyte_temperature_route
            && solve.variables.size() == static_cast<std::size_t>(problem->variable_count())) {
            solve.variables = static_cast<PositiveLogNlpProblem&>(*problem).physical_variables_from_solver(
                solve.variables
            );
        }
        NeutralTwoPhaseEosRouteResult result;
        result.compiled = adapter.compiled;
        result.adapter_available = adapter.adapter_available;
        result.adapter_kind = adapter.adapter_kind;
        result.exact_gradient_required = adapter.exact_gradient_required;
        result.exact_jacobian_required = adapter.exact_jacobian_required;
        result.problem_name = problem_name;
        result.initial_point_strategy = "deterministic_seed_sweep";
        result.seed_name = seed_name;
        const bool can_postsolve = apply_neutral_route_solve_result(result, solve);
        if (!can_postsolve) {
            attempts.push_back(neutral_seed_attempt_from_result(result));
            if (!have_best || neutral_boundary_route_quality(result) > neutral_boundary_route_quality(best)) {
                best = result;
                have_best = true;
            }
            return result;
        }

        const double solved_temperature = solve.variables.back();
        result.phase_amounts = pressure_route_phase_amounts(solve.variables, species_count);
        result.phase_volumes = pressure_route_phase_volumes(solve.variables, species_count);
        NeutralTwoPhaseEosPostsolve postsolve = fixed_temperature_pressure_postsolve(
            args,
            solved_temperature,
            target_pressure,
            result.phase_amounts,
            result.phase_volumes,
            fixed_phase_index,
            normalized_composition,
            charges,
            phase_total_tolerance,
            pressure_tolerance,
            charge_tolerance,
            chemical_potential_tolerance,
            phase_distance_tolerance,
            problem_name
        );
        apply_neutral_route_postsolve(
            result,
            std::move(postsolve),
            NeutralRouteCertificationLevel::LocalPostsolve
        );
        attempts.push_back(neutral_seed_attempt_from_result(result));
        if (!have_best || neutral_boundary_route_quality(result) > neutral_boundary_route_quality(best)) {
            best = result;
            have_best = true;
        }
        return result;
    };

    if (!options.initial_variables.empty()) {
        const NeutralTwoPhaseEosRouteResult continuation = run_attempt("continuation_state", options);
        if (neutral_route_strict_ipopt_success(continuation)) {
            best.seed_attempts = attempts;
            return best;
        }
    }

    for (const auto& seed : seeds) {
        IpoptSolveOptions attempt_options = options;
        attempt_options.initial_variables = seed.variables;
        attempt_options.initial_bound_lower_multipliers.clear();
        attempt_options.initial_bound_upper_multipliers.clear();
        attempt_options.initial_constraint_multipliers.clear();
        const NeutralTwoPhaseEosRouteResult attempt = run_attempt(seed.seed_name, attempt_options);
        if (neutral_route_strict_ipopt_success(attempt)) {
            break;
        }
    }

    best.initial_point_strategy = "deterministic_seed_sweep";
    best.seed_attempts = attempts;
    return best;
}

// AlgID: neutral_tp_flash_ipopt
NeutralTwoPhaseEosRouteResult solve_flash_route(
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
    const std::string problem_name = "neutral_tp_flash_eos";
    const IpoptAdapterInfo adapter = native_ipopt_adapter_info();
    NeutralTwoPhaseEosRouteResult best;
    best.compiled = adapter.compiled;
    best.adapter_available = adapter.adapter_available;
    best.adapter_kind = adapter.adapter_kind;
    best.exact_gradient_required = adapter.exact_gradient_required;
    best.exact_jacobian_required = adapter.exact_jacobian_required;
    best.problem_name = problem_name;
    apply_route_metadata(best, fixed_temperature_pressure_flash_route_metadata());
    if (!adapter.compiled) {
        mark_neutral_route_ipopt_dependency_required(best);
        return best;
    }

    const std::vector<double> normalized_feed =
        normalized_positive_values(feed_composition, problem_name + " feed composition");
    const std::vector<double> feed_amounts = [&]() {
        std::vector<double> out;
        out.reserve(normalized_feed.size());
        for (double value : normalized_feed) {
            out.push_back(kTwoPhaseFlashFeedBasis * value);
        }
        return out;
    }();
    const std::vector<NamedInitialVariables> seeds = flash_route_seed_candidates(
        args,
        normalized_feed,
        temperature,
        target_pressure,
        problem_name
    );
    bool have_best = false;
    std::vector<RouteSeedAttempt> attempts;
    attempts.reserve(seeds.size() + (options.initial_variables.empty() ? 0 : 1));

    auto run_attempt = [&](const std::string& seed_name, const IpoptSolveOptions& attempt_options) {
        NeutralFixedTemperaturePressureFlashProblem problem(
            args,
            temperature,
            target_pressure,
            normalized_feed,
            problem_name
        );
        const IpoptSolveResult solve = solve_ipopt_nlp(problem, attempt_options);
        NeutralTwoPhaseEosRouteResult result;
        result.compiled = adapter.compiled;
        result.adapter_available = adapter.adapter_available;
        result.adapter_kind = adapter.adapter_kind;
        result.exact_gradient_required = adapter.exact_gradient_required;
        result.exact_jacobian_required = adapter.exact_jacobian_required;
        result.problem_name = problem_name;
        result.initial_point_strategy = "deterministic_seed_sweep";
        result.seed_name = seed_name;
        const bool can_postsolve = apply_neutral_route_solve_result(result, solve);
        if (!can_postsolve) {
            attempts.push_back(neutral_seed_attempt_from_result(result));
            if (!have_best || neutral_route_quality(result) > neutral_route_quality(best)) {
                best = result;
                have_best = true;
            }
            return result;
        }

        const int species_count = problem.species_count();
        result.phase_amounts = flash_route_phase_amounts(solve.variables, species_count);
        result.phase_volumes = flash_route_phase_volumes(solve.variables, species_count);
        NeutralTwoPhaseEosPostsolve postsolve = fixed_temperature_pressure_flash_postsolve(
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
            true
        );
        apply_neutral_route_postsolve(
            result,
            std::move(postsolve),
            NeutralRouteCertificationLevel::PhaseSetCertified
        );
        attempts.push_back(neutral_seed_attempt_from_result(result));
        if (!have_best || neutral_route_quality(result) > neutral_route_quality(best)) {
            best = result;
            have_best = true;
        }
        return result;
    };

    if (!options.initial_variables.empty()) {
        const NeutralTwoPhaseEosRouteResult continuation = run_attempt("continuation_state", options);
        if (continuation.accepted) {
            best.seed_attempts = attempts;
            return best;
        }
    }

    if (seeds.empty()) {
        throw ValueError(problem_name + " could not construct a deterministic flash seed.");
    }
    for (const auto& seed : seeds) {
        IpoptSolveOptions attempt_options = options;
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

std::vector<std::vector<double>> activated_phase_amounts(
    const std::vector<double>& variables,
    const epcsaft::native::equilibrium::VariableLayout& layout
) {
    require_size(
        variables,
        static_cast<std::size_t>(layout.variable_count),
        "Activated neutral TP flash variable"
    );
    std::vector<std::vector<double>> out(
        static_cast<std::size_t>(layout.phase_count),
        std::vector<double>(static_cast<std::size_t>(layout.species_count), 0.0)
    );
    for (int phase = 0; phase < layout.phase_count; ++phase) {
        for (int species = 0; species < layout.species_count; ++species) {
            out[static_cast<std::size_t>(phase)][static_cast<std::size_t>(species)] =
                variables[static_cast<std::size_t>(layout.phase_amount_index(phase, species))];
        }
    }
    return out;
}

std::vector<double> activated_phase_volumes(
    const std::vector<double>& variables,
    const epcsaft::native::equilibrium::VariableLayout& layout
) {
    require_size(
        variables,
        static_cast<std::size_t>(layout.variable_count),
        "Activated neutral TP flash variable"
    );
    std::vector<double> out(static_cast<std::size_t>(layout.phase_count), 0.0);
    for (int phase = 0; phase < layout.phase_count; ++phase) {
        out[static_cast<std::size_t>(phase)] =
            variables[static_cast<std::size_t>(layout.phase_volume_index(phase))];
    }
    return out;
}

NeutralTwoPhaseEosRouteResult solve_activated_flash_route(
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
    const std::string problem_name = "neutral_tp_flash_eos";
    const epcsaft::native::equilibrium::ActivationPlan plan =
        epcsaft::native::equilibrium::build_neutral_tp_flash_activation_plan(
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
    apply_route_metadata(best, fixed_temperature_pressure_flash_route_metadata());
    if (!adapter.compiled) {
        mark_neutral_route_ipopt_dependency_required(best);
        return best;
    }

    const std::vector<double>& normalized_feed = plan.feed_composition;
    const std::vector<double> feed_amounts = [&]() {
        std::vector<double> out;
        out.reserve(normalized_feed.size());
        for (double value : normalized_feed) {
            out.push_back(kTwoPhaseFlashFeedBasis * value);
        }
        return out;
    }();
    const std::vector<NamedInitialVariables> seeds = flash_route_seed_candidates(
        args,
        normalized_feed,
        temperature,
        target_pressure,
        problem_name
    );
    bool have_best = false;
    std::vector<RouteSeedAttempt> attempts;
    attempts.reserve(seeds.size() + (options.initial_variables.empty() ? 0 : 1));

    auto run_attempt = [&](const std::string& seed_name, const IpoptSolveOptions& attempt_options) {
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
        apply_route_metadata(result, fixed_temperature_pressure_flash_route_metadata());
        if (!can_postsolve) {
            attempts.push_back(neutral_seed_attempt_from_result(result));
            if (!have_best || neutral_route_quality(result) > neutral_route_quality(best)) {
                best = result;
                have_best = true;
            }
            return result;
        }

        result.phase_amounts = activated_phase_amounts(solve.variables, layout);
        result.phase_volumes = activated_phase_volumes(solve.variables, layout);
        NeutralTwoPhaseEosPostsolve postsolve = fixed_temperature_pressure_flash_postsolve(
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
            true
        );
        apply_neutral_route_postsolve(
            result,
            std::move(postsolve),
            NeutralRouteCertificationLevel::PhaseSetCertified
        );
        attempts.push_back(neutral_seed_attempt_from_result(result));
        if (!have_best || neutral_route_quality(result) > neutral_route_quality(best)) {
            best = result;
            have_best = true;
        }
        return result;
    };

    if (!options.initial_variables.empty()) {
        const NeutralTwoPhaseEosRouteResult continuation = run_attempt("continuation_state", options);
        if (continuation.accepted) {
            best.seed_attempts = attempts;
            return best;
        }
    }

    if (seeds.empty()) {
        throw ValueError(problem_name + " could not construct a deterministic flash seed.");
    }
    for (const auto& seed : seeds) {
        IpoptSolveOptions attempt_options = options;
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

}  // namespace

std::unique_ptr<NlpProblem> make_neutral_tp_flash_eos_problem(
    const add_args& args,
    double temperature,
    double target_pressure,
    const std::vector<double>& feed_composition,
    const std::string& problem_name
) {
    return std::make_unique<NeutralFixedTemperaturePressureFlashProblem>(
        args,
        temperature,
        target_pressure,
        feed_composition,
        problem_name
    );
}

NeutralTwoPhaseEosNlpContract evaluate_neutral_bubble_p_eos_nlp_contract(
    const add_args& args,
    double temperature,
    const std::vector<double>& liquid_composition
) {
    NeutralFixedTemperaturePressureProblem problem(
        args,
        temperature,
        liquid_composition,
        0,
        "neutral_bubble_p_eos"
    );
    return make_contract(problem, problem.phase_count(), problem.species_count());
}

NeutralTwoPhaseEosNlpContract evaluate_neutral_dew_p_eos_nlp_contract(
    const add_args& args,
    double temperature,
    const std::vector<double>& vapor_composition
) {
    NeutralFixedTemperaturePressureProblem problem(
        args,
        temperature,
        vapor_composition,
        1,
        "neutral_dew_p_eos"
    );
    return make_contract(problem, problem.phase_count(), problem.species_count());
}

NeutralTwoPhaseEosNlpContract evaluate_neutral_bubble_t_eos_nlp_contract(
    const add_args& args,
    double target_pressure,
    const std::vector<double>& liquid_composition
) {
    NeutralFixedPressureTemperatureProblem problem(
        args,
        target_pressure,
        liquid_composition,
        0,
        "neutral_bubble_t_eos"
    );
    return make_contract(problem, problem.phase_count(), problem.species_count());
}

NeutralTwoPhaseEosNlpContract evaluate_neutral_dew_t_eos_nlp_contract(
    const add_args& args,
    double target_pressure,
    const std::vector<double>& vapor_composition
) {
    NeutralFixedPressureTemperatureProblem problem(
        args,
        target_pressure,
        vapor_composition,
        1,
        "neutral_dew_t_eos"
    );
    return make_contract(problem, problem.phase_count(), problem.species_count());
}

NeutralTwoPhaseEosNlpContract evaluate_neutral_tp_flash_eos_nlp_contract(
    const add_args& args,
    double temperature,
    double target_pressure,
    const std::vector<double>& feed_composition
) {
    NeutralFixedTemperaturePressureFlashProblem problem(
        args,
        temperature,
        target_pressure,
        feed_composition,
        "neutral_tp_flash_eos"
    );
    return make_contract(problem, problem.phase_count(), problem.species_count());
}

NeutralTwoPhaseEosNlpContract evaluate_neutral_single_component_vle_nlp_contract(
    const add_args& args,
    double temperature
) {
    if (args.m.size() != 1) {
        throw ValueError("single_component_vle requires exactly one component.");
    }
    NeutralFixedTemperaturePressureProblem problem(
        args,
        temperature,
        {1.0},
        0,
        "single_component_vle_eos"
    );
    return make_contract(problem, problem.phase_count(), problem.species_count());
}

NeutralTwoPhaseEosRouteResult solve_neutral_bubble_p_eos_route(
    const add_args& args,
    double temperature,
    const std::vector<double>& liquid_composition,
    const IpoptSolveOptions& options,
    double phase_total_tolerance,
    double pressure_tolerance,
    double chemical_potential_tolerance,
    double phase_distance_tolerance
) {
    return solve_pressure_route(
        args,
        temperature,
        liquid_composition,
        0,
        "neutral_bubble_p_eos",
        {},
        options,
        phase_total_tolerance,
        pressure_tolerance,
        0.0,
        chemical_potential_tolerance,
        phase_distance_tolerance
    );
}

NeutralTwoPhaseEosRouteResult solve_neutral_dew_p_eos_route(
    const add_args& args,
    double temperature,
    const std::vector<double>& vapor_composition,
    const IpoptSolveOptions& options,
    double phase_total_tolerance,
    double pressure_tolerance,
    double chemical_potential_tolerance,
    double phase_distance_tolerance
) {
    return solve_pressure_route(
        args,
        temperature,
        vapor_composition,
        1,
        "neutral_dew_p_eos",
        {},
        options,
        phase_total_tolerance,
        pressure_tolerance,
        0.0,
        chemical_potential_tolerance,
        phase_distance_tolerance
    );
}

NeutralTwoPhaseEosRouteResult solve_neutral_bubble_t_eos_route(
    const add_args& args,
    double target_pressure,
    const std::vector<double>& liquid_composition,
    const IpoptSolveOptions& options,
    double phase_total_tolerance,
    double pressure_tolerance,
    double chemical_potential_tolerance,
    double phase_distance_tolerance
) {
    return solve_temperature_route(
        args,
        target_pressure,
        liquid_composition,
        0,
        "neutral_bubble_t_eos",
        {},
        options,
        phase_total_tolerance,
        pressure_tolerance,
        0.0,
        chemical_potential_tolerance,
        phase_distance_tolerance
    );
}

NeutralTwoPhaseEosRouteResult solve_neutral_dew_t_eos_route(
    const add_args& args,
    double target_pressure,
    const std::vector<double>& vapor_composition,
    const IpoptSolveOptions& options,
    double phase_total_tolerance,
    double pressure_tolerance,
    double chemical_potential_tolerance,
    double phase_distance_tolerance
) {
    return solve_temperature_route(
        args,
        target_pressure,
        vapor_composition,
        1,
        "neutral_dew_t_eos",
        {},
        options,
        phase_total_tolerance,
        pressure_tolerance,
        0.0,
        chemical_potential_tolerance,
        phase_distance_tolerance
    );
}

NeutralTwoPhaseEosRouteResult solve_electrolyte_bubble_t_eos_route(
    const add_args& args,
    double target_pressure,
    const std::vector<double>& liquid_composition,
    const std::vector<double>& charges,
    const IpoptSolveOptions& options,
    double phase_total_tolerance,
    double pressure_tolerance,
    double charge_tolerance,
    double chemical_potential_tolerance,
    double phase_distance_tolerance
) {
    return solve_temperature_route(
        args,
        target_pressure,
        liquid_composition,
        0,
        "electrolyte_bubble_t_eos",
        charges,
        options,
        phase_total_tolerance,
        pressure_tolerance,
        charge_tolerance,
        chemical_potential_tolerance,
        phase_distance_tolerance
    );
}

NeutralTwoPhaseEosRouteResult solve_neutral_cloud_t_eos_route(
    const add_args& args,
    double target_pressure,
    const std::vector<double>& parent_liquid_composition,
    const IpoptSolveOptions& options,
    double phase_total_tolerance,
    double pressure_tolerance,
    double chemical_potential_tolerance,
    double phase_distance_tolerance
) {
    NeutralTwoPhaseEosRouteResult result = solve_temperature_route(
        args,
        target_pressure,
        parent_liquid_composition,
        0,
        kNeutralCloudTemperatureProblemName,
        {},
        options,
        phase_total_tolerance,
        pressure_tolerance,
        0.0,
        chemical_potential_tolerance,
        phase_distance_tolerance
    );
    result.phase_labels = {"parent_liquid", "shadow_liquid"};
    result.phase_roles = {"parent_liquid", "incipient_liquid"};
    return result;
}

NeutralTwoPhaseEosRouteResult solve_neutral_single_component_vle_route(
    const add_args& args,
    double temperature,
    const IpoptSolveOptions& options,
    double phase_total_tolerance,
    double pressure_tolerance,
    double chemical_potential_tolerance,
    double phase_distance_tolerance
) {
    if (args.m.size() != 1) {
        throw ValueError("single_component_vle requires exactly one component.");
    }
    return solve_pressure_route(
        args,
        temperature,
        {1.0},
        0,
        "single_component_vle_eos",
        {},
        options,
        phase_total_tolerance,
        pressure_tolerance,
        0.0,
        chemical_potential_tolerance,
        phase_distance_tolerance
    );
}

NeutralTwoPhaseEosRouteResult solve_neutral_tp_flash_eos_route(
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
    return solve_flash_route(
        args,
        temperature,
        target_pressure,
        feed_composition,
        options,
        material_tolerance,
        pressure_tolerance,
        chemical_potential_tolerance,
        phase_distance_tolerance
    );
}

NeutralTwoPhaseEosRouteResult solve_activated_neutral_tp_flash_eos_route(
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
    return solve_activated_flash_route(
        args,
        temperature,
        target_pressure,
        feed_composition,
        options,
        material_tolerance,
        pressure_tolerance,
        chemical_potential_tolerance,
        phase_distance_tolerance
    );
}

}  // namespace epcsaft::native::equilibrium_nlp
