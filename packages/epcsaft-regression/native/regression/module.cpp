#include <pybind11/numpy.h>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include <cmath>
#include <stdexcept>
#include <string>
#include <vector>

#include "model/native_types.h"

namespace py = pybind11;

namespace {

std::vector<double> array_to_double_vector(const py::array& array) {
    py::array_t<double, py::array::forcecast> casted(array);
    py::buffer_info info = casted.request();
    const auto* data = static_cast<const double*>(info.ptr);
    std::size_t size = 1;
    for (py::ssize_t dim : info.shape) {
        size *= static_cast<std::size_t>(dim);
    }
    return std::vector<double>(data, data + size);
}

std::vector<int> array_to_int_vector(const py::array& array) {
    py::array_t<int, py::array::forcecast> casted(array);
    py::buffer_info info = casted.request();
    const auto* data = static_cast<const int*>(info.ptr);
    std::size_t size = 1;
    for (py::ssize_t dim : info.shape) {
        size *= static_cast<std::size_t>(dim);
    }
    return std::vector<int>(data, data + size);
}

std::vector<PureNeutralRegressionDensityRecord> density_records_from_arrays(
    const py::array& density_t,
    const py::array& density_p,
    const py::array& density_rho_exp,
    const py::array& density_phase
) {
    auto t = array_to_double_vector(density_t);
    auto p = array_to_double_vector(density_p);
    auto rho = array_to_double_vector(density_rho_exp);
    auto phase = array_to_int_vector(density_phase);
    if (t.size() != p.size() || t.size() != rho.size() || t.size() != phase.size()) {
        throw std::invalid_argument("density record arrays must have matching lengths");
    }
    std::vector<PureNeutralRegressionDensityRecord> records;
    records.reserve(t.size());
    for (std::size_t i = 0; i < t.size(); ++i) {
        PureNeutralRegressionDensityRecord record;
        record.t = t[i];
        record.p = p[i];
        record.rho_exp = rho[i];
        record.phase = phase[i];
        records.push_back(record);
    }
    return records;
}

std::vector<PureNeutralRegressionVLERecord> vle_records_from_arrays(
    const py::array& vle_t,
    const py::array& vle_p
) {
    auto t = array_to_double_vector(vle_t);
    auto p = array_to_double_vector(vle_p);
    if (t.size() != p.size()) {
        throw std::invalid_argument("pure VLE record arrays must have matching lengths");
    }
    std::vector<PureNeutralRegressionVLERecord> records;
    records.reserve(t.size());
    for (std::size_t i = 0; i < t.size(); ++i) {
        PureNeutralRegressionVLERecord record;
        record.t = t[i];
        record.p = p[i];
        records.push_back(record);
    }
    return records;
}

py::dict regression_result_to_dict(const PureNeutralRegressionResult& result) {
    py::dict out;
    out["x"] = result.x;
    out["cost"] = result.cost;
    out["residual_norm"] = result.residual_norm;
    out["density_metric"] = result.density_metric;
    out["pure_vle_metric"] = result.pure_vle_metric;
    out["initial_cost"] = result.initial_cost;
    out["initial_density_metric"] = result.initial_density_metric;
    out["initial_pure_vle_metric"] = result.initial_pure_vle_metric;
    out["success"] = result.success;
    out["status"] = result.status;
    out["nfev"] = result.nfev;
    out["iterations"] = result.iterations;
    out["starts_tried"] = result.starts_tried;
    out["objective_evaluations"] = result.objective_evaluations;
    out["gradient_evaluations"] = result.gradient_evaluations;
    out["residual_evaluations"] = result.residual_evaluations;
    out["density_solves"] = result.density_solves;
    out["fused_state_evaluations"] = result.fused_state_evaluations;
    out["callback_wall_time_s"] = result.callback_wall_time_s;
    out["solve_wall_time_s"] = result.solve_wall_time_s;
    out["message"] = result.message;
    out["backend"] = result.backend;
    out["optimizer_backend"] = result.optimizer_backend.empty() ? result.backend : result.optimizer_backend;
    out["derivative_backend"] = result.derivative_backend.empty() ? result.jacobian_backend : result.derivative_backend;
    out["objective_initial"] = result.initial_cost;
    out["objective_final"] = result.cost;
    out["residual_norm_initial"] = std::sqrt(std::max(0.0, 2.0 * result.initial_cost));
    out["residual_norm_final"] = result.residual_norm;
    out["n_residual_evaluations"] = result.objective_evaluations;
    out["n_jacobian_evaluations"] = result.gradient_evaluations;
    out["gradient_norm"] = result.gradient_norm;
    out["step_norm"] = result.step_norm;
    out["python_objective_used"] = false;
    out["jacobian_available"] = result.jacobian_available;
    out["jacobian_backend"] = result.jacobian_backend;
    return out;
}

py::dict regression_debug_to_dict(const PureNeutralRegressionDebugResult& result) {
    py::dict out;
    out["objective"] = result.objective;
    out["gradient"] = result.gradient;
    out["residuals"] = result.residuals;
    out["jacobian_row_major"] = result.jacobian_row_major;
    out["jacobian_shape"] = py::make_tuple(result.jacobian_rows, result.jacobian_cols);
    out["jacobian_available"] = result.jacobian_available;
    out["jacobian_backend"] = result.jacobian_backend;
    out["density_raw_residuals"] = result.density_raw_residuals;
    out["pure_vle_raw_residuals"] = result.pure_vle_raw_residuals;
    out["residual_evaluations"] = result.residual_evaluations;
    out["density_solves"] = result.density_solves;
    out["fused_state_evaluations"] = result.fused_state_evaluations;
    out["callback_wall_time_s"] = result.callback_wall_time_s;
    return out;
}

py::dict generic_regression_result_to_dict(const GenericRegressionResult& result) {
    py::dict out;
    out["x"] = result.x;
    out["cost"] = result.cost;
    out["residual_norm"] = result.residual_norm;
    out["initial_cost"] = result.initial_cost;
    out["initial_residual_norm"] = result.initial_residual_norm;
    py::dict metrics;
    for (const auto& item : result.metrics_by_term) {
        metrics[py::str(item.first)] = item.second;
    }
    out["metrics_by_term"] = metrics;
    out["success"] = result.success;
    out["status"] = result.status;
    out["nfev"] = result.nfev;
    out["iterations"] = result.iterations;
    out["starts_tried"] = result.starts_tried;
    out["message"] = result.message;
    out["backend"] = result.backend;
    out["optimizer_backend"] = result.optimizer_backend;
    out["derivative_backend"] = result.derivative_backend;
    out["jacobian_available"] = result.jacobian_available;
    out["jacobian_backend"] = result.jacobian_backend;
    return out;
}

py::dict generic_regression_debug_to_dict(const GenericRegressionDebugResult& result) {
    py::dict out;
    out["cost"] = result.cost;
    out["residual_norm"] = result.residual_norm;
    out["residuals"] = result.residuals;
    py::dict metrics;
    for (const auto& item : result.metrics_by_term) {
        metrics[py::str(item.first)] = item.second;
    }
    out["metrics_by_term"] = metrics;
    out["jacobian_row_major"] = result.jacobian_row_major;
    out["jacobian_shape"] = py::make_tuple(result.jacobian_rows, result.jacobian_cols);
    out["jacobian_available"] = result.jacobian_available;
    out["jacobian_backend"] = result.jacobian_backend;
    return out;
}

GenericRegressionRecord generic_record_from_dict(const py::dict& input) {
    GenericRegressionRecord record;
    if (input.contains("term_name") && !input["term_name"].is_none()) {
        record.term_name = input["term_name"].cast<std::string>();
    }
    record.term = input["term"].cast<int>();
    record.t = input["T"].cast<double>();
    record.p = input["P"].cast<double>();
    record.phase = input.contains("phase") ? input["phase"].cast<int>() : 0;
    if (input.contains("x") && !input["x"].is_none()) {
        record.x = input["x"].cast<std::vector<double>>();
    }
    if (input.contains("y") && !input["y"].is_none()) {
        record.y = input["y"].cast<std::vector<double>>();
    }
    if (input.contains("target") && !input["target"].is_none()) {
        record.target = input["target"].cast<double>();
    }
    if (input.contains("target_index") && !input["target_index"].is_none()) {
        record.target_index = input["target_index"].cast<int>();
    }
    if (input.contains("target_index_2") && !input["target_index_2"].is_none()) {
        record.target_index_2 = input["target_index_2"].cast<int>();
    }
    if (input.contains("density_kind") && !input["density_kind"].is_none()) {
        record.density_kind = input["density_kind"].cast<int>();
    }
    if (input.contains("activity_basis") && !input["activity_basis"].is_none()) {
        record.activity_basis = input["activity_basis"].cast<int>();
    }
    if (input.contains("solvent_index") && !input["solvent_index"].is_none()) {
        record.solvent_index = input["solvent_index"].cast<int>();
    }
    if (input.contains("scale") && !input["scale"].is_none()) {
        record.scale = input["scale"].cast<double>();
    }
    return record;
}

std::vector<GenericRegressionRecord> generic_records_from_list(const py::list& records) {
    std::vector<GenericRegressionRecord> out;
    out.reserve(static_cast<std::size_t>(py::len(records)));
    for (py::handle item : records) {
        out.push_back(generic_record_from_dict(item.cast<py::dict>()));
    }
    return out;
}

std::vector<add_args> native_args_from_list(const py::list& args_by_record) {
    std::vector<add_args> out;
    out.reserve(static_cast<std::size_t>(py::len(args_by_record)));
    for (py::handle item : args_by_record) {
        out.push_back(item.cast<add_args>());
    }
    return out;
}

#ifdef EPCSAFT_HAS_CERES
py::dict fit_pure_neutral_native_ceres_binding(
    const add_args& args,
    const py::array& density_t,
    const py::array& density_p,
    const py::array& density_rho_exp,
    const py::array& density_phase,
    double density_scale,
    const py::array& vle_t,
    const py::array& vle_p,
    double pure_vle_scale,
    const py::array& x0,
    const py::array& lower,
    const py::array& upper
) {
    auto density_records = density_records_from_arrays(density_t, density_p, density_rho_exp, density_phase);
    auto pure_vle_records = vle_records_from_arrays(vle_t, vle_p);
    auto cpp_x0 = array_to_double_vector(x0);
    auto cpp_lower = array_to_double_vector(lower);
    auto cpp_upper = array_to_double_vector(upper);
    PureNeutralRegressionResult result;
    {
        py::gil_scoped_release release;
        result = fit_pure_neutral_ceres_cpp(
            args,
            density_records,
            density_scale,
            pure_vle_records,
            pure_vle_scale,
            cpp_x0,
            cpp_lower,
            cpp_upper
        );
    }
    return regression_result_to_dict(result);
}

py::dict evaluate_pure_neutral_objective_debug_binding(
    const add_args& args,
    const py::array& density_t,
    const py::array& density_p,
    const py::array& density_rho_exp,
    const py::array& density_phase,
    double density_scale,
    const py::array& vle_t,
    const py::array& vle_p,
    double pure_vle_scale,
    const py::array& x
) {
    auto density_records = density_records_from_arrays(density_t, density_p, density_rho_exp, density_phase);
    auto pure_vle_records = vle_records_from_arrays(vle_t, vle_p);
    auto cpp_x = array_to_double_vector(x);
    PureNeutralRegressionDebugResult result;
    {
        py::gil_scoped_release release;
        result = evaluate_pure_neutral_objective_debug_cpp(
            args,
            density_records,
            density_scale,
            pure_vle_records,
            pure_vle_scale,
            cpp_x
        );
    }
    return regression_debug_to_dict(result);
}

py::dict fit_generic_native_ceres_binding(
    const py::list& args_by_record,
    const py::list& records,
    const py::array& target_kinds,
    const py::array& target_indices,
    const py::array& target_indices_2,
    const py::array& x0,
    const py::array& lower,
    const py::array& upper,
    int max_nfev
) {
    auto cpp_args = native_args_from_list(args_by_record);
    auto cpp_records = generic_records_from_list(records);
    auto cpp_target_kinds = array_to_int_vector(target_kinds);
    auto cpp_target_indices = array_to_int_vector(target_indices);
    auto cpp_target_indices_2 = array_to_int_vector(target_indices_2);
    auto cpp_x0 = array_to_double_vector(x0);
    auto cpp_lower = array_to_double_vector(lower);
    auto cpp_upper = array_to_double_vector(upper);
    GenericRegressionResult result;
    {
        py::gil_scoped_release release;
        result = fit_generic_ceres_cpp(
            cpp_args,
            cpp_records,
            cpp_target_kinds,
            cpp_target_indices,
            cpp_target_indices_2,
            cpp_x0,
            cpp_lower,
            cpp_upper,
            max_nfev
        );
    }
    return generic_regression_result_to_dict(result);
}

py::dict evaluate_generic_native_debug_binding(
    const py::list& args_by_record,
    const py::list& records,
    const py::array& target_kinds,
    const py::array& target_indices,
    const py::array& target_indices_2,
    const py::array& x
) {
    auto cpp_args = native_args_from_list(args_by_record);
    auto cpp_records = generic_records_from_list(records);
    auto cpp_target_kinds = array_to_int_vector(target_kinds);
    auto cpp_target_indices = array_to_int_vector(target_indices);
    auto cpp_target_indices_2 = array_to_int_vector(target_indices_2);
    auto cpp_x = array_to_double_vector(x);
    GenericRegressionDebugResult result;
    {
        py::gil_scoped_release release;
        result = evaluate_generic_regression_debug_cpp(
            cpp_args,
            cpp_records,
            cpp_target_kinds,
            cpp_target_indices,
            cpp_target_indices_2,
            cpp_x
        );
    }
    return generic_regression_debug_to_dict(result);
}
#endif

}  // namespace

PYBIND11_MODULE(_native_core, m) {
    py::module_::import("epcsaft._core");
    m.doc() = "package-owned native backend for epcsaft-regression";

    m.def("_native_ceres_smoke", []() {
        py::dict out;
#ifdef EPCSAFT_HAS_CERES
        const bool compiled = true;
#else
        const bool compiled = false;
#endif
        out["backend"] = "ceres";
        out["compiled"] = compiled;
        out["available"] = compiled;
        out["status"] = compiled ? "enabled_available" : "disabled";
        return out;
    });

#ifdef EPCSAFT_HAS_CERES
    m.def("_fit_pure_neutral_native_ceres", &fit_pure_neutral_native_ceres_binding);
    m.def("_fit_pure_neutral_native_debug", &evaluate_pure_neutral_objective_debug_binding);
    m.def("_fit_generic_native_ceres", &fit_generic_native_ceres_binding);
    m.def("_evaluate_generic_native_debug", &evaluate_generic_native_debug_binding);
#endif
}
