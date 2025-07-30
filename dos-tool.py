from qetool import *

def run_dos_triad(basepath="./testruns/", filename="filename", globalparams: dict = {}, localparams:list[dict] = [{},{},{}], cpus=4, templates="./input_templates/DOS/"):
    """ Runs three qespresso simulations in series with a fixed structure.
        1. scf to approximate bands
        2. nscf to bake bands, with more k-points
        3. DOS calculation
    """

    # First scf calculation
    first_params = globalparams.update(localparams[0])
    run_simulation(program="pw.x", basepath=basepath, filename=f"{filename}_first", params=first_params, template_path=f"{templates}first.in")

    # Second nscf calculation
    second_params = globalparams.update(localparams[1])
    run_simulation(program="pw.x", basepath=basepath, filename=f"{filename}_second", params=second_params, template_path=f"{templates}second.in")

    # Last DOS calculation
    third_params = globalparams.update(localparams[2])
    run_simulation(program="dos.x", basepath=basepath, filename=f"{filename}_third", params=second_params, template_path=f"{templates}third.in")