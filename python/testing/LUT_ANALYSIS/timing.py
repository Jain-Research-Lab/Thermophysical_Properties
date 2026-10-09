import os
gbm_base = os.environ.get('GBM_BASE')
from DOA.config.config import config
mode = 1
config.update("lib_mode", mode) # mode == 0 pure jax, mode == 1: jax/python mix, mode == 2 pure python

from DOA.general_functions.general_utility.function_utility import compile_from_f
import time
import matplotlib.pyplot as plt
import matplotlib.transforms as trs

from DOA.modular_functions.material_properties.parametrized.pure_fluid_2d import get_pure_fluid_2d_HP
from DOA.modular_functions.material_properties.parametrized.pure_fluid_2d import get_pure_fluid_2d_AB
from DOA.config.lib_config import numpy as np
import pickle

material = "PROPANE"

def get_HP_input(N):
    props_r = get_pure_fluid_2d_HP(material, "bilinear", (25,25), diff_idx=(3,))
    hr_Nd, Pr_Nd = np.meshgrid(np.linspace(props_r.HP_min[0], props_r.HP_max[0], N), np.linspace(props_r.HP_min[1], props_r.HP_max[1], N))
    
    return hr_Nd.flatten(), Pr_Nd.flatten()

def get_AB_input(N):
    props_r = get_pure_fluid_2d_AB(material, "bilinear", (25,25), diff_idx=(4,2), use_nonlin=True, mesh_type='')
    Ar_Nd, Br_Nd = np.meshgrid(np.linspace(props_r.AB_min[0], props_r.AB_max[0], N), np.linspace(props_r.AB_min[1], props_r.AB_max[1], N))
    
    return Ar_Nd.flatten(), Br_Nd.flatten()

def get_timing_single(N, M, interp_type, coordinate_system, P1_vec, P2_vec, mesh_type=None):
    if coordinate_system == 'HP':
        props_r = get_pure_fluid_2d_HP(material, interp_type, (N,N), diff_idx=(3,))

    elif coordinate_system == 'AB':
        props_r = get_pure_fluid_2d_AB(material, interp_type, (N,N), diff_idx=(4,2), use_nonlin=True, mesh_type=mesh_type)

    # ahead of time (AOT) compile for maximum computation speed
    fODE_compiled = compile_from_f(props_r.fODE.f, ((P1_vec, P2_vec),), static_argnums=None, dim_idx=1)

    # do multiple runs to warmup the XLA and dont take first few runs
    T = np.empty((M,))

    for i in range(M):
        t0 = time.time()
        fODE_prop_sample, fODE_dA_sample, fODE_dB_sample = fODE_compiled((P1_vec, P2_vec))
        fODE_prop_sample.block_until_ready()
        fODE_dA_sample.block_until_ready()
        fODE_dB_sample.block_until_ready()
        T = T.at[i].set(time.time() - t0)

    return T

def get_timing_multiple(interp_type, coordinate_system, N, M, P, P1_vec, P2_vec, mesh_type=None):
    T_ALL = np.empty((len(N), M))

    for i in range(len(N)):
        T_ALL = T_ALL.at[i].set(get_timing_single(N[i], M, interp_type, coordinate_system, P1_vec, P2_vec, mesh_type) / (P1_vec.size))

    return 1000000.0*np.mean(T_ALL[:,P:], axis=1)

def get_timing_shape_multiple(L, N, M, P):
    NL = L.size
    T_HP_BILIN_AVG = np.empty((NL, M-P-1))
    T_AB_BILIN_AVG = np.empty((NL, M-P-1))

    for i in range(NL):
        hr_vec, Pr_vec = get_HP_input(L[i])
        Ar_vec, Br_vec = get_AB_input(L[i])

        # LUT 1: HP with bilinear
        T_HP_BILIN_AVG = T_HP_BILIN_AVG.at[i].set(get_timing_multiple("bilinear", "HP", N, M, P, hr_vec, Pr_vec))

        # # LUT 3: AB with bilinear
        T_AB_BILIN_AVG = T_AB_BILIN_AVG.at[i].set(get_timing_multiple("bilinear", "AB", N, M, P, Ar_vec, Br_vec, ''))

    return T_HP_BILIN_AVG, T_AB_BILIN_AVG

# Objectives:
# BILIN is faster than BICUB
# AB is not that much slower than HP

L = np.array([1, 2, 3, 4, 5, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100])
N = np.array([25, 50, 100, 200, 400])
M = 10
P = 4
sim = False
if sim:
    T_HP_BILIN_AVG, T_AB_BILIN_AVG = get_timing_shape_multiple(L, N, M, P)
    with open(gbm_base + "/DOA/benchmarks/Coordinate_Transform_Benchmarks/data/T_DATA.pkl", 'wb') as f:
        pickle.dump((T_HP_BILIN_AVG, T_AB_BILIN_AVG), f)

else:
    with open(gbm_base + "/DOA/benchmarks/Coordinate_Transform_Benchmarks/data/T_DATA.pkl", 'rb') as f:
        T_HP_BILIN_AVG, T_AB_BILIN_AVG = pickle.load(f)

