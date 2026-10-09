from DOA.modular_functions.material_properties.sampling.lib_COOLPROP import get_crit_COOLPROP
from DOA.general_functions.file_management.save_load_class import save_Class, load_Class
from ctREFPROP.ctREFPROP import REFPROPFunctionLibrary
from DOA.config.lib_config import numpy as np
from CoolProp.CoolProp import AbstractState
from scipy.optimize import brentq
import matplotlib.pyplot as plt
import CoolProp as CP
import importlib
import h5py
import os

def get_AB_GRID(AB_table_config, library_flag, parameters):
    # unpack config
    szA = parameters["sz"][0]
    szB = parameters["sz"][1]
    P_min = AB_table_config["P_min"]
    P_max = AB_table_config["P_max"]
    H_max = AB_table_config["H_max"]
    T_SCALE = AB_table_config["T_SCALE"]

    # all pressure breakpoints
    P_vec = np.linspace(P_min, P_max, szA)

    if library_flag == "refprop":
        ORACLE = REFPROPFunctionLibrary(os.environ['RPPREFIX'])
        MASS_BASE_SI = ORACLE.GETENUMdll(0,"MASS BASE SI").iEnum
        D_max = ORACLE.REFPROPdll(parameters["material"], 'PQ', 'D', MASS_BASE_SI, MASS_BASE_SI, 0, P_vec[0], 0.0, parameters["composition"]).Output[0]
        H_min = ORACLE.REFPROPdll(parameters["material"], 'PQ', 'H', MASS_BASE_SI, MASS_BASE_SI, 0, P_vec[0], 0.0, parameters["composition"]).Output[0]
        D_min = ORACLE.REFPROPdll(parameters["material"], 'PH', 'D', MASS_BASE_SI, MASS_BASE_SI, 0, P_vec[0], H_max, parameters["composition"]).Output[0]
        T_max = ORACLE.REFPROPdll(parameters["material"], 'PQ', 'T', MASS_BASE_SI, MASS_BASE_SI, 0, P_vec[0], H_max, parameters["composition"]).Output[0]
        T_sat = ORACLE.REFPROPdll(parameters["material"], 'PQ', 'T', MASS_BASE_SI, MASS_BASE_SI, 0, P_vec[0], 1.0, parameters["composition"]).Output[0]

    elif library_flag == "coolprop":
        ORACLE = AbstractState(parameters["method"], parameters["material"])
        ORACLE.update(CP.PQ_INPUTS, P_vec[0], 0.0)
        D_max = ORACLE.rhomass()
        H_min = ORACLE.hmass()
        T_max = ORACLE.T()
        ORACLE.update(CP.HmassP_INPUTS, H_max, P_vec[0])
        D_min = ORACLE.rhomass()

        ORACLE.update(CP.PQ_INPUTS, P_vec[0], 1)
        T_sat = ORACLE.T()

    r = (1000.0*np.abs(D_max - D_min))/np.abs(H_max - H_min)
    L_REF = (r*np.abs(H_max - H_min)/1000.0 + np.abs(D_max - D_min) + r*np.abs(T_max - T_sat)) / (szB - 1)

    # sample along DH
    LUT = get_AB_GRID_dDH(library_flag, parameters, szB, P_vec, H_min, L_REF, r, T_SCALE, 'not_last')
    LUT = resample_pressure(library_flag, parameters, LUT, szB, H_min, L_REF, r, T_SCALE)
    
    return LUT

