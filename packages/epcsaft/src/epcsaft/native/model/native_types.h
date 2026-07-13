#pragma once

#include <vector>
#include <string>
#include <memory>
#include <limits>
#include <map>

using std::vector;

const static double kb = 1.380648465952442093e-23; // Boltzmann constant, J K^-1
const static double PI = 3.141592653589793;
const static double N_AV = 6.022140857e23; // Avagadro's number
const static double E_CHRG = 1.6021766208e-19; // elementary charge, units of coulomb
const static double perm_vac = 8.854187817e-22; //permittivity in vacuum, C V^-1 Angstrom^-1

#ifndef DBL_EPSILON
    #define DBL_EPSILON std::numeric_limits<double>::epsilon()
#endif

const static double HUGE_DBL = std::numeric_limits<double>::infinity();

struct ActivityCoefficientNative {
    vector<double> component_activity_coefficients;
    vector<double> mean_ionic_activity_coefficients_mole_fraction;
    vector<double> mean_ionic_activity_coefficients_molality;
    vector<double> solvation_free_energy;
    vector<double> pair_molality;
    vector<double> pair_conversion_factor;
    vector<int> cation_indices;
    vector<int> anion_indices;
    vector<int> solvent_indices;
    vector<int> pair_cation_indices;
    vector<int> pair_anion_indices;
    vector<int> pair_nu_cation;
    vector<int> pair_nu_anion;
    int solvent_index;
    double osmotic_coefficient;
};

struct ScalarContributionTerms {
    double hc = 0.0;
    double disp = 0.0;
    double assoc = 0.0;
    double ion = 0.0;
    double born = 0.0;
    double total = 0.0;
};

struct CompressibilityFactorResult {
    ScalarContributionTerms raw;
    ScalarContributionTerms terms;
};

struct VectorContributionTerms {
    vector<double> hc;
    vector<double> disp;
    vector<double> assoc;
    vector<double> ion;
    vector<double> born;
    vector<double> total;
};

struct CompositionContributionResult {
    VectorContributionTerms dadx;
    ScalarContributionTerms ares;
    ScalarContributionTerms sum_x_dadx;
    ScalarContributionTerms z_raw;
    ScalarContributionTerms z;
    std::map<std::string, std::string> derivative_backend;
    bool derivative_available = true;
};

struct ResidualChemicalPotentialResult {
    VectorContributionTerms mu;
    CompositionContributionResult composition;
};

struct FugacityContributionResult {
    VectorContributionTerms mu;
    VectorContributionTerms lnfugcoef;
    CompositionContributionResult composition;
};

struct BornDerivativeResult {
    bool supported = false;
    std::string backend = "unspecified";
    std::string message;
    vector<double> a_born_d_d_born;
    vector<double> a_born_d_f_solv;
    vector<double> mu_res_d_d_born_row_major;
    vector<double> mu_res_d_f_solv_row_major;
    vector<double> lnfug_d_d_born_row_major;
    vector<double> lnfug_d_f_solv_row_major;
    vector<double> lngamma_d_d_born_row_major;
    vector<double> lngamma_d_f_solv_row_major;
    int ncomp = 0;
};

struct ReferenceStateKey {
    double t = 0.0;
    double p = 0.0;
    int phase = 0;
    vector<double> x_ref;
};

struct ReferenceStateValue {
    double rho = 0.0;
    vector<double> fugcoef;
};

struct ReferenceStateCacheEntry {
    ReferenceStateKey key;
    ReferenceStateValue value;
};

struct DensityCandidateDiagnostics {
    double rho_sort = 0.0;
    double rho = 0.0;
    double gres = 1.0e300;
    double rel_resid = 1.0e300;
    double abs_p_error = 1.0e300;
    bool valid = false;
};

