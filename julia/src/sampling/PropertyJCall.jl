# SI: "HEOS", "REFPROP", "IF97"
# AS: "HEOS", "REFPROP", "IF97", "BICUBIC&HEOS", "TTSE&HEOS", "BICUBIC&REFPROP", "TTSE&REFPROP"
# MISSING: SVDSBTL&HEOS, SVDSBTL&REFPROP, SVDSBTL&IF97
##############################################################################
const PROPS_CP_SHORTHAND = Dict{String, String}(
    "D" => "Dmass",          # Mass Density
    "H" => "Hmass",          # Mass Specific Enthalpy
    "S" => "Smass",          # Mass Specific Entropy
    "E" => "Umass",          # Mass Specific Internal Energy
    "U" => "Umass",          # Mass Specific Internal Energy
    "C" => "CPmass",         # Mass Specific Heat (Constant Pressure)
    "O" => "CVmass",         # Mass Specific Heat (Constant Volume)
    "V" => "VISCOSITY",      # Dynamic Viscosity
    "L" => "CONDUCTIVITY",   # Thermal Conductivity
    "A" => "SPEED_OF_SOUND", # Speed of Sound
)

const PROPS_AS_SHORTHAND = Dict{String, String}(
    "TP_INPUTS" => "PT_INPUTS",
    "TQ_INPUTS" => "QT_INPUTS",
    "PQ_INPUTS" => "QP_INPUTS",

    "TDmass_INPUTS" => "DmassT_INPUTS",
    "PHmass_INPUTS" => "HmassP_INPUTS",
    "THmass_INPUTS" => "HmassT_INPUTS",
    "SmassP_INPUTS" => "PSmass_INPUTS",
    "PDmass_INPUTS" => "DmassP_INPUTS",
    "TSmass_INPUTS" => "SmassT_INPUTS",

    "SmassHmass_INPUTS" => "HmassSmass_INPUTS",
    "SmassDmass_INPUTS" => "DmassSmass_INPUTS",
    "HmassDmass_INPUTS" => "DmassHmass_INPUTS",
)

function get_full_prop_CP(prop::String)
    return get(PROPS_CP_SHORTHAND, prop, prop)
end

const PROPS_RP_SHORTHAND = Dict{String, String}(
    "Q" => "Qmass",          # Vapor Quality
)

function get_full_prop_RP(prop::String)
    return get(PROPS_RP_SHORTHAND, prop, prop)
end

@inline function propidx(props::Tuple{Vararg{String}}, name::String)
    i = findfirst(==(name), props)
    i === nothing && error("property \"$name\" not found in $props")
    return i
end
##############################################################################

##############################################################################
const SI, AS, DL, FL = Val(:SI), Val(:AS), Val(:DL), Val(:FL)

struct Params_property_crit{Cache_Type}
    Material::Vector{String}
    Composition::Vector{Float64}
    ref_system::String
    Method::String
    Cache::Cache_Type
end
##############################################################################

##############################################################################
struct CoolpropSICache_crit{Cache_Type}
    params::Params_property_crit{Cache_Type} # params used to generate the struct
    material::String                         # material formatted for coolprop SI usage 

    hcrit::Array{Float64,0}
    Pcrit::Array{Float64,0}
    Dcrit::Array{Float64,0}
    Tcrit::Array{Float64,0}
    ucrit::Array{Float64,0}
end

struct CoolpropASCache_crit{Cache_Type}
    params::Params_property_crit{Cache_Type} # params used to generate the struct
    material::String                    # material formatted for coolprop AS usage
    PROP_IN::Clong                      # integer corresponding to the input properties
    
    hcrit::Array{Float64,0}
    Pcrit::Array{Float64,0}
    Dcrit::Array{Float64,0}
    Tcrit::Array{Float64,0}
    ucrit::Array{Float64,0}

    handle::Clong
    i_Tcrit::Clong
    i_Pcrit::Clong
    i_Dcrit::Clong
    i_Hmass::Clong
    i_Umass::Clong    
end

