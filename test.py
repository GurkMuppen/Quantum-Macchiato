from qetool import *
from pseudo_tool import *

copper = structure([atom_position("Cu", 0, 0, 0), atom_position("Li", 1, 1, 1)])

copper.ibrav = 2

copper.get_nbnd()

print(copper.to_params())

simulate_structure(copper, cpus=4, params={"celldm":8.18})