struct DensitySolveDiagnostics {
    std::string phase_label = "density";
    std::string phase_kind = "liq";
    std::string rejection_reason = "";
    double t = 0.0;
    double p = 0.0;
    std::vector<double> composition;
    int scan_point_count = 0;
    int finite_point_count = 0;
    int coarse_bracket_count = 0;
    int refined_bracket_count = 0;
    int candidate_root_count = 0;
    DensityCandidateDiagnostics best_near_root;
    std::vector<DensityCandidateDiagnostics> candidate_roots;
    bool best_candidate_refinement_used = false;
    std::string best_candidate_rejection_reason = "";
    std::string warm_start_source = "scan";
    std::string validity_gate = "not_evaluated";
};

struct DensitySolveResult {
    double rho = 0.0;
    bool valid = false;
    DensitySolveDiagnostics diagnostics;
};

struct PureNeutralRegressionDensityRecord {
    double t = 0.0;
    double p = 0.0;
    double rho_exp = 0.0;
    int phase = 0;
};

struct PureNeutralRegressionVLERecord {
    double t = 0.0;
    double p = 0.0;
};

struct PureNeutralRegressionDebugResult {
    double objective = 0.0;
    vector<double> gradient;
    vector<double> residuals;
    vector<double> jacobian_row_major;
    int jacobian_rows = 0;
    int jacobian_cols = 0;
    bool jacobian_available = true;
    std::string jacobian_backend = "cppad_implicit";
    vector<double> density_raw_residuals;
    vector<double> pure_vle_raw_residuals;
    int residual_evaluations = 0;
    int density_solves = 0;
    int fused_state_evaluations = 0;
    double callback_wall_time_s = 0.0;
};

struct PureNeutralRegressionResult {
    vector<double> x;
    double cost = HUGE_DBL;
    double residual_norm = HUGE_DBL;
    double density_metric = HUGE_DBL;
    double pure_vle_metric = HUGE_DBL;
    double initial_cost = HUGE_DBL;
    double initial_density_metric = HUGE_DBL;
    double initial_pure_vle_metric = HUGE_DBL;
    bool success = false;
    int status = 0;
    int nfev = 0;
    int iterations = 0;
    int starts_tried = 0;
    int objective_evaluations = 0;
    int gradient_evaluations = 0;
    int residual_evaluations = 0;
    int density_solves = 0;
    int fused_state_evaluations = 0;
    double callback_wall_time_s = 0.0;
    double solve_wall_time_s = 0.0;
    std::string message;
    std::string backend;
    std::string optimizer_backend;
    std::string derivative_backend;
    double gradient_norm = 0.0;
    double step_norm = 0.0;
    bool jacobian_available = true;
    std::string jacobian_backend = "cppad_implicit";
};

struct GenericRegressionRecord {
    std::string term_name;
    int term = 0;
    double t = 0.0;
    double p = 0.0;
    int phase = 0;
    vector<double> x;
    vector<double> y;
    double target = 0.0;
    int target_index = -1;
    int target_index_2 = -1;
    int density_kind = 0;
    int activity_basis = 0;
    int solvent_index = -1;
    double scale = 1.0;
};

struct GenericRegressionDebugResult {
    double cost = HUGE_DBL;
    double residual_norm = HUGE_DBL;
    vector<double> residuals;
    vector<double> jacobian_row_major;
    int jacobian_rows = 0;
    int jacobian_cols = 0;
    bool jacobian_available = true;
    std::string jacobian_backend = "unspecified";
    std::map<std::string, double> metrics_by_term;
};

struct GenericRegressionResult {
    vector<double> x;
    double cost = HUGE_DBL;
    double residual_norm = HUGE_DBL;
    double initial_cost = HUGE_DBL;
    double initial_residual_norm = HUGE_DBL;
    std::map<std::string, double> metrics_by_term;
    bool success = false;
    int status = 0;
    int nfev = 0;
    int iterations = 0;
    int starts_tried = 0;
    bool jacobian_available = true;
    std::string jacobian_backend = "unspecified";
    std::string optimizer_backend = "unspecified";
    std::string derivative_backend = "unspecified";
    std::string message;
    std::string backend;
};

