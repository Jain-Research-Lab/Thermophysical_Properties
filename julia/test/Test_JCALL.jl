using JOA
using BenchmarkTools
using AllocCheck

# test_type 0: @time : time your code, check if code runs (allocation can be non-zero)
# test_type 1: @code_warntype : check if code is type stable (no red text)
# test_type 2: @report_opt : check for dynamic dispatch (compilation does not allow dynamic dispatch)
# test_type 3: @btime : check allocation during runtime, valid for the supplied input values (allocation must be zero)
# test_type 4: @check_allocs: check if your code is zero-allocation, valid for supplied input types (no print output)

test_type = 0

# raw parameters
material = ["PROPANE"]
composition = [1.0]
RefSystem_CP = "IIR"
RefSystem_RP = "IIR"
method = "HEOS"
PROPS_IN = JOA.HP
PROPS_OUT = ("T", "S", "Q", "D")
N = 200

# initialize parameters
paramsSI_crit = JOA.Params_property_crit(material, composition, RefSystem_CP, method, JOA.SI)
paramsAS_crit = JOA.Params_property_crit(material, composition, RefSystem_CP, method, JOA.AS)
paramsDL_crit = JOA.Params_property_crit(material, composition, RefSystem_RP, "", JOA.DL)
paramsFL_crit = JOA.Params_property_crit(material, composition, RefSystem_RP, "", JOA.FL)

paramsSI_base = JOA.Params_property_base(material, composition, RefSystem_CP, method, PROPS_IN, PROPS_OUT, 1, JOA.SI)
paramsAS_base = JOA.Params_property_base(material, composition, RefSystem_CP, method, PROPS_IN, PROPS_OUT, 1, JOA.AS)
paramsDL_base = JOA.Params_property_base(material, composition, RefSystem_RP, "", PROPS_IN, PROPS_OUT, 1, JOA.DL)
paramsFL_base = JOA.Params_property_base(material, composition, RefSystem_RP, "", PROPS_IN, PROPS_OUT, 1, JOA.FL)

paramsSI_multiple = JOA.Params_property_base(material, composition, RefSystem_CP, method, PROPS_IN, PROPS_OUT, N, JOA.SI)
paramsAS_multiple = JOA.Params_property_base(material, composition, RefSystem_CP, method, PROPS_IN, PROPS_OUT, N, JOA.AS)
paramsDL_multiple = JOA.Params_property_base(material, composition, RefSystem_RP, "", PROPS_IN, PROPS_OUT, N, JOA.DL)
paramsFL_multiple = JOA.Params_property_base(material, composition, RefSystem_RP, "", PROPS_IN, PROPS_OUT, N, JOA.FL)

# initialize cache
cacheSI_crit = JOA.init_props_crit(paramsSI_crit)
cacheAS_crit = JOA.init_props_crit(paramsAS_crit)
cacheDL_crit = JOA.init_props_crit(paramsDL_crit)
cacheFL_crit = JOA.init_props_crit(paramsFL_crit)

cacheSI_base = JOA.init_props_base(paramsSI_base)
cacheAS_base = JOA.init_props_base(paramsAS_base)
cacheDL_base = JOA.init_props_base(paramsDL_base)
cacheFL_base = JOA.init_props_base(paramsFL_base)

cacheSI_multiple = JOA.init_props_base(paramsSI_multiple)
cacheAS_multiple = JOA.init_props_base(paramsAS_multiple)
cacheDL_multiple = JOA.init_props_base(paramsDL_multiple)
cacheFL_multiple = JOA.init_props_base(paramsFL_multiple)

# initialize data
DATA_base = [400000.0, 101325.0]
HV = collect(LinRange(300000, 400000, N))
PV = collect(LinRange(100000, 200000, N))
DATA_multiple = vcat(HV', PV')

# check that all code runs and outputs correctly
if test_type == -1
    @timed JOA.get_prop_call!(cacheSI_base, DATA_base[1], DATA_base[2], 1)
    println(cacheSI_base.output)

    @timed JOA.get_prop_call!(cacheFL_base, DATA_base[1], DATA_base[2], 1)
    println(cacheFL_base.output)

