from Utilities import ComeWhatRayUtil as CWR
import sys


# It is assumed that all input is a set of points derived from MIDI_Extraction.py

options = {
}

# if __name__ == '__main__':
#     work = sys.argv[1]
#     # Updating Options
#     CWR.updateOldDictionaryEntriesWithNewDictionaryEntries(options, sys.argv[2])
#
#     return work


# The Coordinates returned by MIDI_Extraction.py is the geometric representation
def generateRepresentation(work, inputOptions=None):
    # Updating Options
    CWR.updateOldDictionaryEntriesWithNewDictionaryEntries(options, inputOptions)

    return work