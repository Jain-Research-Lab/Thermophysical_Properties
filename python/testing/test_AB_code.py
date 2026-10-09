# construct environment
import os
gbm_base = os.environ.get('GBM_BASE')
from DOA.config.config import config
lib_mode = 1 # mode == 0 pure jax, mode == 1: use jax/python mix, mode == 2 use pure python
config.update("lib_mode", lib_mode)

from functools import partial

from DOA.config.lib_config import numpy as np
import jax
import textwrap
from jax import make_jaxpr
jax.config.update("jax_enable_x64", True)

from DOA.general_functions.python_jax_equivalents.vmap import vmap
from DOA.modular_functions.material_properties.parametrized.pure_fluid_2d import get_pure_fluid_2d_AB

props_r_AB = get_pure_fluid_2d_AB("PROPANE")

mode = "Brvmap" # "hr"  "Br"  "Brvmap"

if mode == "hr": # f1 current: 409 & 433
    Pvmap = (np.ones((400,10)), np.ones((400,10)))
    vmapped = vmap(partial(props_r_AB.hr.f, dim_idx=1), in_axes=(0,)).f
    test_jaxpr = make_jaxpr(vmapped)(Pvmap)
    compiled_fn = jax.jit(vmapped).lower(Pvmap).compile()

elif mode == "Br": # f2 current: 2247 & 2597
    vmapped = partial(props_r_AB.Br, invert_idx=4)
    test_jaxpr = make_jaxpr(vmapped)(np.ones((2,)))
    compiled_fn = jax.jit(vmapped, static_argnums=None).lower(np.ones((2,))).compile()

elif mode == "Brvmap": # f3 current: 2689 & 3609
    vmapped = vmap(partial(props_r_AB.Br, invert_idx=4), in_axes=(0,)).f
    test_jaxpr = make_jaxpr(vmapped)(np.ones((2000,2)))
    compiled_fn = jax.jit(vmapped).lower(np.ones((2000,2))).compile()

# PR
with open(gbm_base + '/DOA/modular_functions/material_properties/debug/jaxpr_' + mode + '.txt', 'w') as f:
    f.write(str(test_jaxpr))
    f.write('\n\n' + '='*80 + '\n\n')
    f.write(textwrap.dedent(str(test_jaxpr)))

# HLO
with open(gbm_base + '/DOA/modular_functions/material_properties/debug/jaxHLO_' + mode + '.txt', 'w') as f:
    f.write(str(compiled_fn.as_text()))
    f.write('\n\n' + '='*80 + '\n\n')
    f.write(textwrap.dedent(str(compiled_fn.as_text())))