#pragma once

#include "model/resolved_input.h"

#include <string>
#include <vector>

template <typename Scalar>
struct ProviderParameterAccessV1;

template <>
struct ProviderParameterAccessV1<double> {
    const std::vector<double>& m;
    const std::vector<double>& s;
    const std::vector<double>& e;
    const std::vector<double>& k_ij;
    const std::vector<double>& e_assoc;
    const std::vector<double>& vol_a;
    const std::vector<double>& z;
    const std::vector<double>& dielc;
    const std::vector<double>& mw;
    const std::vector<double>& mixed_rel_perm_a;
    const std::vector<double>& mixed_rel_perm_b;
    const std::vector<double>& mixed_rel_perm_c;
    const std::vector<int>& mixed_rel_perm_mask;
    const int& mixed_rel_perm_water_index;
    const int& dielc_rule;
    const int& dielc_diff_mode;
    const int& hc_dadx_diff_mode;
    const int& disp_dadx_diff_mode;
    const int& assoc_dadx_diff_mode;
    const int& d_ion_mode;
    const int& mu_DH_diff_mode;
    const int& mu_DH_comp_dep_rel_perm;
    const int& mu_DH_include_sum_term;
    const int& include_born_model;
    const int& d_born_mode;
    const int& born_solvation_shell_model;
    const int& born_dielectric_saturation;
    const int& born_bulk_mode;
    const int& mu_born_diff_mode;
    const int& mu_born_comp_dep_rel_perm;
    const int& mu_born_include_sum_term;
    const int& mu_born_comp_dep_delta_d;
    const std::vector<double>& d_born;
    const std::vector<double>& f_solv;
    const int& born_model;
    const int& born_radius_model;
    const int& born_diff_mode;
    const int& born_eps_mode;
    const int& DH_model;
    const std::vector<int>& assoc_num;
    const std::vector<int>& assoc_matrix;
    const std::vector<double>& k_hb;
    const std::vector<double>& l_ij;
    const std::string& parameter_source_label;
    const std::string& parameter_provenance_status;
    const std::string& binary_interaction_provenance_status;
    const std::vector<std::string>& parameter_provenance_fields;

    explicit ProviderParameterAccessV1(const NativeEvaluatedInputSnapshot& input)
        : m(input.m),
          s(input.s),
          e(input.e),
          k_ij(input.k_ij),
          e_assoc(input.e_assoc),
          vol_a(input.vol_a),
          z(input.z),
          dielc(input.dielc),
          mw(input.mw),
          mixed_rel_perm_a(input.mixed_rel_perm_a),
          mixed_rel_perm_b(input.mixed_rel_perm_b),
          mixed_rel_perm_c(input.mixed_rel_perm_c),
          mixed_rel_perm_mask(input.mixed_rel_perm_mask),
          mixed_rel_perm_water_index(input.mixed_rel_perm_water_index),
          dielc_rule(input.dielc_rule),
          dielc_diff_mode(input.dielc_diff_mode),
          hc_dadx_diff_mode(input.hc_dadx_diff_mode),
          disp_dadx_diff_mode(input.disp_dadx_diff_mode),
          assoc_dadx_diff_mode(input.assoc_dadx_diff_mode),
          d_ion_mode(input.d_ion_mode),
          mu_DH_diff_mode(input.mu_DH_diff_mode),
          mu_DH_comp_dep_rel_perm(input.mu_DH_comp_dep_rel_perm),
          mu_DH_include_sum_term(input.mu_DH_include_sum_term),
          include_born_model(input.include_born_model),
          d_born_mode(input.d_born_mode),
          born_solvation_shell_model(input.born_solvation_shell_model),
          born_dielectric_saturation(input.born_dielectric_saturation),
          born_bulk_mode(input.born_bulk_mode),
          mu_born_diff_mode(input.mu_born_diff_mode),
          mu_born_comp_dep_rel_perm(input.mu_born_comp_dep_rel_perm),
          mu_born_include_sum_term(input.mu_born_include_sum_term),
          mu_born_comp_dep_delta_d(input.mu_born_comp_dep_delta_d),
          d_born(input.d_born),
          f_solv(input.f_solv),
          born_model(input.born_model),
          born_radius_model(input.born_radius_model),
          born_diff_mode(input.born_diff_mode),
          born_eps_mode(input.born_eps_mode),
          DH_model(input.DH_model),
          assoc_num(input.assoc_num),
          assoc_matrix(input.assoc_matrix),
          k_hb(input.k_hb),
          l_ij(input.l_ij),
          parameter_source_label(input.parameter_source_label),
          parameter_provenance_status(input.parameter_provenance_status),
          binary_interaction_provenance_status(input.binary_interaction_provenance_status),
          parameter_provenance_fields(input.parameter_provenance_fields) {}

