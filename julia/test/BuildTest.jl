using JuliaC

# 0. refresh build directory
PATH = ENV["GBM_BASE"] * "/JOA/test/build"
for entry in readdir(PATH; join=true)
    rm(entry; force=true, recursive=true)
end

# 1. Compile the code into an object file, enforcing the trim
img = ImageRecipe(
    output_type = "--output-exe",
    file = "TestMat",
    trim_mode = "unsafe-warn", 
    verbose = true
)

# 2. Link it into an executable named "TestJuliaApp"
link = LinkRecipe(
    image_recipe = img,
    outname = "build/TestMat"
)

# 3. Bundle the required trimmed libraries so it runs on any machine
bun = BundleRecipe(
    link_recipe = link,
    output_dir = "build/TestMat"
)

# Execute the explicit compile → link → bundle steps
open("compile_output_v1.txt", "w") do io
    redirect_stdout(io) do
        redirect_stderr(io) do
            compile_products(img)
            link_products(link)
            bundle_products(bun)
        end
    end
end

# julia --experimental BuildTest.jl
# C:/Users/Inver/.julia/bin/juliac HelloApp --output-exe hello --trim

# C:/Users/dgulewic/.julia/bin/juliac HelloApp --output-exe hello --trim