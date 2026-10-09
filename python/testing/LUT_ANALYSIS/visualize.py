import os
gbm_base = os.environ.get('GBM_BASE')
from DOA.config.config import config
mode = 2
config.update("lib_mode", mode) # mode == 0 pure jax, mode == 1: jax/python mix, mode == 2 pure python

import matplotlib.pyplot as plt
import matplotlib.transforms as trs

from DOA.modular_functions.material_properties.parametrized.pure_fluid_2d import get_pure_fluid_2d_HP
from DOA.modular_functions.material_properties.parametrized.pure_fluid_2d import get_pure_fluid_2d_AB
from DOA.config.lib_config import numpy as np

import numpy as np

def compute_mesh_quality(x, y, z):
    """
    Computes mesh quality metrics for a structured grid defined by x, y, z matrices.
    Returns dictionaries of cell-centered metrics: Aspect Ratio, Skewness, Expansion Ratio, and Scaled Jacobian.
    """
    # Stack inputs into a single (M, N, 3) coordinate array
    P = np.stack([x[1:-1,1:-1], y[1:-1,1:-1], z[1:-1,1:-1]], axis=-1)

    # 1. Define the four corners of every cell (Shape: M-1, N-1, 3)
    P1 = P[:-1, :-1, :] # Bottom-left
    P2 = P[:-1, 1:, :] # Bottom-right
    P3 = P[1:, 1:, :] # Top-right
    P4 = P[1:, :-1, :] # Top-left

    # 2. Compute the four edge vectors for every cell
    e1 = P2 - P1
    e2 = P3 - P2
    e3 = P4 - P3
    e4 = P1 - P4

    # Compute edge lengths with a tiny epsilon to prevent division by zero
    eps = 1e-16
    L1 = np.linalg.norm(e1, axis=-1)
    L2 = np.linalg.norm(e2, axis=-1)
    L3 = np.linalg.norm(e3, axis=-1)
    L4 = np.linalg.norm(e4, axis=-1)

    # --- Metric 1: Aspect Ratio ---
    L_all = np.stack([L1, L2, L3, L4], axis=0)
    aspect_ratio = np.max(L_all, axis=0) / (np.min(L_all, axis=0) + eps)

    # --- Metric 2: Skewness (Maximum angle deviation from 90 degrees) ---
    # Dot products of outgoing edge vectors at each corner
    cos1 = np.sum(e1 * -e4, axis=-1) / (L1 * L4 + eps)
    cos2 = np.sum(e2 * -e1, axis=-1) / (L2 * L1 + eps)
    cos3 = np.sum(e3 * -e2, axis=-1) / (L3 * L2 + eps)
    cos4 = np.sum(e4 * -e3, axis=-1) / (L4 * L3 + eps)

    # Clip to avoid NaN in arccos due to floating point rounding
    cos_all = np.clip(np.stack([cos1, cos2, cos3, cos4], axis=0), -1.0, 1.0)
    angles = np.arccos(cos_all)
    skewness = np.max(np.abs(angles - np.pi/2), axis=0)

    # --- Metric 3: Expansion Ratio ---
    # Area of a 3D quad is half the magnitude of the cross product of its diagonals
    diag1 = P3 - P1
    diag2 = P4 - P2
    cross_diags = np.cross(diag1, diag2, axis=-1)
    areas = 0.5 * np.linalg.norm(cross_diags, axis=-1)

    # Compare each cell's area to its immediate adjacent neighbors
    # Pad areas to handle the edges of the grid
    pad_areas = np.pad(areas, pad_width=1, mode='edge')

    # Get arrays of the neighbors' areas
    area_up = pad_areas[2:, 1:-1]
    area_down = pad_areas[:-2, 1:-1]
    area_left = pad_areas[1:-1, :-2]
    area_right = pad_areas[1:-1, 2:]

    neighbor_max = np.maximum.reduce([area_up, area_down, area_left, area_right])
    neighbor_min = np.minimum.reduce([area_up, area_down, area_left, area_right])

    # Expansion ratio is the worst-case size jump (must be >= 1)
    exp_ratio_max = neighbor_max / (areas + eps)
    exp_ratio_min = areas / (neighbor_min + eps)
    expansion_ratio = np.maximum(exp_ratio_max, exp_ratio_min)

    # --- Metric 4: Scaled Jacobian ---
    # First, find the average unit normal vector of the cell surface
    n_avg = cross_diags / (np.linalg.norm(cross_diags, axis=-1, keepdims=True) + eps)

    # Compute corner cross products (representing the 4 corner areas)
    C1 = np.cross(e1, -e4, axis=-1)
    C2 = np.cross(e2, -e1, axis=-1)
    C3 = np.cross(e3, -e2, axis=-1)
    C4 = np.cross(e4, -e3, axis=-1)

    # Project these corner cross products onto the surface normal
    # Divide by edge lengths to get the Scaled Jacobian (-1 to 1)
    SJ1 = np.sum(C1 * n_avg, axis=-1) / (L1 * L4 + eps)
    SJ2 = np.sum(C2 * n_avg, axis=-1) / (L2 * L1 + eps)
    SJ3 = np.sum(C3 * n_avg, axis=-1) / (L3 * L2 + eps)
    SJ4 = np.sum(C4 * n_avg, axis=-1) / (L4 * L3 + eps)

    # The cell's scaled Jacobian is the minimum value across its 4 corners
    scaled_jacobian = np.min([SJ1, SJ2, SJ3, SJ4], axis=0)
    
    n = 2

    return {
    "aspect_ratio": np.round(np.max(aspect_ratio), n),
    "skewness": np.round(np.max(skewness), n),
    "expansion_ratio": np.round(np.max(expansion_ratio), n),
    "scaled_jacobian": np.round(np.max(scaled_jacobian), n),
    "areas": np.round(np.max(areas), n)}, {
    "aspect_ratio": np.round(np.min(aspect_ratio), n),
    "skewness": np.round(np.min(skewness), n),
    "expansion_ratio": np.round(np.min(expansion_ratio), n),
    "scaled_jacobian": np.round(np.min(scaled_jacobian), n),
    "areas": np.round(np.min(areas), n)}

