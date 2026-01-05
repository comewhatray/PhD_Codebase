import os
import sys
from Utilities import ComeWhatRayUtil as CWR

membershipBatchesLocation = "CoreConfigurations/Paper2Paramaters/Membership"
combinedDictionaryLocation = "CoreConfigurations/Paper2Paramaters/CombinedConstructedDirectories"
membershipExperiment = "Papers/Paper_2/Extension/Experiment_15_Breathing_membership.py"

if __name__ == '__main__':

    additionalConfig = None
    if len(sys.argv) > 1:
        configuration = [sys.argv[i] for i in range(1, len(sys.argv))]
        print(configuration)
        additionalConfig = CWR.openFile(configuration[0])
        priorTitle = additionalConfig["title"]

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

        os.system(f"python3 {membershipExperiment} {configDetails}")


