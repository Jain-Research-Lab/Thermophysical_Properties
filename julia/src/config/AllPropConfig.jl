##############################################################################
struct Params_property_grid{N}
    Material::NTuple{N, Vector{String}}
    Composition::NTuple{N, Vector{Float64}}
    RefSystem::NTuple{N, String}
    Method::NTuple{N, String}

    P1min::NTuple{N, Float64}
    P1max::NTuple{N, Float64}
    P2min::NTuple{N, Float64}
    P2max::NTuple{N, Float64}
end
##############################################################################

##############################################################################
const ParamsSI_Materials = ()
const ParamsSI_Compositions = ()
const ParamsSI_RefSystem = ()
const ParamsSI_Methods = ()

const ParamsSI_Pmin_PH = ()
const ParamsSI_Pmax_PH = ()
const ParamsSI_Hmin_PH = ()
const ParamsSI_Hmax_PH = ()

const ParamsSI_PH_GRID = Params_property_grid(ParamsSI_Materials, ParamsSI_Compositions, ParamsSI_RefSystem, ParamsSI_Methods, ParamsSI_Pmin_PH, ParamsSI_Pmax_PH, ParamsSI_Hmin_PH, ParamsSI_Hmax_PH)

const ParamsSI_Pmin_PD = ()
const ParamsSI_Pmax_PD = ()
const ParamsSI_Dmin_PD = ()
const ParamsSI_Dmax_PD = ()

const ParamsSI_PD_GRID = Params_property_grid(ParamsSI_Materials, ParamsSI_Compositions, ParamsSI_RefSystem, ParamsSI_Methods, ParamsSI_Pmin_PD, ParamsSI_Pmax_PD, ParamsSI_Dmin_PD, ParamsSI_Dmax_PD)

const ParamsSI_Pmin_PS = ()
const ParamsSI_Pmax_PS = ()
const ParamsSI_Smin_PS = ()
const ParamsSI_Smax_PS = ()

const ParamsSI_PS_GRID = Params_property_grid(ParamsSI_Materials, ParamsSI_Compositions, ParamsSI_RefSystem, ParamsSI_Methods, ParamsSI_Pmin_PS, ParamsSI_Pmax_PS, ParamsSI_Smin_PS, ParamsSI_Smax_PS)
##############################################################################

##############################################################################
const ParamsAS_Materials = (["Water"], ["R407C"])
const ParamsAS_Compositions = ([1.0], [1.0])
const ParamsAS_RefSystem = ("DEF", "DEF")
const ParamsAS_Methods = ("HEOS", "HEOS")

const ParamsAS_Pmin_PH = (100000.0,   100000.0)
const ParamsAS_Pmax_PH = (15000000.0, 4500000.0)
const ParamsAS_Hmin_PH = (200000.0,   120000.0)
const ParamsAS_Hmax_PH = (3200000.0,  600000.0)

const ParamsAS_PH_GRID = Params_property_grid(ParamsAS_Materials, ParamsAS_Compositions, ParamsAS_RefSystem, ParamsAS_Methods, ParamsAS_Pmin_PH, ParamsAS_Pmax_PH, ParamsAS_Hmin_PH, ParamsAS_Hmax_PH)

const ParamsAS_Pmin_PD = (100000.0,   100000.0)
const ParamsAS_Pmax_PD = (15000000.0, 4500000.0)
const ParamsAS_Dmin_PD = (20.0,       100.0)
const ParamsAS_Dmax_PD = (950.0,      1400.0)

const ParamsAS_PD_GRID = Params_property_grid(ParamsAS_Materials, ParamsAS_Compositions, ParamsAS_RefSystem, ParamsAS_Methods, ParamsAS_Pmin_PD, ParamsAS_Pmax_PD, ParamsAS_Dmin_PD, ParamsAS_Dmax_PD)

const ParamsAS_Pmin_PS = (100000.0,   100000.0)
const ParamsAS_Pmax_PS = (15000000.0, 4500000.0)
const ParamsAS_Smin_PS = (2000.0,     2000.0)
const ParamsAS_Smax_PS = (3000.0,     3000.0)

const ParamsAS_PS_GRID = Params_property_grid(ParamsAS_Materials, ParamsAS_Compositions, ParamsAS_RefSystem, ParamsAS_Methods, ParamsAS_Pmin_PS, ParamsAS_Pmax_PS, ParamsAS_Smin_PS, ParamsAS_Smax_PS)
##############################################################################

##############################################################################
const ParamsDL_Materials = ()
const ParamsDL_Compositions = ()
const ParamsDL_RefSystem = ()
const ParamsDL_Methods = ()

const ParamsDL_Pmin_PH = ()
const ParamsDL_Pmax_PH = ()
const ParamsDL_Hmin_PH = ()
const ParamsDL_Hmax_PH = ()

const ParamsDL_PH_GRID = Params_property_grid(ParamsDL_Materials, ParamsDL_Compositions, ParamsDL_RefSystem, ParamsDL_Methods, ParamsDL_Pmin_PH, ParamsDL_Pmax_PH, ParamsDL_Hmin_PH, ParamsDL_Hmax_PH)

const ParamsDL_Pmin_PD = ()
const ParamsDL_Pmax_PD = ()
const ParamsDL_Dmin_PD = ()
const ParamsDL_Dmax_PD = ()

