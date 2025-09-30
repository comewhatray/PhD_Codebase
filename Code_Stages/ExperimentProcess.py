from Utilities import ComeWhatRayUtil as CWR
import os.path
import importlib
from parallelbar import progress_map

# The Default Experiment run if no details are provided
options = {
    "ExperimentName": "Testing",
    "ExperimentSignifier": "",
    "WorkspaceLocation": "Code_Stages/TestingWorkspace",
    "Dataset_Configuration": "Code_Stages/defaultDataset/Configurations/defaultConfig.json",
    "threading": True,
    "maxWorkers": 24,
    "Stages": [
        # Default Experiment
        # First Extract the midi file into points
        {
            "file": "Code_Stages/0:MIDI_Interface/MIDI_Extraction.py",
             "options": {
                "function": "convertMidiToPoints",
                "saveType": ".json"
             }
         },

        # Then transform it into a more usable representation
        {
            "file": "Code_Stages/1:MIDI_Representations/GeometricRepresentation.py",
             "options": {
                "function": "generateRepresentation",
                "saveType": ".json"
             }
        },
        # Minimum details needed for a stage
        # {
        #     "file": "",
        #     "options": {
        #         "function": "",
        #         "saveType": ""
        #     }
        # },

    ]
}

# Experiment Option Types
# ----------------------------------------------------------------------------------------------------------------------

# For experiments that require operating on a bunch of data
def batchExperiment(details=None):
    CWR.updateOldDictionaryEntriesWithNewDictionaryEntries(options, details)

    # Get Workspace Name
    WorkspaceName = CWR.appendDirectory(options["WorkspaceLocation"], [options["ExperimentSignifier"], options["ExperimentName"]])
    options["WorkspaceLocation"] = WorkspaceName
    # Deletes all contents of the default directory
    if options["ExperimentName"] == "Testing":
        CWR.deleteDirectory(options["WorkspaceLocation"])

    # Creates a directory for the workspace of an experiment
    CWR.ensureDirectory(options["WorkspaceLocation"])

    # Get Dataset Details
    if ".json" in options["Dataset_Configuration"]:
        datasetConfig = CWR.openFile(options["Dataset_Configuration"])
    else:
        datasetConfig = options["Dataset_Configuration"]

    LocationsDict = {
        "directory": options["WorkspaceLocation"],
        "Initial": {}
    }

    if "Labels" in datasetConfig:
        # If there is a set of labels

        # Converts the more human read able configuration file into the full directory paths
        for label in datasetConfig['Labels']:
            LocationsDict['Initial'][label] = []
            for file in datasetConfig['Labels'][label]:
                LocationsDict['Initial'][label].append(CWR.appendDirectory(datasetConfig['Directory'], file))


        previousLocation = "Initial"
        # Iterate through the processes
        for process in options["Stages"]:

            # Create the current task key if it doesn't exist
            processFunction = process['options']['function']

            if processFunction not in LocationsDict:
                LocationsDict[processFunction] = {}

            # Iterate through the labels
            for label in datasetConfig["Labels"]:

                # TODO MultiProcess
                # update midi location data

                if not options["threading"]:
                    iterationStep(LocationsDict, previousLocation, label, process)
                else:
                    multiProcessItterationStep(LocationsDict, previousLocation, label, process)

                # update where to find the relevant midis
            previousLocation = process['options']['function']

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
        previousLocation = "Initial"


        # Iterate through processes
        for process in options["Stages"]:

            # Create the current task key if it doesn't exist
            processFunction = process['options']['function']
            if processFunction not in LocationsDict:
                LocationsDict[processFunction] = {}

            iterationStep(LocationsDict, previousLocation, 'Default', process)
            #update where to find the relevant midis
            previousLocation = process['options']['function']

    return LocationsDict

# For Experiments that wish to compile data into new knowledge
def aggregationExperiment(locationsDict, details=None):
    if not options['threading']:
        print("Aggregation Experiment")
    lastLocation = locationsDict[options["Stages"][-1]['options']['function']]

    CWR.updateOldDictionaryEntriesWithNewDictionaryEntries(options, details)

    for process in options["Stages"]:

        processFunction = process['options']['function']

        if processFunction not in locationsDict:
            locationsDict[processFunction] = {}

        # locationsDict[processFunction] = {}

        results = processTask(lastLocation, process)

        lastLocation = processFunction


    # return


