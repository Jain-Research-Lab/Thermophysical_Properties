import os
gbm_base = os.environ.get('GBM_BASE')
from DOA.config.config import config
mode = 1
config.update("lib_mode", mode) # mode == 0 pure jax, mode == 1: jax/python mix, mode == 2 pure python
    
from DOA.modular_functions.material_properties.parametrized.pure_fluid_2d import get_pure_fluid_2d_AB
from DOA.config.lib_config import numpy as np
import time

# get property function
props_r_AB = get_pure_fluid_2d_AB("PROPANE")

# pick inputs
Ar_0d = 300.0
Br_0d = 300.0

# Test 1: single point, single table, no partial derivatives
if (config.lib_mode == 1):
    from DOA.general_functions.general_utility.function_utility import compile_from_f
    
    Pr_compiled = compile_from_f(props_r_AB.Pr.f, (Ar_0d,), static_argnums=None, dim_idx=0)
    Dr_compiled = compile_from_f(props_r_AB.Dr.f, ((Ar_0d, Br_0d),), static_argnums=None, dim_idx=0)
    hr_compiled = compile_from_f(props_r_AB.hr.f, ((Ar_0d, Br_0d),), static_argnums=None, dim_idx=0)
    Tr_compiled = compile_from_f(props_r_AB.Tr.f, ((Ar_0d, Br_0d),), static_argnums=None, dim_idx=0)
    xr_compiled = compile_from_f(props_r_AB.xr.f, ((Ar_0d, Br_0d),), static_argnums=None, dim_idx=0)
    
    # warmup the XLA
    Pr_sample = Pr_compiled(Ar_0d+10)
    Dr_sample = Dr_compiled((Ar_0d+10, Br_0d+10))
    hr_sample = hr_compiled((Ar_0d+10, Br_0d+10))
    Tr_sample = Tr_compiled((Ar_0d+10, Br_0d+10))
    xr_sample = xr_compiled((Ar_0d+10, Br_0d+10))
    Pr_sample.block_until_ready()
    Dr_sample.block_until_ready()
    hr_sample.block_until_ready()
    Tr_sample.block_until_ready()
    xr_sample.block_until_ready()

    t0 = time.time()
    Pr_sample = Pr_compiled(Ar_0d)
    Dr_sample = Dr_compiled((Ar_0d, Br_0d))
    hr_sample = hr_compiled((Ar_0d, Br_0d))
    Tr_sample = Tr_compiled((Ar_0d, Br_0d))
    xr_sample = xr_compiled((Ar_0d, Br_0d))
    Pr_sample.block_until_ready()
    Dr_sample.block_until_ready()
    hr_sample.block_until_ready()
    Tr_sample.block_until_ready()
    xr_sample.block_until_ready()
    
elif (config.lib_mode == 2):
    t0 = time.time()
    Pr_sample = props_r_AB.Pr.f(Ar_0d, dim_idx=0)
    Dr_sample = props_r_AB.Dr.f((Ar_0d, Br_0d), dim_idx=0)
    hr_sample = props_r_AB.hr.f((Ar_0d, Br_0d), dim_idx=0)
    Tr_sample = props_r_AB.Tr.f((Ar_0d, Br_0d), dim_idx=0)
    xr_sample = props_r_AB.xr.f((Ar_0d, Br_0d), dim_idx=0)
    
print(time.time() - t0)
print(np.array((Pr_sample, Dr_sample, hr_sample, Tr_sample, xr_sample)))
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
    
    Dr_compiled = compile_from_f(props_r_AB.Dr.f_source_0d, ((Ar_0d, Br_0d),), static_argnums=(8,), grids=grids, H=H, dH=dH, di=di, mx=mx, x_min=x_min, NP_max=NP_max, diff_idx=(1,))
    
    # warmup the XLA
    Dr_sample, Dr_dA_sample, Dr_dB_sample = Dr_compiled((Ar_0d+10, Br_0d+10))
    Dr_sample.block_until_ready()
    Dr_dA_sample.block_until_ready()
    Dr_dB_sample.block_until_ready()

    t0 = time.time()
    Dr_sample, Dr_dA_sample, Dr_dB_sample = Dr_compiled((Ar_0d, Br_0d))
    Dr_sample.block_until_ready()
    Dr_dA_sample.block_until_ready()
    Dr_dB_sample.block_until_ready()
    
elif (config.lib_mode == 2):
    t0 = time.time()
    Dr_sample, Dr_dA_sample, Dr_dB_sample = props_r_AB.Dr.f_source_0d((Ar_0d, Br_0d), props_r_AB.Dr.grids, props_r_AB.Dr.H, props_r_AB.Dr.dH, props_r_AB.Dr.di, props_r_AB.Dr.mx, props_r_AB.Dr.x_min, props_r_AB.Dr.NP_max, diff_idx=[0])
    
print(time.time() - t0)
print(np.array((Dr_sample)))
print(np.array((Dr_dA_sample)))
print(np.array((Dr_dB_sample)))
print("------------")

# Test 3: single point, multiple tables, no partial derivatives
if (config.lib_mode == 1):
    from DOA.general_functions.general_utility.function_utility import compile_from_f
    fThx_compiled = compile_from_f(props_r_AB.fThxD.f, ((Ar_0d, Br_0d),), static_argnums=None, dim_idx=0)

    # warmup the XLA
    fTHx_sample = fThx_compiled((Ar_0d+10, Br_0d+10))
    fTHx_sample.block_until_ready()

    t0 = time.time()
    fTHx_sample = fThx_compiled((Ar_0d, Br_0d))
    fTHx_sample.block_until_ready()
    
elif (config.lib_mode == 2):
    t0 = time.time()
    fTHx_sample = props_r_AB.fThxD.f((Ar_0d, Br_0d), dim_idx=0)

print(time.time() - t0)
print(fTHx_sample)
print("------------")

# Test 4: single point, multiple tables, partial derivatives
if (config.lib_mode == 1):
    from DOA.general_functions.general_utility.function_utility import compile_from_f
    fODE_compiled = compile_from_f(props_r_AB.fODE.f, ((Ar_0d, Br_0d),), static_argnums=None, dim_idx=0)

    # warmup the XLA
    fODE_sample, fODE_dA_sample, fODE_dB_sample = fODE_compiled((Ar_0d+10, Br_0d+10))
    fODE_sample.block_until_ready()
    fODE_dA_sample.block_until_ready()
    fODE_dB_sample.block_until_ready()

    t0 = time.time()
    fODE_prop_sample, fODE_dA_sample, fODE_dB_sample = fODE_compiled((Ar_0d, Br_0d))
    fODE_prop_sample.block_until_ready()
    fODE_dA_sample.block_until_ready()
    fODE_dB_sample.block_until_ready()
    
elif (config.lib_mode == 2):
    t0 = time.time()
    fODE_prop_sample, fODE_dA_sample, fODE_dB_sample = props_r_AB.fODE.f((Ar_0d, Br_0d), dim_idx=0)

print(time.time() - t0)
print(fODE_prop_sample)
print(fODE_dA_sample)
print(fODE_dB_sample)
print("------------")