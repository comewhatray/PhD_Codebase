from Utilities import ComeWhatRayUtil as CWR
import os

subsetsLocation = "Papers/Paper_2/Extension/ParamaterisedBatches/subsets"

if __name__ == '__main__':

    for experiment in os.listdir(subsetsLocation):

        print(CWR.extraLargeSpacer)
        print("DEFAULT EXPERIMENTS")
        print(CWR.extraLargeSpacer)
        print(f"Experiment: {experiment}")
        print(CWR.extraLargeSpacer)

        experimentLocaiton = os.path.join(subsetsLocation, experiment)

        os.system(f"python3 {experimentLocaiton}")

    print(CWR.extraLargeSpacer)
    print("END OF BATCH EXPERIMENTS")
