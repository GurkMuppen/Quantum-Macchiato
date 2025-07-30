import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

df = pd.read_csv('./testruns/benchmark-setup-lattice/results.final', sep=';',skiprows=1, names=['ecutwfc','kpoints','celldm','cpus','runtime','energy'])
print(df)

dfs = []

unique_ecutwfc = df['ecutwfc'].unique()
for ecutwfc in unique_ecutwfc:
    temp = df.loc[df['ecutwfc'] == ecutwfc]
    print(temp)
    unique_kpoints = temp['kpoints'].unique()
    for kpoints in unique_kpoints:
        subset = temp[temp['kpoints'] == kpoints]
        dfs.append(subset)

for data in dfs:
    plt.plot(data['celldm'], data['energy'], label=f"ecut:{data['ecutwfc'].iloc[0]} k:{data['kpoints'].iloc[0]}")

plt.legend()
plt.title("Setup benchmark of calculation for lattice constant")
plt.xlabel("celldm (Bohr)")
plt.ylabel("Total energy (Ry)")

plt.show()