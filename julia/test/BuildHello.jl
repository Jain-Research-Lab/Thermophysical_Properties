using JuliaC

# 1. Compile the code into an object file, enforcing the trim
img = ImageRecipe(
    output_type = "--output-exe",
    file = "HelloApp",
    trim_mode = "safe", 
    verbose = true
)

# 2. Link it into an executable named "TestJuliaApp"
link = LinkRecipe(
    image_recipe = img,
    outname = "build/HelloApp"
)

# 3. Bundle the required trimmed libraries so it runs on any machine
bun = BundleRecipe(
    link_recipe = link,
    output_dir = "build"
)

# Execute the explicit compile → link → bundle steps
compile_products(img)
link_products(link)
bundle_products(bun)


# C:/Users/Inver/.julia/bin/juliac HelloApp --output-exe hello --trim