############# Constant DH Breakpoint Spacing #############
def get_AB_GRID_dDH(library_flag, parameters, szB, P_vec, H_min, L_REF, r, T_SCALE, iteration):
    szA = P_vec.size
    A_vec = np.linspace(0, szA-1, szA)           # When inverting, get this FIRST
    B_vec = np.linspace(0, szB-1, szB)           # When inverting, get this SECOND
    A_grid, B_grid = np.meshgrid(A_vec, B_vec, indexing='ij') # 

    # Data Matrices    
    P_grid = np.empty((szA, szB))
    D_grid = np.empty((szA, szB))
    E_grid = np.empty((szA, szB))
    H_grid = np.empty((szA, szB))
    T_grid = np.empty((szA, szB))
    S_grid = np.empty((szA, szB))
    Q_grid = np.empty((szA, szB))

    if library_flag == "refprop":
        ORACLE = REFPROPFunctionLibrary(os.environ['RPPREFIX'])
        MASS_BASE_SI = ORACLE.GETENUMdll(0,"MASS BASE SI").iEnum

        DATA0 = ORACLE.REFPROPdll(parameters["material"], 'PH', 'E;D;T;S;Q', MASS_BASE_SI, MASS_BASE_SI, 0, P_vec[0], H_min, parameters["composition"])
        DATA0 = np.array([DATA0.Output[0], DATA0.Output[1], DATA0.Output[2], DATA0.Output[3], DATA0.q])

    elif library_flag == "coolprop":
        ORACLE = AbstractState(parameters["method"], parameters["material"])

        ORACLE.update(CP.HmassP_INPUTS, H_min, P_vec[0])
        DATA0 = np.array([ORACLE.umass(), ORACLE.rhomass(), ORACLE.T(), ORACLE.smass(), ORACLE.Q()])

    # sample data
    for i in range(szA):
        if library_flag == "refprop":
            DATA = ORACLE.REFPROPdll(parameters["material"], 'PE', 'H;T;S;D;Qmass', MASS_BASE_SI, MASS_BASE_SI, 0, P_vec[i], DATA0[0], parameters["composition"])
            DATA = np.array([DATA.Output[0], DATA.Output[1], DATA.Output[2], DATA.Output[3], DATA.Output[4], DATA.q])

        elif library_flag == "coolprop":
            ORACLE.update(CP.PUmass_INPUTS, P_vec[i], DATA0[0])
            DATA = np.array([ORACLE.hmass(), ORACLE.T(), ORACLE.smass(), ORACLE.rhomass(), ORACLE.Q()])

        P_grid[i,0] = P_vec[i]
        D_grid[i,0] = DATA[3]
        E_grid[i,0] = DATA0[0]
        H_grid[i,0] = DATA[0]
        T_grid[i,0] = DATA[1]
        S_grid[i,0] = DATA[2]
        Q_grid[i,0] = np.clip(DATA[4], 0, 1)

    def get_distance_2d_DH(H0, H1, P, ORACLE):
        if library_flag == "refprop":
            D0 = ORACLE.REFPROPdll(parameters["material"], 'PH', 'D', MASS_BASE_SI, MASS_BASE_SI, 0, P, H0, parameters["composition"]).Output[0]
            D1 = ORACLE.REFPROPdll(parameters["material"], 'PH', 'D', MASS_BASE_SI, MASS_BASE_SI, 0, P, H1, parameters["composition"]).Output[0]

            T0 = ORACLE.REFPROPdll(parameters["material"], 'PH', 'T', MASS_BASE_SI, MASS_BASE_SI, 0, P, H0, parameters["composition"]).Output[0]
            T1 = ORACLE.REFPROPdll(parameters["material"], 'PH', 'T', MASS_BASE_SI, MASS_BASE_SI, 0, P, H1, parameters["composition"]).Output[0]

            h_g = ORACLE.REFPROPdll(parameters["material"], 'PQ', 'H', MASS_BASE_SI, MASS_BASE_SI, 0, P, 1.0, parameters["composition"]).Output[0]
        
        elif library_flag == "coolprop":
            ORACLE.update(CP.HmassP_INPUTS, H0, P)
            D0 = ORACLE.rhomass()
            T0 = ORACLE.T()

            ORACLE.update(CP.HmassP_INPUTS, H1, P)
            D1 = ORACLE.rhomass()
            T1 = ORACLE.T()

            ORACLE.update(CP.PQ_INPUTS, P, 1)
            h_g = ORACLE.hmass()

        return r*np.abs(H0 - H1)/1000.0 + np.abs(D0 - D1) + (H1 >= h_g)*T_SCALE*np.abs(T0 - T1)

    def dist_res(H1, H0, P, L_REF):
        return get_distance_2d_DH(H0, H1, P, ORACLE) - np.abs(L_REF)

    # compute remaining columns
    for j in range(szA):
        print(f"starting {j}")
        for i in range(szB-1):
            Hq = brentq(dist_res, H_grid[j,i], H_grid[j,i]+20000*L_REF, (H_grid[j,i],P_grid[j,i],L_REF))

            if library_flag == "refprop":
                DATA = ORACLE.REFPROPdll(parameters["material"], 'PH', 'E;T;S;D;Qmass', MASS_BASE_SI, MASS_BASE_SI, 0, P_grid[j,i], Hq, parameters["composition"])
                DATA = np.array([DATA.Output[0], DATA.Output[1], DATA.Output[2], DATA.Output[3], DATA.q])
            
            elif library_flag == "coolprop":
                ORACLE.update(CP.HmassP_INPUTS, Hq, P_grid[j,i])
                DATA = np.array([ORACLE.umass(), ORACLE.T(), ORACLE.smass(), ORACLE.rhomass(), ORACLE.Q()])

            if  (j > 0) & (DATA[0] < E_grid[j-1,i+1]):
                if library_flag == "refprop":
                    DATA = ORACLE.REFPROPdll(parameters["material"], 'PE', 'H;T;S;D;Qmass', MASS_BASE_SI, MASS_BASE_SI, 0, P_grid[j,i], E_grid[j-1,i+1], parameters["composition"])
                    DATA = np.array([DATA.Output[0], DATA.Output[1], DATA.Output[2], DATA.Output[3], DATA.q])
                
                elif library_flag == "coolprop":
                    ORACLE.update(CP.PUmass_INPUTS, P_grid[j,i], E_grid[j-1,i+1])
                    DATA = np.array([ORACLE.hmass(), ORACLE.T(), ORACLE.smass(), ORACLE.rhomass(), ORACLE.Q()])

                P_grid[j,i+1] = P_grid[j,i]
                D_grid[j,i+1] = DATA[3]
                E_grid[j,i+1] = E_grid[j-1,i+1]
                H_grid[j,i+1] = DATA[0]
                T_grid[j,i+1] = DATA[1]
                S_grid[j,i+1] = DATA[2]
                Q_grid[j,i+1] = np.clip(DATA[4], 0, 1)

            else:
                P_grid[j,i+1] = P_grid[j,i]
                D_grid[j,i+1] = DATA[3]
                E_grid[j,i+1] = DATA[0]
                H_grid[j,i+1] = Hq
                T_grid[j,i+1] = DATA[1]
                S_grid[j,i+1] = DATA[2]
                Q_grid[j,i+1] = np.clip(DATA[4], 0, 1)

    if library_flag == "coolprop":
        Tcrit, Pcrit, hcrit, Dcrit, Ecrit = get_crit_COOLPROP(parameters["material"], parameters["method"])
        Q_grid[:,1:][np.logical_or.accumulate(np.bitwise_and(Q_grid[:,:-1] > 0.0, Q_grid[:,1:] <= 0.0), axis=1)] = 1.0
        Q_grid[np.bitwise_and(P_grid >= Pcrit, H_grid >= hcrit)] = 1.0

    if iteration == 'last':
        D_grid = safe_extrapolate_grid(D_grid)
        H_grid = safe_extrapolate_grid(H_grid)
        E_grid = safe_extrapolate_grid(E_grid)
        T_grid = safe_extrapolate_grid(T_grid)
        S_grid = safe_extrapolate_grid(S_grid)
        Q_grid = constant_extrapolate_grid(Q_grid)

    return AB_LUT_CLASS(A_grid, B_grid, D_grid, H_grid, E_grid, P_grid, T_grid, Q_grid, S_grid)

