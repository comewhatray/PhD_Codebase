from Code_Stages.MIDI_Representations import MIDI_Extraction as ME
from Utilities import ComeWhatRayUtil as CWR

from music21 import *

# Music 21 Settings Change needed or else it complains
e = environment.Environment()
e['directoryScratch'] = ""

def main():
    print("List of Sanity Checks")
    print(CWR.largeSpacer)
    durationSanityTest()
    mozartSanityTest()

def durationSanityTest():
    print("Sanity test for duration calculations")
    print(CWR.largeSpacer)
    DurationTestMidi = "Sanity_Checks/Sanity_MIDIS/Testing_Duration_Calculations.mid"

    notes = ME.convertMidiToPoints(DurationTestMidi)
    print("Interesting note here is how musescore changes semibreaves to tripple dotted minums")
    for note in notes:
        print(note)

    print(CWR.largeSpacer)

def mozartSanityTest():
    print("Sanity test for Mozart extract")
    print(CWR.largeSpacer)

    sanityMozart = "Sanity_Checks/Sanity_MIDIS/Mini Motzart.mid"

    notes = ME.convertMidiToPoints(sanityMozart)

    for note in notes:
        print(note)

    print(CWR.largeSpacer)

main()