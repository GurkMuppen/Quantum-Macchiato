import subprocess
import os
import time
import pandas as pd
import numpy as np
import jinja2 as j2
import re
from pseudo_tool import *

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

    def __init__(self, atom : str, x : float, y : float, z : float):
        self.atom = atom
        self.x = x
        self.y = y
        self.z = z

    def __str__(self):
        return f"{self.atom} {self.x} {self.y} {self.z}"
    
class lattice_vector :
    x: float
    y: float
    z: float

    def __init__(self, x: float, y: float, z: float):
        self.x = x
        self.y = y
        self.z = z
        pass

    def to_params(self):
        return f"{self.x} {self.y} {self.z}"

class structure:
    """A Quantum Espresso structure"""
    ibrav : int 
    lattice_constant : float 
    """Used as celldm in cubic structures, or as reference length with alat when using a custom cell shape."""
    species : pd.DataFrame
    positions : list[atom_position]
    
    lattice_vectors : list[lattice_vector]
    """Optional way of describing non-cubic lattices"""
    vector_unit = "alat"
    """ Determines which unit lattice_vectors and positions are interpreted as \n 
    vector_unit = {"alat", "bohr", "angstrom"}, default = "alat". """


    total_energy : float = np.inf # Simulated energy, is set after simulation

    def __init__(self, positions : atom_position, lattice_constant, ibrav=2, lattice_vectors=[], vector_unit="alat"):
        species = []
        for position in positions:
            if position.atom not in species:
                species.append(position.atom)
        self.species = get_pseudo_data(species)
        self.positions = positions
        self.lattice_constant = lattice_constant
        self.ibrav = ibrav
        self.lattice_vectors = lattice_vectors
        self.vector_unit = vector_unit

    def positions_to_string(self):
        output = []
        for position in self.positions:
            output.append(str(position))
        return "\n".join(output)
    
    def get_nbnd(self):
        sum = 0
        for position in self.positions:
            sum += self.species.loc[position.atom, 'n_valance']
        return sum

    def to_params(self):
        output = {
            "ibrav":self.ibrav,
            "celldm":self.lattice_constant,
            "nat":len(self.positions),
            "ntyp":len(self.species),
            "nbnd":int(self.get_nbnd()) + 4, # 4 IF METAL, THIS HAS TO BE ADAPTED,
            "vector_unit":self.vector_unit,
            "species":define_species(self.species),
            "positions": self.positions_to_string()
            }
        if not np.isnan(self.ibrav):
            output.update({"ibrav":self.ibrav})
        else:
            output.update({"ibrav":2})

        if len(self.lattice_vectors) != 0:
            output.update({
                "CELL_PARAMETERS":self.cell_parameters()
            })
        return output
    
    def cell_parameters(self):
        output = f"""CELL_PARAMETERS ({self.vector_unit})
        {self.lattice_vectors[0].to_params()}
        {self.lattice_vectors[1].to_params()}
        {self.lattice_vectors[2].to_params()}"""
        return output


def structure_from_output_file(path : str, filetype = "vc-relax"):
    """ Import structure parameters from previously simulated structure \n
    Implemented calculations: 'vc-relax'"""   

    reading_phase = None
    isFinalCoordinates = False
    total_energy = np.inf
    lattice_constant = np.inf
    cell_parameter_lines = []
    atomic_positions_lines = []

    with open(path, mode="r") as file:

        for line in file:
            
            if "!    total energy              =" in line:
                total_energy = float(line[33:-4].strip())
                continue

            if "Begin final coordinates" in line:
                isFinalCoordinates = True

            if "CELL_PARAMETERS" in line and isFinalCoordinates:
                match = re.search(r"alat=\s*([0-9]+\.[0-9]+)", line)
                if match: lattice_constant = float(match.group(1))
                reading_phase = "cell_parameters"; 
                continue

            if "ATOMIC_POSITIONS" in line and isFinalCoordinates:
                reading_phase = "atomic_positions";
                continue

            if "End final coordinates" in line and isFinalCoordinates: 
                reading_phase = None;
                isFinalCoordinates = False
                break

            match reading_phase:
                case "cell_parameters":
                    if (len(cell_parameter_lines) < 3):
                        cell_parameter_lines.append(line)
                case "atomic_positions":
                    atomic_positions_lines.append(line)
        
    lattice_vectors = []
    for cell_parameter in cell_parameter_lines:
        vector = [float(x) for x in cell_parameter.split()]
        lattice_vectors.append(lattice_vector(vector[0], vector[1], vector[2]))
    positions = []
    for atomic_position in atomic_positions_lines :
        values : list = atomic_position.split()
        positions.append(atom_position(values[0], float(values[1]), float(values[2]), float(values[3])))
    imported_structure = structure(positions, lattice_constant, 0, lattice_vectors)
    return imported_structure
        

