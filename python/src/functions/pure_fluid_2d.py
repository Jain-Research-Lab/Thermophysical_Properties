from DOA.config.lib_config import numpy as np
from DOA.general_functions.general_utility.function_utility import static_partial
from DOA.general_functions.python_jax_equivalents.vmap import vmap

from DOA.general_functions.solvers.root1d_bounded.brentq_SAFE import brentq_SAFE
from DOA.general_functions.mathGBM.interp2d import interp2d_bilinear
from DOA.general_functions.mathGBM.polynomial import logpoly, polyexp
from DOA.general_functions.mathGBM.polynomial import poly4_2d
from DOA.general_functions.mathGBM.interp1d import interp1d_linear_spaced

from functools import partial

class AB_refprop:
    # grids order for bilinear: T_grid, h_grid, u_grid, x_grid, D_grid, P_grid (tuple)
    def __init__(self, grids, Ar_min, Ar_max, Br_min, Br_max, T_given_P_fit, P_given_T_fit, H0_given_P_fit, H1_given_P_fit, hSH_given_PT_fit, hSC_given_PT_fit, DSH_given_PT_fit, DSC_given_PT_fit, ArClass, diff_idx, invert_Ar_flag=False):
        # coefficients for equally spaced 2d lut with input clamping
        self.AB_min = np.array((Ar_min, Br_min))
        self.AB_max = np.array((Ar_max, Br_max))
        self.grids = grids

        # lookup tables
        self.Tr = interp2d_bilinear(x_min=self.AB_min, x_max=self.AB_max, grids=(grids[0],))
        self.hr = interp2d_bilinear(x_min=self.AB_min, x_max=self.AB_max, grids=(grids[1],))
        self.Er = interp2d_bilinear(x_min=self.AB_min, x_max=self.AB_max, grids=(grids[2],))
        self.xr = interp2d_bilinear(x_min=self.AB_min, x_max=self.AB_max, grids=(grids[3],))
        self.Dr = interp2d_bilinear(x_min=self.AB_min, x_max=self.AB_max, grids=(grids[4],))
        self.Pr = interp1d_linear_spaced(x_min=Ar_min, x_max=Ar_max, vecs=grids[5][:,0:1].T, enable_inverse=True)

        self.fODE = interp2d_bilinear(x_min=self.AB_min, x_max=self.AB_max, grids=grids, diff_idx=diff_idx)

        grids_ThxD = np.concatenate((self.Tr.grids,self.hr.grids,self.xr.grids,self.Dr.grids), axis=0)
        self.fThxD = interp2d_bilinear(x_min=self.AB_min, x_max=self.AB_max, grids=grids_ThxD)

        self.NABr_max = np.array(grids[0].shape) - 2
        self.mABr = (self.NABr_max + 1) / (self.AB_max - self.AB_min)
                
        # Define individual lookup tables
        self.ArClass = ArClass
        self.invert_Ar_flag = invert_Ar_flag
                
        # saturated properties
        self.Tsat = logpoly(T_given_P_fit)
        self.H0sat = logpoly(H0_given_P_fit)
        self.H1sat = logpoly(H1_given_P_fit)
        self.Psat = polyexp(P_given_T_fit)
        
        # properties outside the dome
        self.hSH_PT = poly4_2d(hSH_given_PT_fit)
        self.hSC_PT = poly4_2d(hSC_given_PT_fit)
        self.DSH_PT = poly4_2d(DSH_given_PT_fit)
        self.DSC_PT = poly4_2d(DSC_given_PT_fit)
        
        # inversion functions
        self.prop_funcs = [self.Tr.f, self.Er.f, self.xr.f, self.Dr.f, self.hr.f]
        self.Ar = static_partial(self.source_Ar_Explicit, (2,), Ar_bounds=(Ar_min, Ar_max))
        self.ArT = static_partial(self.source_Ar, (1,), Ar_bounds=(Ar_min, Ar_max))
        self.Br = static_partial(self.source_Br, (1,), Br_bounds=(Br_min, Br_max))
        self.AB = static_partial(self.source_AB, (1,))
        
        # Sweep Functions
        self.DB2A = vmap(partial(self.ArT, invert_idx=3), in_axes=(0,)).f
        self.Ah2B = vmap(partial(self.Br, invert_idx=4), in_axes=(0,)).f
        self.AD2B = vmap(partial(self.Br, invert_idx=3), in_axes=(0,)).f
        self.Ph2AB = vmap(partial(self.AB, invert_idx=4), in_axes=(0,)).f
        self.PT2AB = vmap(partial(self.AB, invert_idx=0), in_axes=(0,)).f
    
    def source_AB(self, bc, invert_idx):
        Pr, Prop = bc
        
        Ar, converged_Ar = self.Ar(Pr, dim_idx=0)
        Br, converged_Br, iterations_Br = self.Br((Ar, Prop), invert_idx)
        F = np.array([converged_Ar & converged_Br, converged_Ar, converged_Br, iterations_Br])
        
        return Ar, Br, F
    
    def source_Ar_Explicit(self, Pr, Ar_bounds, dim_idx):
        if self.invert_Ar_flag:
            Ar = self.ArClass.fi(Pr, invert_idx=0, dim_idx=dim_idx)
        else:
            Ar = self.ArClass.fi(Pr, dim_idx=dim_idx)
            
        converged_Ar = (Ar >= Ar_bounds[0]) & (Ar <= Ar_bounds[1])
        return Ar, converged_Ar
    
    def source_Ar(self, bc, invert_idx, Ar_bounds):
        return brentq_SAFE(self.res_Ar, 1e-14, 1e-14, 100, (2,3), invert_idx=invert_idx, dim_idx=0).f(Ar_bounds, (bc,))

    def res_Ar(self, Ar, bc, invert_idx, dim_idx):
        Br, Prop_REF = bc

        return Prop_REF - self.prop_funcs[invert_idx]((Ar, Br), dim_idx=dim_idx)
    
    def source_Br(self, bc, invert_idx, Br_bounds):
        return brentq_SAFE(self.res_Br, 1e-14, 1e-14, 100, (2,3), invert_idx=invert_idx, dim_idx=0).f(Br_bounds, (bc,))
    
    def res_Br(self, Br, bc, invert_idx, dim_idx):
        Ar, Prop_REF = bc
        
        return Prop_REF - self.prop_funcs[invert_idx]((Ar, Br), dim_idx=dim_idx)