def queryAggregationExperiment(queryDataLocation, datasetDataLocation, details=None):
    if not options['threading']:
        print("Query Experiment")

    queryLastLocation = list(queryDataLocation)[-1]
    datasetLastLocation = list(datasetDataLocation)[-1]

    CWR.updateOldDictionaryEntriesWithNewDictionaryEntries(options, details)



    # print(queryLastLocation)
    # print(datasetLastLocation)

    dataset = {
        "querySet": queryDataLocation,
        "queryLastLocation": queryLastLocation,
        "dataSet": datasetDataLocation,
        "datasetLastLocation": datasetLastLocation,
    }

    outputDict = {}

    results = None

    for process in options["Stages"]:

        processFunction = process['options']['function']
        if processFunction not in outputDict:
            outputDict[processFunction] = {}

        results = processTask(dataset, process)


    return results


# Helper Methods
# ----------------------------------------------------------------------------------------------------------------------

# Iteratively goes through the dataset
def iterationStep(locationsDict, previousLocation, label, process):

    if not options['threading']:
        print("Iterative step")

    processName = process['options']['function']

    if not options['threading']:
        print(f"Process: {processName}")
        print(CWR.midSpacer)

    # Go through all locations for files
    for location in locationsDict[previousLocation][label]:
        # create the locations space to store the next locations
        if label not in locationsDict[processName]:
            locationsDict[processName][label] = []
        # save the results and store location
        saveLocation = CWR.appendDirectory(locationsDict['directory'], [label, process['options']['function']])
        CWR.ensureDirectory(saveLocation)
        # Getting the name of the file
        fileName = CWR.getFileNameFromPath(location)
        if process['options']['saveType'] is not None:
            fileName += process['options']['saveType']
        # getting final location and saving data
        fileLocation = CWR.appendDirectory(saveLocation, fileName)

        # If we don't want to multiProcess the approach
        if not os.path.exists(fileLocation):

            # checking that the results don't already exist
            results = processTask(location, process)

            # Saving results
            if process['options']['saveType'] is not None:
                CWR.saveFile(fileLocation, results)
                locationsDict[processName][label].append(fileLocation)

        else:
            if not options["threading"]:
                print(f"Results for {fileLocation} file already exist")

            if process['options']['saveType'] is not None:
                locationsDict[processName][label].append(fileLocation)


def multiProcessItterationStep(locationsDict, previousLocation, label, process):

    # List of arguments to be processed
    multiProcessArgsList = []

    # New Location to store the files to be worked on
    processName = process['options']['function']

    locationsDict[processName][label] = []

    # Ensures each piece
    saveLocation = CWR.appendDirectory(locationsDict['directory'], [label, process['options']['function']])
    CWR.ensureDirectory(saveLocation)

    # Going through each piece associated with the label
    for location in locationsDict[previousLocation][label]:

        # Getting the name of the file
        fileName = CWR.getFileNameFromPath(location)
        # Get the filetype
        if process['options']['saveType'] is not None:
            fileName += process['options']['saveType']

        # getting final location to save to
        finalLocation = CWR.appendDirectory(saveLocation, fileName)

        # If the finalLocation already exists just append that value to the locationsDict as we don't need to process it
        if os.path.exists(finalLocation):
            if not options["threading"]:
                print(f"Results for {finalLocation} file already exist")

            if process['options']['saveType'] is not None:
                locationsDict[processName][label].append(finalLocation)

        # Else we need to process this file.
        else:
            # Creating an entry in the multiProcessArgs list for each piece
            multiArg = (location, process, finalLocation)
            multiProcessArgsList.append(multiArg)

    # Run with multiprocessing
    print(f"MultiProcessing: Process-> {processName}| Label-> {label} | Size-> {len(multiProcessArgsList)}")
    results = progress_map(multiProcessTask, multiProcessArgsList, n_cpu=options["maxWorkers"], chunk_size=1)


    for i in range(len(results)):
        CWR.saveFile(multiProcessArgsList[i][2], results[i], printDisplay=False)
        locationsDict[processName][label].append(multiProcessArgsList[i][2])

    return

# Mask to transform our arguments into how the process task function reads it
def multiProcessTask(arguments):

    return processTask(arguments[0], arguments[1])

# Sends data to the relevant file
def processTask(location, process):

    # Import the relevant python file
    # This allows to name the directory of the file and automatically transform it into a way python understands
    processName = CWR.removeExtension(process["file"])
    processName = processName.replace('/', '.')

    stage = importlib.import_module(processName)

    # Calls the startProcess function of the relevant file
    return stage.startProcess(location, process['options'])