    ProviderParameterAccessV1(
        const ProviderParameterAccessV1<double>& input,
        const std::vector<double>& e_assoc_override,
        const std::vector<double>& vol_a_override,
        const std::vector<int>& assoc_num_override,
        const std::vector<int>& assoc_matrix_override,
        const std::vector<double>& k_hb_override
    )
        : m(input.m),
          s(input.s),
          e(input.e),
          k_ij(input.k_ij),
          e_assoc(e_assoc_override),
          vol_a(vol_a_override),
          z(input.z),
          dielc(input.dielc),
          mw(input.mw),
          mixed_rel_perm_a(input.mixed_rel_perm_a),
          mixed_rel_perm_b(input.mixed_rel_perm_b),
          mixed_rel_perm_c(input.mixed_rel_perm_c),
          mixed_rel_perm_mask(input.mixed_rel_perm_mask),
          mixed_rel_perm_water_index(input.mixed_rel_perm_water_index),
          dielc_rule(input.dielc_rule),
          dielc_diff_mode(input.dielc_diff_mode),
          hc_dadx_diff_mode(input.hc_dadx_diff_mode),
          disp_dadx_diff_mode(input.disp_dadx_diff_mode),
          assoc_dadx_diff_mode(input.assoc_dadx_diff_mode),
          d_ion_mode(input.d_ion_mode),
          mu_DH_diff_mode(input.mu_DH_diff_mode),
          mu_DH_comp_dep_rel_perm(input.mu_DH_comp_dep_rel_perm),
          mu_DH_include_sum_term(input.mu_DH_include_sum_term),
          include_born_model(input.include_born_model),
          d_born_mode(input.d_born_mode),
          born_solvation_shell_model(input.born_solvation_shell_model),
          born_dielectric_saturation(input.born_dielectric_saturation),
          born_bulk_mode(input.born_bulk_mode),
          mu_born_diff_mode(input.mu_born_diff_mode),
          mu_born_comp_dep_rel_perm(input.mu_born_comp_dep_rel_perm),
          mu_born_include_sum_term(input.mu_born_include_sum_term),
          mu_born_comp_dep_delta_d(input.mu_born_comp_dep_delta_d),
          d_born(input.d_born),
          f_solv(input.f_solv),
          born_model(input.born_model),
          born_radius_model(input.born_radius_model),
          born_diff_mode(input.born_diff_mode),
          born_eps_mode(input.born_eps_mode),
          DH_model(input.DH_model),
          assoc_num(assoc_num_override),
          assoc_matrix(assoc_matrix_override),
          k_hb(k_hb_override),
          l_ij(input.l_ij),
          parameter_source_label(input.parameter_source_label),
          parameter_provenance_status(input.parameter_provenance_status),
          binary_interaction_provenance_status(input.binary_interaction_provenance_status),
          parameter_provenance_fields(input.parameter_provenance_fields) {}
};

struct SnapshotParameterAccessV1 final : ProviderParameterAccessV1<double> {
    explicit SnapshotParameterAccessV1(const NativeEvaluatedInputSnapshot& input)
        : ProviderParameterAccessV1<double>(input) {}
};

struct AssociationDisabledParameterAccessV1 final : ProviderParameterAccessV1<double> {
    explicit AssociationDisabledParameterAccessV1(
        const ProviderParameterAccessV1<double>& input
    )
        : ProviderParameterAccessV1<double>(
              input,
              empty_double_vector(),
              empty_double_vector(),
              empty_int_vector(),
              empty_int_vector(),
              empty_double_vector()
          ) {}

private:
    static const std::vector<double>& empty_double_vector() {
        static const std::vector<double> value;
        return value;
    }

    static const std::vector<int>& empty_int_vector() {
        static const std::vector<int> value;
        return value;
    }
};
