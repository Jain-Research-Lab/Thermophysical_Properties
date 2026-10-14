# from DOA.modular_functions.material_properties.sampling.lib_COOLPROP import get_prop_str_short
# from DOA.general_functions.file_management.save_load_class import save_Class, load_Class
# from DOA.modular_functions.material_properties.sampling.lib_REFPROP import loop_REFPROP, is_valid_material
# from DOA.modular_functions.material_properties.sampling.lib_COOLPROP import loop_COOLPROP

# from dataclasses import dataclass
from ctREFPROP.ctREFPROP import REFPROPFunctionLibrary
from pydantic.dataclasses import dataclass
from typing import Tuple
import warnings
import numpy as np
import h5py
import math
import os
 
class DATA:
    def __init__(self):
        pass
    
def save_Class(self, h5group):
    for attr_name in self.__dict__:
        val = getattr(self, attr_name)
        val = np.asarray(val)
        if isinstance(val, np.ndarray):
            h5group.create_dataset(attr_name, data=val)

        else:
            raise TypeError(f"Unsupported type for attribute '{attr_name}': {type(val)}")

def load_Class(h5group):
    CLASS = DATA() # data instance
    data = h5group[list(h5group.keys())[0]] # the data
    Data_keys = list(data.keys()) # all of the arrays in this file

    for key in Data_keys:
        setattr(CLASS, key, np.array(data[key]))

    return CLASS
    
def get_prop_str_short(PROP_STR):
    prop_map = {"Qmass": "Q", "Hmass": "H", "Dmass": "D", 
                "Emass": "U", "Umass": "U", "Smass": "S"}

    return "".join(prop_map.get(p.strip(), p.strip()) for p in PROP_STR)
    
def is_valid_material(material):
    RP = REFPROPFunctionLibrary(os.environ['RPPREFIX'])
    return RP.SETFLUIDSdll("|".join(material)) == 0

def init_refprop_dl(PROP_IN, PROP_OUT):
    RP = REFPROPFunctionLibrary(os.environ['RPPREFIX'])
    MASS_BASE_SI = RP.GETENUMdll(0,"MASS BASE SI").iEnum
    Qflag = ("Qmass" in PROP_OUT)
    
    return RP, MASS_BASE_SI, PROP_IN, PROP_OUT, Qflag

def loop_REFPROP(material, composition, PROP_IN, PROP_OUT, input_values):
    RP, MASS_BASE_SI, PROP_IN, PROP_OUT, Qflag = init_refprop_dl(PROP_IN, PROP_OUT)
    
    data_and_herr = [loop_call_REFPROP(material, composition, PROP_IN, PROP_OUT, p1xi, p2xi, N, Qflag, RP, MASS_BASE_SI) for p1xi, p2xi in input_values]
    
    M = len(data_and_herr)
    data = np.stack([data_and_herr[i][0] for i in range(M)], axis=0)
    
    return data
        
def loop_call_REFPROP(material, composition, PROP_IN, PROP_OUT, p1xi, p2xi, N, Qflag, RP, MASS_BASE_SI):
    out = RP.REFPROPdll(material, PROP_IN, PROP_OUT, MASS_BASE_SI,MASS_BASE_SI,0, p1xi,p2xi, composition)

    if Qflag:
        data = np.hstack((out.Output[0:N], [np.clip(out.q,0,1),]))
    else:
        data = out.Output[0:N]
        
    return data

def call_REFPROP(material, composition, PROP_IN, PROP_OUT, p1xi, p2xi, N, Qflag):
    # initialize refprop
    RP = REFPROPFunctionLibrary(os.environ['RPPREFIX'])
    MASS_BASE_SI = RP.GETENUMdll(0,"MASS BASE SI").iEnum
        
    out = RP.REFPROPdll(material, PROP_IN, PROP_OUT, MASS_BASE_SI,MASS_BASE_SI,0, p1xi,p2xi, composition)

    if Qflag:
        data = np.hstack((out.Output[0:N], [np.clip(out.q,0,1),]))
    else:
        data = out.Output[0:N]
        
    return data

