#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include <memory>
#include <string>
#include <vector>

#include "regression_problem.h"

namespace py = pybind11;

namespace {

std::vector<std::string> row_ids(const NativeRegressionProblem& problem) {
    std::vector<std::string> values;
    values.reserve(problem.rows.size());
    for (const NativeRegressionRow& row : problem.rows) values.push_back(row.row_id);
    return values;
}

std::vector<std::string> source_ids(const NativeRegressionProblem& problem) {
    std::vector<std::string> values;
    values.reserve(problem.rows.size());
    for (const NativeRegressionRow& row : problem.rows) values.push_back(row.source_id);
    return values;
}

std::vector<std::string> snapshot_fingerprints(const NativeRegressionProblem& problem) {
    std::vector<std::string> values;
    values.reserve(problem.provider_handles.size());
    for (const auto& handle : problem.provider_handles) {
        values.push_back(handle->snapshot().snapshot_fingerprint_sha256);
    }
    return values;
}

std::vector<std::string> parameter_keys(const NativeRegressionProblem& problem) {
    std::vector<std::string> values;
    values.reserve(problem.parameters.size());
    for (const NativeFittedParameter& parameter : problem.parameters) values.push_back(parameter.key);
    return values;
}

py::tuple strings_to_tuple(const std::vector<std::string>& values) {
    py::tuple output(values.size());
    for (std::size_t index = 0; index < values.size(); ++index) {
        output[index] = py::str(values[index]);
    }
    return output;
}

py::dict controls_to_dict(const NativeRegressionControls& controls) {
    py::dict output;
    output["loss"] = controls.loss;
    output["max_num_iterations"] = controls.max_num_iterations;
    output["function_tolerance"] = controls.function_tolerance;
    output["gradient_tolerance"] = controls.gradient_tolerance;
    output["parameter_tolerance"] = controls.parameter_tolerance;
    return output;
}

py::dict problem_receipt_to_dict(const NativeRegressionProblem& problem) {
    py::dict output;
    output["contract_id"] = "epcsaft.regression.native-problem";
    output["schema_version"] = 1;
    output["dataset_id"] = problem.dataset_id;
    output["provider_definition_fingerprint"] = problem.provider_definition_fingerprint;
    output["snapshot_fingerprints"] = snapshot_fingerprints(problem);
    py::list provider_records;
    for (const auto& handle : problem.provider_handles) {
        const NativeEvaluatedInputSnapshot& snapshot = handle->snapshot();
        py::dict item;
        item["definition_fingerprint_sha256"] = snapshot.definition_fingerprint_sha256;
        item["snapshot_fingerprint_sha256"] = snapshot.snapshot_fingerprint_sha256;
        item["component_order"] = snapshot.component_order;
        item["temperature_K"] = snapshot.temperature_K;
        item["composition_basis"] = snapshot.composition_basis;
        item["canonical_composition"] = snapshot.canonical_composition;
        provider_records.append(std::move(item));
    }
    output["provider_handles"] = std::move(provider_records);
    output["row_ids"] = row_ids(problem);
    output["source_ids"] = source_ids(problem);
    output["parameter_keys"] = parameter_keys(problem);
    py::list row_records;
    for (const NativeRegressionRow& row : problem.rows) {
        py::dict item;
        item["row_id"] = row.row_id;
        item["source_id"] = row.source_id;
        item["source_kind"] = row.source_kind;
        item["target_family"] = row.target_family;
        item["provider_handle_indices"] = row.provider_handle_indices;
        item["pressure_Pa"] = row.pressure_Pa;
        item["weight"] = row.weight;
        item["residual_scale"] = row.residual_scale;
        item["target_value"] = row.target_value;
        item["model_intercept"] = row.model_intercept;
        item["parameter_coefficients"] = row.parameter_coefficients;
        item["derivative_owner"] = row.derivative_owner;
        row_records.append(std::move(item));
    }
    output["rows"] = std::move(row_records);
    py::list parameter_records;
    for (const NativeFittedParameter& parameter : problem.parameters) {
        py::dict item;
        item["key"] = parameter.key;
        item["target_kind"] = parameter.target_kind;
        item["first_index"] = parameter.first_index;
        item["second_index"] = parameter.second_index;
        item["start"] = parameter.start;
        item["lower"] = parameter.lower;
        item["upper"] = parameter.upper;
        parameter_records.append(std::move(item));
    }
    output["parameters"] = std::move(parameter_records);
    py::list fixed_records;
    for (const auto& [record_id, fingerprint] : problem.fixed_parameter_fingerprints) {
        py::dict item;
        item["record_id"] = record_id;
        item["sha256"] = fingerprint;
        fixed_records.append(std::move(item));
    }
    output["fixed_parameter_fingerprints"] = std::move(fixed_records);
    output["controls"] = controls_to_dict(problem.controls);
    output["problem_fingerprint"] = problem.problem_fingerprint;
    return output;
}

py::dict derivative_metadata_to_dict(const NativeRegressionEvaluation& evaluation) {
    py::dict output;
    output["complete"] = evaluation.derivative_complete;
    output["parameter_keys"] = py::list();
    output["column_owners"] = evaluation.derivative_column_owners;
    return output;
}

py::list row_diagnostics_to_list(const NativeRegressionEvaluation& evaluation) {
    py::list output;
    for (const NativeRegressionRowDiagnostic& row : evaluation.row_diagnostics) {
        py::dict item;
        item["row_id"] = row.row_id;
        item["source_id"] = row.source_id;
        item["raw_residual"] = row.raw_residual;
        item["weighted_residual"] = row.weighted_residual;
        output.append(std::move(item));
    }
    return output;
}

py::dict evaluation_to_dict(
    const NativeRegressionProblem& problem,
    const NativeRegressionEvaluation& evaluation
) {
    py::dict output;
    output["receipt_schema_version"] = 1;
    output["problem_receipt"] = problem_receipt_to_dict(problem);
    output["problem_fingerprint"] = problem.problem_fingerprint;
    output["termination_type"] = "EVALUATION_ONLY";
    output["solution_usable"] = evaluation.finite_outputs && evaluation.derivative_complete;
    output["effective_ceres_options"] = py::dict();
    output["parameter_values"] = evaluation.parameter_values;
    output["row_diagnostics"] = row_diagnostics_to_list(evaluation);
    output["objective"] = evaluation.objective;
    output["jacobian_row_major"] = evaluation.jacobian_row_major;
    output["jacobian_shape"] = py::make_tuple(evaluation.jacobian_rows, evaluation.jacobian_cols);
    py::dict derivative = derivative_metadata_to_dict(evaluation);
    derivative["parameter_keys"] = parameter_keys(problem);
    output["derivative_metadata"] = std::move(derivative);
    output["success"] = evaluation.finite_outputs && evaluation.derivative_complete;
    return output;
}

py::dict effective_options_to_dict(const NativeEffectiveCeresOptions& options) {
    py::dict output;
    output["max_num_iterations"] = options.max_num_iterations;
    output["function_tolerance"] = options.function_tolerance;
    output["gradient_tolerance"] = options.gradient_tolerance;
    output["parameter_tolerance"] = options.parameter_tolerance;
    return output;
}

py::dict solve_to_dict(
    const NativeRegressionProblem& problem,
    const NativeRegressionSolveResult& result
) {
    py::dict output = evaluation_to_dict(problem, result.evaluation);
    output["termination_type"] = result.termination_type;
    output["solution_usable"] = result.solution_usable;
    output["effective_ceres_options"] = effective_options_to_dict(result.effective_options);
    output["success"] = result.success;
    output["iterations"] = result.iterations;
    output["initial_cost"] = result.initial_cost;
    output["final_cost"] = result.final_cost;
    output["message"] = result.message;
    return output;
}

}  // namespace

