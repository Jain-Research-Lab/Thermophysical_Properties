Name_Vector = "D6"
Composition_Vector = [1.0]

AB_table_config = {"P_min": 100_000,                  # minimum pressure [Pa]
                   "P_max": 1_300_000,                # maximum pressure [Pa]
                   "H_min": -20_000,                  # minimum enthalpy (only guarenteed at P_min) [J/kg]
                   "H_max": 450_000,                  # maximum enthalpy (only guarenteed at P_min) [J/kg]
                   "library_flag": "refprop",         # oracle library
                   "coolprop_METHOD": "HEOS",         # REFPROP or HEOS or TTSE or BICUBIC
                   "T_SCALE": 0                       # scale on temperature
                  }

HP_table_config = {"Hmin": -20_000,                   # Minimum enthalpy [J/kg]
                   "Hmax": 450_000,                   # Maximum enthalpy [J/kg]
                   "Pmin": 100_000,                   # Minimum pressure [J/kg]
                   "Pmax": 1_300_000,                 # Maximum pressure [J/kg]
                   "library_flag": "refprop",         # oracle library
                   "coolprop_METHOD": "HEOS"          # REFPROP or HEOS or TTSE or BICUBIC
                   }

DP_table_config = {"Dmin": 50,                        # Minimum density [kg/m^3]
                   "Dmax": 750,                       # Maximum density [kg/m^3]
                   "Pmin": 100_000,                   # Minimum pressure [J/kg]
                   "Pmax": 1_300_000,                 # Maximum pressure [J/kg]
                   "library_flag": "refprop",         # oracle library
                   "coolprop_METHOD": "HEOS"          # REFPROP or HEOS or TTSE or BICUBIC
                   }

single_phase_config = {"Pmin": 100_000,               # Minimum pressure [J/kg]
                       "Pmax": 900_000,               # Maximum pressure [J/kg]
                       "hlim_liq": -20_000,           # Smallest enthalpy to get [J/kg]
                       "hlim_gas": 450_000,           # Largest enthalpy to get [J/kg]
                       "szP": 40,                     # number of samples along pressure
                       "szH": 40,                     # number of samples along enthalpy
                       "library_flag": "refprop",     # oracle library
                       "coolprop_METHOD": "HEOS"      # REFPROP or HEOS or TTSE or BICUBIC
                      }

sat_table_config = {"Tmin_SAT_TP": 450.0,             # [T] lowest temperature to sample for saturated pressure-temperature function
                    "Pmin_SAT_TP": 100_000,           # [Pa] lowest temperature to sample for saturated pressure-temperature function
                    "Pmax_SAT_TP": 940_000,           # [Pa] largest pressure to generate vapor dome with PQ, above this use HP
                    "sz_Sat_side": 150,               # Number of samples to construct saturated pressure-temperature function
                    "sz_Sat_top":  50,                # Number of samples to construct top of vapor dome
                    "library_flag": "refprop",        # oracle library
                    "coolprop_METHOD": "HEOS"         # REFPROP or HEOS or TTSE or BICUBIC
                    }