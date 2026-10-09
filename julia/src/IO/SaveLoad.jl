write_field(io::IO, x::Float64) = write(io, x)
write_field(io::IO, x::Int64)   = write(io, x)
write_field(io::IO, x::Int32)   = write(io, x)
write_field(io::IO, x::Bool)    = write(io, x)
function write_field(io::IO, x::String)
    write(io, Int64(sizeof(x))); write(io, x)
end
function write_field(io::IO, x::Array{T,N}) where {T,N}
    for d in size(x); write(io, Int64(d)); end
    write(io, x)   # only valid when T is a bitstype like Float64/Int64
end
function write_field(io::IO, x::Vector{String})
    write(io, Int64(length(x)))
    for s in x
        write_field(io, s)   # reuses your existing String writer
    end
end

read_field(io::IO, ::Type{Float64}) = read(io, Float64)
read_field(io::IO, ::Type{Int64})   = read(io, Int64)
read_field(io::IO, ::Type{Int32})   = read(io, Int32)
read_field(io::IO, ::Type{Bool})    = read(io, Bool)
function read_field(io::IO, ::Type{String})
    n = read(io, Int64); String(read(io, n))
end
function read_field(io::IO, ::Type{Array{T,N}}) where {T,N}
    dims = ntuple(_ -> read(io, Int64), N)
    data = Array{T,N}(undef, dims)
    read!(io, data)
    return data
end
function read_field(io::IO, ::Type{Vector{String}})
    n = read(io, Int64)
    result = Vector{String}(undef, n)
    for i in 1:n
        result[i] = read_field(io, String)
    end
    return result
end


@generated function write_field(io::IO, x::T) where T
    if T <: Tuple
        exprs = [:(write_field(io, x[$i])) for i in 1:fieldcount(T)]
    elseif isstructtype(T) && fieldcount(T) > 0
        exprs = [:(write_field(io, x.$(fieldname(T,i)))) for i in 1:fieldcount(T)]
    else
        return :(error("no write_field method for $T"))
    end
    return Expr(:block, exprs...)
end

@generated function read_field(io::IO, ::Type{T}) where T
    if T <: Tuple
        elems = [:(read_field(io, $(fieldtype(T,i)))) for i in 1:fieldcount(T)]
        return :(($(elems...),))
    elseif isstructtype(T) && fieldcount(T) > 0
        elems = [:(read_field(io, $(fieldtype(T,i)))) for i in 1:fieldcount(T)]
        return :($T($(elems...)))
    else
        return :(error("no read_field method for $T"))
    end
end

function save_struct(path::String, x)
    io = open(path, "w")
    try
        write_field(io, x)
    finally
        close(io)
    end
end

function load_struct(path::String, ::Type{T}) where T
    io = open(path, "r")
    try
        return read_field(io, T)
    finally
        close(io)
    end
end