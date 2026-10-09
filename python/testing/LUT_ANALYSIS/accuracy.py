import os
gbm_base = os.environ.get('GBM_BASE')
from DOA.config.config import config
mode = 2
config.update("lib_mode", mode) # mode == 0 pure jax, mode == 1: jax/python mix, mode == 2 pure python

from DOA.modular_functions.material_properties.sampling.lib_REFPROP import loop_REFPROP
from DOA.modular_functions.material_properties.sampling.lib_COOLPROP import loop_COOLPROP
from matplotlib.colors import LogNorm
import matplotlib.pyplot as plt
import matplotlib.transforms as trs

from DOA.modular_functions.material_properties.parametrized.pure_fluid_2d import get_pure_fluid_2d_HP
from DOA.modular_functions.material_properties.parametrized.pure_fluid_2d import get_pure_fluid_2d_AB
from DOA.config.lib_config import numpy as np

import h5py
from DOA.general_functions.file_management.save_load_class import load_Class
from DOA.general_functions.file_management.save_load_class import save_Class

material = "PROPANE"

def get_HP_input(N):
    props_r = get_pure_fluid_2d_HP(material, "bilinear", (25,25), diff_idx=(3,))
    hr_Nd, Pr_Nd = np.meshgrid(np.linspace(props_r.HP_min[0], props_r.HP_max[0], N), np.linspace(props_r.HP_min[1], props_r.HP_max[1], N))
    
    hr_Nd_mid = (hr_Nd[:-1,:-1] + hr_Nd[:-1,1:]) / 2.0
    Pr_Nd_mid = (Pr_Nd[:-1,:-1] + Pr_Nd[1:,:-1]) / 2.0

    return hr_Nd_mid, Pr_Nd_mid

def get_AB_input(N):
    props_r = get_pure_fluid_2d_AB(material, "bilinear", (25,25), diff_idx=(4,2), use_nonlin=True, mesh_type='')
    Ar_Nd, Br_Nd = np.meshgrid(np.linspace(props_r.AB_min[0], props_r.AB_max[0], N), np.linspace(props_r.AB_min[1], props_r.AB_max[1], N))
    
    Ar_Nd_mid = (Ar_Nd[:-1,:-1] + Ar_Nd[:-1,1:]) / 2.0
    Br_Nd_mid = (Br_Nd[:-1,:-1] + Br_Nd[1:,:-1]) / 2.0

    return Ar_Nd_mid, Br_Nd_mid

def get_data_single(N, interp_type, coordinate_system, P1_grid, P2_grid, mesh_type=None):
    if coordinate_system == 'HP':
        props_r = get_pure_fluid_2d_HP(material, interp_type, (N,N), diff_idx=(3,))

    elif coordinate_system == 'AB':
        props_r = get_pure_fluid_2d_AB(material, interp_type, (N,N), diff_idx=(4,2), use_nonlin=True, mesh_type=mesh_type)

    # get data
    fODE_prop_sample, fODE_dA_sample, fODE_dB_sample = props_r.fODE.f((P1_grid, P2_grid), dim_idx=2)

    return fODE_prop_sample

def get_data_multiple(interp_type, coordinate_system, N, P1_grid, P2_grid, mesh_type=None):
    D_ALL = tuple(get_data_single(i, interp_type, coordinate_system, P1_grid, P2_grid, mesh_type) for i in N)
    return np.stack(D_ALL, axis=3)

def get_ref_HP_multiple(h, P):
    # data, herr = loop_REFPROP(material, [1.0], "HP", "T;D;E;Qmass", 1000.0*np.vstack((h.flatten(), P.flatten())).T)
    data = loop_COOLPROP(material, "HEOS", "HP", "T;D;E;Qmass", 1000.0*np.vstack((h.flatten(), P.flatten())).T)
    props_tuple = np.split(data, 4, axis=1)
    return np.stack(tuple(i.reshape(h.shape) for i in props_tuple), axis=0)