struct NeutralBinaryKijPhaseDerivatives {
    double ares = 0.0;
    double dares_dk_fixed_rho = 0.0;
    double pressure = 0.0;
    double rho = 0.0;
    double z = 0.0;
    double dpdrho = 0.0;
    double dpdk = 0.0;
    double drhodk = 0.0;
    vector<double> mu_res;
    vector<double> dmu_res_dk_fixed_rho;
    vector<double> lnphi;
    vector<double> dlnphi_drho;
    vector<double> dlnphi_dk_fixed_rho;
    vector<double> dlnphi_dk_total;
    std::string backend = "cppad_implicit";
    std::string association_sensitivity_backend;
    std::string association_sensitivity_helper;
    int association_site_count = 0;
    vector<double> association_site_sensitivity_row_major;
};

struct PhaseStateCompositionSensitivityResult {
    bool supported = false;
    std::string backend = "unspecified";
    std::string density_backend = "unspecified";
    std::string message;
    double temperature = 0.0;
    double pressure = 0.0;
    double density = 0.0;
    double pressure_density_derivative = 0.0;
    double pressure_density_second_derivative = 0.0;
    int rows = 0;
    int cols = 0;
    vector<double> composition;
    vector<double> ln_fugacity;
    vector<double> density_composition_derivative;
    vector<double> density_composition_hessian_row_major;
    vector<double> pressure_composition_fixed_density_derivative;
    vector<double> pressure_density_composition_cross_derivative;
    vector<double> pressure_composition_fixed_density_hessian_row_major;
    vector<double> ln_fugacity_density_derivative;
    vector<double> ln_fugacity_density_second_derivative;
    vector<double> ln_fugacity_density_composition_cross_derivative;
    vector<double> fixed_density_jacobian_row_major;
    vector<double> fixed_density_hessian_tensor_row_major;
    vector<double> jacobian_row_major;
    vector<double> hessian_tensor_row_major;
    std::string association_sensitivity_backend;
    std::string association_sensitivity_helper;
    int association_site_count = 0;
    vector<double> association_site_sensitivity_row_major;
    vector<double> association_site_second_sensitivity_tensor_row_major;
};

class ePCSAFTMixtureNative;
class ProviderResolvedInputHandleV1;
struct NativeEvaluatedInputSnapshot;

class ePCSAFTStateNative {
public:
    ePCSAFTStateNative(std::shared_ptr<ePCSAFTMixtureNative> mixture, double t, vector<double> x,
        int phase, bool has_p, double p, bool has_rho, double rho,
        bool has_rho_guess = false, double rho_guess = 0.0);

    double temperature() const;
    int phase() const;
    const vector<double>& composition() const;

    double pressure();
    double density();
    double compressibility_factor();
    CompressibilityFactorResult compressibility_factor_result();
    double residual_helmholtz();
    ScalarContributionTerms residual_helmholtz_result();
    double temperature_derivative_residual_helmholtz();
    ScalarContributionTerms temperature_derivative_residual_helmholtz_result();
    double residual_enthalpy();
    double residual_entropy();
    double residual_gibbs();
    vector<double> residual_chemical_potential();
    ResidualChemicalPotentialResult residual_chemical_potential_result();
    CompositionContributionResult composition_derivative_residual_helmholtz_result();
    vector<double> ln_fugacity_coefficient();
    vector<double> fugacity_coefficient();
    FugacityContributionResult fugacity_coefficient_result();
    BornDerivativeResult born_parameter_derivatives();
    vector<double> relative_permittivity();
    std::string configuration_fingerprint() const;
    double osmotic_coefficient();
    vector<double> solvation_free_energy();
    ActivityCoefficientNative activity_coefficient_native(
        bool include_aux = true,
        bool has_solvent_override = false,
        int solvent_override_index = -1
    );

private:
    std::shared_ptr<ePCSAFTMixtureNative> mixture_;
    double t_;
    vector<double> x_;
    int phase_;
    bool has_p_;
    bool has_rho_;
    double p_;
    double rho_;
    bool pressure_cached_;
    bool density_cached_;
    bool activity_coefficient_cached_;
    ActivityCoefficientNative activity_coefficient_cache_;
};

