import os
import sys
from Utilities import ComeWhatRayUtil as CWR

rhythmBatchesLocation = "CoreConfigurations/Paper2Paramaters/Rhythm"
combinedDictionaryLocation = "CoreConfigurations/Paper2Paramaters/CombinedConstructedDirectories"
rhythmExperiment = "Papers/Paper_2/Extension/Experiment_21_Rhythm.py"

def subsetConfigurations(Location, topX=10):
    listings = CWR.openFile(Location)

    listings = listings[:topX]
    configNames = []
    for listing in listings:
        configNames.append(listing[0])

    return configNames

if __name__ == '__main__':

    additionalConfig = None
    reducedListings = False
    if len(sys.argv) > 1:
        configuration = [sys.argv[i] for i in range(1, len(sys.argv))]
        additionalConfig = CWR.openFile(configuration[0])
        priorTitle = additionalConfig["title"]

        # This is where we will allow the restrictions to occur
        if len(configuration) > 1:
            reducedListings = True
            reducedList = subsetConfigurations(configuration[1])
            # print("ReducedList")
            # print(reducedList)
            priorTitle += f"_{CWR.getFileNameFromPath(configuration[1])}"
            print(priorTitle)

    for rhythmConfig in os.listdir(rhythmBatchesLocation):
        configDetails = os.path.join(rhythmBatchesLocation, rhythmConfig)

        if additionalConfig is not None:
            rythmConfigDetails = CWR.openFile(configDetails)

            combinedTitle = f"{additionalConfig['title']}-{rythmConfigDetails['title']}"
            combinedLocation = os.path.join(combinedDictionaryLocation, combinedTitle)
            combinedLocation += ".json"

            if not os.path.exists(combinedLocation):
                combinedDicts = [additionalConfig, rythmConfigDetails]
                combinedDictionary = CWR.combineDictionaries(combinedDicts)
                combinedDictionary["title"] = combinedTitle
                CWR.saveFile(combinedLocation, combinedDictionary)

            # os.system(f"python3 {rhythmExperiment} {combinedLocation}")

            if reducedListings:
                for reduction in reducedList:

                    reduction += ".json"
                    # print(f"is {reduction} in {configLocation}")
                    if reduction in combinedLocation:
                        # print(True)
                        os.system(f"python3 {rhythmExperiment} {combinedLocation}")
                    # else:
                    # print(False)
            else:
                os.system(f"python3 {rhythmExperiment} {combinedLocation}")



        os.system(f"python3 {rhythmExperiment} {configDetails}")


