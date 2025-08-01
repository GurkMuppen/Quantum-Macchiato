from qetool import *
from pseudo_tool import *
from dos_tool import *

copper = structure([atom_position("Cu", 0, 0, 0)])

copper.ibrav = 2

simulate_structure(copper, filename="test1", cpus=4, params={"celldm":8.1, "ecutwfc":50})
simulate_structure(copper, filename="test2", cpus=4, params={"celldm":8.18, "ecutwfc":50})
simulate_structure(copper, filename="test3", cpus=4, params={"celldm":8.3, "ecutwfc":50})

run_dos_triad(copper, filename="dos_copper_test")