def loop_REFPROP_SAT(material, composition, PROP_IN, PROP_OUT, input_value, Q):
    input_values = np.vstack((input_value, Q*np.ones(input_value.shape))).T
    return loop_REFPROP(material, composition, PROP_IN, PROP_OUT, input_values)

def get_crit_REFPROP(material, composition):
    # setup refprop
    RP = REFPROPFunctionLibrary(os.environ['RPPREFIX'])
    MASS_BASE_SI = RP.GETENUMdll(0,"MASS BASE SI").iEnum
    
    # get critical properties
    Tcrit = RP.REFPROPdll(material,"","TCRIT", MASS_BASE_SI,MASS_BASE_SI,0,0,0, composition).Output[0]
    Pcrit = RP.REFPROPdll(material,"","PCRIT", MASS_BASE_SI,MASS_BASE_SI,0,0,0, composition).Output[0]
    hcrit = RP.REFPROPdll(material,"TQ","H", MASS_BASE_SI,MASS_BASE_SI,0,Tcrit,0, composition).Output[0]
    Dcrit = RP.REFPROPdll(material,"TQ","H", MASS_BASE_SI,MASS_BASE_SI,0,Tcrit,0, composition).Output[0]
    Ecrit = RP.REFPROPdll(material,"TQ","H", MASS_BASE_SI,MASS_BASE_SI,0,Tcrit,0, composition).Output[0]
    
    return Tcrit, Pcrit, hcrit, Dcrit, Ecrit
    
      
@dataclass
class RPGridConfig:
    material: Tuple[str, ...]
    composition: Tuple[float, ...]
    IN: Tuple[str, ...]
    OUT: Tuple[str, ...]
    sz: Tuple[int, int]
    P1min: float
    P1max: float
    P2min: float
    P2max: float

@dataclass
class CPGridConfig:
    method : str
    material: Tuple[str, ...]
    IN: Tuple[str, ...]
    OUT: Tuple[str, ...]
    sz: Tuple[int, int]
    P1min: float
    P1max: float
    P2min: float
    P2max: float

def init_RPGridConfig(material, composition, IN, OUT, sz, P1min, P1max, P2min, P2max):
    if not is_valid_material(material):
        raise ValueError(f"The requested material does not exist")
    
    if len(material) != len(composition):
        raise ValueError(f"material {material} and composition {composition} tuples must have equal number of elements")
    
    if not math.isclose(sum(composition), 1.0, abs_tol=1e-14) or not all(x > 0.0 for x in composition):
        raise ValueError(f"The composition vector {composition} must sum to 1.0 and be strictly non-negative")
    
    if not is_valid_property(IN+OUT):
        raise ValueError(f"The Input and/or output property vectors {IN} must be contained in")
    
    if (len(sz) != 2) or (sz[0] < 2) or (sz[1] < 2):
        raise ValueError(f"the table size array {sz} must be 2 integers, and each integer must be >= 2")
    
    if sz[0]*sz[1] > 1_000_000:
        warnings.warn(f"Requesting a lookup table with {sz[0]*sz[1]}  points")
    
    if (P1min >= P1max) | (P2min >= P2max):
        raise ValueError(f"property upper bounds must be strictly larger than property lower bounds")
        
    # if error_during_box_sample:
    #     raise ValueError(f"could not successfully evaluate extreme points of table")
    
    IN_SHORT = get_prop_str_short(IN)
    OUT_SHORT = get_prop_str_short(OUT)
    
    return RPGridConfig(material, composition, IN_SHORT, OUT_SHORT, sz, P1min, P1max, P2min, P2max)
    
    
def init_CPGridConfig():
    return 0
   
def is_valid_property(LST):
    valid_prop_map = ("Q", "h", "D", "u", "s", "T", "P")
    return np.all([i in valid_prop_map for i in LST])
    

def make_input_vec(table_config):
    szP1 = table_config.sz[0]
    szP2 = table_config.sz[1]
    
    P1_brkpt = np.linspace(table_config.P1min, table_config.P1max, num=szP1)
    P2_brkpt = np.linspace(table_config.P2min, table_config.P2max, num=szP2)
    P1_gridT, P2_gridT = np.meshgrid(P1_brkpt, P2_brkpt, indexing='ij')
    P1_vec = P1_gridT.reshape((szP1*szP2, 1))
    P2_vec = P2_gridT.reshape((szP1*szP2, 1))
    return np.hstack((P1_vec, P2_vec)) 