class ePCSAFTMixtureNative : public std::enable_shared_from_this<ePCSAFTMixtureNative> {
public:
    explicit ePCSAFTMixtureNative(std::shared_ptr<ProviderResolvedInputHandleV1> handle);
    const NativeEvaluatedInputSnapshot& snapshot() const;
    std::shared_ptr<ePCSAFTStateNative> state(double t, vector<double> x, int phase,
        bool has_p, double p, bool has_rho, double rho, bool has_rho_guess = false, double rho_guess = 0.0);
    size_t ncomp() const;
    bool has_ionic() const;
    const vector<int>& cation_indices() const;
    const vector<int>& anion_indices() const;
    const vector<int>& solvent_indices() const;
    const vector<int>& pair_cation_indices() const;
    const vector<int>& pair_anion_indices() const;
    const vector<int>& pair_nu_cation() const;
    const vector<int>& pair_nu_anion() const;
    double solve_density(double t, double p, const vector<double>& x, int phase);
    double solve_density_with_guess(double t, double p, const vector<double>& x, int phase, double rho_guess);
    double solve_density_scoped(double t, double p, const vector<double>& x, int phase, const std::string& scope);
    const DensitySolveDiagnostics& last_density_diagnostics() const;
    bool lookup_reference_state(const ReferenceStateKey& key, ReferenceStateValue* out);
    void store_reference_state(const ReferenceStateKey& key, const ReferenceStateValue& value);
    void clear_runtime_caches();
    void reset_runtime_cache_stats();
    size_t reference_state_cache_hits() const;
    size_t reference_state_cache_misses() const;
    size_t density_warm_start_hits() const;
    size_t density_warm_start_rejections() const;

private:
    std::shared_ptr<ProviderResolvedInputHandleV1> handle_;
    std::shared_ptr<const NativeEvaluatedInputSnapshot> snapshot_;
    bool has_ionic_;
    vector<int> cation_indices_;
    vector<int> anion_indices_;
    vector<int> solvent_indices_;
    vector<int> pair_cation_indices_;
    vector<int> pair_anion_indices_;
    vector<int> pair_nu_cation_;
    vector<int> pair_nu_anion_;
    vector<ReferenceStateCacheEntry> reference_state_cache_;
    double liquid_density_seed_ = 0.0;
    double vapor_density_seed_ = 0.0;
    bool liquid_density_seed_valid_ = false;
    bool vapor_density_seed_valid_ = false;
    std::map<std::string, double> scoped_density_seeds_;
    DensitySolveDiagnostics last_density_diagnostics_;
    size_t reference_state_cache_hits_ = 0;
    size_t reference_state_cache_misses_ = 0;
    size_t density_warm_start_hits_ = 0;
    size_t density_warm_start_rejections_ = 0;
};

// functions used to solve for XA and its derivatives
vector<double> XA_find(vector<double> XA_guess, vector<double> delta_ij, double den,
    vector<double> x);
vector<double> dXAdx_find(vector<int> assoc_num, vector<double> delta_ij,
    double den, vector<double> XA, vector<double> ddelta_dx, vector<double> x);
vector<double> dXAdt_find(vector<double> delta_ij, double den,
    vector<double> XA, vector<double> ddelta_dt, vector<double> x);

class ValueError: public std::exception
{
public:
    ValueError(const std::string &err) throw() : m_err(err) {}
    ~ValueError() throw() {};
    virtual const char* what() const throw() { return m_err.c_str(); }
private:
    std::string m_err;
};

class SolutionError: public std::exception
{
public:
    SolutionError(const std::string &err) throw() : m_err(err) {}
    ~SolutionError() throw() {};
    virtual const char* what() const throw() { return m_err.c_str(); }
private:
    std::string m_err;
};

// density and composition helpers
vector<double> association_site_fractions_cpp(vector<double> XA_guess, vector<double> delta_ij, double den,
    vector<double> x);
vector<double> association_site_fraction_dt_cpp(vector<double> delta_ij, double den,
    vector<double> XA, vector<double> ddelta_dt, vector<double> x);
vector<double> association_site_fraction_dx_cpp(vector<int> assoc_num, vector<double> delta_ij,
    double den, vector<double> XA, vector<double> ddelta_dx, vector<double> x);
