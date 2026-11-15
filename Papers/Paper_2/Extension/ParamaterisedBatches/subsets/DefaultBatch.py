import sys
import os

defaultExperiment = "Papers/Paper_2/Extension/Experiment_17_Default_Overlap.py"


# def subsetConfigurations(Location, topX=30):
#     listings = CWR.openFile(Location")
#
#     listings = listings[:topX]
#     configNames = []
#     for listing in listings:
#         configNames.append(listing[0])
#
#     return configNames

if __name__ == '__main__':

    additionalConfig = None
    if len(sys.argv) > 1:
        configuration = [sys.argv[i] for i in range(1, len(sys.argv))]
        additionalConfig = configuration[0]
        print(additionalConfig)
        os.system(f"python3 {defaultExperiment} {additionalConfig}")

    os.system(f"python3 {defaultExperiment} ")


