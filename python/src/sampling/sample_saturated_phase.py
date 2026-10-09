from DOA.modular_functions.material_properties.sampling.lib_REFPROP import loop_REFPROP, call_REFPROP, get_crit_REFPROP
from DOA.modular_functions.material_properties.sampling.lib_COOLPROP import loop_COOLPROP, get_crit_COOLPROP
from DOA.general_functions.file_management.save_load_class import save_Class, load_Class
from scipy.interpolate import Akima1DInterpolator
from DOA.config.lib_config import numpy as np
import matplotlib.transforms as trs
import matplotlib.pyplot as plt
import importlib
import h5py
import os

def sample_PQ(sat_table_config, library_flag, parameters, Qval, OUTPUT, spacing_flag=False, Pmax_flag=False):
    Pmin = sat_table_config["Pmin_SAT_TP"]
    if Pmax_flag:
        Pmax = sat_table_config["Pmax_SAT_TP"]
    else:
        if library_flag == "refprop":
            Tcrit, Pcrit, hcrit, Dcrit, Ecrit = get_crit_REFPROP(parameters["material"], parameters["composition"])

        elif library_flag == "coolprop":
            Tcrit, Pcrit, hcrit, Dcrit, Ecrit = get_crit_COOLPROP(parameters["material"], parameters["method"])

        Pmax = Pcrit
        
    sz_Sat = sat_table_config["sz_Sat_side"]
    
    if spacing_flag:
        P = np.linspace(Pmin, Pmax[0], num=sz_Sat)
    else:
        P = np.logspace(np.log10(Pmin), np.log10(Pmax), num=sz_Sat).reshape((-1,1))
    
    Q = Qval*np.ones((sz_Sat,1))
    DATA = np.concatenate((P, Q), axis=1)

    if library_flag == "refprop":
        Data, error = loop_REFPROP(parameters["material"], parameters["composition"], 'PQmass', OUTPUT, DATA), Pmax

    elif library_flag == "coolprop":
        Data = loop_COOLPROP(parameters["material"], parameters["method"], 'PQ', OUTPUT, DATA), Pmax

    return Data

def sample_TQ(material, sat_table_config, Qval, OUTPUT):
    Tmin = sat_table_config["Tmin_SAT_TP"]
    Tmax, herrPmax = call_REFPROP(material, "", "TCRIT", 0.0, 0.0, 1, 0)
    sz_Sat = sat_table_config["sz_Sat_side"]
    
    T = np.linspace(Tmin, Tmax, num=sz_Sat)
    Q = Qval*np.ones((sz_Sat,))
    DATA = np.stack((T, Q), axis=1)
    
    return loop_REFPROP(material, 'TQ', OUTPUT, DATA), Tmax

def sample_HQ(material, H, Qval, OUTPUT):    
    Q = Qval*np.ones((H.size,))
    DATA = np.stack((H, Q), axis=1)
    
    return loop_REFPROP(material, 'HQ', OUTPUT, DATA)
        
