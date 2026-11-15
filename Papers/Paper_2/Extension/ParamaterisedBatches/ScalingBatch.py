from Utilities import ComeWhatRayUtil as CWR
import os

scalingDirectories = "CoreConfigurations/Paper2Paramaters/Scaling"
subsetsLocation = "Papers/Paper_2/Extension/ParamaterisedBatches/subsets"

subsetConfigs = True
subsetConfigLocation = "Papers/Paper_2/Extension/OnceOffStorage/NoScale/BestResults_0.7.pkl"
tempFileDirectory = "CoreConfigurations/Paper2Paramaters/CombinedConstructedDirectories"
subsetTemp = "ExperimentResults/scale_x1_y6_BestResults_0.7-membership_0.7-rhythm_ins_1_del_0.json"

if __name__ == '__main__':

    subsetConfiguration = None
    if subsetConfigs:
        subsetConfiguration = subsetConfigLocation

    for scalingDirectory in os.listdir(scalingDirectories):

        scalingLocation = os.path.join(scalingDirectories, scalingDirectory)

        for experiment in os.listdir(subsetsLocation):
            print(CWR.extraLargeSpacer)
            print("Scaling EXPERIMENTS")
            print(CWR.extraLargeSpacer)
            print(f"Experiment: {experiment}")
            print(CWR.extraLargeSpacer)

            experimentLocaiton = os.path.join(subsetsLocation, experiment)

            if subsetConfiguration is None:
                os.system(f"python3 {experimentLocaiton} {scalingLocation}")

            else:
                os.system(f"python3 {experimentLocaiton} {scalingLocation} {subsetConfiguration}")

    print(CWR.extraLargeSpacer)
    print("END OF BATCH EXPERIMENTS")