# check that the code runs and outputs correctly
elseif test_type == 0
    r = @timed JOA.get_crit_call!(cacheSI_crit)
    r = @timed JOA.get_crit_call!(cacheSI_crit)
    @time JOA.get_crit_call!(cacheSI_crit)
    println(cacheSI_crit.Pcrit)

    r = @timed JOA.get_crit_call!(cacheAS_crit)
    r = @timed JOA.get_crit_call!(cacheAS_crit)
    @time JOA.get_crit_call!(cacheAS_crit)
    println(cacheAS_crit.Pcrit)

    r = @timed JOA.get_crit_call!(cacheDL_crit)
    r = @timed JOA.get_crit_call!(cacheDL_crit)
    @time JOA.get_crit_call!(cacheDL_crit)
    println(cacheDL_crit.Pcrit)

    r = @timed JOA.get_crit_call!(cacheFL_crit)
    r = @timed JOA.get_crit_call!(cacheFL_crit)
    @time JOA.get_crit_call!(cacheFL_crit)
    println(cacheFL_crit.Pcrit)

    r = @timed JOA.get_prop_call!(cacheSI_base, DATA_base[1], DATA_base[2], 1)
    r = @timed JOA.get_prop_call!(cacheSI_base, DATA_base[1], DATA_base[2], 1)
    @time JOA.get_prop_call!(cacheSI_base, DATA_base[1], DATA_base[2], 1)
    println(cacheSI_base.output)

    r = @timed JOA.get_prop_call!(cacheAS_base, DATA_base[1], DATA_base[2], 1)
    r = @timed JOA.get_prop_call!(cacheAS_base, DATA_base[1], DATA_base[2], 1)
    @time JOA.get_prop_call!(cacheAS_base, DATA_base[1], DATA_base[2], 1)
    println(cacheAS_base.output)

    r = @timed JOA.get_prop_call!(cacheDL_base, DATA_base[1], DATA_base[2], 1)
    r = @timed JOA.get_prop_call!(cacheDL_base, DATA_base[1], DATA_base[2], 1)
    @time JOA.get_prop_call!(cacheDL_base, DATA_base[1], DATA_base[2], 1)
    println(cacheDL_base.output)

    r = @timed JOA.get_prop_call!(cacheFL_base, DATA_base[1], DATA_base[2], 1)
    r = @timed JOA.get_prop_call!(cacheFL_base, DATA_base[1], DATA_base[2], 1)
    @time JOA.get_prop_call!(cacheFL_base, DATA_base[1], DATA_base[2], 1)
    println(cacheFL_base.output)

    r = @timed JOA.get_props_call!(cacheSI_multiple, DATA_multiple)
    r = @timed JOA.get_props_call!(cacheSI_multiple, DATA_multiple)
    @time JOA.get_props_call!(cacheSI_multiple, DATA_multiple)
    println(cacheSI_multiple.output[:,1])

    r = @timed JOA.get_props_call!(cacheAS_multiple, DATA_multiple)
    r = @timed JOA.get_props_call!(cacheAS_multiple, DATA_multiple)
    @time JOA.get_props_call!(cacheAS_multiple, DATA_multiple)
    println(cacheAS_multiple.output[:,1])

    r = @timed JOA.get_props_call!(cacheDL_multiple, DATA_multiple)
    r = @timed JOA.get_props_call!(cacheDL_multiple, DATA_multiple)
    @time JOA.get_props_call!(cacheDL_multiple, DATA_multiple)
    println(cacheDL_multiple.output[:,1])

    r = @timed JOA.get_props_call!(cacheFL_multiple, DATA_multiple)
    r = @timed JOA.get_props_call!(cacheFL_multiple, DATA_multiple)
    @time JOA.get_props_call!(cacheFL_multiple, DATA_multiple)
    println(cacheFL_multiple.output[:,1])

# check that all code is type stable
elseif test_type == 1
    @code_warntype JOA.get_crit_call!(cacheSI_crit)
    @code_warntype JOA.get_crit_call!(cacheAS_crit)
    @code_warntype JOA.get_crit_call!(cacheDL_crit)
    @code_warntype JOA.get_crit_call!(cacheFL_crit)

    @code_warntype JOA.get_prop_call!(cacheSI_base, DATA_base[1], DATA_base[2], 1)
    @code_warntype JOA.get_prop_call!(cacheAS_base, DATA_base[1], DATA_base[2], 1)
    @code_warntype JOA.get_prop_call!(cacheDL_base, DATA_base[1], DATA_base[2], 1)
    @code_warntype JOA.get_prop_call!(cacheFL_base, DATA_base[1], DATA_base[2], 1)

    @code_warntype JOA.get_props_call!(cacheSI_multiple, DATA_multiple)
    @code_warntype JOA.get_props_call!(cacheAS_multiple, DATA_multiple)
    @code_warntype JOA.get_props_call!(cacheDL_multiple, DATA_multiple)
    @code_warntype JOA.get_props_call!(cacheFL_multiple, DATA_multiple)

