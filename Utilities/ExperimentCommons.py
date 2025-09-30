from Utilities import ComeWhatRayUtil as CWR
from Code_Stages import ExperimentProcess as EP
from Utilities import parrallelism as PM

def runExperiment(queryDetails, datasetDetails, aggregationDetails, systemArgs=None):

    multiProcess = queryDetails["threading"]


    if systemArgs is not None:

        experimentModification = CWR.openFile(systemArgs)

        # Update Identifier to create new Directories
        queryDetails["ExperimentSignifier"] = experimentModification["title"]
        datasetDetails["ExperimentSignifier"] = experimentModification["title"]

        # Update Query with modifications
        if "queryModifications" in experimentModification:
            CWR.updateOldDictionaryEntriesWithNewDictionaryEntries(queryDetails, experimentModification["queryModifications"])

        # Update Dataset with modifications
        if "datasetModification" in experimentModification:
            CWR.updateOldDictionaryEntriesWithNewDictionaryEntries(datasetDetails, experimentModification["datasetModifications"])

        # Update Aggregation with modifications
        if "aggregationModification" in experimentModification:
            for stage in aggregationDetails["Stages"]:
                stage["options"]["saveResultsLabel"] = experimentModification["title"]
                CWR.updateOldDictionaryEntriesWithNewDictionaryEntries(stage["options"], experimentModification["aggregationModification"])



    # Query Run
    # Where to save
    querySaveLoc = CWR.appendDirectory(queryDetails["WorkspaceLocation"], "QueryLocationData.json")
    # Run Experiment
    locationDetails = EP.batchExperiment(queryDetails)
    # Save the details of the experiment
    CWR.saveFile(querySaveLoc, locationDetails)

    # Dataset Run
    # Where to save
    datasetSaveLoc = CWR.appendDirectory(datasetDetails["WorkspaceLocation"], "DatasetLocationData.json")
    # Run Experiment
    locationDetails = EP.batchExperiment(datasetDetails)
    # Save the details of the experiment
    CWR.saveFile(datasetSaveLoc, locationDetails)

    queryDeets = CWR.openFile(querySaveLoc)
    datasetDeets = CWR.openFile(datasetSaveLoc)

    # MultiProcess
    if multiProcess:
        PM.threadedAnalysis(queryDeets, datasetDeets, aggregationDetails)
    else:
        # SingleProcess
        experimentResults = EP.queryAggregationExperiment(CWR.openFile(querySaveLoc), CWR.openFile(datasetSaveLoc),
                                                          aggregationDetails)