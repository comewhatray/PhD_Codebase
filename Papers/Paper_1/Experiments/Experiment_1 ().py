import ExperimentProcess as EP

ExperimentDetails = {
    "ExperimentName": "Confirming Components",
    "Description": "Ensuring ",
    "Dataset_Configuration": "Papers/Paper_1/Dataset/Configurations/Similarity(4x4)_Configuration.json",
    "MIDI_Interface": "",
    "MIDI_Representation": "",
    "Pattern_Extraction": "",
    "Similarity_Measure": ""
}

if __name__ == '__main__':
    EP.begin(ExperimentDetails)