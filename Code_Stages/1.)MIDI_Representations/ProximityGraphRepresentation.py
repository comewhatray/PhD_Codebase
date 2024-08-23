from Utilities import ComeWhatRayUtil as CWR

# It is assumed that all input is a set of points derived from MIDI_Extraction.py

options = {
    "Polygon": "Rectangle",
    "Dimensions": [4, 4],
}

# The Coordinates returned by MIDI_Extraction.py is the geometric representation
def generateRepresentation(work, inputOptions=None):
    # Updating Options
    CWR.updateOldDictionaryEntriesWithNewDictionaryEntries(options, inputOptions)

    return work