from qetool import *

def run_dos_triad(structure : structure, basepath="./testruns/", prefix="filename", globalparams: dict = {}, localparams:list[dict] = [{},{},{}], cpus=4, templates="./input_templates/DOS/"):
    """ Runs three qespresso simulations in series with a fixed structure.
        1. scf to approximate bands
        2. nscf to bake bands, with more k-points
        3. DOS calculation
    """
    
    # First scf calculation
    tmp_params = globalparams
    tmp_params.update(localparams[0])

    path = path_object(basepath, f"{prefix}_first", prefix, f"{templates}first.in")
    path.input_file = path.render_input_file(tmp_params, structure)

    run_simulation(path, "pw.x", 4)

    # Second nscf calculation
    tmp_params = globalparams
    tmp_params.update(localparams[1])

    path = path_object(basepath, f"{prefix}_second", prefix, f"{templates}second.in")
    path.input_file = path.render_input_file(tmp_params, structure)

    run_simulation(path, "pw.x", 4)

    # Final DOS calculation
    tmp_params = globalparams
    tmp_params.update(localparams[2])

    path = path_object(basepath, f"{prefix}_third", prefix, f"{templates}third.in")
    path.input_file = path.render_input_file(tmp_params, structure)

    run_simulation(path, "pw.x", 4)