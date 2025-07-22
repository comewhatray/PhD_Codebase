from Utilities import ComeWhatRayUtil as CWR
import os
import sys

experimentsToRun = [
    "Papers/Paper_3/Experiments/Experiment_13_CustomP.py",
    "Papers/Paper_3/Experiments/Experiment_14_ComparisonP.py"
]

itterations = 5

if __name__ == '__main__':

    for i in range(itterations):
        for experiment in experimentsToRun:
            print(CWR.extraLargeSpacer)
            print(f"Experiment: {experiment}")
            print(f"Itteration: {i}")
            print(CWR.extraLargeSpacer)

            os.system(f"python3 {experiment}")

