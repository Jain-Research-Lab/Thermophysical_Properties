using JOA
using BenchmarkTools
using AllocCheck
using JET
using GLMakie

##############################################################################
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

function plot_PH_scatter(props)
    figT = plot_scatter(props.P, props.h, props.T, "Pressure (kPa)", "Enthalpy (kJ/kg)", "Temperature (K)")
    figD = plot_scatter(props.P, props.h, props.D, "Pressure (kPa)", "Enthalpy (kJ/kg)", "Density (kg/m^3)")
    figQ = plot_scatter(props.P, props.h, props.Q, "Pressure (kPa)", "Enthalpy (kJ/kg)", "Quality")
    figu = plot_scatter(props.P, props.h, props.u, "Pressure (kPa)", "Enthalpy (kJ/kg)", "Specific Internal Energy (kJ/kg)")
    figs = plot_scatter(props.P, props.h, props.s, "Pressure (kPa)", "Enthalpy (kJ/kg)", "Specific Entropy (kJ/(kg K))")
end

function plot_PD_scatter(props)
    figT = plot_scatter(props.P, props.D, props.T, "Pressure (kPa)", "Density (m^3/kg)", "Temperature (K)")
    figD = plot_scatter(props.P, props.D, props.h, "Pressure (kPa)", "Density (m^3/kg)", "Specific Enthalpy (kJ/kg)")
    figQ = plot_scatter(props.P, props.D, props.Q, "Pressure (kPa)", "Density (m^3/kg)", "Quality")
    figu = plot_scatter(props.P, props.D, props.u, "Pressure (kPa)", "Density (m^3/kg)", "Specific Internal Energy (kJ/kg)")
    figs = plot_scatter(props.P, props.D, props.s, "Pressure (kPa)", "Density (m^3/kg)", "Specific Entropy (kJ/(kg K))")
end

function plot_PS_scatter(props)
    figT = plot_scatter(props.P, props.s, props.T, "Pressure (kPa)", "Specific Entropy (kJ/kg K)", "Temperature (K)")
    figD = plot_scatter(props.P, props.s, props.D, "Pressure (kPa)", "Specific Entropy (kJ/kg K)", "Density (m^3/kg)")
    figQ = plot_scatter(props.P, props.s, props.Q, "Pressure (kPa)", "Specific Entropy (kJ/kg K)", "Quality")
    figu = plot_scatter(props.P, props.s, props.u, "Pressure (kPa)", "Specific Entropy (kJ/kg K)", "Specific Internal Energy (kJ/kg)")
    figs = plot_scatter(props.P, props.s, props.h, "Pressure (kPa)", "Specific Entropy (kJ/kg K)", "Specific Enthalpy (kJ/kg)")
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
    PROPS_IN = JOA.PS
    sz = (400, 400)
    params = JOA.ParamsFL_PS_GRID
    i = 1

    PATH = JOA.getPropPath(params.Material[i], params.Composition[i], JOA.FL, PROPS_IN, sz)
    props = JOA.load_struct(PATH, JOA.Props2D)

    print(props.P[1,1])
    print(props.P[1,end])
    print(props.P[end,1])
    print(props.P[end,end])

    print(props.s[1,1])
    print(props.s[1,end])
    print(props.s[end,1])
    print(props.s[end,end])

    plot_PH_scatter(props)
    plot_PD_scatter(props)
    plot_PS_scatter(props)

# check that all code runs and outputs correctly
elseif test_type == 0
    @time JOA.GEN_PH_GRIDS()
    @time JOA.GEN_PD_GRIDS()
    @time JOA.GEN_PS_GRIDS()
    
# check that all code is type stable
elseif test_type == 1
    @code_warntype JOA.GEN_PH_GRIDS()
    @code_warntype JOA.GEN_PD_GRIDS()
    @code_warntype JOA.GEN_PS_GRIDS()

# check that no dynamic dispatch exists
elseif test_type == 2
    @report_opt JOA.GEN_PH_GRIDS()
    @report_opt JOA.GEN_PD_GRIDS()
    @report_opt JOA.GEN_PS_GRIDS()

# check that all code with ordinary inputs is 0 allocation
elseif test_type == 3
    @btime JOA.PH_TEST()
    @btime JOA.PD_TEST()
    @btime JOA.PS_TEST()

# check that all code is always 0 allocation
elseif test_type == 4
    errors = check_allocs(JOA.GEN_PH_GRIDS, ())
    for err in errors
        println(err)
    end

    errors = check_allocs(JOA.GEN_PD_GRIDS, ())
    for err in errors
        println(err)
    end

    errors = check_allocs(JOA.GEN_PS_GRIDS, ())
    for err in errors
        println(err)
    end

end