struct RefpropDLCache_crit{Cache_Type}
    params::Params_property_crit{Cache_Type} # params used to generate the struct
    material::String                   # material formatted for refprop DLL usage
    z::Vector{Float64}                 # composition vector, sum is 1, non-negative

    hcrit::Array{Float64,0}
    Pcrit::Array{Float64,0}
    Dcrit::Array{Float64,0}
    Tcrit::Array{Float64,0}
    ucrit::Array{Float64,0}
    
    Output::Vector{Float64}       # ordered array of requested properties, except quality
    x::Vector{Float64}
    y::Vector{Float64}
    x3::Vector{Float64}
    hUnits_buf::Vector{UInt8}
    herr_buf::Vector{UInt8}
    q::Vector{Float64}            # material static quality
    ierr::Vector{Cint}            # error code, is an error has occured
    iMass::Int64                  # integer indicating what unit system to use
end

struct RefpropFLCache_crit{Cache_Type}
    params::Params_property_crit{Cache_Type}   # params used to generate the struct
    material::String                           # material formatted for refprop DLL usage
    z::Vector{Float64}                         # composition vector, sum is 1, non-negative

    hcrit::Array{Float64,0}
    Pcrit::Array{Float64,0}
    Dcrit::Array{Float64,0}
    Tcrit::Array{Float64,0}
    ucrit::Array{Float64,0}

    MW::Float64
    Output::Vector{Float64}           # ordered array of requested properties, except quality

    T::Base.RefValue{Float64}
    P::Base.RefValue{Float64}
    D::Base.RefValue{Float64}
    e::Base.RefValue{Float64}
    h::Base.RefValue{Float64}
    s::Base.RefValue{Float64}
    q::Base.RefValue{Float64}

    Dl::Base.RefValue{Float64}
    Dv::Base.RefValue{Float64}
    Cv::Base.RefValue{Float64}
    Cp::Base.RefValue{Float64}
    w::Base.RefValue{Float64}

    x::Vector{Float64}
    y::Vector{Float64}

    kr::Base.RefValue{Int32}
    kq::Base.RefValue{Int32}
    ierr::Base.RefValue{Int32}
    herr::Vector{UInt8}
end
##############################################################################

##############################################################################
function init_props_crit(params::Params_property_crit{Val{:SI}})
    length(params.Material) == length(params.Composition) || error("material and composition must have same length")

    partial_material = join(string.(params.Material, "[", params.Composition, "]"), "&")
    material = params.Method*"::"*partial_material
    set_reference_stateS_ccall!(join(params.Material, "&"), params.ref_system)

    return CoolpropSICache_crit(params, material, Array{Float64,0}(undef), Array{Float64,0}(undef),
    Array{Float64,0}(undef), Array{Float64,0}(undef), Array{Float64,0}(undef))
end

function init_props_crit(params::Params_property_crit{Val{:AS}})
    length(params.Material) == length(params.Composition) || error("material and composition must have same length")

    material = join(params.Material, "&")
    set_reference_stateS_ccall!(material, params.ref_system)
    handle = AbstractState_factory_ccall(params.Method, material)
    AbstractState_set_fractions_ccall!(handle, params.Composition)
    PROP_IN    = get_input_pair_index_ccall("DmassT_INPUTS")

    i_Tcrit = get_param_index_ccall("T_critical")
    i_Pcrit = get_param_index_ccall("p_critical")
    i_Dcrit = get_param_index_ccall("rhomass_critical")
    i_Hmass = get_param_index_ccall("Hmass")
    i_Umass = get_param_index_ccall("Umass")

    return CoolpropASCache_crit(params, material, PROP_IN, Array{Float64,0}(undef), Array{Float64,0}(undef),
     Array{Float64,0}(undef), Array{Float64,0}(undef), Array{Float64,0}(undef),
     handle, i_Tcrit, i_Pcrit, i_Dcrit, i_Hmass, i_Umass)
end

function init_props_crit(params::Params_property_crit{Val{:DL}})
    length(params.Material) == length(params.Composition) || error("material and composition must have same length")

    # material string and composition
    material = join(params.Material, "|")
    z = zeros(Float64, 20)
    for i in eachindex(params.Composition)
        z[i] = params.Composition[i]
    end
    
    # unit system integer
    SETREFdll_ccall!(params.ref_system, z)
    mass_base_si = GETENUMdll_ccall("MASS BASE SI")

    return RefpropDLCache_crit(params, material, z, Array{Float64,0}(undef),
    Array{Float64,0}(undef), Array{Float64,0}(undef), Array{Float64,0}(undef), Array{Float64,0}(undef), zeros(Float64, 200),
    zeros(Float64, 20), zeros(Float64, 20), zeros(Float64, 20), zeros(UInt8, 255), zeros(UInt8, 255), [0.0], [Cint(0)], mass_base_si)
