from Utilities import ComeWhatRayUtil as CWR
import torch
from torch_geometric.data import Data
from torch_geometric.utils.convert import from_networkx
import networkx as nx
import sys

options = {
    "function": "edgeToNodeTensorEncoding",
    'saveLocation': None,
    "hotEncoderDictionary": {},
    "threading": False

}

def startProcess(work, inputOptions=None):
    # Updating Options
    CWR.updateOldDictionaryEntriesWithNewDictionaryEntries(options, inputOptions)

    # Setting up python voodoo magic to let me use a sting to call a function
    this_module = sys.modules[__name__]
    methodInstanciated = getattr(this_module, options['function'])
    if not options['threading']:
        print(f" Tensor Representations: {options['function']}")
    proximityGraphRepresentation = methodInstanciated(work)

    return proximityGraphRepresentation


def edgeToNodeTensorEncoding(work):

    edgeGraph = edgeNodeSwapGraph(CWR.openFile(work['Location'], printDisplay= not options['threading']))

    pyg_graph = from_networkx(edgeGraph)
    x = []
    for i in range(pyg_graph['num_nodes']):
        x.append([pyg_graph['pitchChange'][i], pyg_graph['onsetGap'][i], pyg_graph['endOnsetGap'][i]])

    pyg_graph.x = torch.tensor(x)
    pyg_graph.y = torch.tensor([hotEncoder(work['Label'])])

    cleanedTorchData = Data(
        # X is a tensor of the features
        x=pyg_graph.x,
        # Edge index is edge index
        edge_index=pyg_graph.edge_index,
        # This is the class it belongs to that has been hot encoded to a number
        y=pyg_graph.y,
        MidiName=work['Name']
    )

    # print(cleanedTorchData)

    # if options['saveLocation'] is not None:
    #     CWR.saveFile(work['Location'], cleanedTorchData)

    return cleanedTorchData

# Helper Methods
# ----------------------------------------------------------------------------------------------------------------------

def edgeNodeSwapGraph(inputGraph):
    edgeGraph = nx.Graph()
    for u, v, d in inputGraph.edges(data=True):

        if options['testing']:
            print(f"({u}, {v}) {d=}")

        currentEdgeName = edgeName(u,v)
        edgeGraph.add_nodes_from([(currentEdgeName, d)])

        # add the edges between edges that are joined by the beginning node
        for u2, v2 in inputGraph.edges(u):
            if v2 != v:
                edgeGraph.add_edge(currentEdgeName, edgeName(u2, v2))

        # add the edges between edges that are joined by the end nodes
        for u2, v2 in inputGraph.edges(v):
            if v2 != u:
                edgeGraph.add_edge(currentEdgeName, edgeName(u2, v2))

    return edgeGraph

def edgeName(start, end):

    if start < end:
        first = start
        last = end
    else:
        first = end
        last = start

    return f"{first}_{last}"

# Turns labels into numbers
def hotEncoder(label):
    if label not in options['hotEncodeDictionary']:
        options['hotEncodeDictionary'][label] = len(options['hotEncodeDictionary'])

    return options['hotEncodeDictionary'][label]
