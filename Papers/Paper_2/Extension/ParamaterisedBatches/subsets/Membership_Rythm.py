import sys
import os
from Utilities import ComeWhatRayUtil as CWR

rhythmBatchesLocation = "CoreConfigurations/Paper2Paramaters/Rhythm"
membershipBatchesLocation = "CoreConfigurations/Paper2Paramaters/Membership"
combinedDictionaryLocation = "CoreConfigurations/Paper2Paramaters/CombinedConstructedDirectories"
experimentName = "Papers/Paper_2/Extension/Experiment_18_Membership_Rhythmn.py"

if __name__ == '__main__':
    defaultTitle = ""

    additionalConfig = None
    if len(sys.argv) > 1:
        configuration = [sys.argv[i] for i in range(1, len(sys.argv))]
        additionalConfig = CWR.openFile(configuration[0])
        defaultTitle = additionalConfig["title"]

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

            os.system(f"python3 {experimentName} {configLocation}")
