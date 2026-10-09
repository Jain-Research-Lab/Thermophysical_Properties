module JOA

# core library imports
using CoolProp
using Libdl
using StaticArrays

# Include files in explicit dependency order


# save and load
include("IO/SaveLoad.jl")

# material property functions
include("ModularFunctions/MaterialProperties/sampling/PropertyCCall.jl")
include("ModularFunctions/MaterialProperties/sampling/PropertyJCall.jl")
include("ModularFunctions/MaterialProperties/sampling/SampleGRID.jl")
include("ModularFunctions/MaterialProperties/sampling/SampleSAT.jl")
include("ModularFunctions/MaterialProperties/sampling/SampleAB.jl")

# build system
include("ModularFunctions/MaterialProperties/config/AllPropConfig.jl")
include("ModularFunctions/MaterialProperties/config/AllSatConfig.jl")
include("ModularFunctions/MaterialProperties/config/AllPropConfig_Extra.jl")

# include("ModularFunctions/MaterialProperties/config/TableConfigTemplate.jl")

# for file in sort(readdir(joinpath(@__DIR__, "ModularFunctions/MaterialProperties/config")))
#     if endswith(file, ".jl") && ("TableConfigTemplate" != splitext(file)[1])
#         include(joinpath(@__DIR__, "ModularFunctions/MaterialProperties/config", file))
#     end
# end

# include("ModularFunctions/MaterialProperties/ImplementFunc/SampleTemplate.jl")

end