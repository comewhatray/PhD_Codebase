from torch_geometric.graphgym import train

from Utilities import ComeWhatRayUtil as CWR
from Utilities import datasetManagment as DM
import networkx as nx
import sys
import os
import math
import matplotlib.pyplot as plt

import torch
from torch_geometric.data import Data
from torch_geometric.utils.convert import from_networkx


import mlx.core as mx
# from mlx_graphs.utils.convert import from_networkx
from mlx_graphs.data.data import GraphData

from parallelbar import progress_map

midiTensorsLocation = "Papers/Paper_3/Datasets/ClassicalComposersDataset/MidiTensors"


options = {
    "function": "GNN",
    "trainPercentage": 0.8,
    "testing": False,
    "saveLocation": None,
    "saveType": None,
    "threading": False,
    # Do I want to save the gpickle in between
    "saveIntermediate": None,
    "maxWorkers": 24,
}

hotEncodeDictionary = {

}

this_module = sys.modules[__name__]

def startProcess(dataset, inputOptions):
    print("Generating Tensor Graphs for GNN")

    CWR.updateOldDictionaryEntriesWithNewDictionaryEntries(options, inputOptions)

    methodInstanciated = getattr(this_module, options['function'])

    classificationFormat = DM.convertDatasetToOldFormat(dataset)

    # Prepopulating the hotEncoding and datapoint ID (For multiprocessing purposes)
    dataPointNum = 0
    for datapoint in classificationFormat:
        hotEncoder(datapoint["Label"])
        datapoint["ID"] = dataPointNum
        dataPointNum += 1

    CWR.saveFile("tempHotEncodings.json", hotEncodeDictionary)


    return methodInstanciated(classificationFormat)

# ----------------------------------------------------------------------------------------------------------------------

def graphClassificationUsingNodeInformation(dataset):
    classificationFormat = dataset

    dataset = []
    for nodeGraph in classificationFormat:

        pyg_graph = from_networkx(CWR.openFile(nodeGraph['Location'], printDisplay= not options['threading']))

        x = []

        for i in range(pyg_graph.num_nodes):
            x.append([pyg_graph['pitch'][i], pyg_graph['position'][i], pyg_graph['duration'][i]])

        pyg_graph.x = torch.tensor(x)
        pyg_graph.y = torch.tensor([hotEncoder(nodeGraph['Label'])])

        cleanedTorchData = Data(
            # X is a tensor of the features
            x=pyg_graph.x,
            # Edge index is edge index
            edge_index=pyg_graph.edge_index,
            # This is the class it belongs to that has been hot encoded to a number
            y=pyg_graph.y,
            MidiName=nodeGraph['Name']
        )

        # save
        saveTo = CWR.appendDirectory(options["saveLocation"], f"data_{nodeGraph["ID"]}{options["saveType"]}")
        CWR.saveFile(saveTo, cleanedTorchData)



    # return

# Uses the edge features to classify the graph
def graphClassificationUsingEdgeInformation(dataset):

    classificationFormat = dataset
    if not options["threading"]:
        for nodeGraph in classificationFormat:
            print("Classify Graph using Edge Information")
            print(f"Datapoint: data_{nodeGraph['ID']}")
            graphClassificationUsingEdgeInformationPointWorker(nodeGraph)

    # If we are multiprocessing this
    else:
        print(f"MultiProcessing: Generating Tensor Graphs for GNN")
        for datapoint in classificationFormat:
            datapoint["OPTIONS"] = options
        results = progress_map(graphClassificationUsingEdgeInformationPointWorker, classificationFormat, n_cpu=options["maxWorkers"], chunk_size=1)

    # dataset = []



        # dataset.append(pyg_graph)

    # I believe this is old code for how I generated random distributions. I'm scared to delete it though
    {
    #So I could create a tensor where the rows is dictated by the number of nodes and the columns are the number of features
    # In my case that would be 3 features

    # division = math.floor(options["trainPercentage"] * len(dataset)) + 1

    # dataset = dataset.shuffle()

    # trainData = dataset[:division]
    # testData = dataset[division:]

    # trainLoader = DataLoader(trainData, batch_size=32, shuffle=True)
    # testLoader = DataLoader(testData, batch_size=32, shuffle=True)

    # datasetPlanet = Planetoid(root='/tmp/Cora', name='Cora')
    # print('test')
    # print(loader[0])

        # nx.draw(edgeGraph, with_labels=True)
        # plt.show()
    }

