using JOA
using BenchmarkTools
using AllocCheck

function print_diagnostics(PATH, func, func_args, func_types)
    open(PATH, "w") do io
        redirect_stdout(io) do
            println("=== @timed ===")
            a1 = @timed func(func_args...)
            show(io, a1); println(io)

            println("\n=== @code_warntype ===")
            @code_warntype func(func_args...)

            println("\n=== @benchmarkable ===")
            trial = Base.invokelatest(run, @benchmarkable $(func)($(func_args)...))
            show(io, MIME"text/plain"(), trial)

            println("\n\n=== check_allocs ===")
            a4 = check_allocs(func, func_types)
            show(io, a4); println(io)

            println("\n=== @code_llvm ===")
            @code_llvm debuginfo=:none optimize=true func(func_args...)

            println("\n=== code_typed ===")
            a6 = code_typed(func, func_types)
            show(io, a6); println(io)
        end
    end
end

# @time : time your code, check if code runs (allocation can be non-zero)
# @code_warntype : check if code is type stable (no red text)
# @benchmarkable : check allocation during runtime, valid for the supplied input values (allocation must be zero)
# check_allocs: check if your code is zero-allocation, valid for supplied input types (no print output)
# @code_llvm: for code optimization, especially if you want to use AI to optimize for you
# code_typed: for another look at type stability partocularily for compilation

# raw parameters
material = ["PROPANE"]
composition = [1.0]
method = "HEOS"
PROPS_IN = ("H", "P")
PROPS_OUT = ("T", "S", "Q", "D")
PROPS_OUT_GRID = ("T", "D", "Q", "S", "E") # sum of PROPS_IN and PROPS_OUT for grid is always these 7
N = 200

Hmin = 95000.0
Hmax = 800000.0
Pmin = 100000.0
Pmax = 5000000.0
sz = (40, 40)

# initialize parameters
paramsSI_crit = JOA.CoolpropSICache_params_crit(material, composition, method)
paramsAS_crit = JOA.CoolpropASCache_params_crit(material, composition, method)
paramsDL_crit = JOA.RefpropDLCache_params_crit(material, composition)

paramsSI_single = JOA.CoolpropSICache_params_single(material, composition, method, PROPS_IN, PROPS_OUT, 1)
paramsAS_single = JOA.CoolpropASCache_params_single(material, composition, method, PROPS_IN, PROPS_OUT, 1)
paramsDL_single = JOA.RefpropDLCache_params_single(material, composition, PROPS_IN, PROPS_OUT, 1)

paramsSI_multiple = JOA.CoolpropSICache_params_single(material, composition, method, PROPS_IN, PROPS_OUT, N)
paramsAS_multiple = JOA.CoolpropASCache_params_single(material, composition, method, PROPS_IN, PROPS_OUT, N)
paramsDL_multiple = JOA.RefpropDLCache_params_single(material, composition, PROPS_IN, PROPS_OUT, N)

paramsSI_grid = JOA.CoolpropSICache_params_single(material, composition, method, PROPS_IN, PROPS_OUT_GRID, sz[1]*sz[2])
paramsAS_grid = JOA.CoolpropASCache_params_single(material, composition, method, PROPS_IN, PROPS_OUT_GRID, sz[1]*sz[2])
paramsDL_grid = JOA.RefpropDLCache_params_single(material, composition, PROPS_IN, PROPS_OUT_GRID, sz[1]*sz[2])

# initialize cache
cacheSI_crit = JOA.init_props_crit(paramsSI_crit)
cacheAS_crit = JOA.init_props_crit(paramsAS_crit)
cacheDL_crit = JOA.init_props_crit(paramsDL_crit)

cacheSI_single = JOA.init_props_single(paramsSI_single)
cacheAS_single = JOA.init_props_single(paramsAS_single)
cacheDL_single = JOA.init_props_single(paramsDL_single)

cacheSI_multiple = JOA.init_props_single(paramsSI_multiple)
cacheAS_multiple = JOA.init_props_single(paramsAS_multiple)
cacheDL_multiple = JOA.init_props_single(paramsDL_multiple)