class path_object:
    """ A container for all paths used by Quantum Macchiato functions """

    basepath : str 
    """ The folder for all inputs & outputs """

    filename : str
    """ The filename used for both the .in & .out file for the calculation """

    prefix : str 
    """ Common prefix used in segmented calculations"""

    template_path : str
    """ External path to the template to be rendered """

    input_file : str
    """ Local path to the rendered input file to be calculated """

    output_file : str
    """ Local path to the output file """
    
    def __init__(self, basepath : str, filename : str, prefix : str = "", template_path : str = ""):
        self.basepath = basepath
        self.filename = filename
        if prefix == "":
            self.prefix = filename
        else :
            self.prefix = prefix
        self.template_path = template_path

    def render_input_file(self, params : dict, structure : structure = None):
        self.input_file = render_template(structure=structure, basepath=self.basepath, filename=self.filename, prefix=self.prefix, params=params, template_path=self.template_path)
        self.output_file = f"{self.basepath}{self.filename}.out"

    def read_output_energy(path) :
        with open(f"{path.basepath}{path.filename}.out", "r") as f:
            for line in f:
                if "!    total energy              =" in line:
                    return float(line[33:-4].strip())
        raise Exception(f"NO ENERGY WAS FOUND IN {path.basepath}{path.filename}.out")

def generate_command(cpus, program="pw.x", input_path="test.in", threads=1, command_only=False, output_file=""):
    if not command_only : return (
        "echo 0 | sudo tee /proc/sys/kernel/yama/ptrace_scope && "
        f"export OMP_NUM_THREADS={threads} && "
        f"conda run -n qespresso --no-capture-output mpirun -np {cpus} {program} -in {input_path} {('> ' + output_file) if output_file else ''}"
    )
    return (f"conda run -n qespresso --no-capture-output mpirun -np {cpus} {program} -in {input_path} {('> ' + output_file) if output_file else ''}")


def commands_to_bashfile(command : str, path : str, file_mode="w", make_executable=True):
    with open(path, file_mode) as file:
        file.write(command)
    print(path)
    if make_executable : 
        subprocess.run(["chmod", "+x", path], check=True)
        print(f"Executable file created: To run simulation run: {path}")

def run_logged_command(command, label=""):
    usagestart = time.time()
    subprocess.run(command, shell=True, check=True)
    usageend = time.time()
    runtime = usageend - usagestart
    print(f"Simulation {label} completed with a runtime of: {runtime:.2f} seconds")
    return runtime

def run_command(command):
    subprocess.run(command, shell=True, check=True)

def render_template(structure : structure = None, basepath="./tmp/", filename="test", prefix="",params={}, template_path="./input_templates/test.in"):
    # Start with default params:
    tmp_params = default_params
    
    if structure != None :
        tmp_params.update(structure.to_params())
        tmp_params.update(get_optimal_ecuts(structure.species.index, 1.0))

    # Update params with inputted ones
    tmp_params.update(params)
    params = tmp_params

    # Define the directory and the filename for the run, to ensure good file management
    currentpath = basepath
    os.makedirs(currentpath, exist_ok=True)

    # Write the correct settings into the template to prepare an input file
    env = j2.Environment(loader=j2.FileSystemLoader("."), keep_trailing_newline=True)
    template = env.get_template(template_path)
    output = template.render(params, outdir=currentpath, prefix=prefix if prefix != "" else filename)
    with open(currentpath + f"{filename}.in", "w") as f:
        f.write(output)
    
    return f"{currentpath}{filename}.in"

def simulate_from_template(program="pw.x", basepath="./tmp/", filename="test", params={}, cpus=1, template_path="./input_templates/test.in", path_obj : path_object = None):
    """Runs a simulation using the selected program and by inputing a rendered inputfile from the template with added params"""
    
    # Use paths derived from the path_object if exists
    if path_obj != None :
        basepath = path_obj.basepath
        filename = path_obj.filename
        template_path = path_obj.template_path

    input_file = render_template(basepath=basepath, filename=filename, params=params, template_path=template_path)

    # Run the simulation
    run_logged_command(generate_command(cpus, program=program, input_path=input_file), output_file=basepath + f"{filename}.out", label=f"{filename}")

def simulate_from_template_logged(program="pw.x", basepath="./tmp/", filename="test", params={}, cpus=1, template_path="./input_templates/test.in"):
    """Runs a simulation using the selected program and by inputing a rendered input file from the template with the selected params. \n
    Logs results in an file under the basepath named "results.final" 
    """
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

def run_simulation(path_obj : path_object, program="pw.x", cpus=1):
    run_logged_command(generate_command(cpus, program=program, input_path=path_obj.input_file, output_file=path_obj.output_file), label=f"{path_obj.filename}")

    
    