from DOA.config.lib_config import numpy as np
from DOA.general_functions.mathGBM.linear import constant
from DOA.general_functions.mathGBM.polynomial import poly
from DOA.general_functions.mathGBM.linear import line1d
from DOA.modular_functions.material_properties.functions.pure_fluid_1d import generic_1p_T, kuD_1p_T

# Tip: use matweb to quickly find reasonable values, although the last
# time I tried to use it, the website seemed down

# class for materials that only do conduction
def constant_k_cp_rho(k, cp, rho):
    k_class = constant(k)
    cp_class = constant(cp)
    rho_class = constant(rho)
    
    return generic_1p_T(k_class, cp_class, rho_class)

# class for materials that do advection
def constant_k_cp_rho_2(k, cp, rho):
    k_class = constant(k)
    cp_class = constant(cp)
    u_class = line1d(0.0, 1.0, 0.0, cp)
    rho_class = constant(rho)
    
    return kuD_1p_T(k_class, u_class, rho_class, cp_class)

def constant_water():
    k = 0.0004    # [kW/(m*K)]
    cp = 4.184     # [kJ/(kg*K)]
    rho = 1080.0  # [kg/m^3]
    
    return constant_k_cp_rho_2(k, cp, rho)

def constant_PG50():
    k = 0.0004    # [kW/(m*K)]
    cp = 3.55     # [kJ/(kg*K)]
    rho = 1080.0  # [kg/m^3]
    
    return constant_k_cp_rho_2(k, cp, rho)

def constant_water_glycol():
    k = 0.00041  # [kW/(m*K)]
    cp = 3.1  # [kJ/(kg*K)]
    rho = 1079.0  # [kg/m^3]

    return constant_k_cp_rho_2(k, cp, rho)

def constant_air():
    k = 0.000025     # [kW/(m*K)]
    cp = 1.0         # [kJ/(kg*K)]
    rho = 1.2        # [kg/m^3]
    
    return constant_k_cp_rho(k, cp, rho)

def PG50_variable_cp():
    k = 0.0004    # [kW/(m*K)]
    rho = 1080.0  # [kg/m^3]

    k_class = constant(k)
    rho_class = constant(rho)
    cp_class = line1d(287.15, 297.15, 3.5067, 3.5452)
    u_class = poly(np.array((0.5*cp_class.my, cp_class.by, 0)), "max")

    # cp_class = line1d(298.15, 322.9825, 3.5509, 3.6010)
    # cp_class = line1d(287.15, 297.15, 3.5067, 3.5452)
    # h_class = poly(np.array((0.5*cp_class.my, cp_class.by, 0)), "max")

    return kuD_1p_T(k_class, u_class, rho_class, cp_class)

def constant_stainless_steel():
    k = 0.0167     # [kW/(m*K)]
    cp = 0.478     # [kJ/(kg*K)]
    rho = 7790.0   # [kg/m^3]
    
    return constant_k_cp_rho(k, cp, rho)

def constant_copper():
    k = 0.0004     # [kW/(m*K)]
    cp = 3.35      # [kJ/(kg*K)]
    rho = 1080.0   # [kg/m^3]
    
    return constant_k_cp_rho(k, cp, rho)

def constant_aluminum():
    k = 0.205     # [kW/(m*K)]
    cp = 0.9      # [kJ/(kg*K)]
    rho = 2700.0  # [kg/m^3]
    
    return constant_k_cp_rho(k, cp, rho)

def constant_rockwool():
    k = 0.00003 # [kW/(m*K)]
    cp = 1.0    # [kJ/(kg*K)]
    rho = 40.0  # kg/m^3
    
    return constant_k_cp_rho(k, cp, rho)