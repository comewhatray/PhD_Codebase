from Utilities import ComeWhatRayUtil as CWR
import os
import shutil
from Code_Stages import ExperimentProcess as EP

ExperimentDetails = {
    # Experiment Name left blank is just for experiments we don't want to store the results of
    "ExperimentName": "TestingRestImplementation",
    "ExperimentSignifier": "",
    "Description": "Experiment to verify that rests are added correctly",
    "WorkspaceLocation": "Papers/Paper_2/Experiments/Extension/ExtensionWorkspace",
    "Dataset_Configuration": "Papers/Paper_2/Datasets/ClassicalComposersDataset/Configurations/3x3_Sample.json",
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
    ]
}

if __name__ == '__main__':
    print("test")
    EP.batchExperiment(ExperimentDetails)