params_sample = JOA.sampleCache_params(Hmin, Hmax, Pmin, Pmax, sz)

cacheSI_sample = JOA.init_sample_props(params_sample, paramsSI_crit, paramsSI_grid)
cacheAS_sample = JOA.init_sample_props(params_sample, paramsAS_crit, paramsAS_grid)
cacheDL_sample = JOA.init_sample_props(params_sample, paramsDL_crit, paramsDL_grid)

# initialize data
DATA_single = [400000.0, 101325.0]
HV = collect(LinRange(300000, 400000, N))
PV = collect(LinRange(100000, 200000, N))
DATA_multiple = vcat(HV', PV')

# thorough diagonostics gamit
PATH = ENV["GBM_BASE"] * "/JOA/examples/PropertyFunctions/results/SI_HP.txt"
print_diagnostics(PATH, JOA.get_GRID, (cacheSI_sample,), (typeof(cacheSI_sample),))

PATH = ENV["GBM_BASE"] * "/JOA/examples/PropertyFunctions/results/AS_HP.txt"
print_diagnostics(PATH, JOA.get_GRID, (cacheAS_sample,), (typeof(cacheAS_sample),))

PATH = ENV["GBM_BASE"] * "/JOA/examples/PropertyFunctions/results/DL_HP.txt"
print_diagnostics(PATH, JOA.get_GRID, (cacheDL_sample,), (typeof(cacheDL_sample),))

PATH = ENV["GBM_BASE"] * "/JOA/examples/PropertyFunctions/results/SI_crit.txt"
print_diagnostics(PATH, JOA.get_crit_call!, (cacheSI_crit,), (JOA.CoolpropSICache_crit,))

PATH = ENV["GBM_BASE"] * "/JOA/examples/PropertyFunctions/results/AS_crit.txt"
print_diagnostics(PATH, JOA.get_crit_call!, (cacheAS_crit,), (JOA.CoolpropASCache_crit,))

PATH = ENV["GBM_BASE"] * "/JOA/examples/PropertyFunctions/results/DL_crit.txt"
print_diagnostics(PATH, JOA.get_crit_call!, (cacheDL_crit,), (JOA.RefpropDLCache_crit,))

PATH = ENV["GBM_BASE"] * "/JOA/examples/PropertyFunctions/results/SI_single.txt"
print_diagnostics(PATH, JOA.get_prop_call!, (cacheSI_single,DATA_single[1],DATA_single[2],1), (typeof(cacheSI_single),Float64,Float64,Int64))

PATH = ENV["GBM_BASE"] * "/JOA/examples/PropertyFunctions/results/AS_single.txt"
print_diagnostics(PATH, JOA.get_prop_call!, (cacheAS_single,DATA_single[1],DATA_single[2],1), (typeof(cacheAS_single),Float64,Float64,Int))

PATH = ENV["GBM_BASE"] * "/JOA/examples/PropertyFunctions/results/DL_single.txt"
print_diagnostics(PATH, JOA.get_prop_call!, (cacheDL_single,DATA_single[1],DATA_single[2],1), (typeof(cacheDL_single),Float64,Float64,Int64))

PATH = ENV["GBM_BASE"] * "/JOA/examples/PropertyFunctions/results/SI_multiple.txt"
print_diagnostics(PATH, JOA.get_props_call!, (cacheSI_multiple,DATA_multiple), (typeof(cacheSI_multiple),Matrix{Float64}))

PATH = ENV["GBM_BASE"] * "/JOA/examples/PropertyFunctions/results/AS_multiple.txt"
print_diagnostics(PATH, JOA.get_props_call!, (cacheAS_multiple,DATA_multiple), (typeof(cacheAS_multiple),Matrix{Float64}))

PATH = ENV["GBM_BASE"] * "/JOA/examples/PropertyFunctions/results/DL_multiple.txt"
print_diagnostics(PATH, JOA.get_props_call!, (cacheDL_multiple,DATA_multiple), (typeof(cacheDL_multiple),Matrix{Float64}))