def get_data_shape_multiple(L, N):
    hr_grid, Pr_grid = get_HP_input(L)
    hr_grid = hr_grid.T
    Pr_grid = Pr_grid.T

    Ar_grid, Br_grid = get_AB_input(L)

    hr_grid_all = np.repeat(hr_grid[np.newaxis, :, :, np.newaxis], N.shape, axis=3)
    Pr_grid_all = np.repeat(Pr_grid[np.newaxis, :, :, np.newaxis], N.shape, axis=3)

    # LUT 1: HP with bilinear
    D_HP_BILIN_TEQD = get_data_multiple("bilinear", "HP", N, hr_grid, Pr_grid)
    D_HP_BILIN_TBL = np.stack((hr_grid_all[0]+100.0, Pr_grid_all[0], D_HP_BILIN_TEQD[0], D_HP_BILIN_TEQD[3], D_HP_BILIN_TEQD[1]+100.0, D_HP_BILIN_TEQD[2]), axis=0)

    # LUT 3: AB with bilinear
    D_AB_BILIN_THEQDP = get_data_multiple("bilinear", "AB", N, Ar_grid, Br_grid, '')
    D_AB_BILIN_TBL = np.stack((D_AB_BILIN_THEQDP[1]+100.0, D_AB_BILIN_THEQDP[5], D_AB_BILIN_THEQDP[0], D_AB_BILIN_THEQDP[4], D_AB_BILIN_THEQDP[2]+100.0, D_AB_BILIN_THEQDP[3]))

    # REF 1: HP with bilinear / bicubic
    D_HP_BILIN_TDEQ = get_ref_HP_multiple(hr_grid, Pr_grid)
    
    Da_grid_all = np.repeat(D_HP_BILIN_TDEQ[:, :, :, np.newaxis], N.shape, axis=3)
    D_HP_BILIN_REF = np.concatenate((hr_grid_all+100.0, Pr_grid_all, Da_grid_all[0:2], Da_grid_all[2:3]/1000.0+100.0, Da_grid_all[3:4]))

    # REF 2: AB with bilinear
    D_AB_BILIN_TDEQ = get_ref_HP_multiple(D_AB_BILIN_THEQDP[1], D_AB_BILIN_TBL[1])
    D_AB_BILIN_REF = np.concatenate((D_AB_BILIN_TBL[0:1], D_AB_BILIN_TBL[1:2], D_AB_BILIN_TDEQ[0:2], D_AB_BILIN_TDEQ[2:3]/1000.0+100.0, D_AB_BILIN_TDEQ[3:4]))

    return D_HP_BILIN_TBL, D_AB_BILIN_TBL, D_HP_BILIN_REF, D_AB_BILIN_REF

def plot_mesh(X, Y, Z, n, xlabel, ylabel, zlabel):
    fig = plt.figure(n)
    ax = fig.add_subplot(111, projection="3d")
    ax.plot_wireframe(X, Y, Z, rstride=1, cstride=1, color="black", linewidth=0.5)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_zlabel(zlabel)
    plt.tight_layout()

def plot_meshes(DATA, xlabel, ylabel, zlabel):
    for i in range(DATA.shape[0]-2):
        plot_mesh(DATA[0,:,:], DATA[1,:,:], DATA[i+2,:,:], i, xlabel, ylabel, zlabel)
    plt.show()

def plot_colormap(Z, extent, n, xlabel, ylabel):
    plt.figure(n)
    plt.imshow(np.flipud(Z), cmap="viridis", norm=LogNorm(vmin=0.01, vmax=50.0), interpolation="none", extent=extent, aspect="auto")
    ax = plt.gca()
    ax.set_box_aspect(1)
    plt.colorbar()
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)

def plot_colormaps(DATA, extent, xlabel, ylabel, name):
    for i in range(DATA.shape[0]):
        plot_colormap(DATA[i,:,:].T, extent, i, xlabel, ylabel)

    bbox = trs.Bbox([[0.0, 0.0], [6.0, 4.5]])
    plt.figure(3)
    plt.savefig(gbm_base + "/DOA/modular_functions/material_properties/LUT_ANALYSIS/images/acc_" + name + ".pdf",dpi=300,bbox_inches=bbox)
    plt.show()

