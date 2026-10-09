##############################################################################
struct Params_property_sat
    P1min::Float64
    P1max::Float64
    sz::Int64
end

struct PropsSat
    P::Vector{Float64}
    T::Vector{Float64}

    Dl::Vector{Float64}
    hl::Vector{Float64}
    ul::Vector{Float64}
    sl::Vector{Float64}

    Dg::Vector{Float64}
    hg::Vector{Float64}
    ug::Vector{Float64}
    sg::Vector{Float64}
end

struct Cache_property_sat{C1,C2,C3}
    params::Params_property_sat
    cache_crit::C1
    cache_satl::C2
    cache_satg::C3
    props::PropsSat

    STR_PROPS::NTuple{7, String}
    IDX_PROPS::NTuple{7, Int64}
end

function init_sat_props(params_sat::Params_property_sat, params_crit, params_satl, params_satg)
    n = params_sat.sz

    cache_crit = init_props_crit(params_crit)
    cache_satl = init_props_base(params_satl)
    cache_satg = init_props_base(params_satg)

    props = PropsSat(Vector{Float64}(undef, n), Vector{Float64}(undef, n), 
    Vector{Float64}(undef, n), Vector{Float64}(undef, n), Vector{Float64}(undef, n), Vector{Float64}(undef, n),
    Vector{Float64}(undef, n), Vector{Float64}(undef, n), Vector{Float64}(undef, n), Vector{Float64}(undef, n))

    STR_PROPS = ("P", "T", "D", "Q", "H", "E", "S")
    IDX_PROPS = Tuple(findfirst(==(p), cache_satl.ALL_PROPS) for p in STR_PROPS)

    return Cache_property_sat(params_sat, cache_crit, cache_satl, cache_satg, props, STR_PROPS, IDX_PROPS)
end
##############################################################################

##############################################################################
@inline function fill_transform!(f::F, dest::AbstractVector{Float64}, out::AbstractMatrix{Float64},
                                   idx::Int64, n::Int64) where {F}
    @inbounds for i in 1:n
        dest[i] = f(out[idx, i])
    end
    return dest
end

function vec2mat!(cache::Cache_property_sat)
    n = cache.params.sz
    outl = cache.cache_satl.output
    outg = cache.cache_satg.output
    idx = cache.IDX_PROPS

    fill_transform!(x -> x * 0.001, cache.props.P, outl, idx[1], n)
    fill_transform!(identity,       cache.props.T, outl, idx[2], n)

    fill_transform!(identity,       cache.props.Dl, outl, idx[3], n)
    fill_transform!(x -> x * 0.001, cache.props.hl, outl, idx[5], n)
    fill_transform!(x -> x * 0.001, cache.props.ul, outl, idx[6], n)
    fill_transform!(x -> x * 0.001, cache.props.sl, outl, idx[7], n)

    fill_transform!(identity,       cache.props.Dg, outg, idx[3], n)
    fill_transform!(x -> x * 0.001, cache.props.hg, outg, idx[5], n)
    fill_transform!(x -> x * 0.001, cache.props.ug, outg, idx[6], n)
    fill_transform!(x -> x * 0.001, cache.props.sg, outg, idx[7], n)
end
##############################################################################

##############################################################################
function get_SAT!(cache::Cache_property_sat)
    get_crit_call!(cache.cache_crit)

    if cache.cache_satg.ALL_PROPS[1] == "P" || cache.cache_satg.ALL_PROPS[2] == "P"
        P1max = cache.cache_crit.Pcrit[]
    elseif cache.cache_satg.ALL_PROPS[1] == "T" || cache.cache_satg.ALL_PROPS[2] == "T"
        P1max = cache.cache_crit.Tcrit[]
    end

    Pl = collect(range(cache.params.P1min, P1max; length=cache.params.sz))
    Pg = collect(range(cache.params.P1min, P1max; length=cache.params.sz))
    Ql = fill(0.0, cache.params.sz)
    Qg = fill(1.0, cache.params.sz)

    get_props_call!(cache.cache_satl, [Ql'; Pl'])
    get_props_call!(cache.cache_satg, [Qg'; Pg'])
    
    vec2mat!(cache)
end
##############################################################################

##############################################################################
function getPropPath(Material::Vector{String}, Composition::Vector{Float64}, PropJCall_Type::jcall_type, PROPS_IN::grid_type, sz::Int64) where {grid_type, jcall_type}
    FILE_NAME = String(typeof(PropJCall_Type).parameters[1]) * "_" * String(typeof(PROPS_IN).parameters[1]) * "_" * string(sz) *  ".matprop"
    FOLDER_NAME = join(string.(Material, "[", Composition, "]"), "&")
    return ENV["GBM_BASE"] * "/JOA/data/MaterialProperties/" * FOLDER_NAME * "/" * FILE_NAME
end

function setPropPath(Material::Vector{String}, Composition::Vector{Float64}, PropJCall_Type::jcall_type, PROPS_IN::grid_type, sz::Int64) where {grid_type, jcall_type}
    FILE_NAME = String(typeof(PropJCall_Type).parameters[1]) * "_" * String(typeof(PROPS_IN).parameters[1]) * "_" * string(sz) *  ".matprop"
    FOLDER_NAME = join(string.(Material, "[", Composition, "]"), "&")
    mkpath(ENV["GBM_BASE"] * "/JOA/data/MaterialProperties/" * FOLDER_NAME)
    return ENV["GBM_BASE"] * "/JOA/data/MaterialProperties/" * FOLDER_NAME * "/" * FILE_NAME
end

function init_SAT(PROPS_IN, PROPS_OUT, Material, Composition, RefSystem, Method, PropJCall_Type, P1min, P1max, sz)
    params_crit = Params_property_crit(Material, Composition, RefSystem, Method, PropJCall_Type)
    params_satl = Params_property_base(Material, Composition, RefSystem, Method, PROPS_IN, PROPS_OUT, sz, PropJCall_Type)
    params_satg = Params_property_base(Material, Composition, RefSystem, Method, PROPS_IN, PROPS_OUT, sz, PropJCall_Type)
    params_sat = Params_property_sat(P1min, P1max, sz) 
    return init_sat_props(params_sat, params_crit, params_satl, params_satg)
end

function make_SAT(PROPS_IN, PROPS_OUT, Material, Composition, RefSystem, Method, PropJCall_Type, P1min, P1max, sz)
    # Run function
    cache_sat = init_SAT(PROPS_IN, PROPS_OUT, Material, Composition, RefSystem, Method, PropJCall_Type, P1min, P1max, sz)
    get_SAT!(cache_sat)

    # save data
    PATH = setPropPath(Material, Composition, PropJCall_Type, PROPS_IN, sz)
    save_struct(PATH, cache_sat.props)
end

function get_SATS(params, PROPS_IN::grid_type, PROPS_OUT::NTuple{N, String}, sz::Int64, PropJCall_Type::jcall_type) where {N, grid_type, jcall_type}
    for i = 1:length(params.Material)
        cache_sat = init_SAT(PROPS_IN, PROPS_OUT, params.Material[i], params.Composition[i], params.RefSystem[i],
        params.Method[i], PropJCall_Type, params.P1min[i], params.P1max[i], sz)

        get_SAT!(cache_sat)

        # save data
        PATH = setPropPath(params.Material[i], params.Composition[i], PropJCall_Type, PROPS_IN, sz)
        save_struct(PATH, cache_sat.props)
    end
end
##############################################################################