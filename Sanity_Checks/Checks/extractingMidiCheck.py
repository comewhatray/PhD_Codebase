from Utilities import ComeWhatRayUtil as CWR
from Code_Stages import ExperimentProcess as EP

ExperimentDetails = {
    # "ExperimentName": "Name left blank on purpose",
    "Description": "For running a sanity check on the Line Proximity graph representation method",
    "WorkspaceLocation": "Sanity_Checks/SanityWorkSpace",
    "Dataset_Configuration": "Sanity_Checks/Sanity_MIDIS/Configurations/MozartTestConfiguration.json",
    "Stages": [
        {
            "file": "Code_Stages/0:MIDI_Interface/MIDI_Extraction.py",
            "options": {
                "function": "convertMidiToPoints",
                "saveType": ".json",
            }
        }
    ]

}

if __name__ == '__main__':
    details = EP.batchExperiment(ExperimentDetails)