# Objectives:
# 1. Mesh looks good, elements are all regularily shaped and about the same area

material = "PROPANE"
interp_type = 'bilinear' # bilinear or bicubic
N = 400 # 25 50 100 200 400 number of points per dimension
M = 25

## Reference
props_r_HP = get_pure_fluid_2d_HP(material, interp_type, (N,N), diff_idx=(0,1,2,3))
hr_Nd_REF, Pr_Nd_REF = np.meshgrid(np.linspace(props_r_HP.HP_min[0], props_r_HP.HP_max[0], N), np.linspace(props_r_HP.HP_min[1], props_r_HP.HP_max[1], N))
fODE_prop_sample, fODE_dA_sample, fODE_dB_sample = props_r_HP.fODE.f((hr_Nd_REF, Pr_Nd_REF), dim_idx=2)
Tr_REF, ur_REF, xr_REF, Dr_REF = fODE_prop_sample

props_r_AB = get_pure_fluid_2d_AB(material, interp_type, (N,N), diff_idx=(0,1,2,3,4,5), use_nonlin=True, mesh_type='')
Ar_Nd_REF, Br_Nd_REF = np.meshgrid(np.linspace(props_r_AB.AB_min[0], props_r_AB.AB_max[0], N), np.linspace(props_r_AB.AB_min[1], props_r_AB.AB_max[1], N))
fODE_prop_sample, fODE_dA_sample, fODE_dB_sample = props_r_AB.fODE.f((Ar_Nd_REF, Br_Nd_REF), dim_idx=2)
Tr_Ft, hr_Ft, ur_Ft, xr_Ft, Dr_Ft, Pr_Ft = fODE_prop_sample

# Grid
# props_r_AB = get_pure_fluid_2d_AB(material, interp_type, N, diff_idx=(0,1,2,3,4,5), use_nonlin=True, mesh_type='_exact')
# Ar_Nd, Br_Nd = np.meshgrid(np.linspace(props_r_AB.AB_min[0], props_r_AB.AB_max[0], M), np.linspace(props_r_AB.AB_min[1], props_r_AB.AB_max[1], M))
# fODE_prop_sample, fODE_dA_sample, fODE_dB_sample = props_r_AB.fODE.f((Ar_Nd, Br_Nd), dim_idx=2)
# Tr_Pt, hr_Pt, ur_Pt, xr_Pt, Dr_Pt, Pr_Pt = fODE_prop_sample

