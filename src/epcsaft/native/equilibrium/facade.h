#pragma once

#include <string>

struct EquilibriumOptionsNative {
    double min_composition = 1.0e-12;
    std::string jacobian_backend = "auto";
};
