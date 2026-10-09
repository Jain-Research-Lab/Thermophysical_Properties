import os
gbm_base = os.environ.get('GBM_BASE')
from DOA.config.config import config
mode = 1
config.update("lib_mode", mode) # mode == 0 pure jax, mode == 1: jax/python mix, mode == 2 pure python

from DOA.modular_functions.material_properties.parametrized.pure_fluid_2d import get_pure_fluid_2d_HP
from DOA.modular_functions.material_properties.testing.plot_gen_3d_plot import plot_3d_compare
from DOA.config.lib_config import numpy as np
import matplotlib.pyplot as plt
import time

# get property function
props_r_HP = get_pure_fluid_2d_HP("PROPANE")

# pick inputs
hr_Nd_in, Pr_Nd_in = np.meshgrid(np.linspace(0.0, 1200.0, 400), np.linspace(100.0, 4000.0, 400))
hr_Nd, Pr_Nd = np.meshgrid(np.linspace(0.0, 1200.0, 20), np.linspace(100.0, 4000.0, 20))

# Test 1: array of points, single table, no partial derivatives
if (config.lib_mode == 1):
    from DOA.general_functions.general_utility.function_utility import compile_from_f
    Dr_compiled = compile_from_f(props_r_HP.Dr.f, ((hr_Nd, Pr_Nd),), static_argnums=None, dim_idx=2)
    Tr_compiled = compile_from_f(props_r_HP.Tr.f, ((hr_Nd, Pr_Nd),), static_argnums=None, dim_idx=2)
    xr_compiled = compile_from_f(props_r_HP.xr.f, ((hr_Nd, Pr_Nd),), static_argnums=None, dim_idx=2)
    
    # warmup the XLA
    Dr_sample = Dr_compiled((hr_Nd+10, Pr_Nd+10))
    Tr_sample = Tr_compiled((hr_Nd+10, Pr_Nd+10))
    xr_sample = xr_compiled((hr_Nd+10, Pr_Nd+10))
    Dr_sample.block_until_ready()
    Tr_sample.block_until_ready()
    xr_sample.block_until_ready()

    t0 = time.time()
    Dr_sample = Dr_compiled((hr_Nd, Pr_Nd))
    Tr_sample = Tr_compiled((hr_Nd, Pr_Nd))
    xr_sample = xr_compiled((hr_Nd, Pr_Nd))
    Dr_sample.block_until_ready()
    Tr_sample.block_until_ready()
    xr_sample.block_until_ready()
    
elif (config.lib_mode == 2):
    t0 = time.time()
    Dr_sample = props_r_HP.Dr.f((hr_Nd, Pr_Nd), dim_idx=2)
    Tr_sample = props_r_HP.Tr.f((hr_Nd, Pr_Nd), dim_idx=2)
    xr_sample = props_r_HP.xr.f((hr_Nd, Pr_Nd), dim_idx=2)
    
print(time.time() - t0)
print(np.vstack((Dr_sample, Tr_sample, xr_sample)))
print("------------")

# Test 2: single point, single table, partial derivatives
if (config.lib_mode == 1):
    from DOA.general_functions.general_utility.function_utility import compile_from_f
    
    grids = props_r_HP.Dr.grids
    mx = props_r_HP.Dr.mx
    x_min = props_r_HP.Dr.x_min
    NP_max = props_r_HP.Dr.NP_max
    H = props_r_HP.Dr.H
    dH = props_r_HP.Dr.dH
    di = props_r_HP.Dr.di

    Dr_compiled = compile_from_f(props_r_HP.Dr.f_source_Nd, ((hr_Nd, Pr_Nd),), static_argnums=(8,), grids=grids, H=H, dH=dH, di=di, mx=mx, x_min=x_min, NP_max=NP_max, diff_idx=(0,))
    
    # warmup the XLA
    Dr_sample, Dr_dA_sample, Dr_dB_sample = Dr_compiled((hr_Nd+10, Pr_Nd+10))
    Dr_sample.block_until_ready()
    Dr_dA_sample.block_until_ready()
    Dr_dB_sample.block_until_ready()

    t0 = time.time()
    Dr_sample, Dr_dA_sample, Dr_dB_sample = Dr_compiled((hr_Nd, Pr_Nd))
    Dr_sample.block_until_ready()
    Dr_dA_sample.block_until_ready()
    Dr_dB_sample.block_until_ready()
    
