from Utilities import ComeWhatRayUtil as CWR
import os

experimentsToRun = [
    # "Papers/Paper_2/Extension/Experiment_13_FragmentisationCheck.py",
    "Papers/Paper_2/Extension/Experiment_14_FragAndMember.py",
    "Papers/Paper_2/Extension/Experiment_15_Breathing_membership.py",
    "Papers/Paper_2/Extension/Experiment_16_Kyna_Membership.py",
    # "Papers/Paper_2/Extension/Experiment_17_Default_Overlap.py"
]

itterations = 1

# modificationParameters = "CoreConfigurations/membership_0.5.json"
# modificationParameters = "CoreConfigurations/membership_0.9.json"
modificationParameters = "CoreConfigurations/bounding_and_membership_0.5.json"

if __name__ == '__main__':

    for i in range(itterations):
        for experiment in experimentsToRun:

            print(CWR.extraLargeSpacer)
            print(f"Experiment: {experiment}")
            print(f"Itteration: {i}")
            print(CWR.extraLargeSpacer)

            experimentName = CWR.getFileNameFromPath(experiment)

            os.system(f"python3 {experiment} {modificationParameters}")

