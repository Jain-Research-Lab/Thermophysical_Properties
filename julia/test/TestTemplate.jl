using JOA
using BenchmarkTools
using AllocCheck

# test_type 0: @time : time your code, check if code runs (allocation can be non-zero)
# test_type 1: @code_warntype : check if code is type stable (no red text)
# test_type 2: @report_opt : check for dynamic dispatch (compilation does not allow dynamic dispatch)
# test_type 3: @btime : check allocation during runtime, valid for the supplied input values (allocation must be zero)
# test_type 4: @check_allocs: check if your code is zero-allocation, valid for supplied input types (no print output)

test_type = 0

if test_type == 0
    @time

# check that all code is type stable
elseif test_type == 1
    @code_warntype

# check that no dynamic dispatch exists
elseif test_type == 2
    @report_opt

# check that all code with ordinary inputs is 0 allocation
elseif test_type == 3
    @btime

# check that all code is always 0 allocation
elseif test_type == 4
    errors = check_allocs()
    for err in errors
        println(err)
    end

# llvm output for optimizing code
elseif test_type == 5
    @code_llvm debuginfo=:none optimize=true
    
elseif test_type == 6
        errors = code_typed()
    for err in errors
        println(err)
    end

end