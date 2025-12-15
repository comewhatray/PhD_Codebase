from Utilities import ComeWhatRayUtil as CWR
import os

experimentsToRun = [
    "Papers/Paper_2/Extension/Experiment_15_Breathing_membership.py",
    "Papers/Paper_2/Extension/Experiment_17_Default_Overlap.py",
    "Papers/Paper_2/Extension/Experiment_18_Membership_Rhythmn.py",
    "Papers/Paper_2/Extension/Experiment_19_NoDeletionCostPrevious.py"

]

itterations = 1
modificationParameters = "CoreConfigurations/boundingYscale4.json"

if __name__ == '__main__':

    for i in range(itterations):
        for experiment in experimentsToRun:

            print(CWR.extraLargeSpacer)
            print(f"Experiment: {experiment}")
            print(f"Itteration: {i}")
            print(CWR.extraLargeSpacer)

            experimentName = CWR.getFileNameFromPath(experiment)

            os.system(f"python3 {experiment} {modificationParameters}")

