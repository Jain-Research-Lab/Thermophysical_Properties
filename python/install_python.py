import subprocess
import platform
import shutil
import time
import os

#####################################################################################
# Step 1: Run this script in mode 1. Close out of everything. Re-open to this script.
# Step 2: Run this script in mode 2. If step 1 is done correctly, the script will not crash.
#####################################################################################

# install as editable modules to use as a module. Run exactly once
def toolbox_install(TP_base, folder):    
    result = subprocess.run('pip install -e'+ TP_base + '/' + folder, shell=True, check=True)
    if result.returncode != 0:
        print(f"Command failed: pip install e")
    else:
        print("success!")
    
    shutil.rmtree(TP_base + '/' + folder + '/' + folder + '.egg-info')

# add path to environmental variables. Run exactly once
def add_path(TP_base):
    os_name = platform.system() # Output is 'Linux', 'Windows', or 'Darwin' (macOS)
    
    if os_name == "Windows":
        result = subprocess.run(['setx', 'TP_base', TP_base], shell=True, check=True)
        if result.returncode != 0:
            print(f"Command failed: setx")

    # check the bottom of /home/your_username/.bashrc
    # Hit ctrl + H to view hidden dot files
    elif os_name == "Linux":
        with open(os.path.expanduser('~/.bashrc'), 'a') as bashrc:
            bashrc.write(f'\nexport TP_base="{TP_base}"\n')
    
if __name__ == "__main__":
    t0 = time.time()
    ##################################################################################
    # set install mode
    mode =  1 # 1: set workspace root as an environmental variable
              #    install required package
              # 2: render templates
    ##################################################################################
    
    TP_base = os.environ.get('TP_BASE')

    if mode == 1:
        add_path(TP_base)
        toolbox_install(TP_base, "python")
        
    print(time.time() - t0)