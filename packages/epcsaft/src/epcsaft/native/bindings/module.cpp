#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include <cmath>
#include <map>
#include <memory>
#include <string>
#include <vector>

#include "autodiff/cppad_smoke_checks.h"
#include "bindings/payload_converters.h"
#include "bindings/resolved_input_bindings.h"
#include "eos/core_internal.h"
#include "eos/contributions/contribution_internal.h"

namespace py = pybind11;

using namespace epcsaft::native::bindings;

PYBIND11_MODULE(_core, m) {
    m.doc() = "pybind11 native backend for epcsaft";

    py::register_exception<ValueError>(m, "NativeValueError");
    py::register_exception<SolutionError>(m, "NativeSolutionError");

    register_resolved_input_bindings(m);

    m.def("_native_cppad_smoke", []() {
        return cppad_smoke_to_dict(epcsaft::native::cppad_support::cppad_square_smoke_derivative(3.0));
    });
    m.def("_native_provider_sdk_contract", []() {
        py::dict out;
        const bool equilibrium_native_enabled = false;
        const bool regression_native_enabled = false;
        out["contract_id"] = "provider_native_sdk_v1";
        out["provider_api_contract_id"] = "provider_api_v1";
        out["owner_package"] = "epcsaft";
        out["native_target"] = "epcsaft_provider_native";
        out["cppad_status"] = epcsaft::native::cppad_support::cppad_build_status();
        out["required_native_dependencies"] = std::vector<std::string>{"cppad", "eigen"};
        out["forbidden_native_dependencies"] = std::vector<std::string>{"ceres", "ipopt"};
        out["extension_consumers"] = std::vector<std::string>{"epcsaft-equilibrium", "epcsaft-regression"};
        out["equilibrium_native_enabled"] = equilibrium_native_enabled;
        out["regression_native_enabled"] = regression_native_enabled;
        out["provider_only_core"] = !equilibrium_native_enabled && !regression_native_enabled;
        return out;
    });
    m.def("_native_cppad_eos_contributions", [](double t, double rho, const std::vector<double>& x, const std::shared_ptr<ProviderResolvedInputHandleV1>& handle) {
        const SnapshotParameterAccessV1 input(handle->snapshot());
        return cppad_smoke_to_dict(cppad_eos_contribution_derivatives_cpp(t, rho, x, input));
    });
    m.def(
        "_native_association_site_fraction_solve",
        [](const std::vector<double>& delta_ij,
           double rho,
           const std::vector<double>& x_assoc,
           int max_iterations,
           double update_tolerance,
           double residual_tolerance) {
            return association_solve_result_to_dict(
                association_site_fraction_solve_result_cpp(
                    delta_ij,
                    rho,
                    x_assoc,
                    max_iterations,
                    update_tolerance,
                    residual_tolerance
                )
            );
        },
        py::arg("delta_ij"),
        py::arg("rho"),
        py::arg("x_assoc"),
        py::arg("max_iterations") = 100,
        py::arg("update_tolerance") = 1.0e-15,
        py::arg("residual_tolerance") = 1.0e-10
    );
    m.def("_native_cppad_pressure_density", [](double t, double rho, const std::vector<double>& x, const std::shared_ptr<ProviderResolvedInputHandleV1>& handle) {
        const SnapshotParameterAccessV1 input(handle->snapshot());
        return cppad_smoke_to_dict(cppad_pressure_density_derivative_cpp(t, rho, x, input));
    });
    m.def("_native_phase_state_ln_fugacity_composition_sensitivity", [](
        double t,
        double p,
        const std::vector<double>& x,
        int phase,
        const std::shared_ptr<ProviderResolvedInputHandleV1>& handle
    ) {
        const SnapshotParameterAccessV1 input(handle->snapshot());
        return phase_state_sensitivity_to_dict(
            phase_state_ln_fugacity_composition_sensitivity_cpp(t, p, x, phase, input)
        );
    });
    m.def("_native_cppad_pure_neutral_parameters", [](double t, double rho, const std::shared_ptr<ProviderResolvedInputHandleV1>& handle) {
        const SnapshotParameterAccessV1 input(handle->snapshot());
        return cppad_smoke_to_dict(cppad_pure_neutral_parameter_derivatives_cpp(t, rho, input));
    });
    m.def("_native_cppad_association_component_parameters", [](
        double t,
        double rho,
        const std::vector<double>& x,
        const std::shared_ptr<ProviderResolvedInputHandleV1>& handle,
        int component_index
    ) {
        const SnapshotParameterAccessV1 input(handle->snapshot());
        NeutralBinaryKijPhaseDerivatives e_assoc =
            generic_component_parameter_phase_derivatives_cpp(t, rho, x, input, 3, component_index);
        NeutralBinaryKijPhaseDerivatives vol_a =
            generic_component_parameter_phase_derivatives_cpp(t, rho, x, input, 4, component_index);
        return association_component_parameter_derivatives_to_dict(e_assoc, vol_a);
    });
    m.def("_native_cppad_neutral_binary_kij_properties", [](double t, double rho, const std::vector<double>& x, const std::shared_ptr<ProviderResolvedInputHandleV1>& handle) {
        const SnapshotParameterAccessV1 input(handle->snapshot());
        NeutralBinaryKijPhaseDerivatives forward = neutral_binary_pair_parameter_phase_derivatives_cpp(t, rho, x, input, 1, "k_ij");
        NeutralBinaryKijPhaseDerivatives reverse = neutral_binary_pair_parameter_phase_derivatives_cpp(t, rho, x, input, 2, "k_ij");
        return neutral_binary_kij_property_derivatives_to_dict(forward, reverse);
    });
    m.def("_native_cppad_neutral_binary_pair_properties", [](double t, double rho, const std::vector<double>& x, const std::shared_ptr<ProviderResolvedInputHandleV1>& handle) {
        const SnapshotParameterAccessV1 input(handle->snapshot());
        NeutralBinaryKijPhaseDerivatives kij_forward = neutral_binary_pair_parameter_phase_derivatives_cpp(t, rho, x, input, 1, "k_ij");
        NeutralBinaryKijPhaseDerivatives kij_reverse = neutral_binary_pair_parameter_phase_derivatives_cpp(t, rho, x, input, 2, "k_ij");
        std::unique_ptr<NeutralBinaryKijPhaseDerivatives> lij_forward;
        std::unique_ptr<NeutralBinaryKijPhaseDerivatives> lij_reverse;
        std::unique_ptr<NeutralBinaryKijPhaseDerivatives> khb_forward;
        std::unique_ptr<NeutralBinaryKijPhaseDerivatives> khb_reverse;
        if (input.l_ij.size() == 4) {
            lij_forward = std::make_unique<NeutralBinaryKijPhaseDerivatives>(
                neutral_binary_pair_parameter_phase_derivatives_cpp(t, rho, x, input, 1, "l_ij")
            );
            lij_reverse = std::make_unique<NeutralBinaryKijPhaseDerivatives>(
                neutral_binary_pair_parameter_phase_derivatives_cpp(t, rho, x, input, 2, "l_ij")
            );
        }
        if (input.k_hb.size() == 4) {
            khb_forward = std::make_unique<NeutralBinaryKijPhaseDerivatives>(
                neutral_binary_pair_parameter_phase_derivatives_cpp(t, rho, x, input, 1, "k_hb_ij")
            );
            khb_reverse = std::make_unique<NeutralBinaryKijPhaseDerivatives>(
                neutral_binary_pair_parameter_phase_derivatives_cpp(t, rho, x, input, 2, "k_hb_ij")
            );
        }
        return neutral_binary_pair_property_derivatives_to_dict(
            kij_forward,
            kij_reverse,
            lij_forward.get(),
            lij_reverse.get(),
            khb_forward.get(),
            khb_reverse.get()
        );
    });

    py::class_<ScalarContributionTerms>(m, "ScalarContributionTerms")
        .def_readonly("hc", &ScalarContributionTerms::hc)
        .def_readonly("disp", &ScalarContributionTerms::disp)
        .def_readonly("assoc", &ScalarContributionTerms::assoc)
        .def_readonly("ion", &ScalarContributionTerms::ion)
        .def_readonly("born", &ScalarContributionTerms::born)
        .def_readonly("total", &ScalarContributionTerms::total);

    py::class_<CompressibilityFactorResult>(m, "CompressibilityFactorResult")
        .def_readonly("raw", &CompressibilityFactorResult::raw)
        .def_readonly("terms", &CompressibilityFactorResult::terms);

    py::class_<VectorContributionTerms>(m, "VectorContributionTerms")
        .def_readonly("hc", &VectorContributionTerms::hc)
        .def_readonly("disp", &VectorContributionTerms::disp)
        .def_readonly("assoc", &VectorContributionTerms::assoc)
        .def_readonly("ion", &VectorContributionTerms::ion)
        .def_readonly("born", &VectorContributionTerms::born)
        .def_readonly("total", &VectorContributionTerms::total);

    py::class_<CompositionContributionResult>(m, "CompositionContributionResult")
        .def_readonly("dadx", &CompositionContributionResult::dadx)
        .def_readonly("ares", &CompositionContributionResult::ares)
        .def_readonly("sum_x_dadx", &CompositionContributionResult::sum_x_dadx)
        .def_readonly("z_raw", &CompositionContributionResult::z_raw)
        .def_readonly("z", &CompositionContributionResult::z)
        .def_readonly("derivative_backend", &CompositionContributionResult::derivative_backend)
        .def_readonly("derivative_available", &CompositionContributionResult::derivative_available);

    py::class_<ResidualChemicalPotentialResult>(m, "ResidualChemicalPotentialResult")
        .def_readonly("mu", &ResidualChemicalPotentialResult::mu)
        .def_readonly("composition", &ResidualChemicalPotentialResult::composition);

    py::class_<FugacityContributionResult>(m, "FugacityContributionResult")
        .def_readonly("mu", &FugacityContributionResult::mu)
        .def_readonly("lnfugcoef", &FugacityContributionResult::lnfugcoef)
        .def_readonly("composition", &FugacityContributionResult::composition);

    py::class_<ActivityCoefficientNative>(m, "ActivityCoefficientNative")
        .def_readonly("component_activity_coefficients", &ActivityCoefficientNative::component_activity_coefficients)
        .def_readonly("mean_ionic_activity_coefficients_mole_fraction", &ActivityCoefficientNative::mean_ionic_activity_coefficients_mole_fraction)
        .def_readonly("mean_ionic_activity_coefficients_molality", &ActivityCoefficientNative::mean_ionic_activity_coefficients_molality)
        .def_readonly("solvation_free_energy", &ActivityCoefficientNative::solvation_free_energy)
        .def_readonly("pair_molality", &ActivityCoefficientNative::pair_molality)
        .def_readonly("pair_conversion_factor", &ActivityCoefficientNative::pair_conversion_factor)
        .def_readonly("cation_indices", &ActivityCoefficientNative::cation_indices)
        .def_readonly("anion_indices", &ActivityCoefficientNative::anion_indices)
        .def_readonly("solvent_indices", &ActivityCoefficientNative::solvent_indices)
        .def_readonly("pair_cation_indices", &ActivityCoefficientNative::pair_cation_indices)
        .def_readonly("pair_anion_indices", &ActivityCoefficientNative::pair_anion_indices)
        .def_readonly("pair_nu_cation", &ActivityCoefficientNative::pair_nu_cation)
        .def_readonly("pair_nu_anion", &ActivityCoefficientNative::pair_nu_anion)
        .def_readonly("solvent_index", &ActivityCoefficientNative::solvent_index)
        .def_readonly("osmotic_coefficient", &ActivityCoefficientNative::osmotic_coefficient);

    py::class_<ePCSAFTMixtureNative, std::shared_ptr<ePCSAFTMixtureNative>>(m, "NativeMixture")
        .def(py::init<std::shared_ptr<ProviderResolvedInputHandleV1>>())
        .def("ncomp", &ePCSAFTMixtureNative::ncomp)
        .def("clear_runtime_caches", &ePCSAFTMixtureNative::clear_runtime_caches)
        .def("reset_runtime_cache_stats", &ePCSAFTMixtureNative::reset_runtime_cache_stats)
        .def("reference_state_cache_hits", &ePCSAFTMixtureNative::reference_state_cache_hits)
        .def("reference_state_cache_misses", &ePCSAFTMixtureNative::reference_state_cache_misses)
        .def("density_warm_start_hits", &ePCSAFTMixtureNative::density_warm_start_hits)
        .def("density_warm_start_rejections", &ePCSAFTMixtureNative::density_warm_start_rejections)
        .def("last_density_diagnostics", [](const ePCSAFTMixtureNative& mixture) {
            return native_density_failure_payload(mixture.last_density_diagnostics());
        });

    py::class_<ePCSAFTStateNative, std::shared_ptr<ePCSAFTStateNative>>(m, "NativeState")
        .def(py::init<
             std::shared_ptr<ePCSAFTMixtureNative>,
             double,
             std::vector<double>,
             int,
             bool,
             double,
             bool,
             double,
             bool,
             double>())
        .def("temperature", &ePCSAFTStateNative::temperature)
        .def("phase", &ePCSAFTStateNative::phase)
        .def("composition", &ePCSAFTStateNative::composition)
        .def("configuration_fingerprint", &ePCSAFTStateNative::configuration_fingerprint)
        .def("pressure", &ePCSAFTStateNative::pressure)
        .def("density", &ePCSAFTStateNative::density)
        .def("compressibility_factor", &ePCSAFTStateNative::compressibility_factor)
        .def("compressibility_factor_result", &ePCSAFTStateNative::compressibility_factor_result)
        .def("residual_helmholtz", &ePCSAFTStateNative::residual_helmholtz)
        .def("residual_helmholtz_result", &ePCSAFTStateNative::residual_helmholtz_result)
        .def("temperature_derivative_residual_helmholtz", &ePCSAFTStateNative::temperature_derivative_residual_helmholtz)
        .def("temperature_derivative_residual_helmholtz_result", &ePCSAFTStateNative::temperature_derivative_residual_helmholtz_result)
        .def("residual_enthalpy", &ePCSAFTStateNative::residual_enthalpy)
        .def("residual_entropy", &ePCSAFTStateNative::residual_entropy)
        .def("residual_gibbs", &ePCSAFTStateNative::residual_gibbs)
        .def("residual_chemical_potential", &ePCSAFTStateNative::residual_chemical_potential)
        .def("residual_chemical_potential_result", &ePCSAFTStateNative::residual_chemical_potential_result)
        .def("composition_derivative_residual_helmholtz_result", &ePCSAFTStateNative::composition_derivative_residual_helmholtz_result)
        .def("ln_fugacity_coefficient", &ePCSAFTStateNative::ln_fugacity_coefficient)
        .def("fugacity_coefficient", &ePCSAFTStateNative::fugacity_coefficient)
        .def("fugacity_coefficient_result", &ePCSAFTStateNative::fugacity_coefficient_result)
        .def("born_parameter_derivatives", [](ePCSAFTStateNative& state) {
            return born_parameter_derivative_to_dict(state.born_parameter_derivatives());
        })
        .def("relative_permittivity", &ePCSAFTStateNative::relative_permittivity)
        .def("osmotic_coefficient", &ePCSAFTStateNative::osmotic_coefficient)
        .def("solvation_free_energy", &ePCSAFTStateNative::solvation_free_energy)
        .def(
            "activity_coefficient_native",
            &ePCSAFTStateNative::activity_coefficient_native,
            py::arg("include_aux") = true,
            py::arg("has_solvent_override") = false,
            py::arg("solvent_override_index") = -1
        );

}