L_mat, N_mat = np.meshgrid(L, N, indexing="ij")

# absolute and relative advantage
ABS_DIFF_BILIN = T_AB_BILIN_AVG - T_HP_BILIN_AVG
REL_DIFF_BILIN = 100*ABS_DIFF_BILIN / T_HP_BILIN_AVG

# First set of figures: 3D plots
# fig0 = plt.figure(1)
# ax0 = fig0.add_subplot(111, projection='3d')
# ax0.scatter(L_mat, N_mat, T_HP_BILIN_AVG, c='g', marker='x', s=10)
# ax0.scatter(L_mat, N_mat, T_HP_BICUB_AVG, c='g', marker='x', s=10)
# ax0.scatter(L_mat, N_mat, T_AB_BILIN_AVG, c='g', marker='x', s=10)
# ax0.scatter(L_mat, N_mat, T_AB_BICUB_AVG, c='g', marker='x', s=10)
# ax0.set_xlabel("Number of Query Points")
# ax0.set_ylabel("Table Size")
# ax0.set_zlabel("Computation time per point (us)")
# ax0.legend()

# fig1 = plt.figure(2)
# ax1 = fig1.add_subplot(111, projection='3d')
# ax1.scatter(L_mat, N_mat, ABS_DIFF_BILIN, c='g', marker='x', s=10)
# ax1.scatter(L_mat, N_mat, ABS_DIFF_BICUB, c='g', marker='x', s=10)
# ax1.set_xlabel("Number of Query Points")
# ax1.set_ylabel("Table Size")
# ax1.set_zlabel("Computation time per point (us)")
# ax1.legend()

# fig2 = plt.figure(3)
# ax2 = fig2.add_subplot(111, projection='3d')
# ax2.scatter(L_mat, N_mat, REL_DIFF_BILIN, c='g', marker='x', s=10)
# ax2.scatter(L_mat, N_mat, REL_DIFF_BICUB, c='g', marker='x', s=10)
# ax2.set_xlabel("Number of Query Points")
# ax2.set_ylabel("Table Size")
# ax2.set_zlabel("Computation time per point (us)")
# ax2.legend()
# plt.show()

# Second set of figures: 2D plots

sz1 = 12
sz2 = 12
plt.rc('font', size=sz1)           # Default font size 
plt.rc('axes', titlesize=sz1)      # Axes title font size
plt.rc('axes', labelsize=sz1)      # Axes label font size
plt.rc('xtick', labelsize=sz2)     # X tick label font size
plt.rc('ytick', labelsize=sz2)     # Y tick label font size
plt.rc('legend', fontsize=sz2)     # Legend font size

bbox = trs.Bbox([[0.0, 0.0], [6.5, 4.5]])
fig, ax1 = plt.subplots()                                                                     ##### SHOW THIS ONE ######
plt.semilogy(L, np.mean(T_HP_BILIN_AVG, axis=1), ":", label="BILIN_HP", color="black")
plt.semilogy(L, np.mean(T_AB_BILIN_AVG, axis=1), '--', label="BILIN_BG", color="#006BB3")
ax1.set_xlabel("Number of Query Points")
ax1.set_ylabel("Computation time per point (μs)")
plt.legend(frameon=False)

ax2 = ax1.twinx()
ax2.plot(L, np.mean(REL_DIFF_BILIN, axis=1), color="#2C2C2C")
ax2.set_ylabel("Relative Advantage (%)", color="#2C2C2C")
ax2.tick_params(axis='y', labelcolor="#2C2C2C")
plt.savefig(gbm_base + "/DOA/modular_functions/material_properties/LUT_ANALYSIS/images/time_abs.pdf",dpi=300,bbox_inches=bbox)

bbox = trs.Bbox([[0.0, 0.0], [6.0, 4.5]])
plt.figure(5)
plt.plot(L, np.mean(ABS_DIFF_BILIN, axis=1), label="BILIN")
plt.xlabel("Number of Query Points")
plt.ylabel("Absolute Computation Time Advantage (us)")
plt.legend()

plt.figure(6)                                                                         ##### SHOW THIS ONE ######
plt.plot(L, np.mean(REL_DIFF_BILIN, axis=1))
plt.xlabel("Number of Query Points")
plt.ylabel("Relative Computation Time Advantage (%)")
plt.legend()
plt.savefig(gbm_base + "/DOA/modular_functions/material_properties/LUT_ANALYSIS/images/time_rel.pdf",dpi=300,bbox_inches=bbox)
plt.show()

# Third set: scalars
print("Results")
print(f"HP_BILIN: {np.mean(T_HP_BILIN_AVG)}")
print(f"AB_BILIN: {np.mean(T_AB_BILIN_AVG)}")

print(f"HP_BILIN ABS: {np.mean(ABS_DIFF_BILIN)}")
print(f"AB_BILIN REL: {np.mean(REL_DIFF_BILIN)}")