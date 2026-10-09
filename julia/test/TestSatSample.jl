using JOA
using BenchmarkTools
using AllocCheck
using JET
using GLMakie

##############################################################################
function plot_scatter(x::Vector{Float64}, y::Vector{Float64}, xLabel::String, yLabel::String)
    fig = Figure()
    ax = Axis(fig[1, 1],
        xlabel = xLabel,
        ylabel = yLabel
    )

    scatter!(ax, x, y;
        markersize = 10,
        color = :blue
    )

    display(GLMakie.Screen(), fig)
end

function plot_P_scatter(props)
    figT = plot_scatter([props.hl; props.hg], [props.P; props.P], "Enthalpy (kJ/kg)", "Pressure (kPa)")
    # figD = plot_scatter(props.P, props.h, props.D, "Pressure (kPa)", "Enthalpy (kJ/kg)", "Density (kg/m^3)")
    # figQ = plot_scatter(props.P, props.h, props.Q, "Pressure (kPa)", "Enthalpy (kJ/kg)", "Quality")
    # figu = plot_scatter(props.P, props.h, props.u, "Pressure (kPa)", "Enthalpy (kJ/kg)", "Specific Internal Energy (kJ/kg)")
    # figs = plot_scatter(props.P, props.h, props.s, "Pressure (kPa)", "Enthalpy (kJ/kg)", "Specific Entropy (kJ/(kg K))")
end

function plot_T_scatter(props)
    figT = plot_scatter([props.hl; props.hg], [props.P; props.P], "Enthalpy (kJ/kg)", "Pressure (kPa)")
    figD = plot_scatter([props.sl; props.sg], [props.P; props.P], "Entropy (kJ/kgK)", "Pressure (kPa)")
    # figQ = plot_scatter(props.P, props.D, props.Q, "Pressure (kPa)", "Density (m^3/kg)", "Quality")
    # figu = plot_scatter(props.P, props.D, props.u, "Pressure (kPa)", "Density (m^3/kg)", "Specific Internal Energy (kJ/kg)")
    # figs = plot_scatter(props.P, props.D, props.s, "Pressure (kPa)", "Density (m^3/kg)", "Specific Entropy (kJ/(kg K))")
end
##############################################################################

# test_type 0: @time : time your code, check if code runs (allocation can be non-zero)
# test_type 1: @code_warntype : check if code is type stable (no red text)
# test_type 2: @report_opt : check for dynamic dispatch (compilation does not allow dynamic dispatch)
# test_type 3: @btime : check allocation during runtime, valid for the supplied input values (allocation must be zero)
# test_type 4: @check_allocs: check if your code is zero-allocation, valid for supplied input types (no print output)

test_type = -1

# check sampling results
if test_type == -1
    PROPS_IN = JOA.QP
    sz = 400
    params = JOA.ParamsFL_SAT_P_GRID
    i = 1
    PATH = JOA.getPropPath(params.Material[i], params.Composition[i], JOA.FL, PROPS_IN, sz)
    props = JOA.load_struct(PATH, JOA.PropsSat)
    plot_P_scatter(props)

    PROPS_IN = JOA.QT
    sz = 400
    params = JOA.ParamsFL_SAT_T_GRID
    i = 1
    PATH = JOA.getPropPath(params.Material[i], params.Composition[i], JOA.FL, PROPS_IN, sz)
    props = JOA.load_struct(PATH, JOA.PropsSat)
    plot_T_scatter(props)

# check that all code runs and outputs correctly
elseif test_type == 0
    @time JOA.GEN_T_SATS()
    @time JOA.GEN_P_SATS()
    
# check that all code is type stable
elseif test_type == 1
    @code_warntype JOA.GEN_T_SATS()
    @code_warntype JOA.GEN_P_SATS()

# check that no dynamic dispatch exists
elseif test_type == 2
    @report_opt JOA.GEN_T_SATS()
    @report_opt JOA.GEN_P_SATS()

# check that all code with ordinary inputs is 0 allocation
elseif test_type == 3
    @btime JOA.PH_TEST()
    @btime JOA.PD_TEST()

# check that all code is always 0 allocation
elseif test_type == 4
    errors = check_allocs(JOA.GEN_T_SATS, ())
    for err in errors
        println(err)
    end

    errors = check_allocs(JOA.GEN_P_SATS, ())
    for err in errors
        println(err)
    end

end