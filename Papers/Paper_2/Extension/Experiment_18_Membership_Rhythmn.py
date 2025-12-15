import sys
from Utilities import ExperimentCommons as EC

experimentName = "Experiment18 (Membership_Rhythmn)"
workspace = "Papers/Paper_2/Extension/ExtensionWorkspace"

queryLoc = "LakhDataset/Configs/Lakh20Experiment(Queries).json"
datasetLoc = "LakhDataset/Configs/Lakh20Experiment(Dataset).json"

## Label2
# queryLoc = "LakhDataset/Configs/SanityChecks/Label2/query.json"
# datasetLoc = "LakhDataset/Configs/SanityChecks/Label2/dataset.json"

## Label16
# queryLoc = "LakhDataset/Configs/SanityChecks/Label16/query.json"
# datasetLoc = "LakhDataset/Configs/SanityChecks/Label16/dataset.json"

multiProcess = True
visualiseProcess = False

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
    "threading": multiProcess,
    "Noise": None
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
                    "minimumOverlap": 0.7,
                    "rhythmThresholdCheck": 0
                },
                "debugging": False,
                "threading": multiProcess,
                "inspectionBuffer": 1,
                "comparisonBuffer": 1,
                "visualiseProcess": visualiseProcess,
                "Scaling": {
                    "xScale": 1,
                    "yScale": 1,
                }
            },
        }
    ]
}


if __name__ == '__main__':
    configuration = None

    if len(sys.argv) > 1:
        configuration = [sys.argv[i] for i in range(1, len(sys.argv))]

    print(f"Threaded Analysis: {experimentName}")
    EC.runExperiment(queryDetails, datasetDetails,aggregationDetails, systemArgs=configuration)
