import pandas as pd

def get_pseudo_data(atoms : list[str]):
    df = pd.read_csv("./pseudos/pseudos.csv", delimiter=';').set_index("species")
    return df.loc[atoms]

def define_species(pseudo_data : pd.DataFrame):
    output = pseudo_data[['weight', 'path']].to_string(header=False)
    return "\n".join(output.splitlines()[1:])

data = get_pseudo_data(["Cu", "Test"])
print(define_species(data))