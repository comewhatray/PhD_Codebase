import sys
from Utilities import ExperimentCommons as EC

experimentName = "Experiment16 (Kyna_Membership)"
experimentSignifier = ""
workspace = "Papers/Paper_2/Extension/ExtensionWorkspace"
QueryConfiguration = "LakhDataset/Configs/Lakh20Experiment(Queries).json"
DatasetConfiguration = "LakhDataset/Configs/Lakh20Experiment(Dataset).json"
multiProcess = True

stages = [
    {
        "file": "Code_Stages/0:MIDI_Interface/MIDI_Extraction.py",
        "options": {
            "function": "convertMidiToPoints",
            "saveType": ".json",
            "includeRests": True
        }
    },
    {
        "file": "Code_Stages/1:MIDI_Representations/ProximityGraphRepresentation.py",
        "options": {
            "function": "karystinaiosModification",
            "saveType": ".gpickle",
            "shortestConsecutiveEvent": True
        }
    }
]

queryDetails = {
    # Experiment Name left blank is just for experiments we don't want to store the results of
    "ExperimentName": experimentName,
    "ExperimentSignifier": experimentSignifier,
    "Description": "Full Scale Test",
    "WorkspaceLocation": workspace,
    "Dataset_Configuration": QueryConfiguration,
    "Stages": stages,
    "threading": multiProcess
}

datasetDetails = {
    # Experiment Name left blank is just for experiments we don't want to store the results of
    "ExperimentName": experimentName,
    "ExperimentSignifier": experimentSignifier,
    "Description": "Full Scale Test",
    "WorkspaceLocation": workspace,
    "Dataset_Configuration": DatasetConfiguration,
    "Stages": stages
}

aggregationDetails = {
    "Stages": [
        {
            "file": "Code_Stages/4:Tasks/Similarity/OverlapSimilarity.py",
            "options": {
                "function": "overlapQueryExperiment",
                "saveType": ".json",
                "queryType": "graphQueryTuneComparison",
                "saveResultsLabel": experimentName,
                "additionalParameters": {
                    "minimumOverlap": 0.7,
                },
                "inspectionBuffer": 1,
                "comparisonBuffer": 1,
                "debugging": False,
                "threading": multiProcess
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