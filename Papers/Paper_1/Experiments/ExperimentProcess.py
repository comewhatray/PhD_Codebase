from Utilities import ComeWhatRayUtil as CWR
import importlib

options = {
    "ExperimentName": "default",
    "Dataset_Configuration": "Papers/Paper_1/Dataset/Configurations/Similarity(4x4)_Configuration.json",
    "Midi_Interface": "Code_Stages.0:MIDI_Interface.MIDI_Extraction",
    "MIDI_Representation": "Code_Stages.1:MIDI_Representations.GeometricRepresentation",
    "Pattern_Extraction": {
        "Location": "Code_Stages.2:Pattern_Extraction.SlidingWindowPatternExtraction",
        "Method": ""
    },
    "Pattern_Encoding": {
        "Location": "Code_Stages.3:Pattern_Encoding.StandardEncoding",
        "Method": "NoEncoding"
    },
    "Similarity_Measure": ""
}

def begin(details=None):
    CWR.updateOldDictionaryEntriesWithNewDictionaryEntries(options, details)

    # Get Dataset Details
    datasetConfig = CWR.openFile(options["Dataset_Configuration"])

    # Code Stage Imports
    MIDI_Interface = importlib.import_module(options["Midi_Interface"])
    MIDI_Representation = importlib.import_module(options["MIDI_Representation"])
    Pattern_Extraction = importlib.import_module(options["Pattern_Extraction"]["Location"])
    Pattern_Encoding = importlib.import_module(options["Pattern_Encoding"]["Location"])
    # Similarity_Measure = importlib.import_module(options["Similarity_Measure"])

    if "Labels" in datasetConfig:

        # Iterate through the labels
        for label in datasetConfig["Labels"]:
            print(f"Label: {label}")
            print(CWR.smallSpacer)

            #Iterate through each piece of a label
            for piece in datasetConfig["Labels"][label]:
                print(piece)






            print(CWR.midSpacer)
    else:
        print("Just Testing functions atm")
        print("Just a list of midis")

        results = MIDI_Interface.convertMidiToPoints("Sanity_Checks/Sanity_MIDIS/Mini Motzart.mid")
        print(results)

        representation = MIDI_Representation.generateRepresentation(results)
        print(representation)

        patternList = Pattern_Extraction.generatePatterns(representation)
        print(patternList)

        encodedPatterns = Pattern_Encoding.encodePatterns(patternList)
        print(encodedPatterns)


begin()