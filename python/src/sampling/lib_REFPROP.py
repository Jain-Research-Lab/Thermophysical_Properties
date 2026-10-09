from ctREFPROP.ctREFPROP import REFPROPFunctionLibrary
from DOA.config.lib_config import numpy as np
from collections import OrderedDict
import time
import os

def loop_REFPROP(material, composition, PROP_IN, PROP_OUT, input_values):
    # initialize refprop
    RP = REFPROPFunctionLibrary(os.environ['RPPREFIX'])
    MASS_BASE_SI = RP.GETENUMdll(0,"MASS BASE SI").iEnum
    
    PROP_OUT_NO_Q = PROP_OUT.replace("Qmass", "")
    PROP_OUT_UNIQUE_NO_Q = "".join(OrderedDict.fromkeys(PROP_OUT_NO_Q))
    N = len(PROP_OUT_UNIQUE_NO_Q.replace(";", ""))
    Qflag = ("Qmass" in PROP_OUT)
    
    data_and_herr = [loop_call_REFPROP(material, composition, PROP_IN, PROP_OUT, p1xi, p2xi, N, Qflag, RP, MASS_BASE_SI) for p1xi, p2xi in input_values]
    
    M = len(data_and_herr)
    data = np.stack([data_and_herr[i][0] for i in range(M)], axis=0)
    herr = np.stack([data_and_herr[i][1] for i in range(M)], axis=0)
    
    return data, herr
        
def loop_call_REFPROP(material, composition, PROP_IN, PROP_OUT, p1xi, p2xi, N, Qflag, RP, MASS_BASE_SI):
    out = RP.REFPROPdll(material, PROP_IN, PROP_OUT, MASS_BASE_SI,MASS_BASE_SI,0, p1xi,p2xi, composition)

    if Qflag:
        data = np.hstack((out.Output[0:N], [np.clip(out.q,0,1),]))
    else:
        data = out.Output[0:N]
        
    return data, out.herr

def call_REFPROP(material, composition, PROP_IN, PROP_OUT, p1xi, p2xi, N, Qflag):
    # initialize refprop
    RP = REFPROPFunctionLibrary(os.environ['RPPREFIX'])
    MASS_BASE_SI = RP.GETENUMdll(0,"MASS BASE SI").iEnum
        
    out = RP.REFPROPdll(material, PROP_IN, PROP_OUT, MASS_BASE_SI,MASS_BASE_SI,0, p1xi,p2xi, composition)

    if Qflag:
        data = np.hstack((out.Output[0:N], [np.clip(out.q,0,1),]))
    else:
        data = out.Output[0:N]
        
    return data, out.herr

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
    
# Example Usage
if __name__ == "__main__":
    # example input parameters
    material = "PROPANE" # name of material
    INPUT = 'PQ' # use pressure and quality choices: T P D E H S Q
    OUTPUT = 'T;Qmass' # get temperature and quality
    
    Pmin = 100000   # Pa
    Pmax = 4000000  # Pa
    szProp = 100    # number of points to sample
    P_brkpt = np.linspace(Pmin, Pmax, num=szProp).reshape((-1,1))
    Q_brkpt = np.zeros((szProp,1))
    DATA = np.hstack((P_brkpt, Q_brkpt))
    
    start_time_0 = time.time()
    T_data, T_data_error = loop_REFPROP(material, [1.0], INPUT, OUTPUT, DATA)
    print(time.time() - start_time_0)