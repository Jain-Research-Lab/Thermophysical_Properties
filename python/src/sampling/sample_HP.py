from DOA.modular_functions.material_properties.sampling.lib_COOLPROP import loop_COOLPROP, get_crit_COOLPROP
from DOA.general_functions.file_management.save_load_class import save_Class, load_Class
from DOA.modular_functions.material_properties.sampling.lib_REFPROP import loop_REFPROP
import matplotlib.pyplot as plt
import numpy as np
import importlib
import h5py
import os

def make_input_vec(table_config):
    # unpack config
    P1min = table_config.P1min
    P1max = table_config.P1max
    P2min = table_config.P2min
    P2max = table_config.P2max
    szP1 = table_config.sz[0]
    szP2 = table_config.sz[1]
    
    P1_brkpt = np.linspace(P1min, P1max, num=szP1)
    P2_brkpt = np.linspace(P2min, P2max, num=szP2)
    P1_gridT, P2_gridT = np.meshgrid(P1_brkpt, P2_brkpt, indexing='ij')
    P1_vec = P1_gridT.reshape((szP1*szP2, 1))
    P2_vec = P2_gridT.reshape((szP1*szP2, 1))
    return np.hstack((P1_vec, P2_vec)) 

def get_HP_GRID(table_config):
    # # unpack config
    # Hmin = table_config.P1min
    # Hmax = table_config.P1max
    # Pmin = table_config.P2min
    # Pmax = table_config.P2max
    
    # sz = table_config.sz
    # szH = parameters["sz"][0]
    # szP = parameters["sz"][1]
    # library_flag = table_config.library_flag
    
    # # get linear, gridded sampling of the input space
    # H_brkpt = np.linspace(Hmin, Hmax, num=szH)
    # P_brkpt = np.linspace(Pmin, Pmax, num=szP)
    # H_gridT, P_gridT = np.meshgrid(H_brkpt, P_brkpt)
    # H_vec = H_gridT.reshape((H_gridT.size, 1))
    # P_vec = P_gridT.reshape((P_gridT.size, 1))
    # HP_vec = np.hstack((H_vec, P_vec))
    
    PP_vec = make_input_vec(table_config)
    
    # get properties
    if isinstance(table_config, RPGridConfig): # refprop
        DATA = loop_REFPROP(table_config.material, table_config.composition, table_config.IN, table_config.OUT, PP_vec)

    elif isinstance(table_config, CPGridConfig): # coolprop
        DATA = loop_COOLPROP(table_config.material, table_config.method, table_config.IN, table_config.OUT, PP_vec)
        
        # # fix Q
        # Tcrit, Pcrit, hcrit, Dcrit, Ecrit = get_crit_COOLPROP(table_config.material, table_config.method)
        # DATA[np.bitwise_and(PP_vec[:,0] > hcrit, PP_vec[:,1] > Pcrit), 4] = 1.0
        # Q_grid = np.clip(DATA[:,4].reshape((szH,szP)), 0, 1)
        # Q_grid[:,1:][np.logical_or.accumulate(np.bitwise_and(Q_grid[:,:-1] > 0.0, Q_grid[:,1:] <= 0.0), axis=1)] = 1.0
        # DATA[:,4] = Q_grid.flatten()
    
    return HP_LUT_CLASS(DATA[:,1], PP_vec[:,0], DATA[:,2], PP_vec[:,1], DATA[:,0], DATA[:,4], DATA[:,3], Hmin, Hmax, Pmin, Pmax, szH, szP)

