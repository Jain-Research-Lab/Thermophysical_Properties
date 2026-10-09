module TestMat

using JOA

# The @main macro serves as the entry point for JuliaC.jl executables
function @main(args::Vector{String})
    JOA.GEN_T_SATS()
    JOA.GEN_P_SATS()
    return 0
end

end

# app add JuliaC

# C:/Users/Inver/.julia/bin/juliac TestMat --output-exe hello --trim
# C:/Users/Inver/Documents/GitHub/graph_modeling_toolbox/JOA/test/build/TestMat/bin/TestMat.exe "TEST"

# C:/Users/dgulewic/.julia/bin/juliac TestMat --output-exe hello --trim
# C:/Users/dgulewic/Documents/GitHub/graph_modeling_toolbox/JOA/test/build/TestMat/bin/TestMat.exe "TEST"