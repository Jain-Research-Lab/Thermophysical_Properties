import os
gbm_base = os.environ.get('GBM_BASE')
from DOA.config.config import config
mode = 2
config.update("lib_mode", mode) # mode == 0 pure jax, mode == 1: jax/python mix, mode == 2 pure python

from DOA.modular_functions.material_properties.sampling.lib_REFPROP import loop_REFPROP
from matplotlib.colors import LogNorm
import matplotlib.pyplot as plt
import matplotlib.transforms as trs

from DOA.modular_functions.material_properties.parametrized.pure_fluid_2d import get_pure_fluid_2d_HP
from DOA.modular_functions.material_properties.parametrized.pure_fluid_2d import get_pure_fluid_2d_AB
from DOA.config.lib_config import numpy as np

material = "PROPANE"

def get_HP_input(N):
    props_r = get_pure_fluid_2d_HP(material, "bilinear", (25,25), diff_idx=(0,1,2,3))
    hr_Nd, Pr_Nd = np.meshgrid(np.linspace(props_r.HP_min[0], props_r.HP_max[0], N), np.linspace(props_r.HP_min[1], props_r.HP_max[1], N))
    
    hr_Nd_mid = (hr_Nd[:-1,:-1] + hr_Nd[:-1,1:]) / 2.0
    Pr_Nd_mid = (Pr_Nd[:-1,:-1] + Pr_Nd[1:,:-1]) / 2.0

    return hr_Nd_mid, Pr_Nd_mid

def get_AB_input(N):
    props_r = get_pure_fluid_2d_AB(material, "bilinear", (25,25), diff_idx=(0,1,2,3,4,5), use_nonlin=True, mesh_type='')
    Ar_Nd, Br_Nd = np.meshgrid(np.linspace(props_r.AB_min[0], props_r.AB_max[0], N), np.linspace(props_r.AB_min[1], props_r.AB_max[1], N))
    
    Ar_Nd_mid = (Ar_Nd[:-1,:-1] + Ar_Nd[:-1,1:]) / 2.0
    Br_Nd_mid = (Br_Nd[:-1,:-1] + Br_Nd[1:,:-1]) / 2.0

    return Ar_Nd_mid, Br_Nd_mid

def get_data_single(N, interp_type, coordinate_system, P1_grid, P2_grid, mesh_type=None):
    if coordinate_system == 'HP':
        props_r = get_pure_fluid_2d_HP(material, interp_type, (N,N), diff_idx=(0,1,2,3))

    elif coordinate_system == 'AB':
        props_r = get_pure_fluid_2d_AB(material, interp_type, (N,N), diff_idx=(0,1,2,3,4,5), use_nonlin=True, mesh_type=mesh_type)

    # get data
    fODE_prop_sample, fODE_dA_sample, fODE_dB_sample = props_r.fODE.f((P1_grid, P2_grid), dim_idx=2)

    return fODE_prop_sample, fODE_dA_sample, fODE_dB_sample

def get_data_multiple(interp_type, coordinate_system, N, P1_grid, P2_grid, mesh_type=None):
    D_ALL = tuple(get_data_single(i, interp_type, coordinate_system, P1_grid, P2_grid, mesh_type) for i in N)

    P_ALL = np.stack(tuple(i[0] for i in D_ALL), axis=3)
    dP1_ALL = np.stack(tuple(i[1] for i in D_ALL), axis=3)
    dP2_ALL = np.stack(tuple(i[2] for i in D_ALL), axis=3)
    
    return P_ALL, dP1_ALL, dP2_ALL