class DP_refprop:
    def __init__(self, T_grid, u_grid, x_grid, h_grid, Dr_min, Dr_max, Pr_min, Pr_max, T_given_P_fit, P_given_T_fit):
        # Range of DP
        self.DP_min = np.array((Dr_min, Pr_min))
        self.DP_max = np.array((Dr_max, Pr_max))
        self.NDPr_max = np.array(T_grid.shape) - 2
        self.mDPr = (self.NDPr_max + 1) / (self.DP_max - self.DP_min)
        
        # Define individual lookup tables
        self.Tr = interp2d_bilinear(x_min=self.DP_min, x_max=self.DP_max, grids=(T_grid,))
        self.Er = interp2d_bilinear(x_min=self.DP_min, x_max=self.DP_max, grids=(u_grid,))
        self.xr = interp2d_bilinear(x_min=self.DP_min, x_max=self.DP_max, grids=(x_grid,))
        self.hr = interp2d_bilinear(x_min=self.DP_min, x_max=self.DP_max, grids=(h_grid,))
        
        # multi-output lookup tables
        self.fODE = interp2d_bilinear(x_min=self.DP_min, x_max=self.DP_max, grids=(T_grid,h_grid,u_grid,x_grid), diff_idx=(2,))

        # saturated properties
        self.Tsat = logpoly(T_given_P_fit)
        self.Psat = polyexp(P_given_T_fit)
    
class HP_refprop:
    # grids order for bilinear: T_grid, u_grid, x_grid, D_grid (tuple)
    def __init__(self, grids, hr_min, hr_max, Pr_min, Pr_max, T_given_P_fit, P_given_T_fit, hSH_given_PT_fit, hSC_given_PT_fit, diff_idx):
        # coefficients for equally spaced 2d lut with input clamping
        self.HP_min = np.array((hr_min, Pr_min))
        self.HP_max = np.array((hr_max, Pr_max))
        
        # lookup tables
        self.Tr = interp2d_bilinear(x_min=self.HP_min, x_max=self.HP_max, grids=(grids[0],))
        self.Er = interp2d_bilinear(x_min=self.HP_min, x_max=self.HP_max, grids=(grids[1],))
        self.xr = interp2d_bilinear(x_min=self.HP_min, x_max=self.HP_max, grids=(grids[2],))
        self.Dr = interp2d_bilinear(x_min=self.HP_min, x_max=self.HP_max, grids=(grids[3],))        
        self.fODE = interp2d_bilinear(x_min=self.HP_min, x_max=self.HP_max, grids=grids, diff_idx=diff_idx)

        self.NHPr_max = np.array(grids[0].shape) - 2
        self.mHPr = (self.NHPr_max + 1) / (self.HP_max - self.HP_min)

        # saturated properties
        self.Tsat = logpoly(T_given_P_fit)
        self.Psat = polyexp(P_given_T_fit)
        
        # properties outside the dome
        self.hSH_PT = poly4_2d(hSH_given_PT_fit)
        self.hSC_PT = poly4_2d(hSC_given_PT_fit)