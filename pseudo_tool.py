import pandas as pd

def get_pseudo_data(atoms : list[str]):
    df = pd.read_csv("./pseudos/pseudos.csv", delimiter=';').set_index("species")
    return df.loc[atoms]

def get_optimal_ecuts(species : list[str], margin_factor = 1.0):
    df = pd.read_csv("./pseudos/pseudos.csv", delimiter=';').set_index("species")
    selection = df.loc[species]
    max_wfc = float(selection["ecutwfc"].max()) * margin_factor
    max_rho = float(selection["ecutrho"].max()) * margin_factor
    return {"ecutwfc":max_wfc, "ecutrho":max_rho}

def define_species(pseudo_data : pd.DataFrame):
    output = pseudo_data[['weight', 'path']].to_string(header=False)
    return "\n".join(output.splitlines()[1:])


