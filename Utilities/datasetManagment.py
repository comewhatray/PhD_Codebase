import os
from Utilities import ComeWhatRayUtil as CWR
import shutil

dsetOrigin = "/Users/rayconlin/Downloads/Classical Music MIDI"
dsetTarget = "Papers/Paper_3/Datasets/ClassicalComposersDataset/Midis"
confLocation = "Papers/Paper_3/Datasets/ClassicalComposersDataset/Configurations/All.json"

datasetConfiguration = {

    "Title": "",
    "Directory": "",
    "Labels": {

    }

}

def exampleTagging(datasetOrigin, datasetTarget, configurationLocation):
    print("Naming files in Directory")

    # Updating the Directory to be where we want to store the dataset
    datasetConfiguration["Directory"] = datasetTarget

    # Get the labels of the dataset
    locations = [x[0] for x in os.walk(datasetOrigin)]
    locations.pop(0)

    # Counting how many works are in the dataset
    totalCount = 0

    # Iterate through each label
    for location in locations:

        # Get the name of the label and create that label in the configuration json
        labelName = CWR.getFileNameFromPath(location)
        datasetConfiguration["Labels"][labelName] = []

        # Get list of files in a label
        files = os.listdir(location)

        # File Count
        fileCount = 1
        for file in files:

            # gets the file original location
            toUpdate = os.path.join(location, file)

            # creates the name of the file target location
            updateName = labelName + "_" + str(fileCount) + ".mid"

            # changes the name of the original data
            # update = CWR.appendDirectory(location, updateName)

            # Adds dataset details to the configuration
            datasetConfiguration["Labels"][labelName].append(updateName)

            # os.rename(toUpdate, update)

            shutil.copyfile(toUpdate, CWR.appendDirectory(datasetTarget, updateName))

            fileCount += 1
            totalCount += 1

    print(totalCount)
    print(datasetConfiguration)
    CWR.saveFile(configurationLocation, datasetConfiguration)

# exampleTagging(dsetOrigin, dsetTarget, confLocation)