##############################################################################
# Coolprop SI
##############################################################################
function PropsSI_ccall(out::String, prop1::String, p1::Float64, prop2::String, p2::Float64, material::String)
    return ccall((:PropsSI, "libcoolprop"), Cdouble,
                 (Ptr{UInt8}, Ptr{UInt8}, Cdouble, Ptr{UInt8}, Cdouble, Ptr{UInt8}),
                 pointer(out), pointer(prop1), p1, pointer(prop2), p2, pointer(material))
end

##############################################################################
# Coolprop AS
##############################################################################
function set_reference_stateS_ccall!(fluid::String, reference_state::String)
    result = ccall((:set_reference_stateS, "libcoolprop"), Int32,
        (Cstring, Cstring),
        fluid, reference_state)
    result != 1 && error("set_reference_stateS failed for fluid \"$fluid\", state \"$reference_state\"")
end

function AbstractState_factory_ccall(backend::String, fluids::String)::Int32
    errcode = Ref{Int32}(0)
    message_buffer = zeros(UInt8, 250)
    handle = ccall((:AbstractState_factory, "libcoolprop"), Int32,
                    (Cstring, Cstring, Ref{Int32}, Ptr{UInt8}, Int32),
                    backend, fluids, errcode, message_buffer, length(message_buffer))
    errcode[] != 0 && error("CoolProp AbstractState_factory error: " * unsafe_string(pointer(message_buffer)))
    return handle
end

function AbstractState_set_fractions_ccall!(handle::Int32, fractions::Vector{Float64})
    errcode = Ref{Int32}(0)
    message_buffer = zeros(UInt8, 250)
    ccall((:AbstractState_set_fractions, "libcoolprop"), Cvoid,
          (Int32, Ptr{Float64}, Int32, Ref{Int32}, Ptr{UInt8}, Int32),
          handle, fractions, length(fractions), errcode, message_buffer, length(message_buffer))
    errcode[] != 0 && error("CoolProp AbstractState_set_fractions error: " * unsafe_string(pointer(message_buffer)))
    return nothing
end

function get_input_pair_index_ccall(pair::String)::Int32
    return ccall((:get_input_pair_index, "libcoolprop"), Int32, (Cstring,), pair)
end

function get_param_index_ccall(param::String)::Int32
    return ccall((:get_param_index, "libcoolprop"), Int32, (Cstring,), param)
end

function AbstractState_update_ccall!(cache, P1::Float64, P2::Float64)
    ccall((:AbstractState_update, "libcoolprop"), Cvoid, 
            (Int32, Int32, Float64, Float64, Ref{Int32}, Ptr{Cchar}, Int32), 
            cache.handle, cache.PROP_IN, P1, P2, Ref{Int32}(0), C_NULL, 0)
end

function AbstractState_keyed_output_ccall(handle::Clong, i_spec::Clong)
    err = Ref{Int32}(0)
    
    return ccall((:AbstractState_keyed_output, "libcoolprop"), Float64, 
                  (Int32, Int32, Ref{Int32}, Ptr{Cchar}, Int32), 
                  handle, i_spec, err, C_NULL, 0)
end

##############################################################################
# Refprop DL
##############################################################################
function find_refprop_path(file_flag::Bool=true)
    # Check if Julia is running in 64-bit or 32-bit to select the correct DLL
    dll_name = Sys.WORD_SIZE == 64 ? "REFPRP64.dll" : "REFPROP.dll"
    
    # 1. Check the official NIST environment variable
    if haskey(ENV, "RPPREFIX")
        candidate = joinpath(ENV["RPPREFIX"], dll_name)
        if file_flag
            isfile(candidate) && return candidate
        else
            isfile(candidate) && return ENV["RPPREFIX"]
        end
    end

    # 2. Fallback to common Windows installation directories
    common_paths = [
        "C:/Program Files (x86)/REFPROP",
        "C:/Program Files/REFPROP",
        "C:/REFPROP"
    ]

    for dir in common_paths
        candidate = joinpath(dir, dll_name)
        if file_flag
            isfile(candidate) && return candidate
        else
            isfile(candidate) && return dir
        end
    end

    error("REFPROP DLL not found. Please set the RPPREFIX environment variable.")
end

