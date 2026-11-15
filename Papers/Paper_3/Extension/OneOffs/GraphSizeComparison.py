from Utilities import ComeWhatRayUtil as CWR
from Code_Stages import ExperimentProcess as EP
import networkx as nx
import torch
from torch_geometric.data import Data
from torch_geometric.utils import to_networkx


ExperimentDetails = {
    # Experiment Name left blank is just for experiments we don't want to store the results of
    "ExperimentName": "sizeComparison",
    "threading": False,
    "ExperimentSignifier": "sizeComparison",
    "Description": "GeneratingSizeComparisons",
    "WorkspaceLocation": "Papers/Paper_3/Extension/Workspace",
    "Dataset_Configuration": "Extracts/Configs/BachSizeConfig.json",
    "Stages": [
        # First Extract the midi file into points
        {
            "file": "Code_Stages/0:MIDI_Interface/MIDI_Extraction.py",
            "options": {
                "function": "convertMidiToPoints",
                "saveType": ".json",
                "includeRests": True,
            }
        },
        # Then transform it into a more usable representation
        {
            "file": "Code_Stages/1:MIDI_Representations/ProximityGraphRepresentation.py",
            "options": {
                "function": "karystinaiosModification",
                "saveType": ".gpickle",
                "edgeAttributes": True
            }
        },
    ]
}

# Specifications for transforming the dataset
aggregationDetails = {
    "threading": False,
    "Stages": [
        {
            "file": "Code_Stages/4:Tasks/Classification/GNN.py",
            "options": {
                "function": "graphClassificationUsingEdgeInformation",
                # "saveType": "",
                "threading": False,
                "saveLocation": "Papers/Paper_3/Extension/Workspace/sizeComparison",
                "saveIntermediate": None,
                "saveType": ".pt",
            }
        }
    ]
}


def main():

    details = EP.batchExperiment(ExperimentDetails)
    EP.aggregationExperiment(details, aggregationDetails)

    kynaRep = CWR.openFile("Papers/Paper_3/Extension/Workspace/sizeComparison/sizeComparison/Bach/karystinaiosModification/Bach_28.gpickle")
    nDiffRep = CWR.openFile("Papers/Paper_3/Extension/Workspace/sizeComparison/data_0.pt")


    print(kynaRep)
    print(nDiffRep)

    num_nodes = nDiffRep.x.shape[0] if nDiffRep.x is not None else nDiffRep.num_nodes

    # Get number of edges
    num_edges = nDiffRep.edge_index.shape[1]

    print(f"Number of nodes: {num_nodes}")
    print(f"Number of edges: {num_edges/2}")



    G = nx.Graph(kynaRep)  # undirected, no duplicate edges
    predicted = sum(d * (d - 1) // 2 for _, d in G.degree())

    print(type(kynaRep))
    print(f"Base graph: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")
    print(f"Formula predicts: {G.number_of_edges()} nodes, {predicted} edges")

    return




main()