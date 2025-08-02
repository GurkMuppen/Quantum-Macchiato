from qetool import *
from pseudo_tool import *
from dos_tool import *

lithium = structure([atom_position("Cu", 0, 0, 0)])

lithium.ibrav = 2

run_dos_triad(lithium, basepath="./testruns/dos_copper/", filename="copper", cpus=4)