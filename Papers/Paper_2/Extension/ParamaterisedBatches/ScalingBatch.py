from Utilities import ComeWhatRayUtil as CWR
import os

scalingDirectories = "CoreConfigurations/Paper2Paramaters/Noise"
subsetsLocation = "Papers/Paper_2/Extension/ParamaterisedBatches/subsets"

if __name__ == '__main__':

    for scalingDirectory in os.listdir(scalingDirectories):

        scalingLocation = os.path.join(scalingDirectories, scalingDirectory)

        for experiment in os.listdir(subsetsLocation):
            print(CWR.extraLargeSpacer)
            print("NOISE EXPERIMENTS")
            print(CWR.extraLargeSpacer)
            print(f"Experiment: {experiment}")
            print(CWR.extraLargeSpacer)

            experimentLocaiton = os.path.join(subsetsLocation, experiment)

            os.system(f"python3 {experimentLocaiton} {scalingLocation}")

    print(CWR.extraLargeSpacer)
    print("END OF BATCH EXPERIMENTS")