props_r_HP = get_pure_fluid_2d_HP(material, interp_type, (N,N), diff_idx=(0,1,2,3))
hr_Nd, Pr_Nd = np.meshgrid(np.linspace(props_r_HP.HP_min[0]+5.0, props_r_HP.HP_max[0]-50.0, M), np.linspace(props_r_HP.HP_min[1], props_r_HP.HP_max[1], M))
fODE_prop_sample, fODE_dA_sample, fODE_dB_sample = props_r_HP.fODE.f((hr_Nd, Pr_Nd), dim_idx=2)
Tr, ur, xr, Dr = fODE_prop_sample

props_r_AB = get_pure_fluid_2d_AB(material, interp_type, (N,N), diff_idx=(0,1,2,3,4,5), use_nonlin=True, mesh_type='')
Ar_Nd, Br_Nd = np.meshgrid(np.linspace(props_r_AB.AB_min[0], props_r_AB.AB_max[0], M), np.linspace(props_r_AB.AB_min[1], props_r_AB.AB_max[1], M))
fODE_prop_sample, fODE_dA_sample, fODE_dB_sample = props_r_AB.fODE.f((Ar_Nd, Br_Nd), dim_idx=2)
Tr_Gt, hr_Gt, ur_Gt, xr_Gt, Dr_Gt, Pr_Gt = fODE_prop_sample

metrics_HP_max, metrics_HP_min = compute_mesh_quality(hr_Nd_REF, Pr_Nd_REF, Dr_REF)
metrics_AB_max, metrics_AB_min = compute_mesh_quality(hr_Ft, Pr_Ft, Dr_Ft)

"aspect_ratio,skewness,expansion_ratio,scaled_jacobian,areas"
print(metrics_HP_min.values(), metrics_HP_max.values())
print(metrics_AB_min.values(), metrics_AB_max.values())

sz1 = 11
sz2 = 11
plt.rc('font', size=sz1)           # Default font size 
plt.rc('axes', titlesize=sz1)      # Axes title font size
plt.rc('axes', labelsize=sz1)      # Axes label font size
plt.rc('xtick', labelsize=sz2)     # X tick label font size
plt.rc('ytick', labelsize=sz2)     # Y tick label font size
plt.rc('legend', fontsize=sz2)     # Legend font size

bbox = trs.Bbox([[1.0, 0.0], [6.0, 4.5]])
save = True
D_MAX = 600.0

fig = plt.figure(1)
ax = fig.add_subplot(111, projection="3d")
ax.plot_wireframe(hr_Gt, Pr_Gt, Dr_Gt, rstride=1, cstride=1, color="black", linewidth=0.9)
surf = ax.plot_surface(hr_Ft, Pr_Ft, Dr_Ft, cmap='viridis', alpha=0.5, edgecolor='none', shade=False)
surf._edgecolors2d = surf._edgecolor3d
surf._facecolors2d = surf._facecolor3d
ax.grid(False)
ax.set_xlabel("Enthalpy ($kJ \cdot kg^{-1}$)")
ax.set_ylabel("Pressure (kPa)")
ax.set_zlabel("Density ($kg \cdot m^{-3}$)")
plt.tight_layout()
ax.set_zlim(0, D_MAX)
if save:
    plt.savefig(gbm_base + "/DOA/modular_functions/material_properties/LUT_ANALYSIS/images/AB_mesh.pdf",dpi=300,bbox_inches=bbox)
    plt.savefig(gbm_base + "/DOA/modular_functions/material_properties/LUT_ANALYSIS/images/AB_mesh.png",dpi=300,bbox_inches=bbox)
    plt.savefig(gbm_base + "/DOA/modular_functions/material_properties/LUT_ANALYSIS/images/AB_mesh.svg",dpi=300,bbox_inches=bbox)

fig = plt.figure(2)
ax = fig.add_subplot(111, projection="3d")
ax.plot_wireframe(hr_Nd, Pr_Nd, Dr, rstride=1, cstride=1, color="black", linewidth=0.9)
surf = ax.plot_surface(hr_Ft, Pr_Ft, Dr_Ft, cmap='viridis', alpha=0.5, edgecolor='none')
surf._edgecolors2d = surf._edgecolor3d
surf._facecolors2d = surf._facecolor3d
ax.grid(False)
ax.set_xlabel("Enthalpy ($kJ \cdot kg^{-1}$)")
ax.set_ylabel("Pressure (kPa)")
ax.set_zlabel("Density ($kg \cdot m^{-3}$)")
plt.tight_layout()
ax.set_zlim(0, D_MAX)
if save:
    plt.savefig(gbm_base + "/DOA/modular_functions/material_properties/LUT_ANALYSIS/images/HP_mesh.pdf",dpi=300,bbox_inches=bbox)
    plt.savefig(gbm_base + "/DOA/modular_functions/material_properties/LUT_ANALYSIS/images/HP_mesh.png",dpi=300,bbox_inches=bbox)
    plt.savefig(gbm_base + "/DOA/modular_functions/material_properties/LUT_ANALYSIS/images/HP_mesh.svg",dpi=300,bbox_inches=bbox)