elif (config.lib_mode == 2):
    t0 = time.time()
    Dr_sample, Dr_dA_sample, Dr_dB_sample = props_r_HP.Dr.f_source_Nd((hr_Nd, Pr_Nd), props_r_HP.Dr.grids, props_r_HP.Dr.H, props_r_HP.Dr.dH, props_r_HP.Dr.di, props_r_HP.Dr.mx, props_r_HP.Dr.x_min, props_r_HP.Dr.NP_max, [0])
    
print(time.time() - t0)
print(np.array((Dr_sample)))
print("------------")

# # Test 3: single point, multiple tables, no partial derivatives
# if (config.lib_mode == 1):
#     from DOA.general_functions.general_utility.function_utility import compile_from_f
#     fThx_compiled = compile_from_f(props_r_HP.fThx.f, ((hr_Nd, Pr_Nd),), static_argnums=None)

#     # warmup the XLA
#     fTHx_sample = fThx_compiled((hr_Nd+10, Pr_Nd+10))
#     fTHx_sample.block_until_ready()

#     t0 = time.time()
#     fTHx_sample = fThx_compiled((hr_Nd, Pr_Nd))
#     fTHx_sample.block_until_ready()
    
# elif (config.lib_mode == 2):
#     t0 = time.time()
#     fTHx_sample = props_r_HP.fThx.f((hr_Nd, Pr_Nd))

# print(time.time() - t0)
# print(fTHx_sample)
# print("------------")

# Test 4: single point, multiple tables, partial derivatives
if (config.lib_mode == 1):
    from DOA.general_functions.general_utility.function_utility import compile_from_f
    fODE_compiled = compile_from_f(props_r_HP.fODE.f, ((hr_Nd, Pr_Nd),), static_argnums=None, dim_idx=2)

    # warmup the XLA
    fODE_prop_sample, fODE_dA_sample, fODE_dB_sample = fODE_compiled((hr_Nd+10, Pr_Nd+10))
    fODE_prop_sample.block_until_ready()
    fODE_dA_sample.block_until_ready()
    fODE_dB_sample.block_until_ready()
    
    fODE_prop_sample, fODE_dA_sample, fODE_dB_sample = fODE_compiled((hr_Nd+10, Pr_Nd+10))
    fODE_prop_sample.block_until_ready()
    fODE_dA_sample.block_until_ready()
    fODE_dB_sample.block_until_ready()
    
    fODE_prop_sample, fODE_dA_sample, fODE_dB_sample = fODE_compiled((hr_Nd+10, Pr_Nd+10))
    fODE_prop_sample.block_until_ready()
    fODE_dA_sample.block_until_ready()
    fODE_dB_sample.block_until_ready()

    t0 = time.time()
    fODE_prop_sample, fODE_dA_sample, fODE_dB_sample = fODE_compiled((hr_Nd, Pr_Nd))
    fODE_prop_sample.block_until_ready()
    fODE_dA_sample.block_until_ready()
    fODE_dB_sample.block_until_ready()
    
elif (config.lib_mode == 2):
    t0 = time.time()
    fODE_prop_sample, fODE_dA_sample, fODE_dB_sample = props_r_HP.fODE.f((hr_Nd, Pr_Nd), dim_idx=2)

print(time.time() - t0)
print(fODE_prop_sample)
print("------------")

Tr, ur, xr, Dr = fODE_prop_sample

plot_3d_compare(hr_Nd_in.T, Pr_Nd_in.T, np.squeeze(props_r_HP.Dr.grids), hr_Nd, Pr_Nd, Dr, "Enthalpy (kJ/kg)", "Pressure (kPa)", "Density (kg/m^3)", 1, 0)
plt.show()