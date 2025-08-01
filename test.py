from qetool import *
from pseudo_tool import *
from dos_tool import *

copper = structure([atom_position("Cu", 0, 0, 0)])

copper.ibrav = 2

copper.get_nbnd()

print(copper.to_params())

simulate_structure(copper, cpus=4, params={"celldm":8.18})

run_dos_triad(copper, filename="dos_copper_test")