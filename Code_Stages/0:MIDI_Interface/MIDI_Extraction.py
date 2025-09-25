from music21 import *
from Utilities import ComeWhatRayUtil as CWR

e = environment.Environment()
e['directoryScratch'] = ""

Options = {
    "decimalPrecision": 3,
    "includeRests": False,
    "debugging": False
}

# Hard coded note name conversions to numbers
noteToNumber = {
    'A': 9,
    'B': 11,
    'C': 0,
    'D': 2,
    'E': 4,
    'F': 5,
    'G': 7,
}

def startProcess(work, inputOptions = None):
    CWR.updateOldDictionaryEntriesWithNewDictionaryEntries(Options, inputOptions)
    return convertMidiToPoints(work)

# Intakes a midifile and returns a set of coordinates and details
def convertMidiToPoints(work):

    work = converter.parse(work)
    # This line makes it so that ties are represented as single notes rather than doubles
    work = work.stripTies()
    work = work.flatten()
    coordinates = []

    if Options["includeRests"]:
        streamOption = work.notesAndRests
    else:
        streamOption = work.notes

    # Go through all notes in the midi file
    for n in streamOption:

        # If a note is present transform it into a computer friendly representation
        if "Note" in n.classSet:
            tempNote = getNotePosition(n)
            if tempNote['pitch'] >= 0:
                # Do not include notes with a negative pitch as these are likely percussion
                coordinates.append(tempNote)

        # Dismantle chords into individual notes
        elif "Chord" in n.classSet:
            for midiNote in n:
                returnedNote = getNotePosition(midiNote)
                returnedNote['position'] = round(float(n.offset), Options["decimalPrecision"])
                returnedNote['duration'] = round(float(n.quarterLength), Options["decimalPrecision"])
                # Do not include notes with a negative pitch as these are likely percussion
                # (Hopefully this has been fixed with the later code increasing the octave of the notes)
                # if returnedNote['pitch'] >= 0:
                #     coordinates.append(returnedNote)
                coordinates.append(returnedNote)

        elif "Rest" in n.classSet:
            # print("RESSSSSTTTTTTIIIIIINNNNNGGGGG")
            noteRest = {
                "type": "Rest",
                "pitch": -1, # An inelegant solution is that all rests have a pitch of -1
                "position": round(float(n.offset), Options["decimalPrecision"]),
                "duration": round(float(n.quarterLength), Options["decimalPrecision"])
            }
            coordinates.append(noteRest)
            # noteRest["position"] = round(float(n.offset), Options["decimalPrecision"])


    pointSet = sortPoints(coordinates)

    return pointSet

# Determines the coordinates of each note and relevant details
def getNotePosition(midiInput):
    # Confirming that the object being looked at is a note
    if "Note" in midiInput.classSet:
        # Augments are sharps and flats and so on, this modifies the semitone

        augment = 0
        # note = input.pitch.name
        note = midiInput.pitch

        # This checks if the note is an accidental and prepares to add or subtract accordingly
        if note.accidental:
            augment = note.accidental.alter

        # Get the note pitch name
        note = midiInput.pitch.name

        # Get Note value in scale
        position = noteToNumber[note[0]]

        # Add sharps and flats
        position = position + augment

        # Check what octave the pitch is at
        # octave = 0
        # if midiInput.pitch.octave >= 0:
        octave = midiInput.pitch.octave

        # Calculating the pitch number based on what pitch it is plus what octave its at
        position = position + 12 * (octave + 1)

        # Getting where the note occurs within a bar
        # 1 is subtracted to make it more computer friendly rather than musicoligist friendly
        barBeat = midiInput.beat - 1

        # combine output
        output = {"type": "Note",
                  'pitch': float(position),
                  'position': round(float(midiInput.offset), Options["decimalPrecision"]),
                  'duration': round(float(midiInput.quarterLength), Options["decimalPrecision"]),
                  'barBeat': round(float(barBeat), Options["decimalPrecision"])
                  }

        return output

# Order -> Onset (Early to Late) | Pitch (Bottom to Top)
def sortPoints(pointSet):
    subGroups = []
    temp = []

    if pointSet:
        for value in pointSet:

            if not subGroups:
                subGroups.append([value])

            # if the position of the current note comes before the last note observed we make a new list(this is probably another instrument)
            elif subGroups[len(subGroups) - 1][len(subGroups[len(subGroups) - 1]) - 1]['position'] > value['position']:
                subGroups.append([value])

            elif subGroups[len(subGroups) - 1][len(subGroups[len(subGroups) - 1]) - 1]['position'] == value['position'] and \
                    subGroups[len(subGroups) - 1][len(subGroups[len(subGroups) - 1]) - 1]['pitch'] > value['pitch']:
                subGroups.append([value])
            else:
                subGroups[len(subGroups) - 1].append(value)



        for i in range(0, len(subGroups)):
            combined = []
            while len(temp) != 0 or len(subGroups[i]) != 0:

                if len(temp) == 0:
                    combined += subGroups[i]
                    subGroups[i].clear()
                    continue

                if len(subGroups[i]) == 0:
                    combined += temp
                    temp.clear()
                    continue

                # Checking positions

                if temp[0]['position'] == subGroups[i][0]['position']:
                    # print(i)
                    # if i == 98:
                    # print('test')
                    if temp[0]['pitch'] == subGroups[i][0]['pitch'] or (
                            len(combined) > 0 and combined[-1]['pitch'] == subGroups[i][0]['pitch']):
                        subGroups[i].pop(0)

                    elif temp[0]['pitch'] < subGroups[i][0]['pitch']:
                        combined.append(temp.pop(0))

                    else:
                        combined.append(subGroups[i].pop(0))

                else:

                    if temp[0]['position'] < subGroups[i][0]['position']:
                        combined.append(temp.pop(0))

                    elif temp[0]['position'] > subGroups[i][0]['position']:
                        combined.append(subGroups[i].pop(0))

            temp = combined.copy()

        # This just checked to see if everything was in order
        weG = True
        afterPos = temp[0]['position']
        afterPit = temp[0]['pitch']
        for value in temp[1:]:

            if afterPos > value['position'] and afterPit > value['pitch']:
                weG = False

            afterPos = value['position']
            afterPit = value['pitch']

        if Options["debugging"]:
            if weG:
                print('Notes are in order')

            else:
                print('Notes are not in order')

    return temp