const REFPROP_DLL = find_refprop_path()
const REFPROP_PTH = find_refprop_path(false)

function GETENUMdll_ccall(enum_string::String)
    iEnum = Ref{Cint}(0)
    ccall((:GETENUMdll, REFPROP_DLL), Cvoid,
          (Ref{Cint}, Cstring, Ref{Cint}, Ref{Cint}, Ptr{UInt8}, Cint, Cint),
          Ref{Cint}(0), enum_string, iEnum, Ref{Cint}(0), zeros(UInt8, 255),
          sizeof(enum_string), 255)
    return Int(iEnum[])
end

function SETREFdll_ccall!(hrf::String, z::Vector{Float64};
                  ixflag::Int32=Int32(1), h0::Float64=0.0, s0::Float64=0.0,
                  T0::Float64=0.0, P0::Float64=0.0)
                  
    ierr = Ref{Int32}(0)
    herr = zeros(UInt8, 255)
    ccall((:SETREFdll, REFPROP_DLL), Cvoid,
        (Cstring, Ref{Int32}, Ptr{Float64},
         Ref{Float64}, Ref{Float64}, Ref{Float64}, Ref{Float64},
         Ref{Int32}, Ptr{UInt8}, Int32, Int32),
        hrf, ixflag, z,
        h0, s0, T0, P0,
        ierr, herr, length(hrf), length(herr))
    ierr[] != 0 && error("SETREFdll failed (ierr=$(ierr[])): $(String(herr))")
end

function REFPROPdll_ccall!(cache, PROP_IN::String, PROP_OUT::String, p1xi::Float64, p2xi::Float64)
    cache.ierr[1] = 0
    
    ccall((:REFPROPdll, REFPROP_DLL), Cvoid, 
          (Cstring, Cstring, Cstring, Ref{Cint}, Ref{Cint}, Ref{Cint}, Ref{Cdouble}, Ref{Cdouble}, 
           Ptr{Cdouble}, Ptr{Cdouble}, Ptr{UInt8}, Ref{Cint}, Ptr{Cdouble}, Ptr{Cdouble}, Ptr{Cdouble}, 
           Ptr{Cdouble}, Ptr{Cint}, Ptr{UInt8}, Cint, Cint, Cint, Cint, Cint),
           cache.material, PROP_IN, PROP_OUT, cache.iMass, cache.iMass, 0, p1xi, p2xi,
           cache.z, cache.Output, cache.hUnits_buf, 0, cache.x, cache.y, cache.x3, cache.q, cache.ierr, cache.herr_buf, 
           sizeof(cache.material), sizeof(PROP_IN), sizeof(PROP_OUT), sizeof(cache.hUnits_buf), sizeof(cache.herr_buf))

end

##############################################################################
# Refprop FL
##############################################################################
function SETPATHdll_ccall!()
    ccall((:SETPATHdll, REFPROP_DLL), Cvoid,
        (Cstring, Int32),
        REFPROP_PTH, length(REFPROP_PTH))
end

function SETFLUIDSdll_ccall!(fluidstring::String)
    ierr = Ref{Int32}(0)
    herr = zeros(UInt8, 255)
    ccall((:SETFLUIDSdll, REFPROP_DLL), Cvoid,
        (Cstring, Ref{Int32}, Int32),
        fluidstring, ierr, length(fluidstring))
    ierr[] != 0 && error("SETFLUIDSdll failed: $(String(herr))")
end

function WMOLdll_ccall(z::Vector{Float64})
    wmm = Ref{Float64}(0.0)
    ccall((:WMOLdll, REFPROP_DLL), Cvoid,
        (Ptr{Float64}, Ref{Float64}), z, wmm)
    return wmm[]  # g/mol
end

function QMASSdll_ccall(cache, qmol::Float64, xl::Vector{Float64}, xv::Vector{Float64})
    qkg = Ref{Float64}(0.0)
    xlkg = zeros(Float64, 20)
    xvkg = zeros(Float64, 20)
    wliq = Ref{Float64}(0.0)
    wvap = Ref{Float64}(0.0)
    ccall((:QMASSdll, REFPROP_DLL), Cvoid,
        (Ref{Float64}, Ptr{Float64}, Ptr{Float64},
         Ref{Float64}, Ptr{Float64}, Ptr{Float64},
         Ref{Float64}, Ref{Float64},
         Ref{Int32}, Ptr{UInt8}, Int32),
        qmol, xl, xv, qkg, xlkg, xvkg, wliq, wvap, cache.ierr, cache.herr, length(cache.herr))
    return qkg[]