end

function init_props_crit(params::Params_property_crit{Val{:FL}})
    length(params.Material) == length(params.Composition) || error("material and composition must have same length")

    material = join(params.Material .* ".FLD", "*")
    z = zeros(Float64, 20)
    for i in eachindex(params.Composition)
        z[i] = params.Composition[i]
    end

    TARGET_PROPS = ("T", "P", "D", "Q", "H", "E", "S")
    Output = Vector{Float64}(undef, length(TARGET_PROPS))

    # setup material
    SETPATHdll_ccall!()
    SETFLUIDSdll_ccall!(material)
    SETREFdll_ccall!(params.ref_system, z)
    MW = WMOLdll_ccall(z)

    return RefpropFLCache_crit(params, material, z, Array{Float64,0}(undef),
        Array{Float64,0}(undef), Array{Float64,0}(undef), Array{Float64,0}(undef),
        Array{Float64,0}(undef), MW, Output, Ref(0.0), Ref(0.0), Ref(0.0), Ref(0.0), Ref(0.0), Ref(0.0), Ref(0.0),
        Ref(0.0), Ref(0.0), Ref(0.0), Ref(0.0), Ref(0.0), zeros(Float64, 20), zeros(Float64, 20),
        Ref(Int32(0)), Ref(Int32(2)), Ref(Int32(0)), zeros(UInt8, 255))
end
##############################################################################

##############################################################################
"Get critical properties for a single material with coolprop using SI with ccall interface"
function get_crit_call!(cache::CoolpropSICache_crit)
    cache.Tcrit .= PropsSI_ccall("T_critical", "", 0.0, "", 0.0, cache.material)
    cache.Pcrit .= PropsSI_ccall("p_critical", "", 0.0, "", 0.0, cache.material)
    cache.Dcrit .= PropsSI_ccall("rhomass_critical", "", 0.0, "", 0.0, cache.material)

    cache.hcrit .= PropsSI_ccall("Hmass", "T", cache.Tcrit[], "Dmass", cache.Dcrit[], cache.material)
    cache.ucrit .= PropsSI_ccall("Umass", "T", cache.Tcrit[], "Dmass", cache.Dcrit[], cache.material)
end

"Get critical properties for a single material with coolprop using abstract state with ccall interface"
function get_crit_call!(cache::CoolpropASCache_crit)
    cache.Tcrit .= AbstractState_keyed_output_ccall(cache.handle, cache.i_Tcrit)
    cache.Pcrit .= AbstractState_keyed_output_ccall(cache.handle, cache.i_Pcrit)
    cache.Dcrit .= AbstractState_keyed_output_ccall(cache.handle, cache.i_Dcrit)

    AbstractState_update_ccall!(cache, cache.Dcrit[], cache.Tcrit[])
    cache.hcrit .= AbstractState_keyed_output_ccall(cache.handle, cache.i_Hmass)
    cache.ucrit .= AbstractState_keyed_output_ccall(cache.handle, cache.i_Umass)
end

"Get critical properties for a single material with refprop using DLL with ccall interface"
function get_crit_call!(cache::RefpropDLCache_crit)
    REFPROPdll_ccall!(cache, "CRIT", "T;P;D", 0.0, 0.0)
    cache.Tcrit .= cache.Output[1]
    cache.Pcrit .= cache.Output[2]
    cache.Dcrit .= cache.Output[3]

    REFPROPdll_ccall!(cache, "TD", "H;E", cache.Tcrit[], cache.Dcrit[])
    cache.hcrit .= cache.Output[1]
    cache.ucrit .= cache.Output[2]
end

"Get critical properties for a single material with refprop using FLSH with ccall interface"
function get_crit_call!(cache::RefpropFLCache_crit)
    Tcrit, Pcrit, Dcrit = compute_crit(cache)
    cache.Tcrit .= Tcrit
    cache.Pcrit .= Pcrit
    cache.Dcrit .= Dcrit

    tdflsh!(cache, Tcrit, Dcrit)
    cache.hcrit .= cache.Output[5]
    cache.ucrit .= cache.Output[6]
