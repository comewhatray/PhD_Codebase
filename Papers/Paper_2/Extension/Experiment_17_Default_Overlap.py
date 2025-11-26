import sys
from Utilities import ExperimentCommons as EC

multiProcess = True

queryLoc = "LakhDataset/Configs/Lakh20Experiment(Queries).json"
datasetLoc = "LakhDataset/Configs/Lakh20Experiment(Dataset).json"

# SanityChecks

## Cruel Angels Thesis
# queryLoc = "LakhDataset/Configs/QuerySanityCheck.json"
# datasetLoc = "LakhDataset/Configs/DatasetSanityCheckShort.json"

## Yesterday
# queryLoc = "LakhDataset/Configs/yesterdaySanityCheck(Query).json"
# datasetLoc = "LakhDataset/Configs/yesterdaySanityCheck(Dataset).json"

## Label2
# queryLoc = "LakhDataset/Configs/SanityChecks/Label2/query.json"
# datasetLoc = "LakhDataset/Configs/SanityChecks/Label2/dataset.json"

experimentName = "Experiment17 (Default Overlap)"
workspace = "Papers/Paper_2/Extension/ExtensionWorkspace"

stages = [
    {
        "file": "Code_Stages/0:MIDI_Interface/MIDI_Extraction.py",
        "options": {
            "function": "convertMidiToPoints",
            "saveType": ".json",
        }
    },
]

queryDetails = {
    # Experiment Name left blank is just for experiments we don't want to store the results of
    "ExperimentName": experimentName,
    "ExperimentSignifier": "",
    "Description": "Full Scale Test",
    "WorkspaceLocation": workspace,
    "Dataset_Configuration": queryLoc,
    "Stages": stages,
    "threading": multiProcess
}

datasetDetails = {
    # Experiment Name left blank is just for experiments we don't want to store the results of
    "ExperimentName": experimentName,
    "ExperimentSignifier": "",
    "Description": "Full Scale Test",
    "WorkspaceLocation": workspace,
    "Dataset_Configuration": datasetLoc,
    "Stages": stages,
    "threading": multiProcess

}

aggregationDetails = {
    "experimentName": experimentName,
    "Stages": [
        {
            "file": "Code_Stages/4:Tasks/Similarity/OverlapSimilarity.py",
            "options": {
                "function": "overlapQueryExperiment",
                "saveType": ".json",
                "queryType": "linesQueryTuneComparison",
                "saveResultsLabel": experimentName,
                "additionalParameters": {
                    # "minimumOverlap": 0.7,
                },
                "debugging": False,
                "threading": multiProcess,
                "inspectionBuffer": 1,
                "comparisonBuffer": 1,
                "visualiseProcess": False,
            },
        }
    ]
}


if __name__ == '__main__':

    configuration = None

    if len(sys.argv) > 1:
        configuration = [sys.argv[i] for i in range(1, len(sys.argv))]


    print(f"Threaded Analysis: {experimentName}")
    EC.runExperiment(queryDetails, datasetDetails, aggregationDetails, systemArgs=configuration)
