import os
gbm_base = os.environ.get('GBM_BASE')
from DOA.config.config import config
mode = 1
config.update("lib_mode", mode) # mode == 0 pure jax, mode == 1: jax/python mix, mode == 2 pure python
    
from DOA.modular_functions.material_properties.parametrized.pure_fluid_2d import get_pure_fluid_2d_AB
from DOA.modular_functions.material_properties.testing.plot_gen_3d_plot import plot_3d_compare
from DOA.config.lib_config import numpy as np
import matplotlib.pyplot as plt
import time
from scipy.stats import gmean

# get property function
props_r_AB = get_pure_fluid_2d_AB("PROPANE")

# pick inputs
Ar_Nd, Br_Nd = np.meshgrid(np.linspace(205.0, 1995.0, 20), np.linspace(205.0, 1995.0, 20))
# Ar_Nd, Br_Nd = np.meshgrid(np.linspace(-2000.0, 4000.0, 40), np.linspace(-2000.0, 4000.0, 40))
# Ar_Nd, Br_Nd = np.meshgrid(np.linspace(0.0, 2200.0, 40), np.linspace(0.0, 2200.0, 40))

# Test 1: array of points, single table, no partial derivatives
if (config.lib_mode == 1):
    from DOA.general_functions.general_utility.function_utility import compile_from_f
    Pr_compiled = compile_from_f(props_r_AB.Pr.f, (Ar_Nd,), static_argnums=None, dim_idx=2)
    Dr_compiled = compile_from_f(props_r_AB.Dr.f, ((Ar_Nd, Br_Nd),), static_argnums=None, dim_idx=2)
    hr_compiled = compile_from_f(props_r_AB.hr.f, ((Ar_Nd, Br_Nd),), static_argnums=None, dim_idx=2)
    Tr_compiled = compile_from_f(props_r_AB.Tr.f, ((Ar_Nd, Br_Nd),), static_argnums=None, dim_idx=2)
    xr_compiled = compile_from_f(props_r_AB.xr.f, ((Ar_Nd, Br_Nd),), static_argnums=None, dim_idx=2)
    
    # warmup the XLA
    Pr_sample = Pr_compiled(Ar_Nd+10)
    Dr_sample = Dr_compiled((Ar_Nd+10, Br_Nd+10))
    hr_sample = hr_compiled((Ar_Nd+10, Br_Nd+10))
    Tr_sample = Tr_compiled((Ar_Nd+10, Br_Nd+10))
    xr_sample = xr_compiled((Ar_Nd+10, Br_Nd+10))
    Pr_sample.block_until_ready()
    Dr_sample.block_until_ready()
    hr_sample.block_until_ready()
    Tr_sample.block_until_ready()
    xr_sample.block_until_ready()

    t0 = time.time()
    Pr_sample = Pr_compiled(Ar_Nd)
    Dr_sample = Dr_compiled((Ar_Nd, Br_Nd))
    hr_sample = hr_compiled((Ar_Nd, Br_Nd))
    Tr_sample = Tr_compiled((Ar_Nd, Br_Nd))
    xr_sample = xr_compiled((Ar_Nd, Br_Nd))
    Pr_sample.block_until_ready()
    Dr_sample.block_until_ready()
    hr_sample.block_until_ready()
    Tr_sample.block_until_ready()
    xr_sample.block_until_ready()
    
elif (config.lib_mode == 2):
    t0 = time.time()
    Pr_sample = props_r_AB.Pr.f(Ar_Nd, dim_idx=2)
    Dr_sample = props_r_AB.Dr.f((Ar_Nd, Br_Nd), dim_idx=2)
    hr_sample = props_r_AB.hr.f((Ar_Nd, Br_Nd), dim_idx=2)
    Tr_sample = props_r_AB.Tr.f((Ar_Nd, Br_Nd), dim_idx=2)
    xr_sample = props_r_AB.xr.f((Ar_Nd, Br_Nd), dim_idx=2)
    
print(time.time() - t0)
print(np.vstack((Pr_sample, Dr_sample, hr_sample, Tr_sample, xr_sample)))
print("------------")

