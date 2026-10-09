from DOA.general_functions.file_management.save_load_class import save_Class, load_Class
from DOA.modular_functions.material_properties.sampling.lib_COOLPROP import loop_COOLPROP
from DOA.modular_functions.material_properties.sampling.lib_REFPROP import loop_REFPROP
from DOA.general_functions.mathGBM.polynomial import poly4_2d
from DOA.config.lib_config import numpy as np
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt
import importlib
import h5py
import os

def get_single_lookup(single_phase_config, library_flag, parameters):
    side_liq = 'liq'
    side_gas = 'gas'
    
    H_given_PT_liq, T_given_PH_liq, D_given_PT_liq, H_liq, P_liq, T_liq, D_liq = get_PHT_single_lookup(single_phase_config, library_flag, parameters, side_liq)
    H_given_PT_gas, T_given_PH_gas, D_given_PT_gas, H_gas, P_gas, T_gas, D_gas = get_PHT_single_lookup(single_phase_config, library_flag, parameters, side_gas)
    
    return single_phase_CLASS(H_given_PT_liq, T_given_PH_liq, D_given_PT_liq, H_liq, P_liq, T_liq, D_liq, H_given_PT_gas, T_given_PH_gas, D_given_PT_gas, H_gas, P_gas, T_gas, D_gas)

def get_PHT_single_lookup(single_phase_config, library_flag, parameters, side):
    # unpack inputs
    Pmin = single_phase_config["Pmin"]
    Pmax = single_phase_config["Pmax"]
    hlim = single_phase_config["hlim_"+side]
    szProp1 = single_phase_config["szP"]
    szProp2 = single_phase_config["szH"]
    
    # get dh
    Prop1_brkpt = np.linspace(Pmin, Pmax, num=szProp1).reshape((-1,1))

    if side == 'liq':
        Q0_brkpt = np.zeros((szProp1,1))

        if library_flag == "refprop":
            H_data, herr = loop_REFPROP(parameters["material"], parameters["composition"], 'PQ', 'H', np.hstack((Prop1_brkpt, Q0_brkpt)))
        elif library_flag == "coolprop":
            H_data = loop_COOLPROP(parameters["material"], parameters["method"], 'PQ', 'H', np.hstack((Prop1_brkpt, Q0_brkpt)))

        Prop2_vec = np.linspace(hlim, H_data[0], num=szProp2).reshape((-1,1))

        for i in range(szProp2-1):
            temp = np.linspace(hlim, H_data[i+1], num=szProp2).reshape((-1,1))
            Prop2_vec = np.hstack((Prop2_vec, temp))

    elif side == 'gas':
        Q1_brkpt = np.ones((szProp1,1))
        if library_flag == "refprop":
            H_data, herr = loop_REFPROP(parameters["material"], parameters["composition"], 'PQ', 'H', np.hstack((Prop1_brkpt, Q1_brkpt)))
        elif library_flag == "coolprop":
            H_data = loop_COOLPROP(parameters["material"], parameters["method"], 'PQ', 'H', np.hstack((Prop1_brkpt, Q1_brkpt)))
        Prop2_vec = np.linspace(H_data[0], hlim, num=szProp2).reshape((-1,1))

        for i in range(szProp2-1):
            temp = np.linspace(hlim, H_data[i+1], num=szProp2).reshape((-1,1))
            Prop2_vec = np.hstack((Prop2_vec, temp))

    # get linear, gridded sampling of the input space
    Prop1_vec = np.tile(Prop1_brkpt, [szProp2, 1])
    Prop2_vec = Prop2_vec.reshape((-1,1))
    Props_vec = np.hstack((Prop1_vec, Prop2_vec))

    # get properties
    if library_flag == "refprop":
        Data_TD, herr = loop_REFPROP(parameters["material"], parameters["composition"], "PH", "T;D", Props_vec)
    elif library_flag == "coolprop":
        Data_TD = loop_COOLPROP(parameters["material"], parameters["method"], 'HP', 'T;D', np.hstack((Prop2_vec, Prop1_vec)))

    # get surface fit of data
    def poly2d_4th(coords, *args):
        return poly4_2d_class.f_source(coords, args, dim_idx=1)
        
    poly4_2d_class = poly4_2d(np.ones((15,)))
    H_given_PT, pcov = curve_fit(poly2d_4th, (Prop1_vec.flatten(), Data_TD[:,0].flatten()), Prop2_vec.flatten(), p0=np.ones((15,)))
    T_given_PH, pcov = curve_fit(poly2d_4th, (Prop1_vec.flatten(), Prop2_vec.flatten()), Data_TD[:,0].flatten(), p0=np.ones((15,)))
    D_given_PT, pcov = curve_fit(poly2d_4th, (Prop1_vec.flatten(), Data_TD[:,0].flatten()), Data_TD[:,1].flatten(), p0=np.ones((15,)))

    return H_given_PT, T_given_PH, D_given_PT, Prop2_vec, Prop1_vec, Data_TD[:,0], Data_TD[:,1]