def plot_error(Z, X, n, xlabel, ylabel):
    plt.figure(n)
    plt.semilogy(X, Z[:,0], label=r"$(h,P)$", color="black")
    plt.semilogy(X, Z[:,1], '--', label=r"$(\beta,\gamma)$", color="#006BB3")
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.legend(frameon=False)

def plot_errors(DATA, X, xlabel, ylabel, j):
    sz1 = 12
    sz2 = 12
    plt.rc('font', size=sz1)           # Default font size 
    plt.rc('axes', titlesize=sz1)      # Axes title font size
    plt.rc('axes', labelsize=sz1)      # Axes label font size
    plt.rc('xtick', labelsize=sz2)     # X tick label font size
    plt.rc('ytick', labelsize=sz2)     # Y tick label font size
    plt.rc('legend', fontsize=sz2)     # Legend font size
    
    for i in range(DATA.shape[0]):
        if i == 3:
            plot_error(DATA[i], X, i*j, xlabel, ylabel)

    bbox = trs.Bbox([[0.0, 0.0], [6.0, 4.5]])
    plt.figure(3*j)
    plt.xlim([50, 1200])
    # plt.ylim([1, 1000])
    plt.savefig(gbm_base + "/DOA/modular_functions/material_properties/LUT_ANALYSIS/images/acc_all.pdf",dpi=300,bbox_inches=bbox)

class DATA_CLASS:
    def __init__(self, D_HP_BILIN_TBL, D_AB_BILIN_TBL, D_HP_BILIN_REF, D_AB_BILIN_REF):
        self.D_HP_BILIN_TBL = D_HP_BILIN_TBL
        self.D_AB_BILIN_TBL = D_AB_BILIN_TBL

        self.D_HP_BILIN_REF = D_HP_BILIN_REF
        self.D_AB_BILIN_REF = D_AB_BILIN_REF

# Objectives:
# 1. AB is more accurate than HP
# 2. AB is more accurate than experimental uncertainty everywhere
# 3. Property functions are continuous
# 4. domain is still rectangular wrt enthalpy and pressure
# 5. exact resolution of phase boundary
# 6. discontinuous property derivative across phase boundary

L = 1200
N = np.array([25, 50, 100, 200, 400, 800, 1200])
load = True

if load:
    with h5py.File(gbm_base + '/DOA/modular_functions/material_properties/data/' + material + '/accuracy_v2.h5', 'r') as f:
        DATA = load_Class(f)
        D_HP_BILIN_TBL = DATA.D_HP_BILIN_TBL
        D_AB_BILIN_TBL = DATA.D_AB_BILIN_TBL
        
        D_HP_BILIN_REF = DATA.D_HP_BILIN_REF
        D_AB_BILIN_REF = DATA.D_AB_BILIN_REF

else:
    D_HP_BILIN_TBL, D_AB_BILIN_TBL, D_HP_BILIN_REF, D_AB_BILIN_REF = get_data_shape_multiple(L, N)
    DATA = DATA_CLASS(D_HP_BILIN_TBL, D_AB_BILIN_TBL, D_HP_BILIN_REF, D_AB_BILIN_REF)

    with h5py.File(gbm_base + '/DOA/modular_functions/material_properties/data/' + material + '/accuracy_v2.h5', 'w') as f:
        save_Class(DATA, f.create_group('LUT'))

HP_BILIN_ABS = np.abs(D_HP_BILIN_TBL - D_HP_BILIN_REF) + 1e-10
AB_BILIN_ABS = np.abs(D_AB_BILIN_TBL - D_AB_BILIN_REF) + 1e-10

HP_BILIN_REL = np.clip(100 * HP_BILIN_ABS / np.clip(D_HP_BILIN_REF, 1e-8, 1.0e10), 1e-2, 1.0e10)
AB_BILIN_REL = np.clip(100 * AB_BILIN_ABS / np.clip(D_AB_BILIN_REF, 1e-8, 1.0e10), 1e-2, 1.0e10)

# remove lowest pressure because this skews things in a way that is not representative
M = 1
HP_BILIN_MAX_REL = np.max(HP_BILIN_REL, axis=(1,2))
AB_BILIN_MAX_REL = np.max(AB_BILIN_REL[:,M:-M,M:-M,:], axis=(1,2))