# bbox = trs.Bbox([[0.5, 0.0], [5.5, 4.5]])
fig = plt.figure(3)
ax = fig.add_subplot(111, projection="3d")
ax.plot_wireframe(Br_Nd, Ar_Nd, Dr_Gt, rstride=1, cstride=1, color="black", linewidth=0.9)
surf = ax.plot_surface(Br_Nd_REF, Ar_Nd_REF, Dr_Ft, cmap='viridis', alpha=0.5, edgecolor='none')
surf._edgecolors2d = surf._edgecolor3d
surf._facecolors2d = surf._facecolor3d
ax.grid(False)
ax.set_xlabel("Gamma (unitless)")
ax.set_ylabel("Beta (unitless)")
ax.set_zlabel("Density ($kg \cdot m^{-3}$)")
plt.tight_layout()
ax.set_zlim(0, D_MAX)
ax.set_xticks([200, 650, 1100, 1550, 2000])
ax.set_yticks([200, 650, 1100, 1550, 2000])
ax.view_init(elev=30, roll=0)
if save:
    plt.savefig(gbm_base + "/DOA/modular_functions/material_properties/LUT_ANALYSIS/images/AB_D.pdf",dpi=300,bbox_inches=bbox)
    plt.savefig(gbm_base + "/DOA/modular_functions/material_properties/LUT_ANALYSIS/images/AB_D.png",dpi=300,bbox_inches=bbox)
    plt.savefig(gbm_base + "/DOA/modular_functions/material_properties/LUT_ANALYSIS/images/AB_D.svg",dpi=300,bbox_inches=bbox)

# bbox = trs.Bbox([[0.5, 0.0], [5.5, 4.5]])
fig = plt.figure(4)
ax = fig.add_subplot(111, projection="3d")
ax.plot_wireframe(Br_Nd, Ar_Nd, Tr_Gt, rstride=1, cstride=1, color="black", linewidth=0.9)
surf = ax.plot_surface(Br_Nd_REF, Ar_Nd_REF, Tr_Ft, cmap='viridis', alpha=0.5, edgecolor='none')
surf._edgecolors2d = surf._edgecolor3d
surf._facecolors2d = surf._facecolor3d
ax.grid(False)
ax.set_xlabel("Gamma (unitless)")
ax.set_ylabel("Beta (unitless)")
ax.set_zlabel("Temperature ($K$)")
plt.tight_layout()
# ax.set_zlim(0, D_MAX)
ax.set_xticks([200, 650, 1100, 1550, 2000])
ax.set_yticks([200, 650, 1100, 1550, 2000])
ax.view_init(elev=30, roll=0, azim=-135)
if save:
    plt.savefig(gbm_base + "/DOA/modular_functions/material_properties/LUT_ANALYSIS/images/AB_T.pdf",dpi=300,bbox_inches=bbox)
    plt.savefig(gbm_base + "/DOA/modular_functions/material_properties/LUT_ANALYSIS/images/AB_T.png",dpi=300,bbox_inches=bbox)

fig = plt.figure(5)
ax = fig.add_subplot(111, projection="3d")
ax.plot_wireframe(Br_Nd, Ar_Nd, hr_Gt, rstride=1, cstride=1, color="black", linewidth=0.9)
surf = ax.plot_surface(Br_Nd_REF, Ar_Nd_REF, hr_Ft, cmap='viridis', alpha=0.5, edgecolor='none')
surf._edgecolors2d = surf._edgecolor3d
surf._facecolors2d = surf._facecolor3d
ax.grid(False)
ax.set_xlabel("Gamma (unitless)")
ax.set_ylabel("Beta (unitless)")
ax.set_zlabel("Enthalpy ($kJ \cdot kg^{-1}$)")
plt.tight_layout()
# ax.set_zlim(0, D_MAX)
ax.set_xticks([200, 650, 1100, 1550, 2000])
ax.set_yticks([200, 650, 1100, 1550, 2000])
ax.view_init(elev=30, roll=0, azim=-135)
if save:
    plt.savefig(gbm_base + "/DOA/modular_functions/material_properties/LUT_ANALYSIS/images/AB_H.pdf",dpi=300,bbox_inches=bbox)
    plt.savefig(gbm_base + "/DOA/modular_functions/material_properties/LUT_ANALYSIS/images/AB_H.png",dpi=300,bbox_inches=bbox)


