from Utilities import ComeWhatRayUtil as CWR
from Code_Stages import ExperimentProcess as EP
import os

ExperimentDetails = {
    # "ExperimentName": "Szeto Comparison Early Example",
    "Description": "Ensuring new methods for running experiments works ",
    "WorkspaceLocation": "Papers/Paper_2/Experiments/ExperimentsWorkspace",
    "Dataset_Configuration": "Papers/Paper_2/Datasets/ClassicalComposersDataset/Configurations/3x3_Sample.json",
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
        {
            "file": "Code_Stages/2:Pattern_Extraction/SimplePathPatternExtraction.py",
            "options": {
                "function": "SimplePathGraphDurationExtraction",
                "saveType": ".json",
            }
        },
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
    # if not os.path.exists(saveLoc):
    locationDetails = EP.batchExperiment(ExperimentDetails)
    CWR.saveFile(saveLoc, locationDetails)
    # else:
    #     locationDetails = CWR.openFile(saveLoc)

    EP.aggregationExperiment(locationDetails, aggregationDetails)

    CWR.saveFile("Papers/Paper_2/LookUpTables/SzetoClassicalTestEnd.json", aggregationDetails["Stages"][0]['options']["LookUpTable"])
