from DOA.modular_functions.material_properties.sampling.sample_single_phase import get_single_lookup, plot_single_phase
from DOA.modular_functions.material_properties.sampling.sample_saturated_phase import get_sat_lookup, plot_sat_lookup
from DOA.modular_functions.material_properties.sampling.sample_AB import get_AB_GRID, plot_AB_grids
from DOA.modular_functions.material_properties.sampling.sample_HP import get_HP_GRID, plot_HP_grids
from DOA.modular_functions.material_properties.sampling.sample_DP import get_DP_GRID, plot_DP_grids
from DOA.general_functions.file_management.save_load_class import save_Class, load_Class
import importlib
import h5py
import os

if __name__ == "__main__":
    # parameters
    material = "PROPANE"
    make_data = True
    plot_data = True
    coordinate_frames = ["AB", "HP", "DP"] # AB, HP, DP
    sz = (50,50)

    module_path = f"DOA.modular_functions.material_properties.config.{material}"
    module = importlib.import_module(module_path)

    gbm_base = os.environ.get('GBM_BASE')
    folder = os.path.join(gbm_base, "DOA/modular_functions/material_properties/data", material)
    os.makedirs(folder, exist_ok=True)   # creates only if missing

    table_config = {"AB":module.AB_table_config, "HP":module.HP_table_config, "DP":module.DP_table_config}
    SAMPLE_FUNCS = {"AB":get_AB_GRID, "HP":get_HP_GRID, "DP":get_DP_GRID}
    PLOT_FUNCS = {"AB":plot_AB_grids, "HP":plot_HP_grids, "DP":plot_DP_grids}

    if make_data:
        for coordinate_frame in coordinate_frames:
            parameters = {}
            library_flag = table_config[coordinate_frame]["library_flag"]
            parameters["sz"] = sz
            if library_flag == "refprop":
                parameters["composition"] = module.Composition_Vector
                parameters["material"] = module.Name_Vector
                
            elif library_flag == "coolprop":
                parameters["method"] = table_config[coordinate_frame]["coolprop_METHOD"]
                parameters["material"] = material

            DATA = SAMPLE_FUNCS[coordinate_frame](table_config[coordinate_frame], library_flag, parameters)
            sz = DATA.h_grid.shape
            with h5py.File(gbm_base + '/DOA/modular_functions/material_properties/data/' + material + '/' + coordinate_frame + '_DHEPTQS_' + str(sz[0]) + '_' + str(sz[1]) + '.h5', 'w') as f:
                save_Class(DATA, f.create_group('LUT'))

            if plot_data:
                PLOT_FUNCS[coordinate_frame](DATA)

        parameters = {}
        library_flag = module.sat_table_config["library_flag"]
        if library_flag == "refprop":
            parameters["composition"] = module.Composition_Vector
            parameters["material"] = module.Name_Vector
            
        elif library_flag == "coolprop":
            parameters["method"] = module.sat_table_config["coolprop_METHOD"]
            parameters["material"] = material

        DATA = get_sat_lookup(module.sat_table_config, library_flag, parameters)
        with h5py.File(gbm_base + '/DOA/modular_functions/material_properties/data/' + material + '/sat.h5', 'w') as f:
            save_Class(DATA, f.create_group('LUT'))

        if plot_data:
            plot_sat_lookup(DATA)

        parameters = {}
        library_flag = module.single_phase_config["library_flag"]
        if library_flag == "refprop":
            parameters["composition"] = module.Composition_Vector
            parameters["material"] = module.Name_Vector
            
        elif library_flag == "coolprop":
            parameters["method"] = module.single_phase_config["coolprop_METHOD"]
            parameters["material"] = material

        DATA = get_single_lookup(module.single_phase_config, library_flag, parameters)
        with h5py.File(gbm_base + '/DOA/modular_functions/material_properties/data/' + material + '/single_phase.h5', 'w') as f:
            save_Class(DATA, f.create_group('LUT'))

        if plot_data:
            plot_single_phase(DATA)

    else:
        for coordinate_frame in ["AB", "HP", "DP"]:
            with h5py.File(gbm_base + '/DOA/modular_functions/material_properties/data/' + material + '/' + coordinate_frame + '_DHEPTQS_' + str(sz[0]) + '_' + str(sz[1]) + '.h5', 'r') as f:
                DATA = load_Class(f)

            PLOT_FUNCS[coordinate_frame](DATA)

        with h5py.File(gbm_base + '/DOA/modular_functions/material_properties/data/' + material + '/sat.h5', 'r') as f:
            DATA = load_Class(f)

        plot_sat_lookup(DATA)

        with h5py.File(gbm_base + '/DOA/modular_functions/material_properties/data/' + material + '/single_phase.h5', 'r') as f:
            DATA = load_Class(f)

        plot_single_phase(DATA)