from Utilities import ComeWhatRayUtil as CWR
import os
import shutil
from Code_Stages import ExperimentProcess as EP


workspace = "Papers/Paper_2/Extension/ExtensionWorkspace"
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
    },
    # {
    #     "file": "Code_Stages/2:Pattern_Extraction/SimplePathPatternExtraction.py",
    #     "options": {
    #         "function": "SimplePathGraphDurationExtraction",
    #         "saveType": ".json",
    #     }
    # }
]


# datasetStages = [
#     {
#         "file": "Code_Stages/0:MIDI_Interface/MIDI_Extraction.py",
#         "options": {
#             "function": "convertMidiToPoints",
#             "saveType": ".json",
#             "includeRests": True
#         }
#     }
# ]

queryDetails = {
    # Experiment Name left blank is just for experiments we don't want to store the results of
    "ExperimentName": "Experiment_6 New Search Function",
    "ExperimentSignifier": "",
    "Description": "A sample Query being tested against two catagories",
    "WorkspaceLocation": workspace,
    "Dataset_Configuration": "LakhDataset/Configs/1Query2Labels(Query).json",
    # "Dataset_Configuration": "LakhDataset/Configs/polyphonicQuery.json",
    "Stages": stages
}

datasetDetails = {
    # Experiment Name left blank is just for experiments we don't want to store the results of
    "ExperimentName": "Experiment_6 New Search Function",
    "ExperimentSignifier": "",
    "Description": "A sample Query being tested against two catagories",
    "WorkspaceLocation": workspace,
    # "Dataset_Configuration": "LakhDataset/Configs/1Query2Labels(Label).json",
    "Dataset_Configuration": "problemConfig.json",
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

    #TODO create method for evaluating the query results
    EP.queryAggregationExperiment(CWR.openFile(querySaveLoc), CWR.openFile(datasetSaveLoc), aggregationDetails)


    # EP.aggregationExperiment(locationDetails, aggregationDetails)
    # CWR.saveFile("ExperimentResults/ExtensionExperiment4/test.json", aggregationDetails["Stages"][0]['options']["LookUpTable"])
