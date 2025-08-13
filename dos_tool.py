from qetool import *

def run_dos_triad(structure : structure, path : path_object, globalparams: dict = {}, localparams:list[dict] = [{},{},{}], cpus=4):
    """ Runs three qespresso simulations in series with a fixed structure.
        1. scf to approximate bands
        2. nscf to bake bands, with more k-points
        3. DOS calculation
        Requires the path_obj field containing: basepath, prefix and template_path
    """

    templates = path.template_path
    if not path.template_path.strip():
        templates = "./input_templates/DOS/"
    
    # First scf calculation
    tmp_params = globalparams
    tmp_params.update(localparams[0])

    path.filename = f"{path.prefix}_first"
    path.template_path = f"{templates}first.in"
    path.input_file = path.render_input_file(tmp_params, structure)

    run_simulation(path, "pw.x", cpus)

    # Second nscf calculation
    tmp_params = globalparams
    tmp_params.update(localparams[1])

    path.filename = f"{path.prefix}_second"
    path.template_path = f"{templates}second.in"
    path.input_file = path.render_input_file(tmp_params, structure)

    run_simulation(path, "pw.x", cpus)

    # Final DOS calculation
    tmp_params = globalparams
    tmp_params.update(localparams[2])

    path.filename = f"{path.prefix}_third"
    path.template_path = f"{templates}third.in"
    path.input_file = path.render_input_file(tmp_params, structure)

    run_simulation(path, "dos.x", cpus)

def get_fermi_level(dos_path):
    with open(dos_path) as file:
        first_line = file.readline()
        fermi_level = float(first_line[42:-3])
        return fermi_level

def get_bandgap(dos_path, fermi_level):
    bandgap = 0
    # Find the correct bandgap
    with open(dos_path) as file:
        for line in file :
            if line[0] == "#" : continue
            if float(line[10:20]) == 0 :
                bandgap += 1
            elif float(line[:7]) < fermi_level: 
                bandgap = 0
                continue
    return float(bandgap * 0.01)