from DOA.modular_functions.material_properties.sampling.lib_COOLPROP import get_prop_str_short
from DOA.general_functions.file_management.save_load_class import save_Class, load_Class

from dataclasses import dataclass
from typing import Tuple
import h5py
import os



@dataclass
class GridConfig:
    library_flag: str
    material: str
    composition: Tuple[float, ...]
    P1: str
    P2: str
    OUT: str
    P1min: float
    P1max: float
    P2min: float
    P2max: float
    sz: Tuple[int, int]

config = GridConfig(
    library_flag="refprop",
    material="PROPANE",
    composition=(1.0,),
    IN=("P","H"),
    OUT=("T", "D", "E", "S", "Qmass"),
    P1min=-20_000.0,
    P1max=450_000.0,
    P2min=100_000.0,
    P2max=1_300_000.0,
    sz=(400, 400)
)

# grid_config = {"library_flag": "refprop",   # oracle library
#                "material": "PROPANE",       # material
#                "composition": (1.0,),       # composition of each material
#                "P1": "P",                   # first input property
#                "P2": "H",                   # second input property
#                "OUT": "T;D;E;S;Qmass",      # output properties
#                "P1min": -20_000,            # Minimum P1
#                "P1max": 450_000,            # Maximum P1
#                "P2min": 100_000,            # Minimum P2
#                "P2max": 1_300_000,          # Maximum P2
#                "sz": (400,400)              # 2-tuple denoting the size
#                }

def save_grid_single(config):
    

    DATA = get_HP_GRID(config)
    
    # save data
    folder = os.path.join(os.environ.get('GBM_BASE'), "python/data", config.material)
    os.makedirs(folder, exist_ok=True)   # creates only if missing
    OUT_STR = get_prop_str_short(config.OUT)
    with h5py.File(folder + '/' + config.IN[0] + config.IN[1] + '_' + OUT_STR + '_' + str(config.sz[0]) + '_' + str(config.sz[1]) + '.h5', 'w') as f:
        save_Class(DATA, f.create_group('LUT'))

    return DATA

def load_grid_single(config):
    # load data
    folder = os.path.join(os.environ.get('GBM_BASE'), "python/data", config.material)
    OUT_STR = get_prop_str_short(config.OUT)
    with h5py.File(folder + '/' + config.IN[0] + config.IN[1] + '_' + OUT_STR + '_' + str(config.sz[0]) + '_' + str(config.sz[1]) + '.h5', 'r') as f:
        DATA = load_Class(f)
        
    return DATA