from Utilities import ComeWhatRayUtil as CWR
from Code_Stages import ExperimentProcess as EP
from Utilities import parrallelism as PM

def runExperiment(queryDetails, datasetDetails, aggregationDetails, systemArgs=None):

    multiProcess = queryDetails["threading"]


    if systemArgs is not None:

        experimentModification = CWR.openFile(systemArgs[0])

        # Update Identifier to create new Directories
        print(experimentModification["title"])
        queryDetails["ExperimentSignifier"] = experimentModification["title"].split('/')[0]
        datasetDetails["ExperimentSignifier"] = experimentModification["title"].split('/')[0]

        # Update Query with modifications
        if "queryModifications" in experimentModification:
            CWR.updateOldDictionaryEntriesWithNewDictionaryEntries(queryDetails, experimentModification["queryModifications"])

        # Update Dataset with modifications
        if "datasetModification" in experimentModification:
            CWR.updateOldDictionaryEntriesWithNewDictionaryEntries(datasetDetails, experimentModification["datasetModifications"])

        # Update Aggregation with modifications
        if "aggregationModification" in experimentModification:
            for stage in aggregationDetails["Stages"]:
                stage["options"]["saveResultsLabel"] = f"{experimentModification['title']}/{aggregationDetails["experimentName"]}"
                CWR.updateOldDictionaryEntriesWithNewDictionaryEntries(stage["options"], experimentModification["aggregationModification"])

    print(CWR.extraLargeSpacer)
    print("AGGREGATION DETAILS:")
    print(aggregationDetails)
    print(CWR.extraLargeSpacer)
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