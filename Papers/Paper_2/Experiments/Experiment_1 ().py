from Utilities import ComeWhatRayUtil as CWR
from Code_Stages import ExperimentProcess as EP
# import ExperimentProcess as EP

ExperimentDetails = {
    "ExperimentName": "4x4 Unpruned Graph",
    "Description": "Ensuring new methods for running experiments works ",
    "WorkspaceLocation": "Papers/Paper_3/Experiments/ExperimentsWorkspace",
    "Dataset_Configuration": "Papers/Paper_3/Datasets/BegginerDataset/Configurations/4x4_Configuration.json",
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
            "file": "Code_Stages/1:MIDI_Representations/GeometricRepresentation.py",
            "options": {
                "function": "GraphLineRepresentation",
                "saveType": ".gpickle",
            }
        },
        # {
        #     "file": "Code_Stages/2:Pattern_Extraction/SlidingWindowPatternExtraction.py",
        #     "options": {
        #         "function": "SlidingWindowMelodyExtraction",
        #         "saveType": ".json",
        #     }
        # },
        # {
        #     "file": "Code_Stages/3:Pattern_Encoding/StandardEncoding.py",
        #     "function": None,
        #          "options": {
        # }},
        # {
        #     "file": "",
        #     "function": "",
        #          "options": {
        # }},
        # {
        #     "file": "",
        #     "function": "",
        #          "options": {
        # }},
    ]
}

if __name__ == '__main__':
    details = EP.batchExperiment(ExperimentDetails)
    saveLoc = CWR.appendDirectory(ExperimentDetails["WorkspaceLocation"], "LocationData.json")
    CWR.saveFile(saveLoc, details)