def get_ref_HP_multiple(h, P):
    data, herr = loop_REFPROP(material, "HP", "T;D;E;Qmass", 1000.0*np.vstack((h.flatten(), P.flatten())).T)
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
    D_HP_BILIN_TEQD, dD1_HP_BILIN_TEQD, dD2_HP_BILIN_TEQD = get_data_multiple("bilinear", "HP", N, hr_grid, Pr_grid)
    D_HP_BILIN_TBL = np.stack((hr_grid_all[0], Pr_grid_all[0], D_HP_BILIN_TEQD[0], D_HP_BILIN_TEQD[3], D_HP_BILIN_TEQD[1], D_HP_BILIN_TEQD[2]), axis=0)
    dD1_HP_BILIN_TBL = np.stack((np.ones((dD1_HP_BILIN_TEQD[0].shape)), np.zeros((dD1_HP_BILIN_TEQD[0].shape)), dD1_HP_BILIN_TEQD[0], dD1_HP_BILIN_TEQD[3], dD1_HP_BILIN_TEQD[1], dD1_HP_BILIN_TEQD[2]), axis=0)
    dD2_HP_BILIN_TBL = np.stack((np.zeros((dD1_HP_BILIN_TEQD[0].shape)), np.ones((dD1_HP_BILIN_TEQD[0].shape)), dD2_HP_BILIN_TEQD[0], dD2_HP_BILIN_TEQD[3], dD2_HP_BILIN_TEQD[1], dD2_HP_BILIN_TEQD[2]), axis=0)

    # LUT 3: AB with bilinear
    D_AB_BILIN_THEQDP, dD1_AB_BILIN_THEQDP, dD2_AB_BILIN_THEQDP = get_data_multiple("bilinear", "AB", N, Ar_grid, Br_grid, '')
    D_AB_BILIN_TBL = np.stack((D_AB_BILIN_THEQDP[1], D_AB_BILIN_THEQDP[5], D_AB_BILIN_THEQDP[0], D_AB_BILIN_THEQDP[4], D_AB_BILIN_THEQDP[2], D_AB_BILIN_THEQDP[3]))
    dD1_AB_BILIN_TBL = np.stack((dD1_AB_BILIN_THEQDP[1], dD1_AB_BILIN_THEQDP[5], dD1_AB_BILIN_THEQDP[0], dD1_AB_BILIN_THEQDP[4], dD1_AB_BILIN_THEQDP[2], dD1_AB_BILIN_THEQDP[3]), axis=0)
    dD2_AB_BILIN_TBL = np.stack((dD2_AB_BILIN_THEQDP[1], dD2_AB_BILIN_THEQDP[5], dD2_AB_BILIN_THEQDP[0], dD2_AB_BILIN_THEQDP[4], dD2_AB_BILIN_THEQDP[2], dD2_AB_BILIN_THEQDP[3]), axis=0)

    return (D_HP_BILIN_TBL, D_AB_BILIN_TBL), (dD1_HP_BILIN_TBL, dD1_AB_BILIN_TBL), (dD2_HP_BILIN_TBL, dD2_AB_BILIN_TBL), (Ar_grid, Br_grid)

# Objectives:
# 1. Lipshitz constant is less for AB
# 2. AB is always invertible
# 3. derivative functions are continuous

L = 400
N = np.array([25, 50, 100, 200, 400])
(D_HP_BILIN_TBL, D_AB_BILIN_TBL), (dD1_HP_BILIN_TBL, dD1_AB_BILIN_TBL), (dD2_HP_BILIN_TBL, dD2_AB_BILIN_TBL), (Ar_grid, Br_grid) = get_data_shape_multiple(L, N)

dD1_max = np.max(np.abs(dD1_HP_BILIN_TBL), axis=(1,2))
dD3_max = np.max(np.abs(dD1_AB_BILIN_TBL), axis=(1,2))

dE1_max = np.max(np.abs(dD2_HP_BILIN_TBL), axis=(1,2))
dE3_max = np.max(np.abs(dD2_AB_BILIN_TBL), axis=(1,2))

D_HP_BILIN_Range = (np.max(D_HP_BILIN_TBL, axis=(1,2,3)) - np.min(D_HP_BILIN_TBL, axis=(1,2,3))).reshape(-1, 1, 1, 1)
D_AB_BILIN_Range = (np.max(D_HP_BILIN_TBL, axis=(1,2,3)) - np.min(D_HP_BILIN_TBL, axis=(1,2,3))).reshape(-1, 1, 1, 1)

dDdA = dD1_AB_BILIN_TBL[3,:,:,:]
dUdA = dD1_AB_BILIN_TBL[4,:,:,:]

dDdB = dD2_AB_BILIN_TBL[3,:,:,:]
dUdB = dD2_AB_BILIN_TBL[4,:,:,:]

DET_BILIN_HP = D_HP_BILIN_TBL[3,:,:,:]*dD2_HP_BILIN_TBL[3,:,:,:] - dD1_HP_BILIN_TBL[3,:,:,:]
MIN_DET_BILIN_HP = np.min(DET_BILIN_HP, axis=(0,1))
MAX_DET_BILIN_HP = np.max(DET_BILIN_HP, axis=(0,1))

DET_BILIN = D_AB_BILIN_TBL[3,:,:,:]*(dD2_AB_BILIN_TBL[4,:,:,:]*dD1_AB_BILIN_TBL[3,:,:,:] - dD1_AB_BILIN_TBL[4,:,:,:]*dD2_AB_BILIN_TBL[3,:,:,:])
MIN_DET_BILIN = np.min(DET_BILIN, axis=(0,1))
MAX_DET_BILIN = np.max(DET_BILIN, axis=(0,1))

