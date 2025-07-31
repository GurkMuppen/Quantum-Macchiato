import subprocess, resource
import os
import time
import pandas as pd
import numpy as np
import jinja2 as j2

testcmd = (
    "echo 0 | sudo tee /proc/sys/kernel/yama/ptrace_scope && "
    "export OMP_NUM_THREADS=1 && "
    "conda run -n qespresso mpirun -np 1 pw.x -in test.in"
)
default_params = {'celldm':6.765, 'ecutwfc':40, 'k':6}

class atom_position:
    atom : str
    x : float
    y : float
    z : float

    def __init__(self, atom, x, y, z):
        self.atom = atom
        self.x = x
        self.y = y
        self.z = z

    def __str__(self):
        return f"{self.atom} {self.x} {self.y} {self.z}"

class structure:
    """A QE-tool structure"""
    ibrav : int 
    celldm : float
    species : pd.DataFrame
    positions : list[atom_position]

    def __init__(self, species, positions):
        self.species = species
        self.positions = positions

    


def generate_command(cpus, program="pw.x", input_path="test.in", threads=1):
    return (
        "echo 0 | sudo tee /proc/sys/kernel/yama/ptrace_scope && "
        f"export OMP_NUM_THREADS={threads} && "
        f"conda run -n qespresso mpirun -np {cpus} {program} -in {input_path}"
    )

def run_logged_command(command, output_file="test.out", label=""):
    usagestart = time.time()
    with open(output_file, "w") as outfile:
        subprocess.run(command, shell=True, check=True, stdout=outfile, stderr=subprocess.STDOUT)
    usageend = time.time()
    runtime = usageend - usagestart
    print(f"Simulation {label} completed with a runtime of: {runtime:.2f} seconds")
    return runtime

def run_command(command, output_file="test.out"):
    with open(output_file, "w") as outfile:
        subprocess.run(command, shell=True, check=True, stdout=outfile, stderr=subprocess.STDOUT)

def run_simulation(program="pw.x", basepath="./tmp/", filename="test", params={}, cpus=1, template_path="./input_templates/test.in"):
    # Use default params if insufficient input:
    tmp_params = default_params
    tmp_params.update(params)
    params = tmp_params

    # Define the directory and the filename for the run, to ensure good file management
    currentpath = basepath + f"{filename}/"
    os.makedirs(currentpath, exist_ok=True)

    # Write the correct settings into the template to prepare an input file
    env = j2.Environment(loader=j2.FileSystemLoader("."))
    template = env.get_template(template_path)
    output = template.render(params, outdir=currentpath, prefix=f"{filename}")
    with open(currentpath + f"{filename}.in", "w") as f:
        f.write(output)

    # Run the simulation
    run_logged_command(generate_command(cpus, program=program, input_path=currentpath + f"{filename}.in"), output_file=currentpath + f"{filename}.out", label=f"{filename}")
                
def run_logged_simulation(program="pw.x", basepath="./tmp/", filename="test", params={}, cpus=1, template_path="./input_templates/test.in"):
    # Use default params if insufficient input:
    tmp_params = default_params
    tmp_params.update(params)
    params = tmp_params

    # Define the directory and the filename for the run, to ensure good file management
    currentpath = basepath + f"{filename}/"
    os.makedirs(currentpath, exist_ok=True)

    # Write the correct settings into the template to prepare an input file
    env = j2.Environment(loader=j2.FileSystemLoader("."))
    template = env.get_template(template_path)
    output = template.render(params, outdir=currentpath, prefix=f"{filename}")
    with open(currentpath + f"{filename}.in", "w") as f:
        f.write(output)

    # Run the simulation and log the runtime
    runtime = run_logged_command(generate_command(cpus, program=program, input_path=currentpath + f"{filename}.in"), output_file=currentpath + f"{filename}.out", label=f"{filename}")
    
    # Write the results to the batch output file
    outpath = currentpath + f"{filename}.out"
    with open(basepath + "results.final", "a") as outfile:
        outfile.write(f"{params['ecutwfc']};{params['k']};{params['celldm']};{cpus};{runtime};")
        with open(outpath, "r") as f:
            for line in f:
                if "!    total energy              =" in line:
                    outfile.write(f"{line[33:-4].strip()}\n")
                    return float(line[33:-4].strip())