import ExperimentProcess as EP

ExperimentDetails = {
    "ExperimentName": "Proof of Concept",
    "Description": "Ensuring new methods for running experiments works ",
    "Dataset_Configuration": "Papers/Paper_1/Dataset/Configurations/Similarity(4x4)_Configuration.json",
    "Stages": [
        {"MIDI_Interface": "Code_Stages.0:MIDI_Interface.MIDI_Extraction"},
        {"MIDI_Representation": ""},
        {"Pattern_Extraction": ""},
        {"Similarity_Measure": ""}
    ]
}

if __name__ == '__main__':
    EP.begin(ExperimentDetails)