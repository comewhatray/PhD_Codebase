from Utilities import ComeWhatRayUtil as CWR
from Code_Stages import ExperimentProcess as EP

ExperimentDetails = {
    # "ExperimentName": "Name left blank on purpose",
    "Description": "For running a sanity check on the Line Proximity graph representation method",
    "WorkspaceLocation": "Sanity_Checks/SanityWorkSpace",
    "Dataset_Configuration": "Sanity_Checks/Sanity_MIDIS/Configurations/MozartTestConfiguration.json",
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
                "function": "GraphLineRepresentation",
                "saveType": ".gpickle",
                "edgeAttributes": True,
                # "pitchWeighting": 0.1
                "polygon": {
                        "type": "Rectangle",
                        "dimensions": {
                            "height": 8,
                            "width": 4
                        }
                }
            }
        },
        # Visualising the results
        {
            "file": "Code_Stages/5:Visualisation/graphVisualisations.py",
            "options": {
                "function": "visualiseSpatialGraph",
                "toSave": False,
                "saveType": None,
            }
        }
    ]
}

if __name__ == '__main__':
    details = EP.batchExperiment(ExperimentDetails)
    saveLoc = CWR.appendDirectory(ExperimentDetails["WorkspaceLocation"], "LocationData.json")
    CWR.saveFile(saveLoc, details)