end

function convert_quality(cache, qmol::Float64)
    if length(cache.params.Composition) == 1
        return qmol
    else
        return QMASSdll_ccall(cache, qmol, cache.x, cache.y)
    end
end

function CRITPdll_ccall(cache)
    Tc = Ref{Float64}(0.0)
    Pc = Ref{Float64}(0.0)
    Dc = Ref{Float64}(0.0)
    ccall((:CRITPdll, REFPROP_DLL), Cvoid,
        (Ptr{Float64}, Ref{Float64}, Ref{Float64}, Ref{Float64},
         Ref{Int32}, Ptr{UInt8}, Int32),
        cache.z, Tc, Pc, Dc, cache.ierr, cache.herr, length(cache.herr))

    return Tc[], Pc[]*1000.0, Dc[]*cache.MW   # K, kPa, mol/L -- REFPROP native units, same convention as everything else
end

function SATSPLNdll_ccall!(cache)
    ccall((:SATSPLNdll, REFPROP_DLL), Cvoid,
        (Ptr{Float64}, Ref{Int32}, Ptr{UInt8}, Int32),
        cache.z, cache.ierr, cache.herr, length(cache.herr))
    cache.ierr[] != 0 && error("SATSPLNdll failed (ierr=$(cache.ierr[])): $(String(cache.herr))")
end

function compute_crit(cache)
    if length(cache.params.Composition) > 1
        SATSPLNdll_ccall!(cache)
    end
    return CRITPdll_ccall(cache)
end

function tpflsh!(cache, T::Float64, P::Float64)
    ccall((:TPFLSHdll, REFPROP_DLL), Cvoid,
        (Ref{Float64}, Ref{Float64}, Ptr{Float64},
         Ref{Float64}, Ref{Float64}, Ref{Float64}, Ptr{Float64}, Ptr{Float64},
         Ref{Float64}, Ref{Float64}, Ref{Float64}, Ref{Float64}, Ref{Float64}, Ref{Float64}, Ref{Float64},
         Ref{Int32}, Ptr{UInt8}, Int32),
        T, P/1000.0, cache.z,
        cache.D, cache.Dl, cache.Dv, cache.x, cache.y,
        cache.q, cache.e, cache.h, cache.s, cache.Cv, cache.Cp, cache.w,
        cache.ierr, cache.herr, length(cache.herr))

    cache.Output[1] = T
    cache.Output[2] = P
    cache.Output[3] = cache.D[]*cache.MW
    cache.Output[4] = convert_quality(cache, cache.q[])
    cache.Output[5] = cache.h[]*1000.0/cache.MW
    cache.Output[6] = cache.e[]*1000.0/cache.MW
    cache.Output[7] = cache.s[]*1000.0/cache.MW
end

function tdflsh!(cache, T::Float64, D::Float64)
    ccall((:TDFLSHdll, REFPROP_DLL), Cvoid,
        (Ref{Float64}, Ref{Float64}, Ptr{Float64},
         Ref{Float64}, Ref{Float64}, Ref{Float64}, Ptr{Float64}, Ptr{Float64},
         Ref{Float64}, Ref{Float64}, Ref{Float64}, Ref{Float64}, Ref{Float64}, Ref{Float64}, Ref{Float64},
         Ref{Int32}, Ptr{UInt8}, Int32),
        T, D/cache.MW, cache.z,
        cache.P, cache.Dl, cache.Dv, cache.x, cache.y,
        cache.q, cache.e, cache.h, cache.s, cache.Cv, cache.Cp, cache.w,
        cache.ierr, cache.herr, length(cache.herr))

    cache.Output[1] = T
    cache.Output[2] = cache.P[]*1000.0
    cache.Output[3] = D
    cache.Output[4] = convert_quality(cache, cache.q[])
    cache.Output[5] = cache.h[]*1000.0/cache.MW
    cache.Output[6] = cache.e[]*1000.0/cache.MW
    cache.Output[7] = cache.s[]*1000.0/cache.MW