const ParamsDL_PD_GRID = Params_property_grid(ParamsDL_Materials, ParamsDL_Compositions, ParamsDL_RefSystem, ParamsDL_Methods, ParamsDL_Pmin_PD, ParamsDL_Pmax_PD, ParamsDL_Dmin_PD, ParamsDL_Dmax_PD)

const ParamsDL_Pmin_PS = ()
const ParamsDL_Pmax_PS = ()
const ParamsDL_Smin_PS = ()
const ParamsDL_Smax_PS = ()

const ParamsDL_PS_GRID = Params_property_grid(ParamsDL_Materials, ParamsDL_Compositions, ParamsDL_RefSystem, ParamsDL_Methods, ParamsDL_Pmin_PS, ParamsDL_Pmax_PS, ParamsDL_Smin_PS, ParamsDL_Smax_PS)
##############################################################################

##############################################################################
const ParamsFL_Materials = (["PROPANE"], ["D6"], ["R134a"])
const ParamsFL_Compositions = ([1.0], [1.0], [1.0])
const ParamsFL_RefSystem = ("DEF", "DEF", "DEF")
const ParamsFL_Methods = ("", "", "")

const ParamsFL_Pmin_PH = (100000.0,  100000.0,  100000.0)
const ParamsFL_Pmax_PH = (5000000.0, 1300000.0, 5000000.0)
const ParamsFL_Hmin_PH = (95000.0,   -20000.0,  150000.0)
const ParamsFL_Hmax_PH = (800000.0,  450000.0,  600000.0)

const ParamsFL_PH_GRID = Params_property_grid(ParamsFL_Materials, ParamsFL_Compositions, ParamsFL_RefSystem, ParamsFL_Methods, ParamsFL_Pmin_PH, ParamsFL_Pmax_PH, ParamsFL_Hmin_PH, ParamsFL_Hmax_PH)

const ParamsFL_Pmin_PD = (100000.0,  100000.0,  100000.0)
const ParamsFL_Pmax_PD = (5000000.0, 1300000.0, 4000000.0)
const ParamsFL_Dmin_PD = (5.0,       50.0,      5.0)
const ParamsFL_Dmax_PD = (600.0,     750.0,     1400.0)

const ParamsFL_PD_GRID = Params_property_grid(ParamsFL_Materials, ParamsFL_Compositions, ParamsFL_RefSystem, ParamsFL_Methods, ParamsFL_Pmin_PD, ParamsFL_Pmax_PD, ParamsFL_Dmin_PD, ParamsFL_Dmax_PD)

const ParamsFL_Pmin_PS = (100000.0,  100000.0,  100000.0)
const ParamsFL_Pmax_PS = (5000000.0, 1300000.0, 4000000.0)
const ParamsFL_Smin_PS = (2000.0,    2000.0,    2000.0)
const ParamsFL_Smax_PS = (3000.0,    3000.0,    3000.0)

const ParamsFL_PS_GRID = Params_property_grid(ParamsFL_Materials, ParamsFL_Compositions, ParamsFL_RefSystem, ParamsFL_Methods, ParamsFL_Pmin_PS, ParamsFL_Pmax_PS, ParamsFL_Smin_PS, ParamsFL_Smax_PS)
##############################################################################

##############################################################################
function GEN_PH_GRIDS()
    sz = (400, 400)
    PROPS_IN = PH
    PROPS_OUT = ("T", "S", "Q", "D", "E")
    
    get_GRIDS(ParamsSI_PH_GRID, PROPS_IN, PROPS_OUT, sz, SI)
    get_GRIDS(ParamsAS_PH_GRID, PROPS_IN, PROPS_OUT, sz, AS)
    get_GRIDS(ParamsDL_PH_GRID, PROPS_IN, PROPS_OUT, sz, DL)
    get_GRIDS(ParamsFL_PH_GRID, PROPS_IN, PROPS_OUT, sz, FL)

    return 0
end

function GEN_PD_GRIDS()
    sz = (400, 400)
    PROPS_IN = PD
    PROPS_OUT = ("T", "S", "Q", "H", "E")
    
    get_GRIDS(ParamsSI_PD_GRID, PROPS_IN, PROPS_OUT, sz, SI)
    get_GRIDS(ParamsAS_PD_GRID, PROPS_IN, PROPS_OUT, sz, AS)
    get_GRIDS(ParamsDL_PD_GRID, PROPS_IN, PROPS_OUT, sz, DL)
    get_GRIDS(ParamsFL_PD_GRID, PROPS_IN, PROPS_OUT, sz, FL)

    return 0
end

function GEN_PS_GRIDS()
    sz = (400, 400)
    PROPS_IN = PS
    PROPS_OUT = ("T", "D", "Q", "H", "E")
    
    get_GRIDS(ParamsSI_PS_GRID, PROPS_IN, PROPS_OUT, sz, SI)
    get_GRIDS(ParamsAS_PS_GRID, PROPS_IN, PROPS_OUT, sz, AS)
    get_GRIDS(ParamsDL_PS_GRID, PROPS_IN, PROPS_OUT, sz, DL)
    get_GRIDS(ParamsFL_PS_GRID, PROPS_IN, PROPS_OUT, sz, FL)

    return 0
end

function GEN_AB_GRIDS()
    sz = (400, 400)

    return 0
end
##############################################################################

# Params_RefSystem = ("IIR", "ASH", "ASH", "ASH", "ASHRAE", "ASH")