end
##############################################################################

##############################################################################
struct Params_property_base{M, PROP_TYPE, Cache_Type}
    Material::Vector{String}
    Composition::Vector{Float64}
    ref_system::String
    Method::String
    PROPS_IN::PROP_TYPE
    PROPS_OUT::NTuple{M, String}
    ncols::Int64
    Cache::Cache_Type
end
##############################################################################

##############################################################################
struct CoolpropSICache_base{M, K, PROP_TYPE, Cache_Type}
    params::Params_property_base{M, PROP_TYPE, Cache_Type} # params used to generate the struct
    material::String                      # material formatted for coolprop SI usage
    PROP_IN::NTuple{2, String}            # 2-element tuple of input properties
    PROP_OUT::NTuple{M, String}           # tuple of properties as simplified strings
    ALL_PROPS::NTuple{K, String}          # tuple of all properties
    output::Matrix{Float64}               # material properties
end

struct CoolpropASCache_base{M, K, PROP_TYPE, Cache_Type}
    params::Params_property_base{M, PROP_TYPE, Cache_Type} # params used to generate the struct
    material::String                      # material formatted for coolprop AS usage
    PROP_IN::Int32                        # integer corresponding to the input properties
    PROP_OUT::NTuple{M, Int32}            # tuple of properties as simplified strings
    ALL_PROPS::NTuple{K, String}          # tuple of all properties
    output::Matrix{Float64}               # material properties

    handle::Clong

    SWAP_PROP_IN::Bool                    # flag for if input properties should be swapped wall passed to ccal
end

struct RefpropDLCache_base{M, K, PROP_TYPE, Cache_Type}
    params::Params_property_base{M, PROP_TYPE, Cache_Type}  # params used to generate the struct
    material::String                      # material formatted for refprop DLL usage
    PROP_IN::String                       # string of input properties
    PROP_OUT::String                      # string of output properties
    ALL_PROPS::NTuple{K, String}          # tuple of all properties
    output::Matrix{Float64}               # material properties

    N::Int64                              # number of properties to compute

    z::Vector{Float64}                    # composition vector, sum is 1, non-negative
    Output::Vector{Float64}               # ordered array of requested properties, except quality
    x::Vector{Float64}
    y::Vector{Float64}
    x3::Vector{Float64}
    hUnits_buf::Vector{UInt8}
    herr_buf::Vector{UInt8}
    q::Vector{Float64}                    # material static quality
    ierr::Vector{Cint}                    # error code, is an error has occured
    iMass::Int64                          # integer indicating what unit system to use
end

struct RefpropFLCache_base{M, K, PROP_TYPE, Cache_Type}
    params::Params_property_base{M, PROP_TYPE, Cache_Type}  # params used to generate the struct
    material::String                      # material formatted for refprop DLL usage
    PROP_IN::PROP_TYPE                          # empty struct indicating which pair
    PROP_OUT::NTuple{M, Int64}            # index of each property to get
    ALL_PROPS::NTuple{K, String}          # tuple of all properties
    output::Matrix{Float64}               # material properties

    N::Int64                              # total number of properties

    z::Vector{Float64}                    # composition vector, sum is 1, non-negative
    MW::Float64
    Output::Vector{Float64}           # ordered array of requested properties, except quality

    T::Base.RefValue{Float64}
    P::Base.RefValue{Float64}
    D::Base.RefValue{Float64}
    e::Base.RefValue{Float64}
    h::Base.RefValue{Float64}
    s::Base.RefValue{Float64}
    q::Base.RefValue{Float64}

    Dl::Base.RefValue{Float64}
    Dv::Base.RefValue{Float64}
    Cv::Base.RefValue{Float64}
    Cp::Base.RefValue{Float64}
    w::Base.RefValue{Float64}

    x::Vector{Float64}
    y::Vector{Float64}

    kr::Base.RefValue{Int32}
    kq::Base.RefValue{Int32}
    ierr::Base.RefValue{Int32}
    herr::Vector{UInt8}
end
##############################################################################

##############################################################################
get_tuple(::Val{S}) where S = (string(S)[1:1], string(S)[2:2])

