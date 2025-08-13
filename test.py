from qetool import *
from pseudo_tool import *
from dos_tool import *
from graph_tools.graph_dos import *

lithium = structure([atom_position("Cu", 0, 0, 0)])

lithium.ibrav = 2

path = path_object("./testruns/dos_copper/", "copper", prefix="copper")
run_dos_triad(lithium, path, cpus=4, localparams=[{}, {}, {"emin":0, "emax":20}])
dos_to_graph(path, "Copper")