end

function teflsh!(cache, T::Float64, e::Float64)
    ccall((:TEFLSHdll, REFPROP_DLL), Cvoid,
        (Ref{Float64}, Ref{Float64}, Ptr{Float64}, Ref{Int32},
         Ref{Float64}, Ref{Float64}, Ref{Float64}, Ref{Float64}, Ptr{Float64}, Ptr{Float64},
         Ref{Float64}, Ref{Float64}, Ref{Float64}, Ref{Float64}, Ref{Float64}, Ref{Float64},
         Ref{Int32}, Ptr{UInt8}, Int32),
        T, e*cache.MW/1000.0, cache.z, cache.kr,
        cache.P, cache.D, cache.Dl, cache.Dv, cache.x, cache.y,
        cache.q, cache.h, cache.s, cache.Cv, cache.Cp, cache.w,
        cache.ierr, cache.herr, length(cache.herr))

    cache.Output[1] = T
    cache.Output[2] = cache.P[]*1000.0
    cache.Output[3] = cache.D[]*cache.MW
    cache.Output[4] = convert_quality(cache, cache.q[])
    cache.Output[5] = cache.h[]*1000.0/cache.MW
    cache.Output[6] = e
    cache.Output[7] = cache.s[]*1000.0/cache.MW
end

function thflsh!(cache, T::Float64, h::Float64)
    ccall((:THFLSHdll, REFPROP_DLL), Cvoid,
        (Ref{Float64}, Ref{Float64}, Ptr{Float64}, Ref{Int32},
         Ref{Float64}, Ref{Float64}, Ref{Float64}, Ref{Float64}, Ptr{Float64}, Ptr{Float64},
         Ref{Float64}, Ref{Float64}, Ref{Float64}, Ref{Float64}, Ref{Float64}, Ref{Float64},
         Ref{Int32}, Ptr{UInt8}, Int32),
        T, h*cache.MW/1000.0, cache.z, cache.kr,
        cache.P, cache.D, cache.Dl, cache.Dv, cache.x, cache.y,
        cache.q, cache.e, cache.s, cache.Cv, cache.Cp, cache.w,
        cache.ierr, cache.herr, length(cache.herr))

    cache.Output[1] = T
    cache.Output[2] = cache.P[]*1000.0
    cache.Output[3] = cache.D[]*cache.MW
    cache.Output[4] = convert_quality(cache, cache.q[])
    cache.Output[5] = h
    cache.Output[6] = cache.e[]*1000.0/cache.MW
    cache.Output[7] = cache.s[]*1000.0/cache.MW
end

function tsflsh!(cache, T::Float64, s::Float64)
    ccall((:TSFLSHdll, REFPROP_DLL), Cvoid,
        (Ref{Float64}, Ref{Float64}, Ptr{Float64}, Ref{Int32},
         Ref{Float64}, Ref{Float64}, Ref{Float64}, Ref{Float64}, Ptr{Float64}, Ptr{Float64},
         Ref{Float64}, Ref{Float64}, Ref{Float64}, Ref{Float64}, Ref{Float64}, Ref{Float64},
         Ref{Int32}, Ptr{UInt8}, Int32),
        T, s*cache.MW/1000.0, cache.z, cache.kr,
        cache.P, cache.D, cache.Dl, cache.Dv, cache.x, cache.y,
        cache.q, cache.e, cache.h, cache.Cv, cache.Cp, cache.w,
        cache.ierr, cache.herr, length(cache.herr))

    cache.Output[1] = T
    cache.Output[2] = cache.P[]*1000.0
    cache.Output[3] = cache.D[]*cache.MW
    cache.Output[4] = convert_quality(cache, cache.q[])
    cache.Output[5] = cache.h[]*1000.0/cache.MW
    cache.Output[6] = cache.e[]*1000.0/cache.MW
    cache.Output[7] = s
end

