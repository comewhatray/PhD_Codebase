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

# Given a folder of data such that each sub folder is a label and contains all examples of that label.
# Create a dataset configuration json file and move the data to a specified location
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

            CWR.moveFile(toUpdate, CWR.appendDirectory(datasetTarget, updateName))

            fileCount += 1
            totalCount += 1

    print(totalCount)
    print(datasetConfiguration)
    CWR.saveFile(configurationLocation, datasetConfiguration)

# An inelegent method for getting my new way of structuring data to work with older methods I don't want to update
def convertDatasetToOldFormat(dataset):
    oldFormat = []
    for label in dataset:

        for piece in dataset[label]:

            Name = CWR.getFileNameFromPath(piece)
            Label = label
            Location = piece

            oldFormat.append({
                "Name": Name,
                "Label": Label,
                "Location": Location
            })

    return oldFormat


def GNNStructureCreation(ExperimentDetails):

    rawConfiguration = CWR.getFileNameFromPath(ExperimentDetails["Dataset_Configuration"], includeExtension=True)

    fileRoot = CWR.appendDirectory(ExperimentDetails["WorkspaceLocation"],
                                   ["MidiTensors", ExperimentDetails["ExperimentSignifier"], CWR.removeExtension(rawConfiguration)])
    CWR.ensureDirectory(fileRoot)
    rawLocation = CWR.appendDirectory(fileRoot, "raw")
    CWR.ensureDirectory(rawLocation)

    configuration = CWR.openFile(ExperimentDetails["Dataset_Configuration"])
    CWR.saveFile(CWR.appendDirectory(rawLocation, rawConfiguration), configuration)

    return fileRoot, rawConfiguration

# exampleTagging(dsetOrigin, dsetTarget, confLocation)