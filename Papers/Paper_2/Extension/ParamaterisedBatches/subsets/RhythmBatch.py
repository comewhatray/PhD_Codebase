import os
import sys
from Utilities import ComeWhatRayUtil as CWR

rhythmBatchesLocation = "CoreConfigurations/Paper2Paramaters/Rhythm"
combinedDictionaryLocation = "CoreConfigurations/Paper2Paramaters/CombinedConstructedDirectories"
rhythmExperiment = "Papers/Paper_2/Extension/Experiment_21_Rhythm.py"

if __name__ == '__main__':

    additionalConfig = None
    if len(sys.argv) > 1:
        configuration = [sys.argv[i] for i in range(1, len(sys.argv))]
        additionalConfig = CWR.openFile(configuration[0])
        priorTitle = additionalConfig["title"]

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

            os.system(f"python3 {rhythmExperiment} {combinedLocation}")

        os.system(f"python3 {rhythmExperiment} {configDetails}")


