from Utilities import ComeWhatRayUtil as CWR
from Code_Stages import ExperimentProcess as EP
from Utilities import Visualisations as VIS
import matplotlib.pyplot as plt
from Utilities import BoundingGenerator as BG


#Uncomment if no save required
toSave = False
# saveLocation = "Papers/Paper_2/Visualisations/StoreImages"
# Directory = "Extracts/Beethoven5/"
# Extract = "Beethovens5Extract-Complete.mid"
# Directory = "LakhDataset/ExperimentDataset/Queries"
# Extract = "TRADNFJ128F92FFA5A_Query.mid"

Directory = "Papers/Paper_2/Visualisations/Extension/Data"
Extract = "HouseRisingSunExtract.mid"


# Update datasetConfiguration with directory information
datasetConfiguration = {
  "Title": "Default Test",
  "Directory": Directory,
  "MIDIS": [
    Extract,
  ]
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

    if not toSave:
        saveLocation = None


    comparison = []

    for extract in details["generateRepresentation"]["Default"]:
        print(extract)


        fileInfo = CWR.openFile(extract)
        comparison.append(fileInfo)

        # Display Point Representation
        # -----------------------------------------------
        plt.title("Point Generation")
        VIS.visualiseJsonAsPoints(fileInfo)

        # Display Line Representation
        # -----------------------------------------------
        # plt.title("Line Generation")
        # VIS.visualiseJsonAsLines(fileInfo,{"alternateColours": ["Blue", "Orange"]})
        VIS.visualiseJsonAsLines(fileInfo)

        multiString = BG.generateMultiLineStringFromExtract(fileInfo)

        polygon = BG.boundingPolygon(multiString,1)
        VIS.visualiseShape(polygon)



    # Display Maximum Overlap Representation




    return

main()