# Test 2: single point, single table, partial derivatives
if (config.lib_mode == 1):
    from DOA.general_functions.general_utility.function_utility import compile_from_f

    grids = props_r_AB.Dr.grids
    mx = props_r_AB.Dr.mx
    x_min = props_r_AB.Dr.x_min
    NP_max = props_r_AB.Dr.NP_max
    H = props_r_AB.Dr.H
    dH = props_r_AB.Dr.dH
    di = props_r_AB.Dr.di

    Dr_compiled = compile_from_f(props_r_AB.Dr.f_source_Nd, ((Ar_Nd, Br_Nd),), static_argnums=(8,), H=H, dH=dH, di=di, grids=grids, mx=mx, x_min=x_min, NP_max=NP_max, diff_idx=(0,))
    
    # warmup the XLA
    Dr_sample, Dr_dA_sample, Dr_dB_sample = Dr_compiled((Ar_Nd+10, Br_Nd+10))
    Dr_sample.block_until_ready()
    Dr_dA_sample.block_until_ready()
    Dr_dB_sample.block_until_ready()

    t0 = time.time()
    Dr_sample, Dr_dA_sample, Dr_dB_sample = Dr_compiled((Ar_Nd, Br_Nd))
    Dr_sample.block_until_ready()
    Dr_dA_sample.block_until_ready()
    Dr_dB_sample.block_until_ready()
    
elif (config.lib_mode == 2):
    t0 = time.time()
    Dr_sample, Dr_dA_sample, Dr_dB_sample = props_r_AB.Dr.f_source_Nd((Ar_Nd, Br_Nd), props_r_AB.Dr.grids, props_r_AB.Dr.H, props_r_AB.Dr.dH, props_r_AB.Dr.di, props_r_AB.Dr.mx, props_r_AB.Dr.x_min, props_r_AB.Dr.NP_max, [0])
    
print(time.time() - t0)
print(np.array((Dr_sample)))
print("------------")

# Test 3: single point, multiple tables, no partial derivatives
if (config.lib_mode == 1):
    from DOA.general_functions.general_utility.function_utility import compile_from_f
    fThxD_compiled = compile_from_f(props_r_AB.fThxD.f, ((Ar_Nd, Br_Nd),), static_argnums=None, dim_idx=2)

    # warmup the XLA
    fTHx_sample = fThxD_compiled((Ar_Nd+10, Br_Nd+10))
    fTHx_sample.block_until_ready()

    t0 = time.time()
    fTHx_sample = fThxD_compiled((Ar_Nd, Br_Nd))
    fTHx_sample.block_until_ready()
    
elif (config.lib_mode == 2):
    t0 = time.time()
    fTHx_sample = props_r_AB.fThxD.f((Ar_Nd, Br_Nd), dim_idx=2)

print(time.time() - t0)
print(fTHx_sample)
print("------------")

# Test 4: single point, multiple tables, partial derivatives
if (config.lib_mode == 1):
    from DOA.general_functions.general_utility.function_utility import compile_from_f
    fODE_compiled = compile_from_f(props_r_AB.fODE.f, ((Ar_Nd, Br_Nd),), static_argnums=None, dim_idx=2)

    # warmup the XLA
    fODE_prop_sample, fODE_dA_sample, fODE_dB_sample = fODE_compiled((Ar_Nd+10, Br_Nd+10))
    fODE_prop_sample.block_until_ready()
    fODE_dA_sample.block_until_ready()
    fODE_dB_sample.block_until_ready()
    
    fODE_prop_sample, fODE_dA_sample, fODE_dB_sample = fODE_compiled((Ar_Nd+10, Br_Nd+10))
    fODE_prop_sample.block_until_ready()
    fODE_dA_sample.block_until_ready()
    fODE_dB_sample.block_until_ready()

    t0 = time.time()
    fODE_prop_sample, fODE_dA_sample, fODE_dB_sample = fODE_compiled((Ar_Nd, Br_Nd))
    fODE_prop_sample.block_until_ready()
    fODE_dA_sample.block_until_ready()
    fODE_dB_sample.block_until_ready()
    
elif (config.lib_mode == 2):
    t0 = time.time()
    fODE_prop_sample, fODE_dA_sample, fODE_dB_sample = props_r_AB.fODE.f((Ar_Nd, Br_Nd), dim_idx=2)

print(time.time() - t0)
print(fODE_prop_sample)
print("------------")

Tr, hr, Er, xr, Dr, Pr = fODE_prop_sample

