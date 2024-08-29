import os.path

from Utilities import ComeWhatRayUtil as CWR
import importlib

options = {
    "ExperimentName": "default",
    "WorkspaceLocation": "Code_Stages/DefaultWorkspace/",
    "Dataset_Configuration": "Code_Stages/defaultDataset/Configurations/defaultConfig.json",
    "Stages": [
        # Default Experiment
        # First Extract the midi file into points
        {"file": "Code_Stages.0:MIDI_Interface.MIDI_Extraction",
         "function": "convertMidiToPoints",
         "options": {
             "saveType": ".json"
         }},

        # Then transform it into a more usable representation
        {"file": "Code_Stages.1:MIDI_Representations.GeometricRepresentation",
         "function": "generateRepresentation",
         "options": {
            "saveType": ".json"
         }},
        # {"file": "",
        #  "function": ""
        #  "options": {
        #  },

    ]
}

def begin(details=None):
    CWR.updateOldDictionaryEntriesWithNewDictionaryEntries(options, details)

    # Get Workspace Name
    options["WorkspaceLocation"] = options["WorkspaceLocation"] + "/" + options["ExperimentName"]
    # Deletes all contents of the default directory
    if options["ExperimentName"] == "default":
        CWR.deleteDirectory(options["WorkspaceLocation"])

    # Creates a directory for the workspace of an experiment
    CWR.ensureDirectory(options["WorkspaceLocation"])

    # Get Dataset Details
    datasetConfig = CWR.openFile(options["Dataset_Configuration"])

    LocationsDict = {
        "directory": options["WorkspaceLocation"],
        "Initial": {}
    }


    # Code Stage Imports
    # MIDI_Interface = importlib.import_module(options["Midi_Interface"])
    # MIDI_Representation = importlib.import_module(options["MIDI_Representation"])
    # Pattern_Extraction = importlib.import_module(options["Pattern_Extraction"]["Location"])
    # Pattern_Encoding = importlib.import_module(options["Pattern_Encoding"]["Location"])
    # Similarity_Measure = importlib.import_module(options["Similarity_Measure"])

    if "Labels" in datasetConfig:
        # If there is a set of labels

        currentTask = "Initial"
        # Iterate through the processes
        for process in options["Stages"]:
            # Iterate through the labels
            for label in datasetConfig["Labels"]:
                for MIDI in datasetConfig["MIDIS"]:
                    LocationsDict['Initial'][label].append(CWR.appendDirectory(datasetConfig["Directory"], MIDI))

                # update midi location data

                iterationStep(LocationsDict, label, currentTask, process)
                # update where to find the relevant midis
            currentTask = process['function']

    else:
        # If there is no labels (Just a list of midis)
        print(CWR.extraLargeSpacer)
        print("Just Testing functions atm")
        print("Just a list of midis")
        print(CWR.largeSpacer)

        # This refers to the location of where each midi is along the process

        LocationsDict['Initial']["Default"] = []

        for MIDI in datasetConfig["MIDIS"]:
            LocationsDict['Initial']["Default"].append(CWR.appendDirectory(datasetConfig["Directory"], MIDI))
        currentTask = "Initial"

        # Itterate through processes
        for process in options["Stages"]:
            iterationStep(LocationsDict, 'Default', currentTask, process)
            #update where to find the relevant midis
            currentTask = process['function']



def iterationStep(locationsDict, label, task, process):
    print("Iterative step")
    print(f"Process: {process['function']}")
    print(CWR.midSpacer)

    # Go through all locations for files
    for location in locationsDict[task][label]:
        # create the locations space to store the next locations
        if process['file'] not in locationsDict:
            locationsDict[process['function']] = {
                label: []
            }
        # save the results and store location
        saveLocation = CWR.appendDirectory(locationsDict['directory'], [label, process['function']])
        CWR.ensureDirectory(saveLocation)
        # Getting the name of the file
        fileName = CWR.getFileNameFromPath(location)
        fileName += process['options']['saveType']
        # getting final location and saving data
        fileLocation = CWR.appendDirectory(saveLocation, fileName)

        if not os.path.exists(fileLocation):

            # checking that the results don't already exist
            results = processTask(location, process)

            # Saving results
            CWR.saveFile(fileLocation, results)
            locationsDict[process['function']][label].append(fileLocation)

        else:
            "Results for current file already exist"


def processTask(work, process):

    # Import the relevant python file
    stage = importlib.import_module(process["file"])
    # Get the relevant python function from that file
    sFunction = getattr(stage, process['function'])
    # Send the relevant options to that function and generate the results
    results = sFunction(work, process['options'])

    return results

begin()