function tqflsh!(cache, T::Float64, q::Float64)
    ccall((:TQFLSHdll, REFPROP_DLL), Cvoid,
        (Ref{Float64}, Ref{Float64}, Ptr{Float64}, Ref{Int32},
         Ref{Float64}, Ref{Float64}, Ref{Float64}, Ref{Float64}, Ptr{Float64}, Ptr{Float64},
         Ref{Float64}, Ref{Float64}, Ref{Float64}, Ref{Float64}, Ref{Float64}, Ref{Float64},
         Ref{Int32}, Ptr{UInt8}, Int32),
        T, q, cache.z, cache.kq,
        cache.P, cache.D, cache.Dl, cache.Dv, cache.x, cache.y,
        cache.e, cache.h, cache.s, cache.Cv, cache.Cp, cache.w,
        cache.ierr, cache.herr, length(cache.herr))

    cache.Output[1] = T
    cache.Output[2] = cache.P[]*1000.0
    cache.Output[3] = cache.D[]*cache.MW
    cache.Output[4] = q
    cache.Output[5] = cache.h[]*1000.0/cache.MW
    cache.Output[6] = cache.e[]*1000.0/cache.MW
    cache.Output[7] = cache.s[]*1000.0/cache.MW
end

function pdflsh!(cache, P::Float64, D::Float64)
    ccall((:PDFLSHdll, REFPROP_DLL), Cvoid,
        (Ref{Float64}, Ref{Float64}, Ptr{Float64},
         Ref{Float64}, Ref{Float64}, Ref{Float64}, Ptr{Float64}, Ptr{Float64},
         Ref{Float64}, Ref{Float64}, Ref{Float64}, Ref{Float64}, Ref{Float64}, Ref{Float64}, Ref{Float64},
         Ref{Int32}, Ptr{UInt8}, Int32),
        P/1000.0, D/cache.MW, cache.z,
        cache.T, cache.Dl, cache.Dv, cache.x, cache.y,
        cache.q, cache.e, cache.h, cache.s, cache.Cv, cache.Cp, cache.w,
        cache.ierr, cache.herr, length(cache.herr))

    cache.Output[1] = cache.T[]
    cache.Output[2] = P
    cache.Output[3] = D
    cache.Output[4] = convert_quality(cache, cache.q[])
    cache.Output[5] = cache.h[]*1000.0/cache.MW
    cache.Output[6] = cache.e[]*1000.0/cache.MW
    cache.Output[7] = cache.s[]*1000.0/cache.MW
end

function peflsh!(cache, P::Float64, e::Float64)
    ccall((:PEFLSHdll, REFPROP_DLL), Cvoid,
        (Ref{Float64}, Ref{Float64}, Ptr{Float64},
         Ref{Float64}, Ref{Float64}, Ref{Float64}, Ref{Float64}, Ptr{Float64}, Ptr{Float64},
         Ref{Float64}, Ref{Float64}, Ref{Float64}, Ref{Float64}, Ref{Float64}, Ref{Float64},
         Ref{Int32}, Ptr{UInt8}, Int32),
        P/1000.0, e*cache.MW/1000.0, cache.z,
        cache.T, cache.D, cache.Dl, cache.Dv, cache.x, cache.y,
        cache.q, cache.h, cache.s, cache.Cv, cache.Cp, cache.w,
        cache.ierr, cache.herr, length(cache.herr))

    cache.Output[1] = cache.T[]
    cache.Output[2] = P
    cache.Output[3] = cache.D[]*cache.MW
    cache.Output[4] = convert_quality(cache, cache.q[])
    cache.Output[5] = cache.h[]*1000.0/cache.MW
    cache.Output[6] = e
    cache.Output[7] = cache.s[]*1000.0/cache.MW
end

function phflsh!(cache, P::Float64, h::Float64)
    ccall((:PHFLSHdll, REFPROP_DLL), Cvoid,
        (Ref{Float64}, Ref{Float64}, Ptr{Float64},
         Ref{Float64}, Ref{Float64}, Ref{Float64}, Ref{Float64}, Ptr{Float64}, Ptr{Float64},
         Ref{Float64}, Ref{Float64}, Ref{Float64}, Ref{Float64}, Ref{Float64}, Ref{Float64},
         Ref{Int32}, Ptr{UInt8}, Int32),
        P/1000.0, h*cache.MW/1000.0, cache.z,
        cache.T, cache.D, cache.Dl, cache.Dv, cache.x, cache.y,
        cache.q, cache.e, cache.s, cache.Cv, cache.Cp, cache.w,
        cache.ierr, cache.herr, length(cache.herr))

    cache.Output[1] = cache.T[]
    cache.Output[2] = P
    cache.Output[3] = cache.D[]*cache.MW
    cache.Output[4] = convert_quality(cache, cache.q[])
    cache.Output[5] = h
    cache.Output[6] = cache.e[]*1000.0/cache.MW
    cache.Output[7] = cache.s[]*1000.0/cache.MW
