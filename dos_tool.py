from qetool import *

def run_dos_triad(structure : structure, basepath="./testruns/", filename="filename", globalparams: dict = {}, localparams:list[dict] = [{},{},{}], cpus=4, templates="./input_templates/DOS/"):
    """ Runs three qespresso simulations in series with a fixed structure.
        1. scf to approximate bands
        2. nscf to bake bands, with more k-points
        3. DOS calculation
    """

    # First scf calculation
    tmp_params = globalparams
    tmp_params.update(localparams[0])
    simulate_structure(structure, program="pw.x", basepath=basepath, filename=f"{filename}_first", params=tmp_params, template_path=f"{templates}first.in", cpus=cpus)

    # Second nscf calculation
    tmp_params = globalparams
    tmp_params.update(localparams[1])
    simulate_structure(structure, program="pw.x", basepath=basepath, filename=f"{filename}_second", params=tmp_params, template_path=f"{templates}second.in", cpus=cpus)

    # Final DOS calculation
    tmp_params = globalparams
    tmp_params.update(localparams[1])
    simulate_structure(structure, program="dos.x", basepath=basepath, filename=f"{filename}_third", params=tmp_params, template_path=f"{templates}third.in", cpus=cpus)