from __future__ import annotations

from analyses.package_validation.explicit_association_toybox.scripts.propagation_evidence import (
    classify_propagated_evidence_band,
    load_propagation_thresholds,
)


def test_load_propagation_thresholds_has_all_bands() -> None:
    thresholds = load_propagation_thresholds()

    assert {
        "exact_reference",
        "candidate_accuracy",
        "speed_only_candidate",
        "diagnostic_only",
        "reject_for_provider_path",
    } <= set(thresholds)
    assert thresholds["candidate_accuracy"]["max_derivative_rel_error"] == 5.0e-2


def test_classify_candidate_accuracy_when_derivatives_and_properties_are_bounded() -> None:
    thresholds = load_propagation_thresholds()

    band = classify_propagated_evidence_band(
        association_model="explicit_approx",
        assoc_ares_rel_error=1.0e-2,
        derivative_rel_error=2.0e-2,
        property_rel_error=3.0e-2,
        mass_action_residual_inf=1.0e-6,
        speedup_vs_exact_implicit=4.0,
        information_loss="none",
        thresholds=thresholds,
    )

    assert band == "candidate_accuracy"


def test_classify_information_loss_as_diagnostic() -> None:
    thresholds = load_propagation_thresholds()

    band = classify_propagated_evidence_band(
        association_model="explicit_approx",
        assoc_ares_rel_error=1.0e-3,
        derivative_rel_error=1.0e-3,
        property_rel_error=1.0e-3,
        mass_action_residual_inf=1.0e-6,
        speedup_vs_exact_implicit=12.0,
        information_loss="reduced_site_information",
        thresholds=thresholds,
    )

    assert band == "diagnostic_only"