function init_props_base(params::Params_property_base{M, P, Val{:SI}}) where {M, P}
    length(params.Material) == length(params.Composition) || error("material and composition must have same length")

    PROPS_IN = get_tuple(params.PROPS_IN)

    partial_material = join(string.(params.Material, "[", params.Composition, "]"), "&")
    material = params.Method*"::"*partial_material
    set_reference_stateS_ccall!(join(params.Material, "&"), params.ref_system)
    PROP_IN = map(get_full_prop_CP, PROPS_IN)
    PROP_OUT = map(get_full_prop_CP, params.PROPS_OUT)
    ALL_PROPS = (PROPS_IN..., params.PROPS_OUT...)
    nrows = length(params.PROPS_OUT) + 2
    output = Matrix{Float64}(undef, nrows, params.ncols)

    return CoolpropSICache_base(params, material, PROP_IN, PROP_OUT, ALL_PROPS, output)
end

function init_props_base(params::Params_property_base{M, P, Val{:AS}}) where {M, P}
    length(params.Material) == length(params.Composition) || error("material and composition must have same length")

    PROPS_IN = get_tuple(params.PROPS_IN)

    material = join(params.Material, "&")
    set_reference_stateS_ccall!(material, params.ref_system)
    handle = AbstractState_factory_ccall(params.Method, material)
    AbstractState_set_fractions_ccall!(handle, params.Composition)

    PROP_IN_MASS = map(get_full_prop_CP, PROPS_IN)
    PROP_IN_INPUT = PROP_IN_MASS[1]*PROP_IN_MASS[2]*"_INPUTS"
    PROP_IN = get_input_pair_index_ccall(get(PROPS_AS_SHORTHAND, PROP_IN_INPUT, PROP_IN_INPUT))
    PROP_OUT = map(get_full_prop_CP, params.PROPS_OUT)
    PROP_OUT = Tuple(get_param_index_ccall(k) for k in PROP_OUT)
    ALL_PROPS = (PROPS_IN..., params.PROPS_OUT...)
    nrows = length(params.PROPS_OUT) + 2
    output = Matrix{Float64}(undef, nrows, params.ncols)
    SWAP_PROP_IN = PROP_IN_INPUT != get(PROPS_AS_SHORTHAND, PROP_IN_INPUT, PROP_IN_INPUT)
    
    return CoolpropASCache_base(params, material, PROP_IN, PROP_OUT, ALL_PROPS, output, handle, SWAP_PROP_IN)
end

function init_props_base(params::Params_property_base{M, P, Val{:DL}}) where {M, P}
    length(params.Material) == length(params.Composition) || error("material and composition must have same length")

    PROPS_IN = get_tuple(params.PROPS_IN)

    PROP_IN = join(map(get_full_prop_RP, PROPS_IN), "")
    PROP_OUT = join(map(get_full_prop_RP, params.PROPS_OUT), ";")
    ALL_PROPS = (PROPS_IN..., params.PROPS_OUT...)   
    nrows = length(params.PROPS_OUT) + 2
    output = Matrix{Float64}(undef, nrows, params.ncols)

    # material string and composition
    material = join(params.Material, "|")
    z = zeros(Float64, 20)
    for i in eachindex(params.Composition)
        z[i] = params.Composition[i]
    end

    N = length(params.PROPS_OUT)

    # unit system integer
    SETREFdll_ccall!(params.ref_system, z)
    mass_base_si = GETENUMdll_ccall("MASS BASE SI")

    return RefpropDLCache_base(params, material, PROP_IN, PROP_OUT, ALL_PROPS, output, N, z, zeros(Float64, 200),
                               zeros(Float64, 20), zeros(Float64, 20), zeros(Float64, 20),
                               zeros(UInt8, 255), zeros(UInt8, 255), [0.0], [Cint(0)], mass_base_si)
end

