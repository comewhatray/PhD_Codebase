import os.path

from Code_Stages import ExperimentProcess as EP
from Utilities import ComeWhatRayUtil as CWR


ExperimentDetails = {
    # Experiment Name left blank is just for experiments we don't want to store the results of
    "ExperimentName": "Transformation of Classical Dataset into Tensors to be used with a gnn",
    "Description": "Initial exploration of GNN learning for paper 3",
    "WorkspaceLocation": "Papers/Paper_3/Experiments/ExperimentsWorkspace",
    # "Dataset_Configuration": "Papers/Paper_3/Datasets/ClassicalComposersDataset/Configurations/3x3_Sample.json",
    "Dataset_Configuration": "Papers/Paper_3/Datasets/ClassicalComposersDataset/Configurations/All.json",
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
                "edgeAttributes": True
            }
        },
        # {
        #     "file": "",
        #     "function": "",
        #          "options": {
        # }},
    ]
}

aggregationDetails = {
    "Stages": [
        {
            "file": "Code_Stages/4:Tasks/Classification/GNN.py",
            "options": {
                "function": "graphClassificationUsingEdgeInformation",
                # "saveType": "",
            }
        }
    ]
}


if __name__ == '__main__':

    # saveLoc = CWR.appendDirectory(ExperimentDetails["WorkspaceLocation"], "LocationData.json")
    # if not os.path.exists(saveLoc):
    #     details = EP.batchExperiment(ExperimentDetails)
    #     CWR.saveFile(saveLoc, details)
    # else:
    #     details = CWR.openFile(saveLoc)

    details = EP.batchExperiment(ExperimentDetails)
    EP.aggregationExperiment(details, aggregationDetails)