# ProcessFunctions
# ----------------------------------------------------------------------------------------------------------------------

def graphClassificationUsingEdgeInformationPointWorker(dataPoint):

    # This solves multiprocessing issue of defaulting to the original options, I simlpy import them when multiprocessing
    if "OPTIONS" in dataPoint:
        CWR.updateOldDictionaryEntriesWithNewDictionaryEntries(options, dataPoint["OPTIONS"])
        hotEncodeDictionary = CWR.openFile("tempHotEncodings.json", printDisplay=not options['threading'])

    saveTo = os.path.join(options["saveLocation"], f"data_{dataPoint["ID"]}{options["saveType"]}")

    if not os.path.exists(saveTo):

        edgeGraph = edgeNodeSwapGraph(CWR.openFile(dataPoint['Location'], printDisplay=not options['threading']))

        if options["saveIntermediate"] is not None:
            CWR.saveFile(f"{options['saveIntermediate']}/{dataPoint['Name']}_edgeGraph.gpickle", edgeGraph)

        # TODO TEMP WORKAROUND FOR LABELED NODES
        # mapping = {}
        # counter = 0
        # for node in edgeGraph.nodes():
        #     mapping[node] = counter
        #     counter += 1
        #
        # edgeGraph = nx.relabel_nodes(edgeGraph, mapping)

        pyg_graph = from_networkx(edgeGraph)

        x = []
        for i in range(pyg_graph['num_nodes']):
            x.append([pyg_graph['pitchChange'][i], pyg_graph['onsetGap'][i], pyg_graph['endOnsetGap'][i]])

        pyg_graph.x = torch.tensor(x)
        pyg_graph.y = torch.tensor([hotEncoder(dataPoint['Label'])])

        # pyg_graph.x = mx.array(x)
        # pyg_graph.y = mx.array([hotEncoder(dataPoint['Label'])])

        cleanedTorchData = Data(
            # X is a tensor of the features
            x=pyg_graph.x,
            # Edge index is edge index
            edge_index=pyg_graph.edge_index,
            # This is the class it belongs to that has been hot encoded to a number
            y=pyg_graph.y,
            MidiName=dataPoint['Name']
        )

        if not options["saveLocation"] == None:
            CWR.saveFile(saveTo , cleanedTorchData, printDisplay=not options['threading'])

    else:
        if not options["threading"]:
            print(f"data_{dataPoint["ID"]}{options["saveType"]} already exists")
            print(CWR.midSpacer)

# Helper Methods
# ----------------------------------------------------------------------------------------------------------------------

# creating a new graph where the node information is the edge information and edges are defined by the nodes that link two edges
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

# The convention for naming nodes when transforming the graph from being edge centric to node centric
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
    if label not in hotEncodeDictionary:
        hotEncodeDictionary[label] = len(hotEncodeDictionary)

    return hotEncodeDictionary[label]


# class MusicDataset(Dataset):
#     def __init__(self, root, transform = None, pre_transform = None):
#
#         super(MusicDataset, self).__init__(root, transform, pre_transform)


# class GCN(torch.nn.Module):
#     def __init__(self, hidden_channels):
#         super(GCN, self).__init__()
#         torch.manual_seed(12345)
#         self.conv1 = GCNConv(dataset.num_node_features, hidden_channels)
#         self.conv2 = GCNConv(hidden_channels, hidden_channels)
#         self.conv3 = GCNConv(hidden_channels, hidden_channels)
#         self.lin = Linear(hidden_channels, dataset.num_classes)
#
#     def forward(self, x, edge_index, batch):
#         # 1. Obtain node embeddings
#         x = self.conv1(x, edge_index)
#         x = x.relu()
#         x = self.conv2(x, edge_index)
#         x = x.relu()
#         x = self.conv3(x, edge_index)
#
#         # 2. Readout layer
#         x = global_mean_pool(x, batch)  # [batch_size, hidden_channels]
#
#         # 3. Apply a final classifier
#         x = F.dropout(x, p=0.5, training=self.training)
#         x = self.lin(x)
#
#         return x
#
# class MyDataset(InMemoryDataset):
#     def __init__(self, root, data_list, transform=None):
#         self.data_list = data_list
#         super().__init__(root, transform)
