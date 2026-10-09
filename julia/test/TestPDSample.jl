using JOA
using BenchmarkTools
using AllocCheck
using GLMakie
using JET

function plot_scatter(x::Matrix{Float64}, y::Matrix{Float64}, z::Matrix{Float64}, xLabel::String, yLabel::String, zLabel::String)
    fig = Figure()
    ax = Axis3(fig[1, 1],
        xlabel = xLabel,
        ylabel = yLabel,
        zlabel = zLabel
    )

    scatter!(ax, x, y, z;
        markersize = 10,
        color = :blue
    )

    display(GLMakie.Screen(), fig)
end

function plot_PD_scatter(props)
    figT = plot_scatter(props.P, props.D, props.T, "Pressure (kPa)", "Density (m^3/kg)", "Temperature (K)")
    figD = plot_scatter(props.P, props.D, props.h, "Pressure (kPa)", "Density (m^3/kg)", "Specific Enthalpy (kJ/kg)")
    figQ = plot_scatter(props.P, props.D, props.Q, "Pressure (kPa)", "Density (m^3/kg)", "Quality")
    figu = plot_scatter(props.P, props.D, props.u, "Pressure (kPa)", "Density (m^3/kg)", "Specific Internal Energy (kJ/kg)")
    figs = plot_scatter(props.P, props.D, props.s, "Pressure (kPa)", "Density (m^3/kg)", "Specific Entropy (kJ/(kg K))")
end

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
PROPS_IN = JOA.PD
PROPS_OUT = ("T", "S", "Q", "H", "E")

Pmin = 200000.0
Pmax = 5000000.0
Dmin = 50.0
Dmax = 600.0
sz = (40, 40)

# initialize parameters
paramsSI_crit = JOA.Params_property_crit(material, composition, RefSystem_CP, method, JOA.SI)
paramsAS_crit = JOA.Params_property_crit(material, composition, RefSystem_CP, method, JOA.AS)
paramsDL_crit = JOA.Params_property_crit(material, composition, RefSystem_RP, "", JOA.DL)
paramsFL_crit = JOA.Params_property_crit(material, composition, RefSystem_RP, "", JOA.FL)

paramsSI_base = JOA.Params_property_base(material, composition, RefSystem_CP, method, PROPS_IN, PROPS_OUT, sz[1]*sz[2], JOA.SI)
paramsAS_base = JOA.Params_property_base(material, composition, RefSystem_CP, method, PROPS_IN, PROPS_OUT, sz[1]*sz[2], JOA.AS)
paramsDL_base = JOA.Params_property_base(material, composition, RefSystem_RP, "", PROPS_IN, PROPS_OUT, sz[1]*sz[2], JOA.DL)
paramsFL_base = JOA.Params_property_base(material, composition, RefSystem_RP, "", PROPS_IN, PROPS_OUT, sz[1]*sz[2], JOA.FL)

params_sample = JOA.Params_property_samp(Pmin, Pmax, Dmin, Dmax, sz)

# initialize cache
cacheSI_sample = JOA.init_sample_props(params_sample, paramsSI_crit, paramsSI_base)
cacheAS_sample = JOA.init_sample_props(params_sample, paramsAS_crit, paramsAS_base)
cacheDL_sample = JOA.init_sample_props(params_sample, paramsDL_crit, paramsDL_base)
cacheFL_sample = JOA.init_sample_props(params_sample, paramsFL_crit, paramsFL_base)

# check that all code runs and outputs correctly
if test_type == 0
    @time JOA.get_GRID!(cacheSI_sample)
    @time JOA.get_GRID!(cacheAS_sample)
    @time JOA.get_GRID!(cacheDL_sample)
    @time JOA.get_GRID!(cacheFL_sample)

    @time JOA.make_GRID(PROPS_IN, PROPS_OUT, material, composition, RefSystem_CP, method, JOA.SI, Pmin, Pmax, Dmin, Dmax, sz)
    @time JOA.make_GRID(PROPS_IN, PROPS_OUT, material, composition, RefSystem_CP, method, JOA.AS, Pmin, Pmax, Dmin, Dmax, sz)
    @time JOA.make_GRID(PROPS_IN, PROPS_OUT, material, composition, RefSystem_RP, method, JOA.DL, Pmin, Pmax, Dmin, Dmax, sz)
    @time JOA.make_GRID(PROPS_IN, PROPS_OUT, material, composition, RefSystem_RP, method, JOA.FL, Pmin, Pmax, Dmin, Dmax, sz)

    plot_PD_scatter(cacheSI_sample.props)
    plot_PD_scatter(cacheAS_sample.props)
    plot_PD_scatter(cacheDL_sample.props)
    plot_PD_scatter(cacheFL_sample.props)

    PATHSI = JOA.getPropPath(material, composition, JOA.SI, PROPS_IN, sz)
    propsSI = JOA.load_struct(PATHSI, JOA.Props2D)

    PATHAS = JOA.getPropPath(material, composition, JOA.AS, PROPS_IN, sz)
    propsAS = JOA.load_struct(PATHAS, JOA.Props2D)

    PATHDL = JOA.getPropPath(material, composition, JOA.DL, PROPS_IN, sz)
    propsDL = JOA.load_struct(PATHDL, JOA.Props2D)
    
    PATHFL = JOA.getPropPath(material, composition, JOA.FL, PROPS_IN, sz)
    propsFL = JOA.load_struct(PATHFL, JOA.Props2D)

    plot_PD_scatter(propsSI)
    plot_PD_scatter(propsAS)
    plot_PD_scatter(propsDL)
    plot_PD_scatter(propsFL)

