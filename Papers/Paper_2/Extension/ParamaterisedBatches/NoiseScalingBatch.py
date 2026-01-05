from Utilities import ComeWhatRayUtil as CWR
import os

noiseDirectories = "CoreConfigurations/Paper2Paramaters/Noise"
scalingDirectories = "CoreConfigurations/Paper2Paramaters/Scaling"
combinedDictionaryLocation = "CoreConfigurations/Paper2Paramaters/CombinedConstructedDirectories"
subsetsLocation = "Papers/Paper_2/Extension/ParamaterisedBatches/subsets"

if __name__ == '__main__':

    for noiseDirectory in os.listdir(noiseDirectories):
        noiseLocation = os.path.join(noiseDirectories, noiseDirectory)

        for scalingDirectory in os.listdir(scalingDirectories):
            scalingLocation = os.path.join(scalingDirectories, scalingDirectory)

            noiseDetails = CWR.openFile(noiseLocation)
            scalingDetails = CWR.openFile(scalingLocation)
            combinedName = f"{noiseDetails["title"]}-{scalingDetails["title"]}"

            combinedFile = combinedName+".json"
            combinedLocation = os.path.join(combinedDictionaryLocation, combinedFile)

            if not os.path.exists(combinedLocation):
                combinedDicts = [noiseDetails, scalingDetails]
                combinedDictionary = CWR.combineDictionaries(combinedDicts)
                combinedDictionary["title"] = combinedName
                CWR.saveFile(combinedLocation, combinedDictionary)


            for experiment in os.listdir(subsetsLocation):
                print(CWR.extraLargeSpacer)
                print("NOISE EXPERIMENTS")
                print(CWR.extraLargeSpacer)
                print(f"Experiment: {experiment}")
                print(CWR.extraLargeSpacer)

                experimentLocaiton = os.path.join(subsetsLocation, experiment)
                os.system(f"python3 {experimentLocaiton} {combinedLocation}")

    print(CWR.extraLargeSpacer)
    print("END OF BATCH EXPERIMENTS")
