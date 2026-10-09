from DOA.modular_functions.material_properties.functions.pure_fluid_2d import AB_refprop, DP_refprop, HP_refprop
from DOA.general_functions.file_management.save_load_class import load_Class
from DOA.general_functions.mathGBM.interp1d import interp1d_linear_spaced
from DOA.general_functions.mathGBM.linear import line1dclip
from DOA.config.lib_config import numpy as np
import h5py
import os
gbm_base = os.environ.get('GBM_BASE')

def get_pure_fluid_2d_AB(material, interp_type='bilinear', N=(400,400), diff_idx=(4,2), use_nonlin=True, mesh_type=''):
    with h5py.File(gbm_base + '/DOA/modular_functions/material_properties/data/' + material + '/sat.h5', 'r') as f:
        sat_prop = load_Class(f)

    T_given_P_fit = sat_prop.T_given_P_fit
    H0_given_P_fit = sat_prop.H0_given_P_fit
    H1_given_P_fit = sat_prop.H1_given_P_fit
    P_given_T_fit = sat_prop.P_given_T_fit

    with h5py.File(gbm_base + '/DOA/modular_functions/material_properties/data/' + material + '/AB_DHEPTQS' + mesh_type + '_' + str(N[0]) + '_' + str(N[1]) + '.h5', 'r') as f:
        AB_LUT = load_Class(f)

    T_grid = np.array(AB_LUT.T_grid)
    h_grid = np.array(AB_LUT.h_grid)
    u_grid = np.array(AB_LUT.u_grid)
    x_grid = np.array(AB_LUT.x_grid)
    D_grid = np.array(AB_LUT.D_grid)
    P_grid = np.array(AB_LUT.P_grid)
    
    grids = (T_grid, h_grid, u_grid, x_grid, D_grid, P_grid)

    Ar_min = AB_LUT.Ar_min
    Ar_max = AB_LUT.Ar_max
    Br_min = AB_LUT.Br_min
    Br_max = AB_LUT.Br_max
    
    with h5py.File(gbm_base + '/DOA/modular_functions/material_properties/data/' + material + '/single_phase.h5', 'r') as f:
        PT_POLY = load_Class(f)
        
    hSH_given_PT_fit = PT_POLY.H_given_PT_gas
    hSC_given_PT_fit = PT_POLY.H_given_PT_liq
    DSH_given_PT_fit = PT_POLY.D_given_PT_gas
    DSC_given_PT_fit = PT_POLY.D_given_PT_liq
    
    if use_nonlin:
        ArClass = interp1d_linear_spaced(Ar_min, Ar_max, P_grid[:,0:1].T, enable_inverse=True)
    else:
        ArClass = line1dclip(Ar_min, Ar_max, P_grid[0,0], P_grid[-1,0])

    return AB_refprop(grids, Ar_min, Ar_max, Br_min, Br_max, T_given_P_fit, P_given_T_fit, H0_given_P_fit, H1_given_P_fit, hSH_given_PT_fit, hSC_given_PT_fit, DSH_given_PT_fit, DSC_given_PT_fit, ArClass, interp_type, diff_idx, use_nonlin)


def get_pure_fluid_2d_DP(material, interp_type='bilinear', N=(400,400)):
    with h5py.File(gbm_base + '/DOA/modular_functions/material_properties/data/' + material + '/sat.h5', 'r') as f:
        sat_prop = load_Class(f)

    T_given_P_fit = sat_prop.T_given_P_fit
    P_given_T_fit = sat_prop.P_given_T_fit

    with h5py.File(gbm_base + '/DOA/modular_functions/material_properties/data/' + material + '/DP_DHEPTQS_' + str(N[0]) + '_' + str(N[1]) +  '.h5', 'r') as f:
        DP_LUT = load_Class(f)

    T_grid_DP = np.array(DP_LUT.T_grid)
    u_grid_DP = np.array(DP_LUT.u_grid/1000.0)
    x_grid_DP = np.array(DP_LUT.x_grid)
    h_grid_DP = np.array(DP_LUT.h_grid/1000.0)
    
    Dr_min = DP_LUT.Dr_min
    Dr_max = DP_LUT.Dr_max
    Pr_min = DP_LUT.Pr_min/1000.0
    Pr_max = DP_LUT.Pr_max/1000.0

    return DP_refprop(T_grid_DP, u_grid_DP, x_grid_DP, h_grid_DP, Dr_min, Dr_max, Pr_min, Pr_max, T_given_P_fit, P_given_T_fit)

def get_pure_fluid_2d_HP(material, interp_type='bilinear', N=(400,400), diff_idx=(3,)):
    with h5py.File(gbm_base + '/DOA/modular_functions/material_properties/data/' + material + '/sat.h5', 'r') as f:
        sat_prop = load_Class(f)

    T_given_P_fit = sat_prop.T_given_P_fit
    P_given_T_fit = sat_prop.P_given_T_fit

    with h5py.File(gbm_base + '/DOA/modular_functions/material_properties/data/' + material + '/HP_DHEPTQS_' + str(N[0]) + '_' + str(N[1]) +  '.h5', 'r') as f:
            HP_LUT = load_Class(f)

    T_grid = np.array(HP_LUT.T_grid)
    u_grid = np.array(HP_LUT.u_grid)
    x_grid = np.array(HP_LUT.x_grid)
    D_grid = np.array(HP_LUT.D_grid)

    grids = (T_grid, u_grid, x_grid, D_grid)
    
    with h5py.File(gbm_base + '/DOA/modular_functions/material_properties/data/' + material + '/single_phase.h5', 'r') as f:
        TP_POLY = load_Class(f)
        
    hSH_given_PT_fit = TP_POLY.H_given_PT_gas
    hSC_given_PT_fit = TP_POLY.H_given_PT_liq
    
    hr_min = HP_LUT.hr_min
    hr_max = HP_LUT.hr_max
    Pr_min = HP_LUT.Pr_min
    Pr_max = HP_LUT.Pr_max

    return HP_refprop(grids, hr_min, hr_max, Pr_min, Pr_max, T_given_P_fit, P_given_T_fit, hSH_given_PT_fit, hSC_given_PT_fit, interp_type, diff_idx)