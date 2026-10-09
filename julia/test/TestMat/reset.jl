using Pkg
using TOML

# ==============================================================================
# 1. DEFINE YOUR REQUIRED PACKAGES HERE
# ==============================================================================
required_packages = [
]

println("Starting environment reset...\n")

if !isfile("Project.toml")
    error("Could not find 'Project.toml'. Please run this script from the JOA root directory.")
end

# ==============================================================================
# 2. EXTRACT PACKAGE METADATA
# ==============================================================================
println("-> Extracting package metadata (name, uuid, version)...")
old_project = TOML.parsefile("Project.toml")

# Keep only the essential package identifiers
header_keys = ["name", "uuid", "version", "authors"]
new_project = Dict{String, Any}()

for k in header_keys
    if haskey(old_project, k)
        new_project[k] = old_project[k]
    end
end

# ==============================================================================
# 3. BACKUP & CLEAN UP
# ==============================================================================
println("-> Backing up 'Project.toml' to 'Project_old.toml'...")
mv("Project.toml", "Project_old.toml", force=true)

if isfile("Manifest.toml")
    println("-> Deleting old 'Manifest.toml'...")
    rm("Manifest.toml", force=true)
end

# ==============================================================================
# 4. WRITE NEW HEADER & INSTALL PACKAGES
# ==============================================================================
println("-> Writing new 'Project.toml' with original metadata...")
open("Project.toml", "w") do io
    TOML.print(io, new_project)
end

println("-> Activating clean package environment...")
Pkg.activate(".")

println("-> Installing specified packages: ", join(required_packages, ", "))
if !isempty(required_packages)
    Pkg.add(required_packages)
else
    println("No packages specified to add.")
end

println("\n=======================================================")
println("   SUCCESS: Clean package Project.toml generated!")
println("=======================================================")