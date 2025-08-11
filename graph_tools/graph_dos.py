import numpy as np
import matplotlib.pyplot as plt
from qetool import *

# This script was partially written by Dante Wigren, my project partner during the programme Rays - for excellence

def dos_to_graph(path_obj : path_object, structure_name, show = True, save = True) :

    data = np.loadtxt(f"{path_obj.basepath}dos.dat")
    energy = data[:, 0]
    dos = data[:, 1]

    fermi_level = 0
    with open(f"{path_obj.basepath}dos.dat") as file:
        first_line = file.readline()
        fermi_level = float(first_line[41:-2])

    # Select begining and enpoints in data for graph
    min_energy = -np.inf
    max_energy = np.inf

    # Select the relevant part of graph
    dos = dos[energy > min_energy and energy < max_energy]
    energy = energy[energy > min_energy and energy < max_energy]

    # Plot
    plt.figure(figsize=(6, 4))
    plt.plot(energy, dos, color='darkblue')
    plt.axvline(fermi_level, color='gray', linestyle=':', label='Fermi level')
    plt.xlabel("Energy (eV)")
    plt.ylabel("Density (states/eV)")
    plt.title(f"Density of States in {structure_name}")
    plt.legend()
    plt.tight_layout()


    if show : plt.show()
    if save : plt.savefig(f"{path_obj.basepath}dos.pdf")
     
    