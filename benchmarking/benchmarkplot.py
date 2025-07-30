import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# Define your parameters
convergence_limit = 0.0005

# Read ecutoff and k-point values from the results.final file
ecutoff_values = []
kpoint_values = []
matrix = []


df = pd.read_csv("./testruns/benchmark/results.final", sep=";", skiprows=1, names=["ecutwfc", "k-points", "celldm", "cpus", "runtime", "energy"])
# Pivot runtime and energy separately
runtime_matrix = df.pivot(index="k-points", columns="ecutwfc", values="runtime").fillna(0).to_numpy()
energy_matrix = df.pivot(index="k-points", columns="ecutwfc", values="energy").fillna(0).to_numpy()

# Normalize both to [0, 1] for RGB encoding
runtime_norm = (runtime_matrix  / runtime_matrix.max())
converged_energy = (energy_matrix[-1, -1] + energy_matrix[-2, -1] + energy_matrix[-1, -2]) / 3.0
print(converged_energy)

energy_norm = np.clip(1 - (abs((energy_matrix / converged_energy) - 1) / convergence_limit), 0, 1)
print(energy_norm)

# Create RGB image: R = runtime, G = energy, B = optional (can be zeros)
rgb_image = np.stack([runtime_norm, energy_norm, np.zeros_like(runtime_norm)], axis=2)

with open('./testruns/benchmark/results.final', 'r') as f:
    lines = f.readlines()[1:]
    for line in lines:
        if line.strip():
            parts = line.strip().split(";")
            # Assuming ecutoff is in the first column and k-point in the second
            ecutoff = float(parts[0])
            kpoints = float(parts[1])
            ecutoff_values.append(ecutoff)
            kpoint_values.append(kpoints)
            # Store as tuple (ecutoff, kpoints, runtime)

# Get unique sorted values for grid axes
x_params = sorted(set(ecutoff_values))
y_params = sorted(set(kpoint_values))


# Create a grid
fig, ax = plt.subplots()
ax.imshow(rgb_image, origin="lower", aspect="auto")

# Formatting
#ax.set_xlim(0, 5)
#ax.set_ylim(0, 5)
ax.set_xticks(np.arange(0, len(x_params), 1))
ax.set_yticks(np.arange(0, len(y_params), 1))
ax.set_xticklabels([f"{x:.0f}" for x in x_params])
ax.set_yticklabels([f"{y:.0f}" for y in y_params])
ax.set_xlabel("Ecutwfc")
ax.set_ylabel("K-points")
ax.set_aspect('equal')

plt.title("Simulation parameter benchmark, with a convergence limit of 0.05%")
plt.grid(False)
plt.show()
