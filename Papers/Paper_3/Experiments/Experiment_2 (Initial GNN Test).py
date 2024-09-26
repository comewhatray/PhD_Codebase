from Code_Stages import ExperimentProcess as EP
from Utilities import ComeWhatRayUtil as CWR


ExperimentDetails = {
    # Experiment Name left blank is just for experiments we don't want to store the results of
    # "ExperimentName": "Proof of Concept",
    "Description": "Initial exploration of GNN learning for paper 3",
    "WorkspaceLocation": "Papers/Paper_3/Experiments/ExperimentsWorkspace",
    "Dataset_Configuration": "Papers/Paper_3/Datasets/ClassicalComposersDataset/Configurations/3x3_Sample.json",
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
                # "pruningMethod": ""
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