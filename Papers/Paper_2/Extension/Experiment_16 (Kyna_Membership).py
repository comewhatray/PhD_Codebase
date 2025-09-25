from Utilities import ComeWhatRayUtil as CWR
import os
import shutil
from Code_Stages import ExperimentProcess as EP

experimentName = "Experiment_16 (Kyna_Membership).py"
workspace = "Papers/Paper_2/Extension/ExtensionWorkspace"
QueryConfiguration = "LakhDataset/Configs/Lakh20Experiment(Queries).json"
DatasetConfiguration = "LakhDataset/Configs/Lakh20Experiment(Dataset).json"


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
    # "Dataset_Configuration": "LakhDataset/Configs/polyphonicQuery.json",
    "Stages": stages
}

datasetDetails = {
    # Experiment Name left blank is just for experiments we don't want to store the results of
    "ExperimentName": experimentName,
    "ExperimentSignifier": "",
    "Description": "Full Scale Test",
    "WorkspaceLocation": workspace,
    "Dataset_Configuration": DatasetConfiguration,
    # "Dataset_Configuration": "problemConfig.json",
    "Stages": stages
    # "Stages": datasetStages
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
                    # "fragmentisationCheck": 3
                },
                "debugging": False
                # "LookUpTable": CWR.openFile("Papers/Paper_2/LookUpTables/SzetoClassicalTest.json")
            },
        }
    ]
}


if __name__ == '__main__':

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

    experimentResults = EP.queryAggregationExperiment(CWR.openFile(querySaveLoc), CWR.openFile(datasetSaveLoc), aggregationDetails)
    # CWR.saveFile("ExperimentResults/ExtensionExperiment4/test.json", aggregationDetails["Stages"][0]['options']["LookUpTable"])
