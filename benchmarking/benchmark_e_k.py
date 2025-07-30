# Run through several simulations to log runtime and accuracy, to check for convergence

from qetool import *
import jinja2 as j2
import os
import numpy as np

ecuts = [10, 20, 30, 40, 50, 60, 70]
kpoints = [2, 4, 6, 8, 10]

batchpath = "./testruns/benchmark/"
os.makedirs(batchpath, exist_ok=True)

# Write into the batch output file
with open(batchpath + "results.final", "w") as outfile:
    outfile.write("ecutwfc; kpoints; celldm; runtime; cpus; energy\n")

# Setup the simulation inputs and rund the simulations for each ecut
for ecut in ecuts:
    for k in kpoints:
        # Define the directory and the filename for the run, to ensure good file management
        filename = f"e{ecut}k{k}"
        params = {'ecutwfc':ecut, 'kx':k, 'ky':k,'kz':k}
        run_logged_simulation(basepath=batchpath, filename=filename, params=params)