end

function psflsh!(cache, P::Float64, s::Float64)
    ccall((:PSFLSHdll, REFPROP_DLL), Cvoid,
        (Ref{Float64}, Ref{Float64}, Ptr{Float64},
         Ref{Float64}, Ref{Float64}, Ref{Float64}, Ref{Float64}, Ptr{Float64}, Ptr{Float64},
         Ref{Float64}, Ref{Float64}, Ref{Float64}, Ref{Float64}, Ref{Float64}, Ref{Float64},
         Ref{Int32}, Ptr{UInt8}, Int32),
        P/1000.0, s*cache.MW/1000.0, cache.z,
        cache.T, cache.D, cache.Dl, cache.Dv, cache.x, cache.y,
        cache.q, cache.e, cache.h, cache.Cv, cache.Cp, cache.w,
        cache.ierr, cache.herr, length(cache.herr))

    cache.Output[1] = cache.T[]
    cache.Output[2] = P
    cache.Output[3] = cache.D[]*cache.MW
    cache.Output[4] = convert_quality(cache, cache.q[])
    cache.Output[5] = cache.h[]*1000.0/cache.MW
    cache.Output[6] = cache.e[]*1000.0/cache.MW
    cache.Output[7] = s
end

function pqflsh!(cache, P::Float64, q::Float64)
    ccall((:PQFLSHdll, REFPROP_DLL), Cvoid,
        (Ref{Float64}, Ref{Float64}, Ptr{Float64}, Ref{Int32},
         Ref{Float64}, Ref{Float64}, Ref{Float64}, Ref{Float64}, Ptr{Float64}, Ptr{Float64},
         Ref{Float64}, Ref{Float64}, Ref{Float64}, Ref{Float64}, Ref{Float64}, Ref{Float64},
         Ref{Int32}, Ptr{UInt8}, Int32),
        P/1000.0, q, cache.z, cache.kq,
        cache.T, cache.D, cache.Dl, cache.Dv, cache.x, cache.y,
        cache.e, cache.h, cache.s, cache.Cv, cache.Cp, cache.w,
        cache.ierr, cache.herr, length(cache.herr))

    cache.Output[1] = cache.T[]
    cache.Output[2] = P
    cache.Output[3] = cache.D[]*cache.MW
    cache.Output[4] = q
    cache.Output[5] = cache.h[]*1000.0/cache.MW
    cache.Output[6] = cache.e[]*1000.0/cache.MW
    cache.Output[7] = cache.s[]*1000.0/cache.MW
end

function deflsh!(cache, D::Float64, e::Float64)
    ccall((:DEFLSHdll, REFPROP_DLL), Cvoid,
        (Ref{Float64}, Ref{Float64}, Ptr{Float64},
         Ref{Float64}, Ref{Float64}, Ref{Float64}, Ref{Float64}, Ptr{Float64}, Ptr{Float64},
         Ref{Float64}, Ref{Float64}, Ref{Float64}, Ref{Float64}, Ref{Float64}, Ref{Float64},
         Ref{Int32}, Ptr{UInt8}, Int32),
        D/cache.MW, e*cache.MW/1000.0, cache.z,
        cache.T, cache.P, cache.Dl, cache.Dv, cache.x, cache.y,
        cache.q, cache.h, cache.s, cache.Cv, cache.Cp, cache.w,
        cache.ierr, cache.herr, length(cache.herr))

    cache.Output[1] = cache.T[]
    cache.Output[2] = cache.P[]*1000.0
    cache.Output[3] = D
    cache.Output[4] = convert_quality(cache, cache.q[])
    cache.Output[5] = cache.h[]*1000.0/cache.MW
    cache.Output[6] = e
    cache.Output[7] = cache.s[]*1000.0/cache.MW
end

