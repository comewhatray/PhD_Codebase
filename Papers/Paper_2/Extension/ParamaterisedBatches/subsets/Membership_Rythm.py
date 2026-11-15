import sys
import os
from Utilities import ComeWhatRayUtil as CWR

rhythmBatchesLocation = "CoreConfigurations/Paper2Paramaters/Rhythm"
membershipBatchesLocation = "CoreConfigurations/Paper2Paramaters/Membership"
combinedDictionaryLocation = "CoreConfigurations/Paper2Paramaters/CombinedConstructedDirectories"
experimentName = "Papers/Paper_2/Extension/Experiment_18_Membership_Rhythmn.py"


def subsetConfigurations(Location, topX=10):
    listings = CWR.openFile(Location)

    listings = listings[:topX]
    configNames = []
    for listing in listings:
        configNames.append(listing[0])

    return configNames

if __name__ == '__main__':
    defaultTitle = ""
    reducedListings = False

    # If there are additional config options
    additionalConfig = None
    print(sys.argv)
    if len(sys.argv) > 1:
        configuration = [sys.argv[i] for i in range(1, len(sys.argv))]
        additionalConfig = CWR.openFile(configuration[0])
        defaultTitle = additionalConfig["title"]

        # This is where we will allow the restrictions to occur
        if len(configuration) > 1:

            reducedListings = True
            reducedList = subsetConfigurations(configuration[1])
            print("ReducedList")
            print(reducedList)

            defaultTitle += f"_{CWR.getFileNameFromPath(configuration[1])}"
            print(defaultTitle)


    for memberConfig in os.listdir(membershipBatchesLocation):
        memberConfigDetails = CWR.openFile(os.path.join(membershipBatchesLocation, memberConfig))

        for rhythmConfig in os.listdir(rhythmBatchesLocation):
            rhythmConfigDetails = CWR.openFile(os.path.join(rhythmBatchesLocation, rhythmConfig))


            titleUpdate = f"{defaultTitle}-{memberConfigDetails['title']}-{rhythmConfigDetails['title']}"
            configLocation = os.path.join(combinedDictionaryLocation, titleUpdate)
            configLocation += ".json"

            if not os.path.exists(configLocation):

                if additionalConfig is not None:
                    combinedDicts = [additionalConfig,memberConfigDetails,rhythmConfigDetails]
                else:
                    combinedDicts = [memberConfigDetails,rhythmConfigDetails]

                combinedDictionary = CWR.combineDictionaries(combinedDicts)
                combinedDictionary["title"] = titleUpdate
                CWR.saveFile(configLocation, combinedDictionary)


            # print(f"reducedListing: {reducedListings}")
            if reducedListings:
                for reduction in reducedList:

                    reduction += ".json"
                    # print(f"is {reduction} in {configLocation}")
                    if reduction in configLocation:
                        # print(True)
                        os.system(f"python3 {experimentName} {configLocation}")
                    # else:
                        # print(False)
            else:
                os.system(f"python3 {experimentName} {configLocation}")



