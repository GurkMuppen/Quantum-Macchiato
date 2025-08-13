import numpy as np
import matplotlib.pyplot as plt
from qetool import *

# This script was partially written by Dante Wigren, my project partner during the programme Rays - for excellence

def dos_to_graph(path_obj : path_object, structure_name, show = True, save = True) :

    data = np.loadtxt(f"{path_obj.basepath}dos.dat")
    energy = data[:, 0]
    dos = data[:, 1]

    fermi_level = 0
    bandgap = 0 
    with open(f"{path_obj.basepath}dos.dat") as file:
        first_line = file.readline()
        fermi_level = float(first_line[42:-3])
        for line in file :
            if line[0] == "#" : continue
            if float(line[:7]) < fermi_level : continue
            if float(line[10:20]) == 0 :
                bandgap += 0.01
            else :
                break

    # Select begining and enpoints in data for graph
    min_energy = -np.inf
    max_energy = np.inf

    # Select the relevant part of graph
    dos = dos[(energy > min_energy) & (energy < max_energy)]
    energy = energy[(energy > min_energy) & (energy < max_energy)]

    # Plot
    plt.figure(figsize=(10, 7))
    valance_band = plt.plot(energy[energy <= fermi_level], dos[energy <= fermi_level], color='royalblue')
    conductive_band = plt.plot(energy[energy > fermi_level], dos[energy > fermi_level], color='tomato')

    plt.axvline(fermi_level, color='darkblue', linestyle=':', label=f"Fermi level:  {fermi_level} eV")
    plt.xlabel("Energy (eV)")
    plt.ylabel("Density (states/eV)")
    plt.title(f"Density of States in {structure_name}")
    plt.margins(y=0)
    plt.plot([], [], "", color="none", label=f"Bandgap:     {bandgap} eV")
    plt.legend()
    plt.tight_layout()


    if show : plt.show()
    if save : plt.savefig(f"{path_obj.basepath}dos.pdf")
     
    