def get_sat_lookup(sat_table_config, library_flag, parameters):
    # saturated functions
    TPH, Pmax = sample_PQ(sat_table_config, library_flag, parameters, 0.0, 'T;P;H')
    H, Pmax = sample_PQ(sat_table_config, library_flag, parameters, 1.0, 'H')
    Tsat = TPH[:,0]
    Psat = TPH[:,1]
    H0 = TPH[:, 2]
    H1 = H[:,0]
    
    T_given_P_fit = np.flip(np.polynomial.polynomial.Polynomial.fit(np.log(Psat/1000.0), Tsat, 4).convert().coef)
    P_given_T_fit = np.flip(np.polynomial.polynomial.Polynomial.fit(Tsat, np.log(Psat/1000.0), 4).convert().coef)
    H0_given_P_fit = np.flip(np.polynomial.polynomial.Polynomial.fit(np.log(Psat / 1000.0), H0, 4).convert().coef)
    H1_given_P_fit = np.flip(np.polynomial.polynomial.Polynomial.fit(np.log(Psat / 1000.0), H1, 4).convert().coef)

    # dome data
    if library_flag == "refprop":
        Tcrit, Pcrit, hcrit, Dcrit, Ecrit = get_crit_REFPROP(parameters["material"], parameters["composition"])

    elif library_flag == "coolprop":
        Tcrit, Pcrit, hcrit, Dcrit, Ecrit = get_crit_COOLPROP(parameters["material"], parameters["method"])
    
    Prop_lower_left, Pmax = sample_PQ(sat_table_config, library_flag, parameters, 0.0, "H;P;T;D;E;S;Qmass", spacing_flag=False, Pmax_flag=False)
    Prop_lower_right, Pmax = sample_PQ(sat_table_config, library_flag, parameters, 1.0, "H;P;T;D;E;S;Qmass", spacing_flag=False, Pmax_flag=False)
    
    # save lower dome data
    mask_lower_left = sat_table_config["Pmax_SAT_TP"] < Prop_lower_left[:,1]
    mask_lower_right = sat_table_config["Pmax_SAT_TP"] < Prop_lower_right[:,1]
    Prop_lower_left_FINAL = Prop_lower_left[~mask_lower_left]
    Prop_lower_right_FINAL = Prop_lower_right[~mask_lower_right]
    
    # re-sample top of dome
    prop_dome = np.concatenate((Prop_lower_left[mask_lower_left], np.flipud(Prop_lower_right[mask_lower_right][0:-1,:])))
    h_upper_left = np.linspace(prop_dome[0,0], hcrit, round(sat_table_config["sz_Sat_top"]/2))
    h_upper_right = np.linspace(hcrit, prop_dome[-1,0], round(sat_table_config["sz_Sat_top"]/2))
    h_upper = np.concatenate((h_upper_left, h_upper_right[1:]))
    P_upper = np.clip(Akima1DInterpolator(prop_dome[:,0], prop_dome[:,1])(h_upper), 0, Pcrit*0.9999)

    if library_flag == "refprop":
        Prop_upper_FINAL, herrProp01 = loop_REFPROP(parameters["material"], parameters["composition"], "HP", "H;P;T;D;E;S;Q", np.column_stack((h_upper, P_upper)))

    elif library_flag == "coolprop":
        Prop_upper_FINAL = loop_COOLPROP(parameters["material"], parameters["method"], 'HP', "H;P;T;D;E;S;Q", np.column_stack((h_upper, P_upper)))
    
    # combine data
    PropN = np.concatenate((Prop_lower_left_FINAL, Prop_upper_FINAL, np.flipud(Prop_lower_right_FINAL)), axis=0)

    return sat_CLASS(T_given_P_fit, P_given_T_fit, H0_given_P_fit, H1_given_P_fit, Tsat, Psat, H0, H1, PropN)

class sat_CLASS:
    def __init__(self, T_given_P_fit, P_given_T_fit, H0_given_P_fit, H1_given_P_fit, Tsat, Psat, H0, H1, dome_data):
        self.T_given_P_fit = T_given_P_fit
        self.P_given_T_fit = P_given_T_fit
        self.H0_given_P_fit = H0_given_P_fit
        self.H1_given_P_fit = H1_given_P_fit
        self.Tsat = Tsat
        self.Psat = Psat
        self.H0 = H0
        self.H1 = H1

        self.h = dome_data[:,0]
        self.P = dome_data[:,1]
        self.T = dome_data[:,2]
        self.D = dome_data[:,3]
        self.E = dome_data[:,4]
        self.S = dome_data[:,5]
        self.Q = dome_data[:,6]

