from Utilities import ComeWhatRayUtil as CWR
from Code_Stages import ExperimentProcess as EP
from Utilities import Visualisations as VIS
import matplotlib.pyplot as plt
from Utilities import BoundingGenerator as BG


#Uncomment if no save required
toSave = False
saveLocation = "Papers/Paper_2/Visualisations/StoreImages"
buffer = 0.25


# Snippet1 = "Beethovens5Extract-1st.mid"
# # Snippet2 = "Beethovens5Extract-2nd.mid"
# Directory = "Extracts/Beethoven5"
# MIDIS = [
#     "Beethovens5Extract-1st.mid",
#     "Beethovens5Extract-2nd.mid"
# ]

# Snippet1 =
Directory = "Extracts/ChopinMorty"
MIDIS = [
    # "ChopinExtract.mid",
    # "ForTheDamagedCoda.mid",
    "RisingSunExtract.mid",
    "Beethovens5Extract-Complete.mid"
]

# Directory = "Extracts/UpDownSample"
# MIDIS = [
#     "DownSample.mid",
#     "UpSample.mid",
# ]

# Update datasetConfiguration with directory information
datasetConfiguration = {
  "Title": "Default Test",
  "Directory": Directory,
  "MIDIS": MIDIS
}

# Update Options information
options = {
    "Dataset_Configuration": datasetConfiguration,
    "Stages": [
            # Default Experiment
            # First Extract the midi file into points
            {
                "file": "Code_Stages/0:MIDI_Interface/MIDI_Extraction.py",
                 "options": {
                    "function": "convertMidiToPoints",
                    "saveType": ".json"
                 }
             },

            # Then transform it into a more usable representation
            {
                "file": "Code_Stages/1:MIDI_Representations/GeometricRepresentation.py",
                 "options": {
                    "function": "generateRepresentation",
                    "saveType": ".json"
                 }
            }
        ]
}

def main():

    details = EP.batchExperiment(options)

    print(details)

    whereSave = None

    comparison = []
    plotCount = 0

    for extract in details["generateRepresentation"]["Default"]:
        print(extract)


        fileInfo = CWR.openFile(extract)
        comparison.append(fileInfo)

        # Display Point Representation
        # -----------------------------------------------
        plt.title("Point Generation")
        # VIS.visualiseJsonAsPoints(fileInfo)

        # Display Line Representation
        # -----------------------------------------------
        plt.title("Line Generation")
        plt.xlabel("Beats")
        plt.ylabel("Pitch")
        if toSave:
            whereSave = f"{saveLocation}/plot{plotCount}.png"
        # VIS.visualiseJsonAsLines(fileInfo,{"alternateColours": ["Blue", "Orange"]}, saveTo=whereSave)
        plotCount += 1

        # Display Bounding Representation
        # -----------------------------------------------
        # VIS.visualiseLineString(fileInfo)
        # VIS.visualiseLineStringBounding(fileInfo, boundary=1)
        plt.title("Linestring and Boundary Generation")
        plt.xlabel("Relative Beats")
        plt.ylabel("Relative Pitch")
        if toSave:
            whereSave = f"{saveLocation}/plot{plotCount}.png"
        VIS.visualiseLineStringWithBoundary(fileInfo, boundary=buffer, saveTo=whereSave)
        plotCount += 1

    # Final comparison


    maxOverlap = BG.maxOverlappingPolygon(comparison[0], comparison[1])


    plt.title(f"Overlap of the Two Boundaries: {maxOverlap['Ratio']}%")
    if toSave:
        whereSave = f"{saveLocation}/plot{plotCount}.png"
    # VIS.visualiseOverlappingPolygons(comparison[0], comparison[1], boundary=1, saveTo=whereSave)
    VIS.visualiseOverlappingPolygonsUsingData(maxOverlap["InitialPolygon"], maxOverlap["ComparisonPolygon"], maxOverlap["MaximalOverlap"])
    plotCount += 1



    # Display Maximum Overlap Representation




    return

main()