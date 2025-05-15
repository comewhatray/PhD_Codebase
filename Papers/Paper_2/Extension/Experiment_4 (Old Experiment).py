from Utilities import ComeWhatRayUtil as CWR
import os
import shutil
from Code_Stages import ExperimentProcess as EP

ExperimentDetails = {
    # Experiment Name left blank is just for experiments we don't want to store the results of
    "ExperimentName": "NewGraphConstructionTest",
    "ExperimentSignifier": "",
    "Description": "Testing new graph construction method for paper 2",
    "WorkspaceLocation": "Papers/Paper_2/Experiments/Extension/ExtensionWorkspace",
    "Dataset_Configuration": "Papers/Paper_2/Datasets/ClassicalComposersDataset/Configurations/3x3_Sample.json",
    # "Dataset_Configuration": "Code_Stages/defaultDataset/Configurations/ticoConfig.json",
    "Stages": [
        # First Extract the midi file into points
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
        {
            "file": "Code_Stages/2:Pattern_Extraction/SimplePathPatternExtraction.py",
            "options": {
                "function": "SimplePathGraphDurationExtraction",
                "saveType": ".json",
            }
        },
    ]
}

aggregationDetails = {
    "Stages": [
        {
            "file": "Code_Stages/4:Tasks/Similarity/OverlapSimilarity.py",
            "options": {
                "function": "totalPatternOverlapSimilarity",
                "saveType": ".json",
                "LookUpTable": CWR.openFile("Papers/Paper_2/LookUpTables/SzetoClassicalTest.json")
            },
        }
    ]
}


if __name__ == '__main__':

    saveLoc = CWR.appendDirectory(ExperimentDetails["WorkspaceLocation"], "LocationData.json")

    locationDetails = EP.batchExperiment(ExperimentDetails)
    CWR.saveFile(saveLoc, locationDetails)

    EP.aggregationExperiment(locationDetails, aggregationDetails)

    CWR.saveFile("ExperimentResults/ExtensionExperiment4/test.json", aggregationDetails["Stages"][0]['options']["LookUpTable"])