# check that all code is type stable
elseif test_type == 1
    @code_warntype JOA.get_GRID!(cacheSI_sample)
    @code_warntype JOA.get_GRID!(cacheAS_sample)
    @code_warntype JOA.get_GRID!(cacheDL_sample)
    @code_warntype JOA.get_GRID!(cacheFL_sample)

    @code_warntype JOA.make_GRID(PROPS_IN, PROPS_OUT, material, composition, RefSystem_CP, method, JOA.SI, Pmin, Pmax, Dmin, Dmax, sz)
    @code_warntype JOA.make_GRID(PROPS_IN, PROPS_OUT, material, composition, RefSystem_CP, method, JOA.AS, Pmin, Pmax, Dmin, Dmax, sz)
    @code_warntype JOA.make_GRID(PROPS_IN, PROPS_OUT, material, composition, RefSystem_RP, method, JOA.DL, Pmin, Pmax, Dmin, Dmax, sz)
    @code_warntype JOA.make_GRID(PROPS_IN, PROPS_OUT, material, composition, RefSystem_RP, method, JOA.FL, Pmin, Pmax, Dmin, Dmax, sz)

# check that no dynamic dispatch exists
elseif test_type == 2
    @report_opt JOA.get_GRID!(cacheSI_sample)
    @report_opt JOA.get_GRID!(cacheAS_sample)
    @report_opt JOA.get_GRID!(cacheDL_sample)
    @report_opt JOA.get_GRID!(cacheFL_sample)

    @report_opt JOA.make_GRID(PROPS_IN, PROPS_OUT, material, composition, RefSystem_CP, method, JOA.SI, Pmin, Pmax, Dmin, Dmax, sz)
    @report_opt JOA.make_GRID(PROPS_IN, PROPS_OUT, material, composition, RefSystem_CP, method, JOA.AS, Pmin, Pmax, Dmin, Dmax, sz)
    @report_opt JOA.make_GRID(PROPS_IN, PROPS_OUT, material, composition, RefSystem_RP, method, JOA.DL, Pmin, Pmax, Dmin, Dmax, sz)
    @report_opt JOA.make_GRID(PROPS_IN, PROPS_OUT, material, composition, RefSystem_RP, method, JOA.FL, Pmin, Pmax, Dmin, Dmax, sz)

# check that all code with ordinary inputs is 0 allocation
elseif test_type == 3
    @btime JOA.get_GRID!($cacheSI_sample)
    @btime JOA.get_GRID!($cacheAS_sample)
    @btime JOA.get_GRID!($cacheDL_sample)
    @btime JOA.get_GRID!($cacheFL_sample)

    @btime JOA.make_GRID(PROPS_IN, PROPS_OUT, material, composition, RefSystem_CP, method, JOA.SI, Pmin, Pmax, Dmin, Dmax, sz)
    @btime JOA.make_GRID(PROPS_IN, PROPS_OUT, material, composition, RefSystem_CP, method, JOA.AS, Pmin, Pmax, Dmin, Dmax, sz)
    @btime JOA.make_GRID(PROPS_IN, PROPS_OUT, material, composition, RefSystem_RP, method, JOA.DL, Pmin, Pmax, Dmin, Dmax, sz)
    @btime JOA.make_GRID(PROPS_IN, PROPS_OUT, material, composition, RefSystem_RP, method, JOA.FL, Pmin, Pmax, Dmin, Dmax, sz)

# check that all code is always 0 allocation
elseif test_type == 4
    errors = check_allocs(JOA.get_GRID!, (typeof(cacheSI_sample),))
    for err in errors
        println(err)
    end

    errors = check_allocs(JOA.get_GRID!, (typeof(cacheAS_sample),))
    for err in errors
        println(err)
    end

    errors = check_allocs(JOA.get_GRID!, (typeof(cacheDL_sample),))
    for err in errors
        println(err)
    end

    errors = check_allocs(JOA.get_GRID!, (typeof(cacheFL_sample),))
    for err in errors
        println(err)
    end

end