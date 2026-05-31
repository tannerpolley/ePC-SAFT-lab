#pragma once
#include "eos/core_internal.h"
#include <map>
#include <string>
namespace residual_backend_detail {
inline std::string contribution_backend_name(int mode) {
    if (mode == 0) return "analytic";
    if (mode == 1) return "unsupported";
    if (mode == 2) return "cppad";
    if (mode == 3 || mode == 5) {
        return "analytic";
    }
    if (mode == 4) return "cppad";
    return "unknown";
}

inline bool has_association_sites(const add_args &cppargs) {
    for (int sites : cppargs.assoc_num) {
        if (sites > 0) {
            return true;
        }
    }
    return false;
}

inline std::string association_backend_name(const add_args &cppargs) {
    if (!has_association_sites(cppargs)) {
        return contribution_backend_name(cppargs.assoc_dadx_diff_mode);
    }
    if (cppargs.assoc_dadx_diff_mode == 0 || cppargs.assoc_dadx_diff_mode == 3 || cppargs.assoc_dadx_diff_mode == 5) {
        return "analytic_implicit";
    }
    return "unsupported";
}

inline std::string born_backend_name(const add_args &cppargs) {
    if (cppargs.born_model == 2 && cppargs.born_diff_mode == 5) {
        return "cppad";
    }
    return contribution_backend_name(cppargs.born_diff_mode);
}

inline std::map<std::string, std::string> composition_derivative_backend_map(const add_args &cppargs) {
    std::map<std::string, std::string> backends;
    backends["hc"] = contribution_backend_name(cppargs.hc_dadx_diff_mode);
    backends["disp"] = contribution_backend_name(cppargs.disp_dadx_diff_mode);
    backends["assoc"] = association_backend_name(cppargs);
    backends["ion"] = contribution_backend_name(cppargs.mu_DH_diff_mode);
    backends["born"] = born_backend_name(cppargs);
    return backends;
}
}  // namespace residual_backend_detail