plt.figure(6)
plt.plot(Br_Nd[:,0], Tr_Gt[:,0])

plt.show()

sz1 = 14
sz2 = 14
plt.rc('font', size=sz1)           # Default font size 
plt.rc('axes', titlesize=sz1)      # Axes title font size
plt.rc('axes', labelsize=sz1)      # Axes label font size
plt.rc('xtick', labelsize=sz2)     # X tick label font size
plt.rc('ytick', labelsize=sz2)     # Y tick label font size
plt.rc('legend', fontsize=sz2)     # Legend font size

bbox = trs.Bbox([[-0.2, -0.2], [6.0, 4.5]])
plt.figure(4)
plt.plot(hr_Nd_REF.T[:,20], Dr_REF.T[:,20], color="black")
plt.xlabel("Enthalpy ($kJ \cdot kg^{-1}$)")
plt.ylabel("Density ($kg \cdot m^{-3}$)")
plt.xlim([100, 700])
plt.ylim([0, 600])
plt.savefig(gbm_base + "/DOA/modular_functions/material_properties/LUT_ANALYSIS/images/HD.pdf",dpi=300,bbox_inches=bbox)
plt.savefig(gbm_base + "/DOA/modular_functions/material_properties/LUT_ANALYSIS/images/HD.png",dpi=300,bbox_inches=bbox)
plt.savefig(gbm_base + "/DOA/modular_functions/material_properties/LUT_ANALYSIS/images/HD.svg",dpi=300,bbox_inches=bbox)

# plt.figure(5)
# plt.plot(hr_Ft[:,20], Dr_Ft[:,20], color="black")
# plt.scatter(hr_Ft[::16,20], Dr_Ft[::16,20], color="black")
# plt.xlabel("Enthalpy ($kJ \cdot kg^{-1}$)")
# plt.ylabel("Density ($kg \cdot m^{-3}$)")
# plt.savefig(gbm_base + "/DOA/modular_functions/material_properties/LUT_ANALYSIS/images/HD2.pdf",dpi=300,bbox_inches=bbox)
# plt.savefig(gbm_base + "/DOA/modular_functions/material_properties/LUT_ANALYSIS/images/HD2.png",dpi=300,bbox_inches=bbox)

# plt.figure(6)
# plt.scatter(hr_Ft[::16,20], Dr_Ft[::16,20], color="black")
# plt.xlabel("Enthalpy (kJ/kg)")
# plt.ylabel("Density ($kg \cdot m^{-3}$)")
# plt.savefig(gbm_base + "/DOA/modular_functions/material_properties/LUT_ANALYSIS/images/HD3.pdf",dpi=300,bbox_inches=bbox)
# plt.savefig(gbm_base + "/DOA/modular_functions/material_properties/LUT_ANALYSIS/images/HD3.png",dpi=300,bbox_inches=bbox)

# plt.figure(7)
# plt.scatter(np.arange(Dr_Ft[::16,20].size), Dr_Ft[::16,20], color="black")
# plt.xlabel("Index")
# plt.ylabel("Density ($kg \cdot m^{-3}$)")
# plt.savefig(gbm_base + "/DOA/modular_functions/material_properties/LUT_ANALYSIS/images/HD4.pdf",dpi=300,bbox_inches=bbox)
# plt.savefig(gbm_base + "/DOA/modular_functions/material_properties/LUT_ANALYSIS/images/HD4.png",dpi=300,bbox_inches=bbox)

# plt.figure(8)
# plt.scatter(np.arange(Dr_Ft[::16,20].size), hr_Ft[::16,20], color="black")
# plt.xlabel("Index")
# plt.ylabel("Enthalpy ($kJ \cdot kg^{-1}$)")
# plt.savefig(gbm_base + "/DOA/modular_functions/material_properties/LUT_ANALYSIS/images/HD5.pdf",dpi=300,bbox_inches=bbox)
# plt.savefig(gbm_base + "/DOA/modular_functions/material_properties/LUT_ANALYSIS/images/HD5.png",dpi=300,bbox_inches=bbox)

plt.show()