function init_props_base(params::Params_property_base{M, P, Val{:FL}}) where {M, P}
    length(params.Material) == length(params.Composition) || error("material and composition must have same length")

    TARGET_PROPS = ("T", "P", "D", "Q", "H", "E", "S")
    PROPS_IN = get_tuple(params.PROPS_IN)

    PROP_IN = params.PROPS_IN
    PROP_OUT = Tuple(propidx(TARGET_PROPS, p) for p in params.PROPS_OUT)
    ALL_PROPS = (PROPS_IN..., params.PROPS_OUT...)
    
    nrows = length(params.PROPS_OUT) + 2
    output = Matrix{Float64}(undef, nrows, params.ncols)
    Output = Vector{Float64}(undef, length(TARGET_PROPS))

    material = join(params.Material .* ".FLD", "*")
    z = zeros(Float64, 20)
    for i in eachindex(params.Composition)
        z[i] = params.Composition[i]
    end

    N = length(params.PROPS_OUT)

    # setup material
    SETPATHdll_ccall!()
    SETFLUIDSdll_ccall!(material)
    SETREFdll_ccall!(params.ref_system, z)
    MW = WMOLdll_ccall(z)

    return RefpropFLCache_base(params, material, PROP_IN, PROP_OUT, ALL_PROPS, output, N, z, MW, Output, 
        Ref(0.0), Ref(0.0), Ref(0.0), Ref(0.0), Ref(0.0), Ref(0.0), Ref(0.0),
        Ref(0.0), Ref(0.0), Ref(0.0), Ref(0.0), Ref(0.0), zeros(Float64, 20), zeros(Float64, 20),
        Ref(Int32(0)), Ref(Int32(2)), Ref(Int32(0)), zeros(UInt8, 255))
end

##############################################################################

##############################################################################
"Get properties for a single point with coolprop using SI with ccall interface"
function get_prop_call!(cache::CoolpropSICache_base, P1::Float64, P2::Float64, Idx::Int64=1)
    cache.output[1, Idx] = P1
    cache.output[2, Idx] = P2
    @inbounds for i in eachindex(cache.PROP_OUT)
        cache.output[i+2, Idx] = PropsSI_ccall(cache.PROP_OUT[i], cache.PROP_IN[1],P1, cache.PROP_IN[2],P2, cache.material)
    end
end

"Get properties for a single point with coolprop using abstract state with ccall interface"
function get_prop_call!(cache::CoolpropASCache_base, P1::Float64, P2::Float64, Idx::Int64=1)
    if cache.SWAP_PROP_IN
        AbstractState_update_ccall!(cache, P2, P1)
    else
        AbstractState_update_ccall!(cache, P1, P2)
    end

    cache.output[1, Idx] = P1
    cache.output[2, Idx] = P2
    @inbounds for i in eachindex(cache.PROP_OUT)
        cache.output[i+2, Idx] = AbstractState_keyed_output_ccall(cache.handle, cache.PROP_OUT[i])
    end
end

"Get properties for a single point with refprop using DLL with ccall interface"
function get_prop_call!(cache::RefpropDLCache_base, P1::Float64, P2::Float64, Idx::Int64=1)
    REFPROPdll_ccall!(cache, cache.PROP_IN, cache.PROP_OUT, P1, P2)

    cache.output[1, Idx] = P1
    cache.output[2, Idx] = P2
    @inbounds for i in 1:cache.N
        cache.output[i+2, Idx] = cache.Output[i]
    end
end

"Get properties for a single point with refprop using FLSH with ccall interface"
function get_prop_call!(cache::RefpropFLCache_base, P1::Float64, P2::Float64, Idx::Int64=1)
    FLSHdll_ccall!(cache, cache.PROP_IN, P1, P2)

    cache.output[1, Idx] = P1
    cache.output[2, Idx] = P2
    @inbounds for i in 1:cache.N
        cache.output[i+2, Idx] = cache.Output[cache.PROP_OUT[i]]
    end
end
##############################################################################

##############################################################################
"Get properties for many points with either coolprop or refprop in various ways"
function get_props_call!(cache, IN_DATA::Matrix{Float64})
    @inbounds for i in axes(IN_DATA, 2)
        get_prop_call!(cache, IN_DATA[1,i], IN_DATA[2,i], i)
    end
end

function get_props_call!(cache, P1::AbstractRange{Float64}, P2::AbstractRange{Float64})
    @inbounds for i in eachindex(P2)
        @inbounds for j in eachindex(P1)
            get_prop_call!(cache, P1[j], P2[i], j + (i-1)*length(P1))
        end
    end
end
##############################################################################