def resample_pressure(library_flag, parameters, LUT, szB, H_min, L_REF, r, T_SCALE):
    # resample pressure breakpoints
    L = np.max(np.abs(LUT.D_grid[1:,:] - LUT.D_grid[:-1,:]) + np.abs(LUT.h_grid[1:,:] - LUT.h_grid[:-1,:]) + np.abs(LUT.P_grid[1:,:] - LUT.P_grid[:-1,:]), axis=1)
    L_data = np.cumsum(np.hstack((0, L)))
    L_vec = np.linspace(0.0, L_data[-1], L_data.size)
    P_vec = 1000.0*np.interp(L_vec, L_data, LUT.P_grid[:,0])

    # sample along DH
    return get_AB_GRID_dDH(library_flag, parameters, szB, P_vec, H_min, L_REF, r, T_SCALE, 'not_last')

def safe_extrapolate_grid(grid):
    m1 = np.mean(grid[:,1] - grid[:,0])
    m2 = np.mean(grid[:,-1] - grid[:,-2])
    m3 = np.mean(grid[1,:] - grid[0,:])
    m4 = np.mean(grid[-1,:] - grid[-2,:])

    grid[:,0] =  grid[:,1] - m1
    grid[:,-1] =  grid[:,-2] + m2
    grid[0,:] = grid[1,:] - m3
    grid[-1,:] = grid[-2,:] + m4

    return grid

def constant_extrapolate_grid(grid):
    grid[:,0] =  grid[:,1]
    grid[:,-1] =  grid[:,-2]
    grid[0,:] = grid[1,:]
    grid[-1,:] = grid[-2,:]

    return grid