# check that no dynamic dispatch exists
elseif test_type == 2
    @report_opt JOA.get_crit_call!(cacheSI_crit)
    @report_opt JOA.get_crit_call!(cacheAS_crit)
    @report_opt JOA.get_crit_call!(cacheDL_crit)
    @report_opt JOA.get_crit_call!(cacheFL_crit)

    @report_opt JOA.get_prop_call!(cacheSI_base, DATA_base[1], DATA_base[2], 1)
    @report_opt JOA.get_prop_call!(cacheAS_base, DATA_base[1], DATA_base[2], 1)
    @report_opt JOA.get_prop_call!(cacheDL_base, DATA_base[1], DATA_base[2], 1)
    @report_opt JOA.get_prop_call!(cacheFL_base, DATA_base[1], DATA_base[2], 1)

    @report_opt JOA.get_props_call!(cacheSI_multiple, DATA_multiple)
    @report_opt JOA.get_props_call!(cacheAS_multiple, DATA_multiple)
    @report_opt JOA.get_props_call!(cacheDL_multiple, DATA_multiple)
    @report_opt JOA.get_props_call!(cacheFL_multiple, DATA_multiple)

# check that all code with ordinary inputs is 0 allocation
elseif test_type == 3
    @btime JOA.get_crit_call!($cacheSI_crit)
    @btime JOA.get_crit_call!($cacheAS_crit)
    @btime JOA.get_crit_call!($cacheDL_crit)
    @btime JOA.get_crit_call!($cacheFL_crit)

    @btime JOA.get_prop_call!($cacheSI_base, $DATA_base[1], $DATA_base[2], 1)
    @btime JOA.get_prop_call!($cacheAS_base, $DATA_base[1], $DATA_base[2], 1)
    @btime JOA.get_prop_call!($cacheDL_base, $DATA_base[1], $DATA_base[2], 1)
    @btime JOA.get_prop_call!($cacheFL_base, $DATA_base[1], $DATA_base[2], 1)

    @btime JOA.get_props_call!($cacheSI_multiple, $DATA_multiple)
    @btime JOA.get_props_call!($cacheAS_multiple, $DATA_multiple)
    @btime JOA.get_props_call!($cacheDL_multiple, $DATA_multiple)
    @btime JOA.get_props_call!($cacheFL_multiple, $DATA_multiple)

# check for zero allocation
elseif test_type == 4
    errors = check_allocs(JOA.get_crit_call!, (typeof(cacheSI_crit),))
    for err in errors
        println(err)
    end

    errors = check_allocs(JOA.get_crit_call!, (typeof(cacheAS_crit),))
    for err in errors
        println(err)
    end

    errors = check_allocs(JOA.get_crit_call!, (typeof(cacheDL_crit),))
    for err in errors
        println(err)
    end

    errors = check_allocs(JOA.get_crit_call!, (typeof(cacheFL_crit),))
    for err in errors
        println(err)
    end

    errors = check_allocs(JOA.get_prop_call!, (typeof(cacheSI_base), Float64, Float64, Int64))
    for err in errors
        println(err)
    end

    errors = check_allocs(JOA.get_prop_call!, (typeof(cacheAS_base), Float64, Float64, Int64))
    for err in errors
        println(err)
    end

    errors = check_allocs(JOA.get_prop_call!, (typeof(cacheDL_base), Float64, Float64, Int64))
    for err in errors
        println(err)
    end

    errors = check_allocs(JOA.get_prop_call!, (typeof(cacheFL_base), Float64, Float64, Int64))
    for err in errors
        println(err)
    end

    errors = check_allocs(JOA.get_props_call!, (typeof(cacheSI_multiple), Matrix{Float64}))
    for err in errors
        println(err)
    end

    errors = check_allocs(JOA.get_props_call!, (typeof(cacheAS_multiple), Matrix{Float64}))
    for err in errors
        println(err)
    end

    errors = check_allocs(JOA.get_props_call!, (typeof(cacheDL_multiple), Matrix{Float64}))
    for err in errors
        println(err)
    end

    errors = check_allocs(JOA.get_props_call!, (typeof(cacheFL_multiple), Matrix{Float64}))
    for err in errors
        println(err)
    end

end