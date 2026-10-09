##############################################################################
struct Params_property_samp
    P1min::Float64
    P1max::Float64
    P2min::Float64
    P2max::Float64
    sz::NTuple{2, Int64}
end

struct Props2D
    P::Matrix{Float64}
    T::Matrix{Float64}
    D::Matrix{Float64}
    Q::Matrix{Float64}
    h::Matrix{Float64}
    u::Matrix{Float64}
    s::Matrix{Float64}
end

struct Cache_property_samp{C1,C2}
    params::Params_property_samp
    cache_crit::C1
    cache_base::C2
    props::Props2D

    STR_PROPS::NTuple{7, String}
    IDX_PROPS::NTuple{7, Int64}
end

function init_sample_props(params_sample::Params_property_samp, params_crit, params_base)
    n = params_sample.sz[1]
    m = params_sample.sz[2]

    cache_crit = init_props_crit(params_crit)
    cache_base = init_props_base(params_base)
    props = Props2D(Matrix{Float64}(undef, n, m), Matrix{Float64}(undef, n, m), Matrix{Float64}(undef, n, m),
    Matrix{Float64}(undef, n, m), Matrix{Float64}(undef, n, m), Matrix{Float64}(undef, n, m), Matrix{Float64}(undef, n, m))

    STR_PROPS = ("P", "T", "D", "Q", "H", "E", "S")
    IDX_PROPS = Tuple(findfirst(==(p), cache_base.ALL_PROPS) for p in STR_PROPS)

    return Cache_property_samp(params_sample, cache_crit, cache_base, props, STR_PROPS, IDX_PROPS)
end
##############################################################################

##############################################################################
@inline function fill_transform!(f::F, dest::AbstractMatrix{Float64}, out::AbstractMatrix{Float64},
                                   idx::Int64, n::Int64, m::Int64) where {F}
    @inbounds for j in 1:m, i in 1:n
        dest[i, j] = f(out[idx, i + (j-1)*n])
    end
    return dest
end

function vec2mat!(cache::Cache_property_samp)
    n, m = cache.params.sz[1], cache.params.sz[2]
    out = cache.cache_base.output
    idx = cache.IDX_PROPS

    fill_transform!(x -> x * 0.001, cache.props.P, out, idx[1], n, m)
    fill_transform!(identity,       cache.props.T, out, idx[2], n, m)
    fill_transform!(identity,       cache.props.D, out, idx[3], n, m)
    fill_transform!(identity,       cache.props.Q, out, idx[4], n, m)
    fill_transform!(x -> x * 0.001, cache.props.h, out, idx[5], n, m)
    fill_transform!(x -> x * 0.001, cache.props.u, out, idx[6], n, m)
    fill_transform!(x -> x * 0.001, cache.props.s, out, idx[7], n, m)

    clampQ!(cache::Cache_property_samp)
end

function clampQ!(cache::Cache_property_samp)
    hcrit, Pcrit = cache.cache_crit.hcrit[]*0.001, cache.cache_crit.Pcrit[]*0.001
    h, P, Q = cache.props.h, cache.props.P, cache.props.Q
    n, m = cache.params.sz[1], cache.params.sz[2]

    @inbounds for j in 1:m, i in 1:n
        if P[i,j] > Pcrit
            if h[i, j] > hcrit
                Q[i, j] = 1.0
            elseif h[i, j] < hcrit
                Q[i, j] = 0.0
            else
                Q[i, j] = clamp(Q[i, j], 0.0, 1.0)
            end
        else
            Q[i, j] = clamp(Q[i, j], 0.0, 1.0)
        end
    end
end

fixQ!(cache::Cache_property_samp, jcall_type::Val{:HP}) = fixQif!(cache)
fixQ!(cache::Cache_property_samp, jcall_type::Val{:SP}) = fixQif!(cache)

fixQ!(cache::Cache_property_samp, jcall_type::Val{:PH}) = fixQir!(cache)
fixQ!(cache::Cache_property_samp, jcall_type::Val{:PS}) = fixQir!(cache)

fixQ!(cache::Cache_property_samp, jcall_type::Val{:DP}) = fixQdr!(cache)
fixQ!(cache::Cache_property_samp, jcall_type::Val{:PD}) = fixQdf!(cache)

function fixQif!(cache)
    Q = cache.props.Q
    n, m = cache.params.sz[1], cache.params.sz[2]

    # quality must be increasing - NEED TO HANDLE THIS SOMEHOW
    @inbounds for j in 1:m
        force = false
        for i in 1:n-1
            force |= Q[i, j] > Q[i+1, j]
            if force
                Q[i+1, j] = 1.0
            end
        end
    end
end

function fixQir!(cache)
    Q = cache.props.Q
    n, m = cache.params.sz[1], cache.params.sz[2]

    # quality must be increasing - NEED TO HANDLE THIS SOMEHOW
    @inbounds for j in 1:n
        force = false
        for i in 1:m-1
            force |= Q[j, i] > Q[j, i+1]
            if force
                Q[j, i+1] = 1.0
            end
        end
    end
