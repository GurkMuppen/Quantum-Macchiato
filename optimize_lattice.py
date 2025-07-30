from qetool import *
import numpy as np
import pandas as pd

def manual_lattice_optimization(basepath, max_points, convergence=0.001, starting_celldms=[6.0, 7.0]):
    slope_left = -np.inf
    slope_right = -np.inf
    min = np.inf

    points = pd.DataFrame({'celldm':[], 'energy':[]})

    # Write into the batch output file
    with open(basepath + "results.final", "w") as outfile:
        outfile.write("ecutwfc; kpoints; celldm; cpus; runtime; energy\n")

    # Run through each of the starting celldms and run simulations, to begin optimization 
    for celldm in starting_celldms:
        energy = run_logged_simulation(basepath, filename=f'start{celldm}', params={'celldm':celldm}, cpus=4)
        new_row = pd.DataFrame({'celldm':[celldm], 'energy':[energy]})
        points = pd.concat([points, new_row], ignore_index=True).sort_values('celldm')

    next_celldm = find_next_celldm(points, convergence)

    while (next_celldm > 0 and len(points) <= max_points):
        energy = run_logged_simulation(basepath, filename=f'point{next_celldm}', params={'celldm':next_celldm}, cpus=4)
        new_row = pd.DataFrame({'celldm':[next_celldm], 'energy':[energy]})
        points = pd.concat([points, new_row], ignore_index=True).sort_values('celldm')
        next_celldm = find_next_celldm(points, convergence)
    if (next_celldm < 0):
        return float(points.loc[points['energy'].idxmin()]['celldm'])
    return -1 # NOT CONVERGED

        
def find_next_celldm(points=type(pd.DataFrame), convergence=0.005):
    dy_left = -np.inf
    dy_right = np.inf
    points = points.sort_values('celldm').reset_index(drop=True)
    min_index = points['energy'].idxmin()

    if min_index != 0:
        dy_left = points.loc[min_index - 1]['energy'] - points.loc[min_index]['energy']
    else:
        celldm_step = points.loc[min_index + 1]['celldm'] - points.loc[min_index]['celldm']
        return points.loc[min_index]['celldm'] - celldm_step
    
    if min_index != len(points) - 1:
        dy_right = points.loc[min_index + 1]['energy'] - points.loc[min_index]['energy']
    else:
        celldm_step = points.loc[min_index]['celldm'] - points.loc[min_index - 1]['celldm']
        return points.loc[min_index]['celldm'] + celldm_step
    
    if (-dy_left > convergence or dy_right > convergence):
        dy_sum = dy_left + dy_right
        if dy_sum > 0:
            return (points.loc[min_index]['celldm'] + points.loc[min_index - 1]['celldm']) / 2
        else:
            return (points.loc[min_index]['celldm'] + points.loc[min_index + 1]['celldm']) / 2
        
    print("--RESULTS--")
    print("CONVERGENCE ACHIEVED")
    print(f"Optimal celldm: {points.loc[min_index]['celldm']}")
    print(points)
    return -1 # EXIT

manual_lattice_optimization(basepath="./tmp/opt/", max_points=10)