def plot_sat_lookup(sat_prop):
    gbm_base = os.environ.get('GBM_BASE')

    sz1 = 14
    sz2 = 14
    plt.rc('font', size=sz1)           # Default font size 
    plt.rc('axes', titlesize=sz1)      # Axes title font size
    plt.rc('axes', labelsize=sz1)      # Axes label font size
    plt.rc('xtick', labelsize=sz2)     # X tick label font size
    plt.rc('ytick', labelsize=sz2)     # Y tick label font size
    plt.rc('legend', fontsize=sz2)     # Legend font size

    T_given_P_fit = sat_prop.T_given_P_fit
    P_given_T_fit = sat_prop.P_given_T_fit
    Tsat = sat_prop.Tsat
    Psat = sat_prop.Psat
    
    T_fit = np.polyval(T_given_P_fit, np.log(Psat.flatten()/1000.0))
    P_fit = np.exp(np.polyval(P_given_T_fit, Tsat.flatten()))
    
    plt.figure(1)
    plt.scatter(Psat / 1000.0, Tsat)
    plt.xlabel("Pressure (kPa)")
    plt.ylabel("Temperature (K)")

    plt.figure(2)
    plt.scatter(Psat / 1000.0, Tsat)
    plt.xlabel("Pressure (kPa)")
    plt.ylabel("Temperature (K)")
    plt.xscale('log')
    
    plt.figure(3)
    plt.scatter(Psat / 1000.0, Tsat, label="Ref")
    plt.scatter(Psat / 1000.0, T_fit, label="Fit T")
    plt.scatter(P_fit, Tsat, label="Fit P")
    plt.xlabel("Pressure (kPa)")
    plt.ylabel("Temperature (K)")
    plt.legend()

    plt.figure(4)
    plt.scatter(Psat / 1000.0, Tsat, label="Ref")
    plt.scatter(Psat / 1000.0, T_fit, label="Fit T")
    plt.scatter(P_fit, Tsat, label="Fit P")
    plt.xlabel("Pressure (kPa)")
    plt.ylabel("Temperature (K)")
    plt.xscale('log')
    plt.legend()

    bbox = trs.Bbox([[0.0, -0.1], [6.5, 4.5]])
    plt.figure(5)
    plt.plot(sat_prop.h/1000, sat_prop.P/1000)
    plt.yscale('log')
    plt.xlabel("Enthalpy ($kJ \cdot kg^{-1}$)")
    plt.ylabel("Pressure (kPa)")
    plt.savefig(gbm_base + "/DOA/modular_functions/material_properties/LUT_ANALYSIS/images/dome.pdf",dpi=300,bbox_inches=bbox)
    plt.savefig(gbm_base + "/DOA/modular_functions/material_properties/LUT_ANALYSIS/images/dome.png",dpi=300,bbox_inches=bbox)
    
    plt.figure(6)
    plt.scatter(sat_prop.h/1000, sat_prop.P/1000)
    plt.yscale('log')
    plt.xlabel("Enthalpy ($kJ \cdot kg^{-1}$)")
    plt.ylabel("Pressure (kPa)")
    plt.xlim([100, 10000])
    plt.show()

    plt.show()

# Example Usage
if __name__ == "__main__":
    # parameters
    material = "PROPANE"
    make_data = True

    module_path = f"DOA.modular_functions.material_properties.config.{material}"
    module = importlib.import_module(module_path)

    gbm_base = os.environ.get('GBM_BASE')
    folder = os.path.join(gbm_base, "DOA/modular_functions/material_properties/data", material)
    os.makedirs(folder, exist_ok=True)   # creates only if missing

    parameters = {}
    library_flag = module.sat_table_config["library_flag"]
    if library_flag == "refprop":
        parameters["composition"] = module.Composition_Vector
        parameters["material"] = module.Name_Vector
        
    elif library_flag == "coolprop":
        parameters["method"] = module.sat_table_config["coolprop_METHOD"]
        parameters["material"] = material

    # saturation data & fit
    if make_data:
        DATA = get_sat_lookup(module.sat_table_config, library_flag, parameters)
        with h5py.File(gbm_base + '/DOA/modular_functions/material_properties/data/' + material + '/sat.h5', 'w') as f:
            save_Class(DATA, f.create_group('LUT'))

    else:
        with h5py.File(gbm_base + '/DOA/modular_functions/material_properties/data/' + material + '/sat.h5', 'r') as f:
                DATA = load_Class(f)

    plot_sat_lookup(DATA)