# metric 1: sum of absolute values
wun = 0.0
ALL_DIST_HP_BILIN = np.abs(np.sum(np.abs(dD1_HP_BILIN_TBL[0:4]/D_HP_BILIN_Range[0:4]), axis=0)*D_HP_BILIN_Range[0,0,0,0] - wun) + np.abs(np.sum(np.abs(dD2_HP_BILIN_TBL[0:4]/D_HP_BILIN_Range[0:4]), axis=0)*D_HP_BILIN_Range[1,0,0,0] - wun)
ALL_DIST_AB_BILIN = np.abs(np.sum(np.abs(dD1_AB_BILIN_TBL[0:4]/D_AB_BILIN_Range[0:4]), axis=0)*200.0 - wun) + np.abs(np.sum(np.abs(dD2_AB_BILIN_TBL[0:4]/D_AB_BILIN_Range[0:4]), axis=0)*200.0 - wun)

S_HP_BILIN = ALL_DIST_HP_BILIN[:,:,-1]
S_AB_BILIN = ALL_DIST_AB_BILIN[:,:,-1]

DIST1_HP_BILIN = (np.max(ALL_DIST_HP_BILIN, axis=(0,1)) - np.min(ALL_DIST_HP_BILIN, axis=(0,1)))
DIST1_AB_BILIN = (np.max(ALL_DIST_AB_BILIN, axis=(0,1)) - np.min(ALL_DIST_AB_BILIN, axis=(0,1)))

DIST1_HP_BILIN_MAX = np.max(ALL_DIST_HP_BILIN, axis=(0,1))
DIST1_HP_BILIN_MIN = np.min(ALL_DIST_HP_BILIN, axis=(0,1))
DIST1_AB_BILIN_MAX = np.max(ALL_DIST_AB_BILIN, axis=(0,1))
DIST1_AB_BILIN_MIN = np.min(ALL_DIST_AB_BILIN, axis=(0,1))

DIST2_HP_BILIN = np.log10(np.max(ALL_DIST_HP_BILIN, axis=(0,1)) / np.min(ALL_DIST_HP_BILIN, axis=(0,1)))
DIST2_AB_BILIN = np.log10(np.max(ALL_DIST_AB_BILIN, axis=(0,1)) / np.min(ALL_DIST_AB_BILIN, axis=(0,1)))

print(np.round(DIST2_HP_BILIN[-1], 2))
print(np.round(DIST2_AB_BILIN[-1], 2))

REL1_HP_BILIN = DIST1_HP_BILIN / np.min(ALL_DIST_HP_BILIN, axis=(0,1))
REL1_AB_BILIN = DIST1_AB_BILIN / np.min(ALL_DIST_AB_BILIN, axis=(0,1))

# second set of figures: 1D plot of sensitivity wrt table size
plt.figure(1)
plt.semilogy(N, DIST2_HP_BILIN, label="HP_BILIN")
plt.semilogy(N, DIST2_AB_BILIN, label="AB_BILIN")
plt.xlabel("Table Size (Count)")
plt.ylabel("Variation in Sensitivty Metric")
plt.legend()

plt.figure(2)
bbox = trs.Bbox([[0.0, 0.0], [6.0, 4.5]])
plt.semilogy(N, REL1_HP_BILIN, label="BILIN_HP")
plt.semilogy(N, REL1_AB_BILIN, label="BILIN_BG")
plt.xlabel("Table Size (Count)")
plt.ylabel("Relative Variation (ratio)")
plt.legend()
plt.savefig(gbm_base + "/DOA/modular_functions/material_properties/LUT_ANALYSIS/images/rel_var.pdf",dpi=300,bbox_inches=bbox)
plt.show()

# # third set of figures: distribution of distance
# plt.figure(4)
# extent = [0.0, 800.0, 100.0, 5000.0]
# plt.imshow(np.flipud(ALL_DIST_HP_BILIN[:,:,-1].T), cmap="viridis", norm=LogNorm(vmin=1.0, vmax=500.0), extent=extent, interpolation="none", aspect="auto")
# ax = plt.gca()
# ax.set_box_aspect(1)
# plt.colorbar()
# plt.xlabel("Enthalpy (kJ/kg)")
# plt.ylabel("Pressure (kPa)")

# plt.figure(5)
# extent = [200.0, 600.0, 200.0, 400.0]
# plt.imshow(np.flipud(ALL_DIST_AB_BILIN[:,:,-1].T), cmap="viridis", norm=LogNorm(vmin=1.0, vmax=500.0), extent=extent, interpolation="none", aspect="auto")
# ax = plt.gca()
# ax.set_box_aspect(1)
# plt.colorbar()
# plt.xlabel("Beta (Unitless)")
# plt.ylabel("Gamma (Unitless)")
# plt.show()

