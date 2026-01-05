from Utilities import ComeWhatRayUtil as CWR
import os

noiseDirectories = "CoreConfigurations/Paper2Paramaters/Noise"
subsetsLocation = "Papers/Paper_2/Extension/ParamaterisedBatches/subsets"

if __name__ == '__main__':

    for noiseDirectory in os.listdir(noiseDirectories):

        noiseLocation = os.path.join(noiseDirectories, noiseDirectory)

        for experiment in os.listdir(subsetsLocation):
            print(CWR.extraLargeSpacer)
            print("NOISE EXPERIMENTS")
            print(CWR.extraLargeSpacer)
            print(f"Experiment: {experiment}")
            print(CWR.extraLargeSpacer)

            experimentLocaiton = os.path.join(subsetsLocation, experiment)

            os.system(f"python3 {experimentLocaiton} {noiseLocation}")

    print(CWR.extraLargeSpacer)
    print("END OF BATCH EXPERIMENTS")
