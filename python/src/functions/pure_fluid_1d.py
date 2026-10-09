from DOA.general_functions.general_utility.function_utility import static_partial
from DOA.general_functions.mathGBM.linear import line1dclip
from DOA.config.lib_config import config

"""
This library consists of material property functions that accept
one temperature needed to compute the material property
"""

class generic_1p_T():
    def __init__(self, k, cp, rho):
        self.k = k
        self.cp = cp
        self.rho = rho
        
        self.f = static_partial(self.f_source, (1,))
        self.h = line1dclip(0.0, 1000.0, 0.0, 1000.0*cp.y)
        
    def f_source(self, T, dim_idx):
        return self.k.f(T, dim_idx=dim_idx), self.cp.f(T, dim_idx=dim_idx), self.rho.f(T, dim_idx=dim_idx)
    
class khD_1p_T():
    def __init__(self, k, h, rho):
        self.k = k
        self.h = h
        self.rho = rho
        
        self.f = static_partial(self.f_source, (1,))
        
    def f_source(self, T, dim_idx):
        return self.k.f(T, dim_idx=dim_idx), self.h.f(T, dim_idx=dim_idx), self.rho.f(T, dim_idx=dim_idx)

class kuD_1p_T():
    def __init__(self, k, u, rho, cp=None):
        self.k = k
        self.u = u
        self.rho = rho

        if (config.lib_mode == 2) | (cp is not None):
            self.cp = cp
        
        elif (config.lib_mode == 1):
            from jax import grad
            self.cp = 1

        else:
            print(f"config.lib_mode invalid setting: {config.lib_mode}")

        self.f = static_partial(self.f_source, (1,))

    def f_source(self, T, dim_idx):
        return self.k.f(T, dim_idx=dim_idx), self.u.f(T, dim_idx=dim_idx), self.cp.f(T, dim_idx=dim_idx), self.rho.f(T, dim_idx=dim_idx)