def plot_HP_grids(DATA):
    fig1 = plt.figure(1)
    ax1 = fig1.add_subplot(111, projection='3d')
    ax1.scatter(DATA.h_grid, DATA.P_grid, DATA.T_grid, c='b', marker='x', s=1)
    ax1.set_xlabel('Enthalpy (kJ/kg)')
    ax1.set_ylabel('Pressure (kPa)')
    ax1.set_zlabel('Temperature (K)')

    fig2 = plt.figure(2)
    ax2 = fig2.add_subplot(111, projection='3d')
    ax2.scatter(DATA.h_grid, DATA.P_grid, DATA.u_grid, c='b', marker='x', s=1)
    ax2.set_xlabel('Enthalpy (kJ/kg)')
    ax2.set_ylabel('Pressure (kPa)')
    ax2.set_zlabel('Specific Internal Energy (J/kg)')

    fig3 = plt.figure(3)
    ax3 = fig3.add_subplot(111, projection='3d')
    ax3.scatter(DATA.h_grid, DATA.P_grid, DATA.D_grid, c='b', marker='x', s=1)
    ax3.set_xlabel('Enthalpy (kJ/kg)')
    ax3.set_ylabel('Pressure (kPa)')
    ax3.set_zlabel('Density (kg/m^3)')

    fig4 = plt.figure(4)
    ax4 = fig4.add_subplot(111, projection='3d')
    ax4.scatter(DATA.h_grid, DATA.P_grid, DATA.x_grid, c='b', marker='x', s=1)
    ax4.set_xlabel('Enthalpy (kJ/kg)')
    ax4.set_ylabel('Pressure (kPa)')
    ax4.set_zlabel('Quality (J/J)')

    fig5 = plt.figure(5)
    ax5 = fig5.add_subplot(111, projection='3d')
    ax5.scatter(DATA.h_grid, DATA.P_grid, DATA.S_grid, c='b', marker='x', s=1)
    ax5.set_xlabel('Enthalpy (kJ/kg)')
    ax5.set_ylabel('Pressure (kPa)')
    ax5.set_zlabel('Entropy (kJ/(kg*K))')
    
    plt.show()

class HP_LUT_CLASS:
    def __init__(self, D_grid, h_grid, u_grid, P_grid, T_grid, Q_grid, S_grid, P1_min, P1_max, P2_min, P2_max, szP1, szP2):
        # data tables
        self.D_grid = D_grid.reshape((szP1, szP2))
        self.h_grid = h_grid.reshape((szP1, szP2)) / 1000.0
        self.u_grid = u_grid.reshape((szP1, szP2)) / 1000.0
        self.P_grid = P_grid.reshape((szP1, szP2)) / 1000.0
        self.T_grid = T_grid.reshape((szP1, szP2))
        self.x_grid = np.clip(Q_grid.reshape((szP1, szP2)), 0, 1)
        self.S_grid = S_grid.reshape((szP1, szP2)) / 1000.0

        self.hr_min = P1_min / 1000.0
        self.hr_max = P1_max / 1000.0
        self.Pr_min = P2_min / 1000.0
        self.Pr_max = P2_max / 1000.0
        
# Example Usage
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
    library_flag = module.HP_table_config["library_flag"]
    parameters["sz"] = sz
    if library_flag == "refprop":
        parameters["composition"] = module.Composition_Vector
        parameters["material"] = module.Name_Vector
        
    elif library_flag == "coolprop":
        parameters["method"] = module.HP_table_config["coolprop_METHOD"]
        parameters["material"] = material

    if make_data:
        DATA = get_HP_GRID(module.HP_table_config, parameters)
        sz = DATA.h_grid.shape
        with h5py.File(gbm_base + '/DOA/modular_functions/material_properties/data/' + material + '/' + 'HP_DHEPTQS_' + str(sz[0]) + '_' + str(sz[1]) + '.h5', 'w') as f:
            save_Class(DATA, f.create_group('LUT'))

    else:
        with h5py.File(gbm_base + '/DOA/modular_functions/material_properties/data/' + material + '/' + 'HP_DHEPTQS_' + str(sz[0]) + '_' + str(sz[1]) + '.h5', 'r') as f:
            DATA = load_Class(f)

    plot_HP_grids(DATA)