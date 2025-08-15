import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from qmacchiato import *
from dos_tool import *

def lattice_optimization_to_graph(data : pd.DataFrame) :
    plt.plot(data['celldm'], data['energy'])

    plt.title("Setup benchmark of calculation for lattice constant")
    plt.xlabel("celldm (Bohr)")
    plt.ylabel("Total energy (Ry)")

    plt.show()
    
def dos_to_graph(path_obj : path_object, structure_name, show = True, save = True) :
    # This script was partially written by Dante Wigren, my project partner during the programme Rays - for excellence

    data = np.loadtxt(f"{path_obj.basepath}dos.dat")
    energy = data[:, 0]
    dos = data[:, 1]

    fermi_level = get_fermi_level(f"{path_obj.basepath}dos.dat")
    bandgap = get_bandgap(f"{path_obj.basepath}dos.dat", fermi_level)
    
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
    plt.plot([], [], "", color="none", label=f"Bandgap:     {bandgap:.2f} eV")
    plt.legend()
    plt.tight_layout()


    if show : plt.show()
    if save : plt.savefig(f"{path_obj.basepath}dos.pdf")
     
    