class LUT_CLASS:
    def __init__(self, table_config, PP_vec, DATA):
        ALL_DATA = np.hstack((PP_vec, DATA))
        ALL_STR = table_config.IN + table_config.OUT
        
        # save data
        for i, field_name in enumerate(ALL_STR):
            setattr(self, field_name, ALL_DATA[:, i].reshape(table_config.sz))
        
        setattr(self, ALL_STR[0] + "_min", table_config.P1_min)
        setattr(self, ALL_STR[0] + "_max", table_config.P1_max)
        setattr(self, ALL_STR[1] + "_min", table_config.P2_min)
        setattr(self, ALL_STR[1] + "_max", table_config.P2_max)

def save_grid_single(library_flag=None, method=None, material=None, composition=None,
                     IN=None, OUT=None, sz=None, 
                     P1min=None, P1max=None, P2min=None, P2max=None):
    
    if library_flag[0] == "C":
        config = CPGridConfig(method, material, 
                    IN, OUT, sz, P1min, P1max, P2min, P2max)
        
        PP_vec = make_input_vec(config)
        DATA = loop_COOLPROP(config.material, config.method, config.IN, config.OUT, PP_vec)
        
    elif library_flag[0] == "R":
        config = init_RPGridConfig(material, composition, 
                    IN, OUT, sz, P1min, P1max, P2min, P2max)
        
        PP_vec = make_input_vec(config)
        DATA = loop_REFPROP(config.material, config.composition, config.IN, config.OUT, PP_vec)
        
    CLASS = LUT_CLASS(config, PP_vec, DATA)
    
    folder = os.path.join(os.environ.get('GBM_BASE'), "python/data", config.material)
    os.makedirs(folder, exist_ok=True)   # creates only if missing
    OUT_STR = get_prop_str_short(config.OUT)
    with h5py.File(folder + '/' + config.IN[0] + config.IN[1] + '_' + OUT_STR + '_' + str(config.sz[0]) + '_' + str(config.sz[1]) + '.h5', 'w') as f:
        save_Class(CLASS, f.create_group('LUT'))

    return CLASS

def load_grid_single(library_flag=None, method=None, material=None, composition=None,
                     IN=None, OUT=None, sz=None):
    
    OUT_STR = get_prop_str_short(OUT)
    
    if library_flag[0] == "C":
        folder = os.path.join(os.environ.get('GBM_BASE'), "python/data", material + "_" + library_flag + "_" + method)
        with h5py.File(folder + '/' + IN[0] + IN[1] + '_' + OUT_STR + '_' + str(sz[0]) + '_' + str(sz[1]) + '.h5', 'r') as f:
            CLASS = load_Class(f)
    
    elif library_flag[0] == "R":
        comp_str = f"({', '.join(f'{x:.2f}' for x in composition)})"
        folder = os.path.join(os.environ.get('GBM_BASE'), "python/data", material + "_" + library_flag + "_" + comp_str)
        with h5py.File(folder + '/' + IN[0] + IN[1] + '_' + OUT_STR + '_' + str(sz[0]) + '_' + str(sz[1]) + '.h5', 'r') as f:
            CLASS = load_Class(f)
        
    return CLASS


# Example Usage
if __name__ == "__main__":
    save_grid_single(library_flag="RP", method=None, material=("PROPANE",), composition=(1.0,),
                         IN=("P","h"), OUT=("T", "D", "s", "u", "Q"), sz=(20, 20), 
                         P1min=100_000.0, P1max=1_000_000.0, P2min=100_00.0, P2max=700_000.0)
    
    # save_grid_single(library_flag="RP", method=None, material="PROPANE", composition=(1.0,),
    #                  IN=("P","h"), OUT=("T", "D", "s", "u", "Q"), sz=(20, 20), 
    #                  P1min=100_000.0, P1max=1_000_000.0, P2min=100_00.0, P2max=700_000.0)