############# Output and Plot #############
def plot_AB_grids(DATA):
    fig1 = plt.figure(1)
    ax1 = fig1.add_subplot(111, projection='3d')
    ax1.scatter(DATA.A_grid, DATA.B_grid, DATA.D_grid, c='b', marker='x', s=1)
    ax1.set_xlabel('a (index)')
    ax1.set_ylabel('b (index)')
    ax1.set_zlabel('Density (kg/m^3)')

    fig2 = plt.figure(2)
    ax2 = fig2.add_subplot(111, projection='3d')
    ax2.scatter(DATA.A_grid, DATA.B_grid, DATA.T_grid, c='b', marker='x', s=1)
    ax2.set_xlabel('a (index)')
    ax2.set_ylabel('b (index)')
    ax2.set_zlabel('Temperature (K)')

    fig3 = plt.figure(3)
    ax3 = fig3.add_subplot(111, projection='3d')
    ax3.scatter(DATA.A_grid, DATA.B_grid, DATA.P_grid, c='b', marker='x', s=1)
    ax3.set_xlabel('a (index)')
    ax3.set_ylabel('b (index)')
    ax3.set_zlabel('Pressure (Pa)')

    fig4 = plt.figure(4)
    ax4 = fig4.add_subplot(111, projection='3d')
    ax4.scatter(DATA.A_grid, DATA.B_grid, DATA.x_grid, c='b', marker='x', s=1)
    ax4.set_xlabel('a (index)')
    ax4.set_ylabel('b (index)')
    ax4.set_zlabel('Quality (J/J)')

    fig5 = plt.figure(5)
    ax5 = fig5.add_subplot(111, projection='3d')
    ax5.scatter(DATA.A_grid, DATA.B_grid, DATA.h_grid, c='b', marker='x', s=1)
    ax5.set_xlabel('a (index)')
    ax5.set_ylabel('b (index)')
    ax5.set_zlabel('Specific Enthalpy (J/kg)')

    fig6 = plt.figure(6)
    ax6 = fig6.add_subplot(111, projection='3d')
    ax6.scatter(DATA.A_grid, DATA.B_grid, DATA.u_grid, c='b', marker='x', s=1)
    ax6.set_xlabel('a (index)')
    ax6.set_ylabel('b (index)')
    ax6.set_zlabel('Specific Internal Energy (J/kg)')

    fig7 = plt.figure(8)
    ax7 = fig7.add_subplot(111, projection='3d')
    ax7.scatter(DATA.h_grid, DATA.P_grid, DATA.D_grid, c='b', marker='x', s=1)
    ax7.set_xlabel('Enthalpy (J/kg)')
    ax7.set_ylabel('Pressure (Pa)')
    ax7.set_zlabel('Density (kg/m^3)')

    plt.show()

class AB_LUT_CLASS:
    def __init__(self, A_grid, B_grid, D_grid, h_grid, e_grid, P_grid, T_grid, Q_grid, S_grid):
        self.A_grid = A_grid
        self.B_grid = B_grid
        self.D_grid = D_grid
        self.h_grid = h_grid / 1000.0
        self.u_grid = e_grid / 1000.0
        self.P_grid = P_grid / 1000.0
        self.T_grid = T_grid
        self.x_grid = Q_grid
        self.S_grid = S_grid / 1000.0

        self.Ar_min = 200.0
        self.Ar_max = 2000.0
        self.Br_min = 200.0
        self.Br_max = 2000.0
        
if __name__ == "__main__":
    # parameters
    material = "PROPANE"
    make_data = True
    sz = (25,25)

    module_path = f"DOA.modular_functions.material_properties.config.{material}"
    module = importlib.import_module(module_path)

    gbm_base = os.environ.get('GBM_BASE')
    folder = os.path.join(gbm_base, "DOA/modular_functions/material_properties/data", material)
    os.makedirs(folder, exist_ok=True)   # creates only if missing

    parameters = {}
    library_flag = module.AB_table_config["library_flag"]
    parameters["sz"] = sz
    if library_flag == "refprop":
        parameters["composition"] = module.Composition_Vector
        parameters["material"] = module.Name_Vector
        
    elif library_flag == "coolprop":
        parameters["method"] = module.AB_table_config["coolprop_METHOD"]
        parameters["material"] = material

    if make_data:
        DATA = get_AB_GRID(module.AB_table_config, library_flag, parameters)
        sz = DATA.h_grid.shape
        with h5py.File(gbm_base + '/DOA/modular_functions/material_properties/data/' + material + '/' + 'AB_DHEPTQS_' + str(sz[0]) + '_' + str(sz[1]) + '.h5', 'w') as f:
            save_Class(DATA, f.create_group('LUT'))

    else:
        with h5py.File(gbm_base + '/DOA/modular_functions/material_properties/data/' + material + '/' + 'AB_DHEPTQS_' + str(sz[0]) + '_' + str(sz[1]) + '.h5', 'r') as f:
            DATA = load_Class(f)

    plot_AB_grids(DATA)