function dhflsh!(cache, D::Float64, h::Float64)
    ccall((:DHFLSHdll, REFPROP_DLL), Cvoid,
        (Ref{Float64}, Ref{Float64}, Ptr{Float64},
         Ref{Float64}, Ref{Float64}, Ref{Float64}, Ref{Float64}, Ptr{Float64}, Ptr{Float64},
         Ref{Float64}, Ref{Float64}, Ref{Float64}, Ref{Float64}, Ref{Float64}, Ref{Float64},
         Ref{Int32}, Ptr{UInt8}, Int32),
        D/cache.MW, h*cache.MW/1000.0, cache.z,
        cache.T, cache.P, cache.Dl, cache.Dv, cache.x, cache.y,
        cache.q, cache.e, cache.s, cache.Cv, cache.Cp, cache.w,
        cache.ierr, cache.herr, length(cache.herr))

    cache.Output[1] = cache.T[]
    cache.Output[2] = cache.P[]*1000.0
    cache.Output[3] = D
    cache.Output[4] = convert_quality(cache, cache.q[])
    cache.Output[5] = h
    cache.Output[6] = cache.e[]*1000.0/cache.MW
    cache.Output[7] = cache.s[]*1000.0/cache.MW
end

function dsflsh!(cache, D::Float64, s::Float64)
    ccall((:DSFLSHdll, REFPROP_DLL), Cvoid,
        (Ref{Float64}, Ref{Float64}, Ptr{Float64},
         Ref{Float64}, Ref{Float64}, Ref{Float64}, Ref{Float64}, Ptr{Float64}, Ptr{Float64},
         Ref{Float64}, Ref{Float64}, Ref{Float64}, Ref{Float64}, Ref{Float64}, Ref{Float64},
         Ref{Int32}, Ptr{UInt8}, Int32),
        D/cache.MW, s*cache.MW/1000.0, cache.z,
        cache.T, cache.P, cache.Dl, cache.Dv, cache.x, cache.y,
        cache.q, cache.e, cache.h, cache.Cv, cache.Cp, cache.w,
        cache.ierr, cache.herr, length(cache.herr))

    cache.Output[1] = cache.T[]
    cache.Output[2] = cache.P[]*1000.0
    cache.Output[3] = D
    cache.Output[4] = convert_quality(cache, cache.q[])
    cache.Output[5] = cache.h[]*1000.0/cache.MW
    cache.Output[6] = cache.e[]*1000.0/cache.MW
    cache.Output[7] = s
end

function hsflsh!(cache, h::Float64, s::Float64)
    ccall((:HSFLSHdll, REFPROP_DLL), Cvoid,
        (Ref{Float64}, Ref{Float64}, Ptr{Float64},
         Ref{Float64}, Ref{Float64}, Ref{Float64}, Ref{Float64}, Ref{Float64}, Ptr{Float64}, Ptr{Float64},
         Ref{Float64}, Ref{Float64}, Ref{Float64}, Ref{Float64}, Ref{Float64},
         Ref{Int32}, Ptr{UInt8}, Int32),
        h*cache.MW/1000.0, s*cache.MW/1000.0, cache.z,
        cache.T, cache.P, cache.D, cache.Dl, cache.Dv, cache.x, cache.y,
        cache.q, cache.e, cache.Cv, cache.Cp, cache.w,
        cache.ierr, cache.herr, length(cache.herr))

    cache.Output[1] = cache.T[]
    cache.Output[2] = cache.P[]*1000.0
    cache.Output[3] = cache.D[]*cache.MW
    cache.Output[4] = convert_quality(cache, cache.q[])
    cache.Output[5] = h
    cache.Output[6] = cache.e[]*1000.0/cache.MW
    cache.Output[7] = s
end

const TP, PT, TD, DT, TE, ET = Val(:TP), Val(:PT), Val(:TD), Val(:DT), Val(:TE), Val(:ET)
const TH, HT, TS, ST, TQ, QT = Val(:TH), Val(:HT), Val(:TS), Val(:ST), Val(:TQ), Val(:QT)
const PD, DP, PE, EP, PH, HP = Val(:PD), Val(:DP), Val(:PE), Val(:EP), Val(:PH), Val(:HP)
const PS, SP, PQ, QP, DE, ED = Val(:PS), Val(:SP), Val(:PQ), Val(:QP), Val(:DE), Val(:ED)
const DH, HD, DS, SD, HS, SH = Val(:DH), Val(:HD), Val(:DS), Val(:SD), Val(:HS), Val(:SH)

