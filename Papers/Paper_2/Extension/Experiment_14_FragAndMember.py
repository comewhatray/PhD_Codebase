import sys
from Utilities import ExperimentCommons as EC

experimentName = "Experiment14 (FragAndMember)"
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
    # {
    #     "file": "Code_Stages/2:Pattern_Extraction/SimplePathPatternExtraction.py",
    #     "options": {
    #         "function": "SimplePathGraphDurationExtraction",
    #         "saveType": ".json",
    #     }
    # }
]

queryDetails = {
    # Experiment Name left blank is just for experiments we don't want to store the results of
    "ExperimentName": experimentName,
    "ExperimentSignifier": "",
    "Description": "Full Scale Test",
    "WorkspaceLocation": workspace,
    "Dataset_Configuration": QueryConfiguration,
    "Stages": stages,
    "threading": multiProcess
}

datasetDetails = {
    # Experiment Name left blank is just for experiments we don't want to store the results of
    "ExperimentName": experimentName,
    "ExperimentSignifier": "",
    "Description": "Full Scale Test",
    "WorkspaceLocation": workspace,
    "Dataset_Configuration": DatasetConfiguration,
    "Stages": stages,
    "threading": multiProcess

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
                    "fragmentationCheck": 3
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

    configuration = "CoreConfigurations/BoundingModificationConfig.json"

    print(f"Threaded Analysis: {experimentName}")
    EC.runExperiment(queryDetails, datasetDetails, aggregationDetails, systemArgs=configuration)
