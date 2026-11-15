import os
import sys
from Utilities import ComeWhatRayUtil as CWR

membershipBatchesLocation = "CoreConfigurations/Paper2Paramaters/Membership"
combinedDictionaryLocation = "CoreConfigurations/Paper2Paramaters/CombinedConstructedDirectories"
membershipExperiment = "Papers/Paper_2/Extension/Experiment_15_Breathing_membership.py"


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
        print(configuration)
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

    for membershipConfig in os.listdir(membershipBatchesLocation):
        configDetails = os.path.join(membershipBatchesLocation, membershipConfig)

        if additionalConfig is not None:
            membershipConfigDetails = CWR.openFile(configDetails)

            combinedTitle = f"{additionalConfig['title']}-{membershipConfigDetails['title']}"
            combinedLocation = os.path.join(combinedDictionaryLocation, combinedTitle)
            combinedLocation += ".json"

            if not os.path.exists(combinedLocation):
                combinedDicts = [additionalConfig, membershipConfigDetails]
                combinedDictionary = CWR.combineDictionaries(combinedDicts)
                combinedDictionary["title"] = combinedTitle
                CWR.saveFile(combinedLocation, combinedDictionary)

            os.system(f"python3 {membershipExperiment} {combinedLocation}")

            # print(f"reducedListing: {reducedListings}")
            if reducedListings:
                for reduction in reducedList:

                    reduction += ".json"
                    # print(f"is {reduction} in {configLocation}")
                    if reduction in combinedLocation:
                        # print(True)
                        os.system(f"python3 {membershipExperiment} {combinedLocation}")
                    # else:
                    # print(False)
            else:
                os.system(f"python3 {membershipExperiment} {combinedLocation}")

        os.system(f"python3 {membershipExperiment} {configDetails}")


