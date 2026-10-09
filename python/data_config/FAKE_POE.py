Name_Vector = "PROPANE;Decane"
Composition_Vector = [0.95, 0.05]

AB_table_config = {"P_min": 100_000,                  # minimum pressure [Pa]
                   "P_max": 4_800_000,                # maximum pressure [Pa]
                   "H_min": 50_000,                   # minimum enthalpy (only guarenteed at P_min) [J/kg]
                   "H_max": 800_000,                  # maximum enthalpy (only guarenteed at P_min) [J/kg]
                   "library_flag": "refprop",         # oracle library
                   "coolprop_METHOD": "HEOS",         # REFPROP or HEOS or TTSE or BICUBIC
                   "T_SCALE": 0                       # scale on temperature
                  }

HP_table_config = {"Hmin": 50_000,                    # Minimum enthalpy [J/kg]
                   "Hmax": 800_000,                   # Maximum enthalpy [J/kg]
                   "Pmin": 100_000,                   # Minimum pressure [J/kg]
                   "Pmax": 4_800_000,                 # Maximum pressure [J/kg]
                   "library_flag": "refprop",         # oracle library
                   "coolprop_METHOD": "HEOS"          # REFPROP or HEOS or TTSE or BICUBIC
                   }

DP_table_config = {"Dmin": 5,                         # Minimum density [kg/m^3]
                   "Dmax": 750,                       # Maximum density [kg/m^3]
                   "Pmin": 100_000,                   # Minimum pressure [J/kg]
                   "Pmax": 4_800_000,                 # Maximum pressure [J/kg]
                   "library_flag": "refprop",         # oracle library
                   "coolprop_METHOD": "HEOS"          # REFPROP or HEOS or TTSE or BICUBIC
                   }

single_phase_config = {"Pmin": 200_000,               # Minimum pressure [J/kg]
                       "Pmax": 4_000_000,             # Maximum pressure [J/kg]
                       "hlim_liq": 50_000,            # Smallest enthalpy to get [J/kg]
                       "hlim_gas": 900_000,           # Largest enthalpy to get [J/kg]
                       "szP": 40,                     # number of samples along pressure
                       "szH": 40,                     # number of samples along enthalpy
                       "library_flag": "refprop",     # oracle library
                       "coolprop_METHOD": "HEOS"      # REFPROP or HEOS or TTSE or BICUBIC
                      }

sat_table_config = {"Tmin_SAT_TP": 230.0,             # [T] lowest temperature to sample for saturated pressure-temperature function
                    "Pmin_SAT_TP": 100_000,           # [Pa] lowest temperature to sample for saturated pressure-temperature function
                    "Pmax_SAT_TP": 3_500_000,         # [Pa] largest pressure to generate vapor dome with PQ, above this use HP
                    "sz_Sat_side": 100,               # Number of samples to construct saturated pressure-temperature function
                    "sz_Sat_top":  50,                # Number of samples to construct top of vapor dome
                    "library_flag": "refprop",        # oracle library
                    "coolprop_METHOD": "HEOS"         # REFPROP or HEOS or TTSE or BICUBIC
                    }