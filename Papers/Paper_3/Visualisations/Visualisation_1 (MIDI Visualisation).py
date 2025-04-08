from Utilities import ComeWhatRayUtil as CWR
from Utilities import Visualisations as VIS
from Code_Stages import ExperimentProcess as EP


ExperimentDetails = {
    "ExperimentName": "LisztVis",
    "Description": "Get graph representation of extract",
    "WorkspaceLocation": "Papers/Paper_3/VisualisaitonData/infered",
    "Dataset_Configuration": "Papers/Paper_3/VisualisaitonData/config/lisztExtractConfig.json",
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

aggregationDetails = {
    "Stages": [
        {
            "file": "Code_Stages/4:Tasks/Classification/GNN.py",
            "options": {
                "function": "graphClassificationUsingEdgeInformation",
                # "saveType": "",
                "saveIntermediate": ExperimentDetails["WorkspaceLocation"],
            }
        }
    ]
}

midiLocation = "Papers/Paper_3/VisualisaitonData/Liebestraum Extract.mid"

szetoGraphLocation = "Papers/Paper_3/VisualisaitonData/infered/LisztVis/Default/SzetoGraphRepresentation/LiebestraumExtract.gpickle"
edgeGraphLocation = "Papers/Paper_3/VisualisaitonData/infered/LiebestraumExtract_edgeGraph.gpickle"


def main():

    # midi =
    getGraphs()

    defaultGraph = CWR.openFile(szetoGraphLocation)
    edgeGraph = CWR.openFile(edgeGraphLocation)

    color="Yellow"
    size=1000

    VIS.visualiseSpatialGraph(defaultGraph, withLabels=True, size=size, color=color)
    VIS.visualiseGraph(edgeGraph, withLabels=True, size=size, color=color)




    return



def getGraphs():
    details = EP.batchExperiment(ExperimentDetails)
    saveLoc = CWR.appendDirectory(ExperimentDetails["WorkspaceLocation"], "LocationData.json")
    CWR.saveFile(saveLoc, details)
    EP.aggregationExperiment(details, aggregationDetails)


main()