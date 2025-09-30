import sys
from Utilities import ExperimentCommons as EC

experimentName = "Experiment15 (BreathingRoom_Membership)"
workspace = "Papers/Paper_2/Extension/ExtensionWorkspace"
multiProcess = True

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
    "Dataset_Configuration": "LakhDataset/Configs/Lakh20Experiment(Queries).json",
    "Stages": stages
}

datasetDetails = {
    # Experiment Name left blank is just for experiments we don't want to store the results of
    "ExperimentName": experimentName,
    "ExperimentSignifier": "",
    "Description": "Full Scale Test",
    "WorkspaceLocation": workspace,
    "Dataset_Configuration": "LakhDataset/Configs/Lakh20Experiment(Dataset).json",
    "Stages": stages
}

aggregationDetails = {
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
                },
                "debugging": False,
                "threading": multiProcess,
                "inspectionBuffer": 1,
                "comparisonBuffer": 1,
            },
        }
    ]
}


if __name__ == '__main__':
    configuration = None

    if len(sys.argv) > 1:
        configuration = sys.argv[1]

    print(f"Threaded Analysis: {experimentName}")
    EC.runExperiment(queryDetails,datasetDetails,aggregationDetails, systemArgs=configuration)