FLSHdll_ccall!(cache, ::Val{:TP}, a::Float64, b::Float64) = tpflsh!(cache, a, b)
FLSHdll_ccall!(cache, ::Val{:PT}, a::Float64, b::Float64) = tpflsh!(cache, b, a)

FLSHdll_ccall!(cache, ::Val{:TD}, a::Float64, b::Float64) = tdflsh!(cache, a, b)
FLSHdll_ccall!(cache, ::Val{:DT}, a::Float64, b::Float64) = tdflsh!(cache, b, a)

FLSHdll_ccall!(cache, ::Val{:TE}, a::Float64, b::Float64) = teflsh!(cache, a, b)
FLSHdll_ccall!(cache, ::Val{:ET}, a::Float64, b::Float64) = teflsh!(cache, b, a)

FLSHdll_ccall!(cache, ::Val{:TH}, a::Float64, b::Float64) = thflsh!(cache, a, b)
FLSHdll_ccall!(cache, ::Val{:HT}, a::Float64, b::Float64) = thflsh!(cache, b, a)

FLSHdll_ccall!(cache, ::Val{:TS}, a::Float64, b::Float64) = tsflsh!(cache, a, b)
FLSHdll_ccall!(cache, ::Val{:ST}, a::Float64, b::Float64) = tsflsh!(cache, b, a)

FLSHdll_ccall!(cache, ::Val{:TQ}, a::Float64, b::Float64) = tqflsh!(cache, a, b)
FLSHdll_ccall!(cache, ::Val{:QT}, a::Float64, b::Float64) = tqflsh!(cache, b, a)

FLSHdll_ccall!(cache, ::Val{:PD}, a::Float64, b::Float64) = pdflsh!(cache, a, b)
FLSHdll_ccall!(cache, ::Val{:DP}, a::Float64, b::Float64) = pdflsh!(cache, b, a)

FLSHdll_ccall!(cache, ::Val{:PE}, a::Float64, b::Float64) = peflsh!(cache, a, b)
FLSHdll_ccall!(cache, ::Val{:EP}, a::Float64, b::Float64) = peflsh!(cache, b, a)

FLSHdll_ccall!(cache, ::Val{:PH}, a::Float64, b::Float64) = phflsh!(cache, a, b)
FLSHdll_ccall!(cache, ::Val{:HP}, a::Float64, b::Float64) = phflsh!(cache, b, a)

FLSHdll_ccall!(cache, ::Val{:PS}, a::Float64, b::Float64) = psflsh!(cache, a, b)
FLSHdll_ccall!(cache, ::Val{:SP}, a::Float64, b::Float64) = psflsh!(cache, b, a)

FLSHdll_ccall!(cache, ::Val{:PQ}, a::Float64, b::Float64) = pqflsh!(cache, a, b)
FLSHdll_ccall!(cache, ::Val{:QP}, a::Float64, b::Float64) = pqflsh!(cache, b, a)

FLSHdll_ccall!(cache, ::Val{:DE}, a::Float64, b::Float64) = deflsh!(cache, a, b)
FLSHdll_ccall!(cache, ::Val{:ED}, a::Float64, b::Float64) = deflsh!(cache, b, a)

FLSHdll_ccall!(cache, ::Val{:DH}, a::Float64, b::Float64) = dhflsh!(cache, a, b)
FLSHdll_ccall!(cache, ::Val{:HD}, a::Float64, b::Float64) = dhflsh!(cache, b, a)

FLSHdll_ccall!(cache, ::Val{:DS}, a::Float64, b::Float64) = dsflsh!(cache, a, b)
FLSHdll_ccall!(cache, ::Val{:SD}, a::Float64, b::Float64) = dsflsh!(cache, b, a)

FLSHdll_ccall!(cache, ::Val{:HS}, a::Float64, b::Float64) = hsflsh!(cache, a, b)
FLSHdll_ccall!(cache, ::Val{:SH}, a::Float64, b::Float64) = hsflsh!(cache, b, a)