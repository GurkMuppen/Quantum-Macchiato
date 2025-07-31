# Run through several simulations to log runtime and accuracy, to check for convergence

from qetool import *
import jinja2 as j2
import os
import numpy as np

param_groups = [
    {'ecutwfc':30, 'k':3},
    {'ecutwfc':40, 'k':4},
    {'ecutwfc':40, 'k':6}
]
celldms = [6.7, 6.75, 6.8, 6.85, 6.9, 6.95, 7]

batchpath = "./testruns/benchmark-setup-lattice/"
os.makedirs(batchpath, exist_ok=True)

# Write into the batch output file
with open(batchpath + "results.final", "w") as outfile:
    outfile.write("ecutwfc; kpoints; celldm; cpus; runtime; energy\n")

# Setup the simulation inputs and rund the simulations for each ecut
for i, params in enumerate(param_groups):
    for celldm in celldms:
        # Define the directory and the filename for the run, to ensure good file management
        filename = f"e{params['ecutwfc']}k{params['k']}a{celldm}"
        params.update({'celldm':celldm})
        simulate_from_template_logged(basepath=batchpath, filename=filename, params=params, cpus=4)