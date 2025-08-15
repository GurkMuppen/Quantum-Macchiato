# Run through several simulations to log runtime and accuracy, to check for convergence

from qmacchiato import *
import jinja2 as j2
import os
import numpy as np

ecuts = [10, 40, 70]
kpoints = [2, 6, 10]
cpus = [1, 2, 4]

batchpath = "./testruns/benchmark-cpus/"
os.makedirs(batchpath, exist_ok=True)

# Write into the batch output file
with open(batchpath + "results.final", "w") as outfile:
    outfile.write("ecutwfc; kpoints; runtime; cpus; energy\n")

# Setup the simulation inputs and rund the simulations for each ecut
for i, ecut in enumerate(ecuts):
    for cpu in cpus:
        # Define the directory and the filename for the run, to ensure good file management
        filename = f"e{ecuts[i]}k{kpoints[i]}-cpu{cpu}"
        params = {'ecutwfc':ecuts[i], 'kx':kpoints[i], 'ky':kpoints[i],'kz':kpoints[i]}
        simulate_from_template_logged(basepath=batchpath, filename=filename, params=params, cpus=cpu)