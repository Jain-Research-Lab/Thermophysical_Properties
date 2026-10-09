from DOA.modular_functions.material_properties.sampling.lib_COOLPROP import loop_COOLPROP, get_crit_COOLPROP
from DOA.general_functions.file_management.save_load_class import save_Class, load_Class
from DOA.modular_functions.material_properties.sampling.lib_REFPROP import loop_REFPROP
import matplotlib.pyplot as plt
import numpy as np
import importlib
import h5py
import os

def get_DP_GRID(DP_table_config, library_flag, parameters):
    # unpack config
    Dmin = DP_table_config["Dmin"]
    Dmax = DP_table_config["Dmax"]
    Pmin = DP_table_config["Pmin"]
    Pmax = DP_table_config["Pmax"]
    szD = parameters["sz"][0]
    szP = parameters["sz"][1]
    
    # get linear, gridded sampling of the input space
    D_brkpt = np.linspace(Dmin, Dmax, num=szD)
    P_brkpt = np.linspace(Pmin, Pmax, num=szP)
    D_gridT, P_gridT = np.meshgrid(D_brkpt, P_brkpt)
    D_vec = D_gridT.reshape((D_gridT.size, 1))
    P_vec = P_gridT.reshape((P_gridT.size, 1))
    PD_vec = np.hstack((P_vec, D_vec))
    DP_vec = np.hstack((D_vec, P_vec))
    
    # get properties
    if library_flag == "refprop":
        DATA, herr = loop_REFPROP(parameters["material"], parameters["composition"], "PD", "T;H;E;S;Qmass", PD_vec)

    elif library_flag == "coolprop":
        DATA = loop_COOLPROP(parameters["material"], parameters["method"], "DP", "T;H;E;S;Q", np.hstack((D_vec, P_vec)))
        
        # fix Q
        Tcrit, Pcrit, hcrit, Dcrit, Ecrit = get_crit_COOLPROP(parameters["material"], parameters["method"])   
        DATA[np.bitwise_and(DATA[:,1] > hcrit, DP_vec[:,1] > Pcrit), 4] = 1.0
        Q_grid = np.fliplr(np.clip(DATA[:,4].reshape((szD,szP)), 0, 1))
        Q_grid[:,1:][np.logical_or.accumulate(np.bitwise_and(Q_grid[:,:-1] > 0.0, Q_grid[:,1:] <= 0.0), axis=1)] = 1.0
        DATA[:,4] = np.fliplr(Q_grid).flatten()

    return DP_LUT_CLASS(D_gridT, DATA[:,1], DATA[:,2], P_gridT, DATA[:,0], DATA[:,4], DATA[:,3], Dmin, Dmax, Pmin, Pmax, szD, szP)

def plot_DP_grids(DATA):
    fig1 = plt.figure(1)
    ax1 = fig1.add_subplot(111, projection='3d')
    ax1.scatter(DATA.D_grid, DATA.P_grid/1000, DATA.T_grid, c='b', marker='x', s=1)
    ax1.set_xlabel('Density (kg/m^3)')
    ax1.set_ylabel('Pressure (kPa)')
    ax1.set_zlabel('Temperature (K)')

    fig2 = plt.figure(2)
    ax2 = fig2.add_subplot(111, projection='3d')
    ax2.scatter(DATA.D_grid, DATA.P_grid/1000, DATA.u_grid/1000, c='b', marker='x', s=1)
    ax2.set_xlabel('Density (kg/m^3)')
    ax2.set_ylabel('Pressure (kPa)')
    ax2.set_zlabel('Specific Internal Energy (J/kg)')

    fig3 = plt.figure(3)
    ax3 = fig3.add_subplot(111, projection='3d')
    ax3.scatter(DATA.D_grid, DATA.P_grid/1000, DATA.h_grid/1000, c='b', marker='x', s=1)
    ax3.set_xlabel('Density (kg/m^3)')
    ax3.set_ylabel('Pressure (kPa)')
    ax3.set_zlabel('Enthalpy (kJ/kg)')

    fig4 = plt.figure(4)
    ax4 = fig4.add_subplot(111, projection='3d')
    ax4.scatter(DATA.D_grid, DATA.P_grid/1000, DATA.x_grid, c='b', marker='x', s=1)
    ax4.set_xlabel('Density (kg/m^3)')
    ax4.set_ylabel('Pressure (kPa)')
    ax4.set_zlabel('Quality (J/J)')

    fig5 = plt.figure(5)
    ax5 = fig5.add_subplot(111, projection='3d')
    ax5.scatter(DATA.D_grid, DATA.P_grid/1000, DATA.S_grid/1000, c='b', marker='x', s=1)
    ax5.set_xlabel('Density (kg/m^3)')
    ax5.set_ylabel('Pressure (kPa)')
    ax5.set_zlabel('Entropy (kJ/(kg*K))')
    
    plt.show()

class DP_LUT_CLASS:
    def __init__(self, D_grid, h_grid, e_grid, P_grid, T_grid, Q_grid, S_grid, Dr_min, Dr_max, Pr_min, Pr_max, szD, szP):
        self.D_grid = D_grid.T
        self.h_grid = h_grid.reshape((szP, szD)).T / 1000.0
        self.u_grid = e_grid.reshape((szP, szD)).T / 1000.0
        self.P_grid = P_grid.T / 1000.0
        self.T_grid = T_grid.reshape((szP, szD)).T
        self.x_grid = np.clip(Q_grid.reshape((szP, szD)).T, 0, 1)
        self.S_grid = S_grid.reshape((szP, szD)).T / 1000.0
        
        self.Dr_min = Dr_min
        self.Dr_max = Dr_max
        self.Pr_min = Pr_min / 1000.0
        self.Pr_max = Pr_max / 1000.0
        
# Example Usage
if __name__ == "__main__":
    # parameters
    material = "FAKE_POE"
    make_data = True
    sz = (25,25)

    module_path = f"DOA.modular_functions.material_properties.config.{material}"
    module = importlib.import_module(module_path)

    gbm_base = os.environ.get('GBM_BASE')
    folder = os.path.join(gbm_base, "DOA/modular_functions/material_properties/data", material)
    os.makedirs(folder, exist_ok=True)   # creates only if missing

    parameters = {}
    library_flag = module.DP_table_config["library_flag"]
    parameters["sz"] = sz
    if library_flag == "refprop":
        parameters["composition"] = module.Composition_Vector
        parameters["material"] = module.Name_Vector
        
    elif library_flag == "coolprop":
        parameters["method"] = module.DP_table_config["coolprop_METHOD"]
        parameters["material"] = material

    if make_data:
        DATA = get_DP_GRID(module.DP_table_config, library_flag, parameters)
        sz = DATA.h_grid.shape
        with h5py.File(gbm_base + '/DOA/modular_functions/material_properties/data/' + material + '/' + 'DP_DHEPTQS_' + str(sz[0]) + '_' + str(sz[1]) + '.h5', 'w') as f:
            save_Class(DATA, f.create_group('LUT'))

    else:
        with h5py.File(gbm_base + '/DOA/modular_functions/material_properties/data/' + material + '/' + 'DP_DHEPTQS_' + str(sz[0]) + '_' + str(sz[1]) + '.h5', 'r') as f:
            load_Class(f)

    plot_DP_grids(DATA)