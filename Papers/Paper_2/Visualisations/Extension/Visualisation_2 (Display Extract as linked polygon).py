from Utilities import ComeWhatRayUtil as CWR
from Code_Stages import ExperimentProcess as EP
from Utilities import Visualisations as VIS
import matplotlib.pyplot as plt
from Utilities import BoundingGenerator as BG


#Uncomment if no save required
toSave = False

nameMapping = {'TRAHACR128F14695DB': 'Query 0', 'TRAJMZR128F42556D2': 'Query 1', 'TRBRZKC128E0792B6B': 'Query 2', 'TRAXYND128F1452E9F': 'Query 3', 'TRBADGV128F92CB713': 'Query 4', 'TRAGOAA128F422214B': 'Query 5', 'TRAQGMY128F425A2F5': 'Query 6', 'TRAONMM128F92DF7B0': 'Query 7', 'TRAPBPB128F933FAAA': 'Query 8', 'TRAJKQZ128F1465490': 'Query 9', 'TRADNFJ128F92FFA5A': 'Query 10', 'TRBCVWC128F932F321': 'Query 11', 'TRAQWII128F93307C2': 'Query 12', 'TRCYIVL12903D0C67B': 'Query 13', 'TRALZTM128F92EC5F0': 'Query 14', 'TRCNWFK128F933DF77': 'Query 15', 'TRBCHAI128F933BD72': 'Query 16', 'TRAKCCA128F92F4EDC': 'Query 17', 'TRBHUGN128F422BB4D': 'Query 18', 'TRDDRYE128F42312D3': 'Query 19', 'TRAMDRT12903CA121C': 'Query 20'}


# saveLocation = "Papers/Paper_2/Visualisations/StoreImages"
# Directory = "Extracts/Beethoven5/"
# Extract = "Beethovens5Extract-Complete.mid"
# Directory = "LakhDataset/ExperimentDataset/Queries"
# Extract = "TRADNFJ128F92FFA5A_Query.mid"

# Directory = "Papers/Paper_2/Visualisations/Extension/Data"
# Extract = ["HouseRisingSunExtract.mid"]

Directory = "LakhDataset/ExperimentDataset/Queries"
Extract = ["TRADNFJ128F92FFA5A_Query.mid",
           "TRAGOAA128F422214B_Query.mid",
           "TRAHACR128F14695DB_Query.mid",
           "TRAJKQZ128F1465490_Query.mid",
           "TRAJMZR128F42556D2_Query.mid",
           "TRAKCCA128F92F4EDC_Query.mid",
           "TRALZTM128F92EC5F0_Query.mid",
           "TRAMDRT12903CA121C_Query.mid",
           "TRAONMM128F92DF7B0_Query.mid",
           "TRAPBPB128F933FAAA_Query.mid",
           "TRAQGMY128F425A2F5_Query.mid",
           "TRAQWII128F93307C2_Query.mid",
           "TRAXYND128F1452E9F_Query.mid",
           "TRBADGV128F92CB713_Query.mid",
           "TRBCHAI128F933BD72_Query.mid",
           "TRBCVWC128F932F321_Query.mid",
           "TRBHUGN128F422BB4D_Query.mid",
           "TRBRZKC128E0792B6B_Query.mid",
           "TRCNWFK128F933DF77_Query.mid",
           "TRCYIVL12903D0C67B_Query.mid",
           "TRDDRYE128F42312D3_Query.mid"]

# Update datasetConfiguration with directory information
datasetConfiguration = {
  "Title": "Default Test",
  "Directory": Directory,
  "MIDIS": Extract
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
                    "saveType": ".json",
                     "includeRests": True
                 }
             },

            # Then transform it into a more usable representation
            {
                "file": "Code_Stages/1:MIDI_Representations/GeometricRepresentation.py",
                 "options": {
                    "function": "generateRepresentation",
                    "saveType": ".json"
                 }
            },

            {
                "file": "Code_Stages/1:MIDI_Representations/ProximityGraphRepresentation.py",
                "options": {
                    "function": "karystinaiosModification",
                    "saveType": ".gpickle",
                    "shortestConsecutiveEvent": False
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

    for extract in details["karystinaiosModification"]["Default"]:
        print(extract)


        fileInfo = CWR.openFile(extract)
        comparison.append(fileInfo)
        title = CWR.getFileNameFromPath(extract)
        title = title.replace("_Query", "")
        title = nameMapping[title]

        # Display Point Representation
        # -----------------------------------------------
        # plt.title("Graph Generation")
        plt.title(title)
        VIS.visualiseSpatialGraph(fileInfo)

        # Display Line Representation
        # -----------------------------------------------
        # plt.title("Line Generation")
        # VIS.visualiseJsonAsLines(fileInfo,{"alternateColours": ["Blue", "Orange"]})
        plt.title(title)
        multiString = BG.convertGraphToMultiLineString(fileInfo, absoluteValue=True)
        VIS.visualiseShape(multiString)

        plt.title(title)
        multiPolygon = BG.convertGraphToMultiPolygon(fileInfo, 1)
        VIS.visualiseShape(multiPolygon)
        # multiString = BG.generateMultiLineStringFromExtract(fileInfo)
        #
        # polygon = BG.boundingPolygon(multiString,1)
        # VIS.visualiseShape(polygon)



    # Display Maximum Overlap Representation




    return

main()