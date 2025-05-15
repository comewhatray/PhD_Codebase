from Utilities import ComeWhatRayUtil as CWR
import os
import shutil
from Code_Stages import ExperimentProcess as EP

ExperimentDetails = {
    # Experiment Name left blank is just for experiments we don't want to store the results of
    # "ExperimentName": "TestingRestImplementation",
    "ExperimentSignifier": "",
    "Description": "Experiment to ensure correct transfer of rest consecutive notes",
    # "WorkspaceLocation": "Papers/Paper_2/Experiments/Extension/ExtensionWorkspace",
    # "Dataset_Configuration": "Code_Stages/defaultDataset/Configurations/ticoConfig.json",
    "Dataset_Configuration": "Papers/Paper_3/VisualisaitonData/config/lisztExtractConfig.json",
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
                # "function": "KarystinaiosRepresentation",
                "function": "karystinaiosModification",
                "saveType": ".gpickle",
                "shortestConsecutiveEvent": True
            }
        },
        {
            "file": "Code_Stages/5:Visualisation/graphVisualisations.py",
            "options": {
                "function": "visualiseSpatialGraph",
                "toSave": False,
                "saveType": None,
                "labelNodes": True,
                "detail": {


                }
            }
        }
    ]
}

if __name__ == '__main__':
    print("test")
    EP.batchExperiment(ExperimentDetails)