class single_phase_CLASS:
    def __init__(self, H_given_PT_liq, T_given_PH_liq, D_given_PT_liq, H_liq, P_liq, T_liq, D_liq, H_given_PT_gas, T_given_PH_gas, D_given_PT_gas, H_gas, P_gas, T_gas, D_gas):
        self.H_given_PT_liq = H_given_PT_liq
        self.T_given_PH_liq = T_given_PH_liq
        self.D_given_PT_liq = D_given_PT_liq
        self.H_liq = H_liq.flatten()
        self.P_liq = P_liq.flatten()
        self.T_liq = T_liq.flatten()
        self.D_liq = D_liq.flatten()
        
        self.H_given_PT_gas = H_given_PT_gas
        self.T_given_PH_gas = T_given_PH_gas
        self.D_given_PT_gas = D_given_PT_gas
        self.H_gas = H_gas.flatten()
        self.P_gas = P_gas.flatten()
        self.T_gas = T_gas.flatten()
        self.D_gas = D_gas.flatten()

def plot_single_phase(DATA):
    h_fit_liq = poly4_2d(DATA.H_given_PT_liq).f((DATA.P_liq.flatten(), DATA.T_liq.flatten()), dim_idx=1)
    t_fit_liq = poly4_2d(DATA.T_given_PH_liq).f((DATA.P_liq.flatten(), DATA.H_liq.flatten()), dim_idx=1)
    d_fit_liq = poly4_2d(DATA.D_given_PT_liq).f((DATA.P_liq.flatten(), DATA.T_liq.flatten()), dim_idx=1)
    h_fit_gas = poly4_2d(DATA.H_given_PT_gas).f((DATA.P_gas.flatten(), DATA.T_gas.flatten()), dim_idx=1)
    t_fit_gas = poly4_2d(DATA.T_given_PH_gas).f((DATA.P_gas.flatten(), DATA.H_gas.flatten()), dim_idx=1)
    d_fit_gas = poly4_2d(DATA.D_given_PT_gas).f((DATA.P_gas.flatten(), DATA.T_gas.flatten()), dim_idx=1)
    
    fig1 = plt.figure(1)
    ax1 = fig1.add_subplot(111, projection='3d')
    ax1.scatter(DATA.H_liq, DATA.P_liq, DATA.T_liq, c='b', marker='x', s=1)
    ax1.scatter(DATA.H_gas, DATA.P_gas, DATA.T_gas, c='b', marker='x', s=1)
    ax1.set_xlabel('Specific Enthalpy (J/kg)')
    ax1.set_ylabel('Pressure (Pa)')
    ax1.set_zlabel('Temperature (K)')
    
    fig2 = plt.figure(2)
    ax2 = fig2.add_subplot(111, projection='3d')
    ax2.scatter(DATA.P_liq, DATA.H_liq, DATA.T_liq, c='b', marker='x', s=1)
    ax2.scatter(DATA.P_liq.flatten(), DATA.H_liq.flatten(), t_fit_liq, c='b', marker='x', s=1)
    ax2.scatter(DATA.P_gas, DATA.H_gas, DATA.T_gas, c='b', marker='x', s=1)
    ax2.scatter(DATA.P_gas.flatten(), DATA.H_gas.flatten(), t_fit_gas, c='b', marker='x', s=1)
    ax2.set_xlabel('Pressure (Pa)')
    ax2.set_ylabel('Specific Enthalpy (J/kg)')
    ax2.set_zlabel('Temperature (K)')
    
    fig1 = plt.figure(3)
    ax1 = fig1.add_subplot(111, projection='3d')
    ax1.scatter(DATA.P_liq, DATA.T_liq, DATA.D_liq, c='b', marker='x', s=1)
    ax1.scatter(DATA.P_liq.flatten(), DATA.T_liq.flatten(), d_fit_liq, c='b', marker='x', s=1)
    ax1.scatter(DATA.P_gas, DATA.T_gas, DATA.D_gas, c='b', marker='x', s=1)
    ax1.scatter(DATA.P_gas.flatten(), DATA.T_gas.flatten(), d_fit_gas, c='b', marker='x', s=1)
    ax1.set_xlabel('Pressure (Pa)')
    ax1.set_ylabel('Temperature (K)')
    ax1.set_zlabel('Density (kg/m^3)')

    fig3 = plt.figure(4)
    ax3 = fig3.add_subplot(111, projection='3d')
    ax3.scatter(DATA.P_liq, DATA.T_liq, DATA.H_liq, c='b', marker='x', s=1)
    ax3.scatter(DATA.P_liq.flatten(), DATA.T_liq.flatten(), h_fit_liq, c='b', marker='x', s=1)
    ax3.scatter(DATA.P_gas, DATA.T_gas, DATA.H_gas, c='b', marker='x', s=1)
    ax3.scatter(DATA.P_gas.flatten(), DATA.T_gas.flatten(), h_fit_gas, c='b', marker='x', s=1)
    ax3.set_xlabel('Pressure (Pa)')
    ax3.set_ylabel('Temperature (K)')
    ax3.set_zlabel('Specific Enthalpy (J/kg)')

    fig4 = plt.figure(5)
    ax4 = fig4.add_subplot(111, projection='3d')
    ax4.scatter(DATA.P_liq, DATA.T_liq, np.abs(DATA.H_liq - h_fit_liq), c='b', marker='x', s=1)
    ax4.scatter(DATA.P_gas, DATA.T_gas, np.abs(DATA.H_gas - h_fit_gas), c='b', marker='x', s=1)
    ax4.set_xlabel('Pressure (Pa)')
    ax4.set_ylabel('Temperature (K)')
    ax4.set_zlabel('Specific Enthalpy (J/kg)')

    plt.show()

