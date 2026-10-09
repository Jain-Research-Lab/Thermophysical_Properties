from DOA.config.lib_config import numpy as np
from CoolProp.CoolProp import AbstractState
# from collections import OrderedDict
import CoolProp
import time

def get_prop_str_short(PROP_STR):
    prop_map = {"Qmass": "Q", "Hmass": "H", "Dmass": "D", 
                "Emass": "U", "Umass": "U", "Smass": "S"}

    return "".join(prop_map.get(p.strip(), p.strip()) for p in PROP_STR)

def init_coolprop_as(material, method, PROP_IN_LST, PROP_OUT_LST):
    AS = AbstractState(method, material)
    
    prop_map = {"Qmass": "Q", "H": "Hmass", "D": "Dmass", 
                "E": "Umass", "U": "Umass", "S": "Smass"}
    
    PROP_IN_STR = "".join(prop_map.get(p.strip(), p.strip()) for p in PROP_IN_LST)
    PROP_OUT_STR = tuple(prop_map.get(p.strip(), p.strip()) for p in PROP_OUT_LST)
    
    PROP_IN = getattr(CoolProp, PROP_IN_STR + "_INPUTS")
    PROP_OUT = tuple(getattr(CoolProp, "i"+i) for i in PROP_OUT_STR)
    
    return AS, PROP_IN, PROP_OUT
    
def loop_COOLPROP(material, method, PROP_IN, PROP_OUT, input_values):
    AS, PROP_IN, PROP_OUT = init_coolprop_as(material, method, PROP_IN, PROP_OUT)
    return np.array([loop_call_COOLPROP(AS, PROP_IN, PROP_OUT, p1xi, p2xi) for p1xi, p2xi in input_values])
                
def loop_call_COOLPROP(AS, PROP_IN, PROP_OUT, p1xi, p2xi):
    AS.update(PROP_IN, p1xi, p2xi)
    return np.array([AS.keyed_output(i) for i in PROP_OUT])

def call_COOLPROP(material, method, PROP_IN, PROP_OUT, p1xi, p2xi):
    AS, PROP_IN, PROP_OUT = init_coolprop_as(material, method, PROP_IN, PROP_OUT)
    AS.update(PROP_IN, p1xi, p2xi)
    return np.array([AS.keyed_output(i) for i in PROP_OUT])

def loop_COOLPROP_SAT(material, COOLPROP_method, PROP_IN, PROP_OUT, input_value, Q):
    input_values = np.vstack((input_value, Q*np.ones(input_value.shape))).T
    return loop_COOLPROP(material, COOLPROP_method, PROP_IN, PROP_OUT, input_values)

def get_crit_COOLPROP(material, method):
    # setup coolprop
    AS = AbstractState(method, material)
    
    # get critical properties
    Tcrit = AS.T_critical()
    Pcrit = AS.p_critical()
    Dcrit = AS.rhomass_critical()
    AS.update(CoolProp.DmassT_INPUTS, Dcrit, Tcrit)
    hcrit = AS.hmass()
    Ecrit = AS.umass()

    return Tcrit, Pcrit, hcrit, Dcrit, Ecrit
    
# Example Usage
if __name__ == "__main__":
    # example input parameters
    material = "PROPANE" # name of material
    INPUT = 'PQ' # use pressure and quality choices: T P D E H S Q
    OUTPUT = 'T;Q' # get temperature and quality
    
    Pmin = 100000   # Pa
    Pmax = 4000000  # Pa
    szProp = 100    # number of points to sample
    P_brkpt = np.linspace(Pmin, Pmax, num=szProp).reshape((-1,1))
    Q_brkpt = np.zeros((szProp,1))
    DATA = np.hstack((P_brkpt, Q_brkpt))
    
    start_time_0 = time.time()
    Data = loop_COOLPROP(material, "HEOS", INPUT, OUTPUT, DATA)
    print(time.time() - start_time_0)