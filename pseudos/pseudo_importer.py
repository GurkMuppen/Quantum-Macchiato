import requests # requests for downloading files 
import re       # REGEX

def import_pseudo():
    atom = input("INPUT SPECIES NAME: ")
    mass = input("INPUT NUCLIDE MASS: ")
    url  = input("INPUT PSEUDO URL:   ")

    # Downloading the pseudopotential file
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception("URL COULD NOT BE READ")
    with open(f"./pseudos/{atom}.UPF", mode="w") as file:
        file.write(response.text)
    ecutwfc = 0
    ecutrho = 0
    nbnd = 0
    # Extract the suggested energy cutoff and number of bands/electrons
    with open(f"./pseudos/{atom}.UPF", "r") as file:
        search_step = 0
        # Run through all lines
        for i, line in enumerate(file):
            # Start searching for ecutoff after the "Functional" header
            if line.startswith("Functional:"):
                search_step = 1
                continue

            # Search for ecutwfc when inside the first header
            if search_step == 1:
                match = re.search(r"Suggested minimum cutoff for wavefunctions:\s*([\d.]+)\s*Ry", line)
                if match:
                    ecutwfc = float(match.group(1))
                    search_step = 2
                continue

            # Search for ecutrho when inside the first header
            if search_step == 2:
                match = re.search(r"Suggested minimum cutoff for wavefunctions:\s*([\d.]+)\s*Ry", line)
                if match:
                    ecutrho = float(match.group(1))
                    search_step = 3
                continue
            
            # Search for nbands if ecutoff has been found
            if search_step == 3:
                if not re.match(r'^\s', line):
                    nbnd = int(line)
                    break
    with open("./pseudos/pseudos.csv", "a") as file:
        file.writelines(f"\n{atom};{mass};{ecutwfc};{ecutrho};{nbnd};{atom}.UPF")
    print("IMPORT COMPLETED!")
    

import_pseudo()