if __name__ == "__main__":
    # parameters
    material = "FAKE_POE"
    make_data = True

    module_path = f"DOA.modular_functions.material_properties.config.{material}"
    module = importlib.import_module(module_path)

    gbm_base = os.environ.get('GBM_BASE')
    folder = os.path.join(gbm_base, "DOA/modular_functions/material_properties/data", material)
    os.makedirs(folder, exist_ok=True)   # creates only if missing

    parameters = {}
    library_flag = module.single_phase_config["library_flag"]
    if library_flag == "refprop":
        parameters["composition"] = module.Composition_Vector
        parameters["material"] = module.Name_Vector
        
    elif library_flag == "coolprop":
        parameters["method"] = module.single_phase_config["coolprop_METHOD"]
        parameters["material"] = material

    if make_data:
        DATA = get_single_lookup(module.single_phase_config, library_flag, parameters)
        with h5py.File(gbm_base + '/DOA/modular_functions/material_properties/data/' + material + '/single_phase.h5', 'w') as f:
            save_Class(DATA, f.create_group('LUT'))
    
    else:
        with h5py.File(gbm_base + '/DOA/modular_functions/material_properties/data/' + material + '/single_phase.h5', 'r') as f:
            DATA = load_Class(f)

    plot_single_phase(DATA)