PYBIND11_MODULE(_native_core, module) {
    py::module_::import("epcsaft._core");
    module.doc() = "typed native backend for epcsaft-regression";

    py::class_<NativeFittedParameter>(module, "NativeFittedParameter")
        .def(py::init<std::string, std::string, int, int, double, double, double>())
        .def_readonly("key", &NativeFittedParameter::key)
        .def_readonly("target_kind", &NativeFittedParameter::target_kind)
        .def_readonly("first_index", &NativeFittedParameter::first_index)
        .def_readonly("second_index", &NativeFittedParameter::second_index)
        .def_readonly("start", &NativeFittedParameter::start)
        .def_readonly("lower", &NativeFittedParameter::lower)
        .def_readonly("upper", &NativeFittedParameter::upper);

    py::class_<NativeRegressionControls>(module, "NativeRegressionControls")
        .def(py::init<std::string, int, double, double, double>())
        .def_readonly("loss", &NativeRegressionControls::loss)
        .def_readonly("max_num_iterations", &NativeRegressionControls::max_num_iterations)
        .def_readonly("function_tolerance", &NativeRegressionControls::function_tolerance)
        .def_readonly("gradient_tolerance", &NativeRegressionControls::gradient_tolerance)
        .def_readonly("parameter_tolerance", &NativeRegressionControls::parameter_tolerance);

    py::class_<NativeRegressionRow>(module, "NativeRegressionRow")
        .def(py::init<
            std::string,
            std::string,
            std::string,
            std::string,
            std::vector<int>,
            double,
            double,
            double,
            double,
            double,
            std::vector<double>,
            std::string
        >())
        .def_readonly("row_id", &NativeRegressionRow::row_id)
        .def_readonly("source_id", &NativeRegressionRow::source_id)
        .def_readonly("source_kind", &NativeRegressionRow::source_kind)
        .def_readonly("target_family", &NativeRegressionRow::target_family)
        .def_readonly("provider_handle_indices", &NativeRegressionRow::provider_handle_indices)
        .def_readonly("pressure_Pa", &NativeRegressionRow::pressure_Pa)
        .def_readonly("weight", &NativeRegressionRow::weight)
        .def_readonly("residual_scale", &NativeRegressionRow::residual_scale)
        .def_readonly("target_value", &NativeRegressionRow::target_value)
        .def_readonly("model_intercept", &NativeRegressionRow::model_intercept)
        .def_readonly("parameter_coefficients", &NativeRegressionRow::parameter_coefficients)
        .def_readonly("derivative_owner", &NativeRegressionRow::derivative_owner);

    py::class_<NativeRegressionProblem>(module, "NativeRegressionProblem")
        .def(py::init<
            std::string,
            std::string,
            std::vector<std::shared_ptr<ProviderResolvedInputHandleV1>>,
            std::vector<std::pair<std::string, std::string>>,
            std::vector<NativeRegressionRow>,
            std::vector<NativeFittedParameter>,
            NativeRegressionControls
        >())
        .def_readonly("dataset_id", &NativeRegressionProblem::dataset_id)
        .def_readonly(
            "provider_definition_fingerprint",
            &NativeRegressionProblem::provider_definition_fingerprint
        )
        .def_readonly("provider_handles", &NativeRegressionProblem::provider_handles)
        .def_readonly(
            "fixed_parameter_fingerprints",
            &NativeRegressionProblem::fixed_parameter_fingerprints
        )
        .def_readonly("rows", &NativeRegressionProblem::rows)
        .def_readonly("parameters", &NativeRegressionProblem::parameters)
        .def_readonly("controls", &NativeRegressionProblem::controls)
        .def_readonly("problem_fingerprint", &NativeRegressionProblem::problem_fingerprint)
        .def_property_readonly("problem_receipt", &problem_receipt_to_dict)
        .def_property_readonly("row_ids", [](const NativeRegressionProblem& problem) {
            return strings_to_tuple(row_ids(problem));
        })
        .def_property_readonly("source_ids", [](const NativeRegressionProblem& problem) {
            return strings_to_tuple(source_ids(problem));
        })
        .def_property_readonly("snapshot_fingerprints", [](const NativeRegressionProblem& problem) {
            return strings_to_tuple(snapshot_fingerprints(problem));
        })
        .def_property_readonly("parameter_keys", [](const NativeRegressionProblem& problem) {
            return strings_to_tuple(parameter_keys(problem));
        });

    module.def("_evaluate_regression", [](
        const NativeRegressionProblem& problem,
        const std::vector<double>& parameter_values
    ) {
        return evaluation_to_dict(
            problem,
            evaluate_regression_problem(problem, parameter_values)
        );
    });
    module.def("_solve_regression", [](const NativeRegressionProblem& problem) {
        return solve_to_dict(problem, solve_regression_problem(problem));
    });
    module.def("_regression_acceptance_from_summary", &regression_acceptance_from_summary);

    module.def("_native_provider_resolved_input_handle_probe", [](
        const std::shared_ptr<ProviderResolvedInputHandleV1>& handle
    ) {
        if (!handle) throw std::invalid_argument("provider resolved-input handle is required");
        const NativeEvaluatedInputSnapshot& snapshot = handle->snapshot();
        py::dict identity;
        identity["contract_id"] = snapshot.contract_id;
        identity["schema"] = snapshot.schema;
        identity["schema_version"] = snapshot.schema_version;
        identity["definition_fingerprint_sha256"] = snapshot.definition_fingerprint_sha256;
        identity["snapshot_fingerprint_sha256"] = snapshot.snapshot_fingerprint_sha256;
        identity["component_order"] = snapshot.component_order;
        identity["temperature_K"] = snapshot.temperature_K;
        identity["composition_basis"] = snapshot.composition_basis;
        identity["canonical_composition"] = snapshot.canonical_composition;
        return identity;
    });

    module.def("_native_ceres_smoke", []() {
        py::dict output;
        output["backend"] = "ceres";
        output["compiled"] = true;
        output["available"] = true;
        output["status"] = "enabled_available";
        return output;
    });
}
