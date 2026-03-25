from Utilities import ComeWhatRayUtil as CWR
from Utilities import Visualisations as VIS
from Code_Stages import ExperimentProcess as EP

# experimentName = "LisztVis"
# datasetConfig = "Papers/Paper_3/VisualisaitonData/config/lisztExtractConfig.json"

experimentName = "TestarVis"
datasetConfig = "Extracts/Configs/TestarExtractConfig.json"

ExperimentDetails = {
    "ExperimentName": experimentName,
    "Description": "Get graph representation of extract",
    "WorkspaceLocation": "Papers/Paper_3/VisualisaitonData/infered",
    "Dataset_Configuration": datasetConfig,
    "Stages": [
        # First Extract the midi file into points
        {
            "file": "Code_Stages/0:MIDI_Interface/MIDI_Extraction.py",
            "options": {
                "function": "convertMidiToPoints",
                "saveType": ".json",
            }
        },
        # Then transform it into a more usable representation
        {
            "file": "Code_Stages/1:MIDI_Representations/ProximityGraphRepresentation.py",
            "options": {
                "function": "SzetoGraphRepresentation",
                "saveType": ".gpickle",
                # "pruningMethod": ""
                "edgeAttributes": True
            }
        }
    ]
}
#
# aggregationDetails = {
#     "Stages": [
#         {
#             "file": "Code_Stages/4:Tasks/Classification/GNN.py",
#             "options": {
#                 "function": "graphClassificationUsingEdgeInformation",
#                 # "saveType": "",
#                 "saveIntermediate": ExperimentDetails["WorkspaceLocation"],
#             }
#         }
#     ]
# }

# szetoGraphLocation = "Papers/Paper_3/VisualisaitonData/infered/LisztVis/Default/SzetoGraphRepresentation/LiebestraumExtract.gpickle"
# edgeGraphLocation = "Papers/Paper_3/VisualisaitonData/infered/LiebestraumExtract_edgeGraph.gpickle"

szetoGraphLocation = "Papers/Paper_3/VisualisaitonData/infered/TestarVis/Default/SzetoGraphRepresentation/Alicia.gpickle"
edgeGraphLocation = "Papers/Paper_3/VisualisaitonData/infered/Bach_1_edgeGraph.gpickle"


def main():

    # midi =
    getGraphs()

    defaultGraph = CWR.openFile(szetoGraphLocation)
    # edgeGraph = CWR.openFile(edgeGraphLocation)

    color="Yellow"
    size=300

    VIS.visualiseSpatialGraph(defaultGraph, withLabels=True, size=size, color=color)
    # VIS.visualiseGraph(edgeGraph, withLabels=True, size=size, color=color)

    print(f"DefaultGraph Nodes: {len(defaultGraph.nodes())}")
    print(f"DefaultGraph Edges: {len(defaultGraph.edges())}")

    # print(f"EdgeGraph Nodes: {len(edgeGraph.nodes())}")
    # print(f"EdgeGraph Edges: {len(edgeGraph.edges())}")




    return



def getGraphs():
    details = EP.batchExperiment(ExperimentDetails)
    saveLoc = CWR.appendDirectory(ExperimentDetails["WorkspaceLocation"], "LocationData.json")
    CWR.saveFile(saveLoc, details)
    # EP.aggregationExperiment(details, aggregationDetails)


main()