end

function fixQdr!(cache)
    Q = cache.props.Q
    n, m = cache.params.sz[1], cache.params.sz[2]

    # quality must be decreasing as density increases (opposite of :HP)
    @inbounds for j in 1:m
        force = false
        for i in 1:n-1
            force |= Q[i, j] < Q[i+1, j]
            if force
                Q[i+1, j] = 0.0
            end
        end
    end
end

function fixQdf!(cache)
    Q = cache.props.Q
    n, m = cache.params.sz[1], cache.params.sz[2]

    @inbounds for j in 1:n
        force = false
        for i in m:-1:2
            force |= Q[j, i] > Q[j, i-1]
            if force
                Q[j, i-1] = 1.0
            end
        end
    end
end
##############################################################################

##############################################################################
function get_GRID!(cache::Cache_property_samp)
    P1 = range(cache.params.P1min, cache.params.P1max; length=cache.params.sz[1])
    P2 = range(cache.params.P2min, cache.params.P2max; length=cache.params.sz[2])
    get_props_call!(cache.cache_base, P1, P2)
    get_crit_call!(cache.cache_crit)
    vec2mat!(cache)
    fixQ!(cache, cache.cache_base.params.PROPS_IN)
end
##############################################################################

##############################################################################
function getPropPath(Material::Vector{String}, Composition::Vector{Float64}, PropJCall_Type::jcall_type, PROPS_IN::grid_type, sz::NTuple{2, Int64}) where {grid_type, jcall_type}
    FILE_NAME = String(typeof(PropJCall_Type).parameters[1]) * "_" * String(typeof(PROPS_IN).parameters[1]) * "_" * string(sz[1]) * "_" * string(sz[2]) *  ".matprop"
    FOLDER_NAME = join(string.(Material, "[", Composition, "]"), "&")
    return ENV["GBM_BASE"] * "/JOA/data/MaterialProperties/" * FOLDER_NAME * "/" * FILE_NAME
end

function setPropPath(Material::Vector{String}, Composition::Vector{Float64}, PropJCall_Type::jcall_type, PROPS_IN::grid_type, sz::NTuple{2, Int64}) where {grid_type, jcall_type}
    FILE_NAME = String(typeof(PropJCall_Type).parameters[1]) * "_" * String(typeof(PROPS_IN).parameters[1]) * "_" * string(sz[1]) * "_" * string(sz[2]) *  ".matprop"
    FOLDER_NAME = join(string.(Material, "[", Composition, "]"), "&")
    mkpath(ENV["GBM_BASE"] * "/JOA/data/MaterialProperties/" * FOLDER_NAME)
    return ENV["GBM_BASE"] * "/JOA/data/MaterialProperties/" * FOLDER_NAME * "/" * FILE_NAME
end

function init_GRID(PROPS_IN, PROPS_OUT, Material, Composition, RefSystem, Method, PropJCall_Type, P1min, P1max, P2min, P2max, sz)
    params_crit = Params_property_crit(Material, Composition, RefSystem, Method, PropJCall_Type)
    params_base = Params_property_base(Material, Composition, RefSystem, Method, PROPS_IN, PROPS_OUT, sz[1]*sz[2], PropJCall_Type)
    params_grid = Params_property_samp(P1min, P1max, P2min, P2max, sz) 
    return init_sample_props(params_grid, params_crit, params_base)
end

function make_GRID(PROPS_IN, PROPS_OUT, Material, Composition, RefSystem, Method, PropJCall_Type, P1min, P1max, P2min, P2max, sz)
    # Run function
    cache_grid = init_GRID(PROPS_IN, PROPS_OUT, Material, Composition, RefSystem, Method, PropJCall_Type, P1min, P1max, P2min, P2max, sz)
    get_GRID!(cache_grid)

    # save data
    PATH = setPropPath(Material, Composition, PropJCall_Type, PROPS_IN, sz)
    save_struct(PATH, cache_grid.props)
end

function get_GRIDS(params, PROPS_IN::grid_type, PROPS_OUT::NTuple{N, String}, sz::NTuple{2, Int64}, PropJCall_Type::jcall_type) where {N, grid_type, jcall_type}
    for i = 1:length(params.Material)
        cache_grid = init_GRID(PROPS_IN, PROPS_OUT, params.Material[i], params.Composition[i], params.RefSystem[i],
        params.Method[i], PropJCall_Type, params.P1min[i], params.P1max[i], params.P2min[i], params.P2max[i], sz)

        get_GRID!(cache_grid)

        # save data
        PATH = setPropPath(params.Material[i], params.Composition[i], PropJCall_Type, PROPS_IN, sz)
        save_struct(PATH, cache_grid.props)
    end
end
##############################################################################