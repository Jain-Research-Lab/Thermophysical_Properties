from DOA.modular_functions.material_properties.functions.composite_1d import matprop_enhanced_PCM

def hexadecane_P0():
    # PCM function
    Tmelt = 315.0 # [K]
    T_min = 310.0 # [K]
    T_max = 320.0 # [K]
    alpha = 1.0 # [none]

    k_pcm_liq = 0.00014 # [kW/(m*K)]
    k_pcm_sol = 0.00033 # [kW/(m*K)]
    k_int = 0.0167 # [kW/(m*K)]

    cp_pcm_liq = 2.21 # [kJ/(kg*K)]
    cp_pcm_sol = 1.9 # [kJ/(kg*K)]
    cp_int = 0.478 # [kJ/(kg*K)]

    rho_pcm_liq = 806.0 # [kg/m^3]
    rho_pcm_sol = 806.0 # [kg/m^3]
    rho_int = 7790.0 # [kg/m^3]

    L = 236.89 # [kJ/kg]

    r = 0.2 # volume ratio of metal to total volume

    return matprop_enhanced_PCM(Tmelt, alpha, k_pcm_liq, k_pcm_sol, k_int, cp_pcm_liq, cp_pcm_sol, cp_int, rho_pcm_liq, rho_pcm_sol, rho_int, L, r, T_min, T_max)

def cexahedane_P0():
    # PCM function
    Tmelt = 290.0 # [K]
    T_min = 285.0 # [K]
    T_max = 395.0 # [K]
    alpha = 1.0 # [none]

    k_pcm_liq = 0.00014 # [kW/(m*K)]
    k_pcm_sol = 0.00033 # [kW/(m*K)]
    k_int = 0.0167 # [kW/(m*K)]

    cp_pcm_liq = 2.21 # [kJ/(kg*K)]
    cp_pcm_sol = 1.9 # [kJ/(kg*K)]
    cp_int = 0.478 # [kJ/(kg*K)]

    rho_pcm_liq = 806.0 # [kg/m^3]
    rho_pcm_sol = 806.0 # [kg/m^3]
    rho_int = 7790.0 # [kg/m^3]

    L = 236.89 # [kJ/kg]

    r = 0.2 # volume ratio of metal to total volume

    return matprop_enhanced_PCM(Tmelt, alpha, k_pcm_liq, k_pcm_sol, k_int, cp_pcm_liq, cp_pcm_sol, cp_int, rho_pcm_liq, rho_pcm_sol, rho_int, L, r, T_min, T_max)




def dexahecane_P0():
    # PCM function
    Tmelt = 280.0 # [K]
    T_min = 275.0 # [K]
    T_max = 285.0 # [K]
    alpha = 1.0 # [none]

    k_pcm_liq = 0.00014 # [kW/(m*K)]
    k_pcm_sol = 0.00033 # [kW/(m*K)]
    k_int = 0.0167 # [kW/(m*K)]

    cp_pcm_liq = 2.21 # [kJ/(kg*K)]
    cp_pcm_sol = 1.9 # [kJ/(kg*K)]
    cp_int = 0.478 # [kJ/(kg*K)]

    rho_pcm_liq = 806.0 # [kg/m^3]
    rho_pcm_sol = 806.0 # [kg/m^3]
    rho_int = 7790.0 # [kg/m^3]

    L = 236.89 # [kJ/kg]

    r = 0.2 # volume ratio of metal to total volume

    return matprop_enhanced_PCM(Tmelt, alpha, k_pcm_liq, k_pcm_sol, k_int, cp_pcm_liq, cp_pcm_sol, cp_int, rho_pcm_liq, rho_pcm_sol, rho_int, L, r, T_min, T_max)

#Altered values for Vismay
def hexadecane_P0_adj():
    # PCM function
    Tmelt = 300 # [K]
    T_min = 295 # [K]
    T_max = 305 # [K]
    alpha = 1.0 # [none]

    k_pcm_liq = 0.00014 # [kW/(m*K)]
    k_pcm_sol = 0.00033 # [kW/(m*K)]
    k_int = 0.0167 # [kW/(m*K)]

    cp_pcm_liq = 2.21 # [kJ/(kg*K)]
    cp_pcm_sol = 1.9 # [kJ/(kg*K)]
    cp_int = 0.478 # [kJ/(kg*K)]

    rho_pcm_liq = 806.0 # [kg/m^3]
    rho_pcm_sol = 806.0 # [kg/m^3]
    rho_int = 7790.0 # [kg/m^3]

    L = 236.89 # [kJ/kg]

    r = 0.2 # volume ratio of metal to total volume

    return matprop_enhanced_PCM(Tmelt, alpha, k_pcm_liq, k_pcm_sol, k_int, cp_pcm_liq, cp_pcm_sol, cp_int, rho_pcm_liq, rho_pcm_sol, rho_int, L, r, T_min, T_max)
