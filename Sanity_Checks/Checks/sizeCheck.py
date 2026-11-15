from Utilities import ComeWhatRayUtil as CWR
from Code_Stages import ExperimentProcess as EP
import networkx

ExperimentDetails1 = {
    "ExperimentName": "Base",
    "Description": "For running a sanity check on the szeto and wong graph representation method",
    "WorkspaceLocation": "Sanity_Checks/SanityWorkSpace/",
    "Dataset_Configuration": "Extracts/Configs/BachSizeConfig.json",
    "Stages": [
        # First Extract the midi file into points
        {
            "file": "Code_Stages/0:MIDI_Interface/MIDI_Extraction.py",
            "options": {
                "function": "convertMidiToPoints",
                "saveType": ".json",
            }
        },
        # Then transform it into a more usable representation
        {
            "file": "Code_Stages/1:MIDI_Representations/ProximityGraphRepresentation.py",
            "options": {
                "function": "SzetoGraphRepresentation",
                "saveType": ".gpickle",
            }
        }
    ]
}


ExperimentDetails2 = {
    "ExperimentName": "Diff",
    "Description": "For running a sanity check on the szeto and wong graph representation method",
    "WorkspaceLocation": "Sanity_Checks/SanityWorkSpace",
    "Dataset_Configuration": "Extracts/Configs/BachSizeConfig.json",
    "Stages": [
        # First Extract the midi file into points
        {
            "file": "Code_Stages/0:MIDI_Interface/MIDI_Extraction.py",
            "options": {
                "function": "convertMidiToPoints",
                "saveType": ".json",
            }
        },
        # Then transform it into a more usable representation
        {
            "file": "Code_Stages/1:MIDI_Representations/ProximityGraphRepresentation.py",
            "options": {
                "function": "SzetoGraphRepresentation",
                "saveType": ".gpickle",
            }
        },
    ]
}

if __name__ == '__main__':
    details = EP.batchExperiment(ExperimentDetails1)
    saveLoc = CWR.appendDirectory(ExperimentDetails1["WorkspaceLocation"], "LocationData.json")
    CWR.saveFile(saveLoc, details)

    details = EP.batchExperiment(ExperimentDetails2)
    saveLoc = CWR.appendDirectory(ExperimentDetails2["WorkspaceLocation"], "LocationData.json")
    CWR.saveFile(saveLoc, details)