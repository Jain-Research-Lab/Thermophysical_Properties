import os
gbm_base = os.environ.get('GBM_BASE')
from DOA.config.config import config
mode = 1
config.update("lib_mode", mode) # mode == 0 pure jax, mode == 1: jax/python mix, mode == 2 pure python

from DOA.modular_functions.material_properties.parametrized.pure_fluid_2d import get_pure_fluid_2d_AB
from DOA.general_functions.python_jax_equivalents.vmap import vmap
from DOA.config.lib_config import numpy as np
from functools import partial
import time

# get property function
props_r_AB = get_pure_fluid_2d_AB("PROPANE")

# Test 1: Invert using hP
hr_Nd, Pr_Nd = np.meshgrid(np.linspace(100.0, 600.0, 20), np.linspace(100.0, 4000.0, 20))
Ph = np.hstack((Pr_Nd.reshape((-1,1)), hr_Nd.reshape((-1,1))))

if (config.lib_mode == 1):
    from DOA.general_functions.general_utility.function_utility import compile_from_f
    
    ABF_compiled = compile_from_f(vmap(partial(props_r_AB.AB, invert_idx=4), in_axes=(0,)).f, (Ph,), static_argnums=None)
    Pr_compiled = compile_from_f(props_r_AB.Pr.f, (Ph[:,0],), static_argnums=None, dim_idx=1)
    hr_compiled = compile_from_f(props_r_AB.hr.f, ((Ph[:,0], Ph[:,1]),), static_argnums=None, dim_idx=1)
    
    t0 = time.time()
    Ar, Br, F = ABF_compiled(Ph)
    Pr_sample = Pr_compiled(Ar)
    hr_sample = hr_compiled((Ar, Br))
    Ar.block_until_ready()
    Br.block_until_ready()
    F.block_until_ready()
    Pr_sample.block_until_ready()
    hr_sample.block_until_ready()

elif (config.lib_mode == 2):
    t0 = time.time()
    Ar, Br, F = props_r_AB.Ph2AB(Ph)
    Pr_sample = props_r_AB.Pr.f(Ar, dim_idx=1)
    hr_sample = props_r_AB.hr.f((Ar, Br), dim_idx=1)
    
print(time.time() - t0)
error = np.abs(Ph - np.stack((Pr_sample, hr_sample), axis=1)) / Ph
print(np.max(error))