# # fourth set of figures: invertibility of AB
# mask = DET_BILIN[:,:,2] >= 0.0
# indices = np.nonzero(mask)
# AA = Ar_grid[indices[0][0],:]
# BB = Br_grid[:,indices[1][0]]

# plt.figure(10)
# plt.scatter(AA, DET_BILIN[:,:,2][indices[0][0],:])

# plt.figure(11)
# plt.scatter(BB, DET_BILIN[:,:,2][:,indices[1][0]])
# plt.show()

# fig = plt.figure(6)
# ax = fig.add_subplot(111, projection="3d")
# ax.plot_wireframe(Ar_grid, Br_grid, DET_BILIN[:,:,2], rstride=1, cstride=1, color="black", linewidth=0.5)
# ax.grid(False)
# ax.set_xlabel("Enthalpy (kJ/kg)")
# ax.set_ylabel("Pressure (kPa)")
# ax.set_zlabel("Density (kg/m^3)")
# plt.tight_layout()

# fig = plt.figure(7)
# ax = fig.add_subplot(111, projection="3d")
# ax.plot_wireframe(Ar_grid, Br_grid, DET_BICUB[:,:,2], rstride=1, cstride=1, color="black", linewidth=0.5)
# ax.grid(False)
# ax.set_xlabel("Enthalpy (kJ/kg)")
# ax.set_ylabel("Pressure (kPa)")
# ax.set_zlabel("Density (kg/m^3)")
# plt.tight_layout()

# fig = plt.figure(8)
# ax = fig.add_subplot(111, projection="3d")
# ax.plot_wireframe(Ar_grid, Br_grid, DET_BILIN_HP[:,:,2], rstride=1, cstride=1, color="black", linewidth=0.5)
# ax.grid(False)
# ax.set_xlabel("Enthalpy (kJ/kg)")
# ax.set_ylabel("Pressure (kPa)")
# ax.set_zlabel("Density (kg/m^3)")
# plt.tight_layout()

# fig = plt.figure(9)
# ax = fig.add_subplot(111, projection="3d")
# ax.plot_wireframe(Ar_grid, Br_grid, DET_BICUB_HP[:,:,2], rstride=1, cstride=1, color="black", linewidth=0.5)
# ax.grid(False)
# ax.set_xlabel("Enthalpy (kJ/kg)")
# ax.set_ylabel("Pressure (kPa)")
# ax.set_zlabel("Density (kg/m^3)")
# plt.tight_layout()
# plt.show()

# plt.figure(10)
# extent = [0.0, 800.0, 100.0, 5000.0]
# plt.imshow(np.flipud(DET_BILIN_HP[:,:,-1].T), cmap="viridis", norm=LogNorm(vmin=0.01, vmax=5000.0), extent=extent, interpolation="none", aspect="auto")
# ax = plt.gca()
# ax.set_box_aspect(1)
# plt.colorbar()
# plt.xlabel("Enthalpy (kJ/kg)")
# plt.ylabel("Pressure (kPa)")

# plt.figure(11)
# extent = [0.0, 800.0, 100.0, 5000.0]
# plt.imshow(np.flipud(DET_BICUB_HP[:,:,-1].T), cmap="viridis", norm=LogNorm(vmin=0.01, vmax=5000.0), extent=extent, interpolation="none", aspect="auto")
# ax = plt.gca()
# ax.set_box_aspect(1)
# plt.colorbar()
# plt.xlabel("Enthalpy (kJ/kg)")
# plt.ylabel("Pressure (kPa)")

# plt.figure(12)
# extent = [200.0, 400.0, 200.0, 400.0]
# plt.imshow(np.flipud(DET_BILIN[:,:,-1].T), cmap="viridis", norm=LogNorm(vmin=1.0, vmax=50000.0), extent=extent, interpolation="none", aspect="auto")
# ax = plt.gca()
# ax.set_box_aspect(1)
# plt.colorbar()
# plt.xlabel("Beta (Unitless)")
# plt.ylabel("Gamma (Unitless)")

# plt.figure(13)
# extent = [200.0, 400.0, 200.0, 400.0]
# plt.imshow(np.flipud(DET_BICUB[:,:,-1].T), cmap="viridis", norm=LogNorm(vmin=1.0, vmax=50000.0), extent=extent, interpolation="none", aspect="auto")
# ax = plt.gca()
# ax.set_box_aspect(1)
# plt.colorbar()
# plt.xlabel("Beta (Unitless)")
# plt.ylabel("Gamma (Unitless)")
# plt.show()