HP_BILIN_MID_REL = np.median(HP_BILIN_REL, axis=(1,2))
AB_BILIN_MID_REL = np.median(AB_BILIN_REL, axis=(1,2))

HP_BILIN_MEN_REL = np.mean(HP_BILIN_REL, axis=(1,2))
AB_BILIN_MEN_REL = np.mean(AB_BILIN_REL, axis=(1,2))

MAX_REL_ERRORS = np.stack((HP_BILIN_MAX_REL, AB_BILIN_MAX_REL), axis=2)
MID_REL_ERRORS = np.stack((HP_BILIN_MID_REL, AB_BILIN_MID_REL), axis=2)
MEN_REL_ERRORS = np.stack((HP_BILIN_MEN_REL, AB_BILIN_MEN_REL), axis=2)

# First set of figures: 3D meshes
# plot_meshes(D_HP_BILIN_TBL[:,:,:,0], "Enthalpy (kJ/kg)", "Pressure (kPa)", "Z")
# plot_meshes(D_AB_BILIN_TBL[:,:,:,0], "Enthalpy (kJ/kg)", "Pressure (kPa)", "Z")
# plot_meshes(D_HP_BILIN_REF[:,:,:,0], "Enthalpy (kJ/kg)", "Pressure (kPa)", "Z")
# plot_meshes(D_AB_BILIN_REF[:,:,:,0], "Enthalpy (kJ/kg)", "Pressure (kPa)", "Z")

# Second set of figures: 2D colormaps
# plot_colormaps(HP_BILIN_REL[:,:,:,-1], [0.0, 800.0, 100.0, 5000.0], "Enthalpy (kJ/kg)", "Pressure (kPa)", "_HP")
# plot_colormaps(AB_BILIN_REL[:,:,:,-1], [200.0, 400.0, 200.0, 400.0], "Gamma (unitless))", "Beta (unitless)", "_AB")

sz1 = 14
sz2 = 14
plt.rc('font', size=sz1)           # Default font size 
plt.rc('axes', titlesize=sz1)      # Axes title font size
plt.rc('axes', labelsize=sz1)      # Axes label font size
plt.rc('xtick', labelsize=sz2)     # X tick label font size
plt.rc('ytick', labelsize=sz2)     # Y tick label font size
plt.rc('legend', fontsize=sz2)     # Legend font size

# Final set of figures: 1D curves
plt.figure(1)
plt.semilogy(N, HP_BILIN_MAX_REL[3,:], label=r"$(P,h)$ max error", color="black")
plt.semilogy(N, AB_BILIN_MAX_REL[3,:], '--', label=r"$(\beta,\gamma)$ max error", color="#006BB3")
plt.semilogy(N, HP_BILIN_MEN_REL[3,:], ':', label=r"$(P,h)$ mean error", color="black")
plt.semilogy(N, AB_BILIN_MEN_REL[3,:], '-.', label=r"$(\beta,\gamma)$ mean error", color="#006BB3")
plt.xlabel("Table Size (square)")
plt.ylabel("Relative Error (%)")
plt.legend(frameon=False, loc="upper right", bbox_to_anchor=(1.03, 1.04))
plt.xlim([100,1000])
plt.ylim([0.01, 1000])
plt.locator_params(axis='x', nbins=9)   # request ~6 ticks
bbox = trs.Bbox([[0.0, 0.0], [6.0, 4.5]])
# ax.set_xticks([100, 200, 300, 400, 500, 600, 700, 800, 900, 1000])  # Keep every second tick
plt.savefig(gbm_base + "/DOA/modular_functions/material_properties/lut_analysis/images/acc_all.pdf",dpi=300,bbox_inches=bbox)
plt.savefig(gbm_base + "/DOA/modular_functions/material_properties/lut_analysis/images/acc_all.tiff",dpi=300,bbox_inches=bbox)
plt.show()

# plot_errors(MAX_REL_ERRORS, N, "Table Size (square)", "Max Relative Error (%)", 1)
# plot_errors(MID_REL_ERRORS, N, "Table Size (square)", "Median Relative Error (%)", 2)
# plot_errors(MEN_REL_ERRORS, N, "Table Size (square)", "Mean Relative Error (%)", 3)