dd_da, du_da = fODE_dA_sample
dd_db, du_db = fODE_dB_sample

# plot_3d_compare(np.squeeze(props_r_AB.hr.grids), np.squeeze(props_r_AB.fODE.grids[-1,:,:]), np.squeeze(props_r_AB.Dr.grids), hr, Pr, Dr, "Enthalpy (kJ/kg)", "Pressure (kPa)", "Density (kg/m^3)", 1, 0)

fig0 = plt.figure(2)
ax0 = fig0.add_subplot(111, projection='3d')
surf = ax0.plot_surface(Ar_Nd, Br_Nd, Dr, cmap='viridis', alpha=0.6, edgecolor='none')
ax0.set_xlabel("Gamma")
ax0.set_ylabel("Beta")
ax0.set_zlabel("Density (kg/m^3)")
surf._edgecolors2d = surf._edgecolor3d
surf._facecolors2d = surf._facecolor3d

fig0 = plt.figure(3)
ax0 = fig0.add_subplot(111, projection='3d')
surf = ax0.plot_surface(Ar_Nd, Br_Nd, hr, cmap='viridis', alpha=0.6, edgecolor='none')
ax0.set_xlabel("Enthalpy (kJ/kg)")
ax0.set_ylabel("Pressure (kPa)")
ax0.set_zlabel("Density (kg/m^3)")
surf._edgecolors2d = surf._edgecolor3d
surf._facecolors2d = surf._facecolor3d

fig0 = plt.figure(4)
ax0 = fig0.add_subplot(111, projection='3d')
surf = ax0.plot_surface(Ar_Nd, Br_Nd, Pr, cmap='viridis', alpha=0.6, edgecolor='none')
ax0.set_xlabel("Enthalpy (kJ/kg)")
ax0.set_ylabel("Pressure (kPa)")
ax0.set_zlabel("Density (kg/m^3)")
surf._edgecolors2d = surf._edgecolor3d
surf._facecolors2d = surf._facecolor3d

fig0 = plt.figure(5)
ax0 = fig0.add_subplot(111, projection='3d')
surf = ax0.plot_surface(Ar_Nd, Br_Nd, Tr, cmap='viridis', alpha=0.6, edgecolor='none')
ax0.set_xlabel("Enthalpy (kJ/kg)")
ax0.set_ylabel("Pressure (kPa)")
ax0.set_zlabel("Density (kg/m^3)")
surf._edgecolors2d = surf._edgecolor3d
surf._facecolors2d = surf._facecolor3d

fig0 = plt.figure(6)
ax0 = fig0.add_subplot(111, projection='3d')
surf = ax0.plot_surface(Ar_Nd, Br_Nd, xr, cmap='viridis', alpha=0.6, edgecolor='none')
ax0.set_xlabel("Enthalpy (kJ/kg)")
ax0.set_ylabel("Pressure (kPa)")
ax0.set_zlabel("Density (kg/m^3)")
surf._edgecolors2d = surf._edgecolor3d
surf._facecolors2d = surf._facecolor3d

fig0 = plt.figure(7)
ax0 = fig0.add_subplot(111, projection='3d')
surf = ax0.plot_surface(Ar_Nd, Br_Nd, Er, cmap='viridis', alpha=0.6, edgecolor='none')
ax0.set_xlabel("Enthalpy (kJ/kg)")
ax0.set_ylabel("Pressure (kPa)")
ax0.set_zlabel("Density (kg/m^3)")
surf._edgecolors2d = surf._edgecolor3d
surf._facecolors2d = surf._facecolor3d

Ci = dd_da / (Dr*(dd_da*du_db - dd_db*du_da))

Ci_Mean = np.mean(Ci)
Ci_Medn = np.median(Ci)
Ci_Min = np.min(Ci)
Ci_gmean = gmean(Ci.flatten())

print(Ci_gmean)

fig0 = plt.figure(8)
ax0 = fig0.add_subplot(111, projection='3d')
surf = ax0.plot_surface(Ar_Nd, Br_Nd, Ci, cmap='viridis', alpha=0.6, edgecolor='none')
ax0.set_xlabel("Ar")
ax0.set_ylabel("Br")
ax0.set_zlabel("Ci")
surf._edgecolors2d = surf._edgecolor3d
surf._facecolors2d = surf._facecolor3d

plt.show()