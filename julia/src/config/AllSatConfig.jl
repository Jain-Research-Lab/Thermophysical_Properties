##############################################################################
struct Params_property_sat_vec{N}
    Material::NTuple{N, Vector{String}}
    Composition::NTuple{N, Vector{Float64}}
    RefSystem::NTuple{N, String}
    Method::NTuple{N, String}

    P1min::NTuple{N, Float64}
    P1max::NTuple{N, Float64}
end
##############################################################################

##############################################################################
const ParamsSI_SAT_Materials = ()
const ParamsSI_SAT_Compositions = ()
const ParamsSI_SAT_RefSystem = ()
const ParamsSI_SAT_Methods = ()

const ParamsSI_SAT_Pmin_T = ()
const ParamsSI_SAT_Pmax_T = ()

const ParamsSI_SAT_T_GRID = Params_property_sat_vec(ParamsSI_SAT_Materials, ParamsSI_SAT_Compositions, ParamsSI_SAT_RefSystem, ParamsSI_SAT_Methods, ParamsSI_SAT_Pmin_T, ParamsSI_SAT_Pmax_T)

const ParamsSI_SAT_Pmin_P = ()
const ParamsSI_SAT_Pmax_P = ()

const ParamsSI_SAT_P_GRID = Params_property_sat_vec(ParamsSI_SAT_Materials, ParamsSI_SAT_Compositions, ParamsSI_SAT_RefSystem, ParamsSI_SAT_Methods, ParamsSI_SAT_Pmin_P, ParamsSI_SAT_Pmax_P)
##############################################################################

##############################################################################
const ParamsAS_SAT_Materials = (["Water"], ["R407C"])
const ParamsAS_SAT_Compositions = ([1.0], [1.0])
const ParamsAS_SAT_RefSystem = ("DEF", "DEF")
const ParamsAS_SAT_Methods = ("HEOS", "HEOS")

const ParamsAS_SAT_Pmin_T = (200.0,   200.0)
const ParamsAS_SAT_Pmax_T = (300.0, 300.0)

const ParamsAS_SAT_T_GRID = Params_property_sat_vec(ParamsAS_SAT_Materials, ParamsAS_SAT_Compositions, ParamsAS_SAT_RefSystem, ParamsAS_SAT_Methods, ParamsAS_SAT_Pmin_T, ParamsAS_SAT_Pmax_T)

const ParamsAS_SAT_Pmin_P = (100000.0, 100000.0)
const ParamsAS_SAT_Pmax_P = (150000.0, 450000.0)

const ParamsAS_SAT_P_GRID = Params_property_sat_vec(ParamsAS_SAT_Materials, ParamsAS_SAT_Compositions, ParamsAS_SAT_RefSystem, ParamsAS_SAT_Methods, ParamsAS_SAT_Pmin_P, ParamsAS_SAT_Pmax_P)
##############################################################################

##############################################################################
const ParamsDL_SAT_Materials = ()
const ParamsDL_SAT_Compositions = ()
const ParamsDL_SAT_RefSystem = ()
const ParamsDL_SAT_Methods = ()

const ParamsDL_SAT_Pmin_T = ()
const ParamsDL_SAT_Pmax_T = ()

const ParamsDL_SAT_T_GRID = Params_property_sat_vec(ParamsDL_SAT_Materials, ParamsDL_SAT_Compositions, ParamsDL_SAT_RefSystem, ParamsDL_SAT_Methods, ParamsDL_SAT_Pmin_T, ParamsDL_SAT_Pmax_T)

const ParamsDL_SAT_Pmin_P = ()
const ParamsDL_SAT_Pmax_P = ()

const ParamsDL_SAT_P_GRID = Params_property_sat_vec(ParamsDL_SAT_Materials, ParamsDL_SAT_Compositions, ParamsDL_SAT_RefSystem, ParamsDL_SAT_Methods, ParamsDL_SAT_Pmin_P, ParamsDL_SAT_Pmax_P)
##############################################################################

##############################################################################
const ParamsFL_SAT_Materials = (["PROPANE"], ["D6"], ["R134a"], ["PROPANE", "DECANE"])
const ParamsFL_SAT_Compositions = ([1.0], [1.0], [1.0], [0.95, 0.05])
const ParamsFL_SAT_RefSystem = ("DEF", "DEF", "DEF", "NBP")
const ParamsFL_SAT_Methods = ("", "", "", "")

const ParamsFL_SAT_Pmin_T = (200.0, 200.0, 200.0, 200.0)
const ParamsFL_SAT_Pmax_T = (300.0, 300.0, 300.0, 300.0)

const ParamsFL_SAT_T_GRID = Params_property_sat_vec(ParamsFL_SAT_Materials, ParamsFL_SAT_Compositions, ParamsFL_SAT_RefSystem, ParamsFL_SAT_Methods, ParamsFL_SAT_Pmin_T, ParamsFL_SAT_Pmax_T)

const ParamsFL_SAT_Pmin_P = (100000.0, 100000.0, 100000.0, 100000.0)
const ParamsFL_SAT_Pmax_P = (500000.0, 130000.0, 400000.0, 480000.0)

const ParamsFL_SAT_P_GRID = Params_property_sat_vec(ParamsFL_SAT_Materials, ParamsFL_SAT_Compositions, ParamsFL_SAT_RefSystem, ParamsFL_SAT_Methods, ParamsFL_SAT_Pmin_P, ParamsFL_SAT_Pmax_P)
##############################################################################

##############################################################################
function GEN_T_SATS()
    sz = 400
    PROPS_IN = QT
    PROPS_OUT = ("P", "S", "H", "D", "E")
    
    get_SATS(ParamsSI_SAT_T_GRID, PROPS_IN, PROPS_OUT, sz, SI)
    get_SATS(ParamsAS_SAT_T_GRID, PROPS_IN, PROPS_OUT, sz, AS)
    get_SATS(ParamsDL_SAT_T_GRID, PROPS_IN, PROPS_OUT, sz, DL)
    get_SATS(ParamsFL_SAT_T_GRID, PROPS_IN, PROPS_OUT, sz, FL)

    return 0
end

function GEN_P_SATS()
    sz = 400
    PROPS_IN = QP
    PROPS_OUT = ("T", "S", "H", "D", "E")
    
    get_SATS(ParamsSI_SAT_P_GRID, PROPS_IN, PROPS_OUT, sz, SI)
    get_SATS(ParamsAS_SAT_P_GRID, PROPS_IN, PROPS_OUT, sz, AS)
    get_SATS(ParamsDL_SAT_P_GRID, PROPS_IN, PROPS_OUT, sz, DL)
    get_SATS(ParamsFL_SAT_P_GRID, PROPS_IN, PROPS_OUT, sz, FL)

    return 0
end
##############################################################################

# Params_RefSystem = ("IIR", "ASH", "ASH", "ASH", "ASHRAE", "ASH")