from torch_geometric.graphgym import train

from Utilities import ComeWhatRayUtil as CWR
from Utilities import datasetManagment as DM
import networkx as nx
import sys
import math
import matplotlib.pyplot as plt

import torch
from torch_geometric.data import Data
from torch_geometric.loader import DataLoader
from torch_geometric.utils.convert import from_networkx
from torch_geometric.datasets import Planetoid
from torch_geometric.nn import GCNConv
from torch_geometric.data import Batch

midiTensorsLocation = "Papers/Paper_3/Datasets/ClassicalComposersDataset/MidiTensors"


options = {
    "function": "GNN",
    "trainPercentage": 0.8,
    "testing": False,
    "saveLocation": None,
}

hotEncodeDictionary = {

}

this_module = sys.modules[__name__]

def startProcess(dataset, inputOptions):
    print("Generating Graphs for GNN")
    CWR.updateOldDictionaryEntriesWithNewDictionaryEntries(options, inputOptions)

    methodInstanciated = getattr(this_module, options['function'])

    return methodInstanciated(dataset)

# ----------------------------------------------------------------------------------------------------------------------

# Default GNN
def GNN(dataset):
    print("Beginning GNN")


def graphClassificationUsingNodeInformation(dataset):
    classificationFormat = DM.convertDatasetToOldFormat(dataset)

    dataset = []
    idx = 0
    for nodeGraph in classificationFormat:

        pyg_graph = from_networkx(CWR.openFile(nodeGraph['Location']))

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

        saveTo = CWR.appendDirectory(options["saveLocation"], f"data_{idx}.pt")
        CWR.saveFile(saveTo, cleanedTorchData)
        idx += 1



    # return




# Uses the edge features to classify the graph
def graphClassificationUsingEdgeInformation(dataset):
    print("Classify Graph using Edge Information")

    classificationFormat = DM.convertDatasetToOldFormat(dataset)

    dataset = []
    idx = 0
    for nodeGraph in classificationFormat:
        edgeGraph = edgeNodeSwapGraph(CWR.openFile(nodeGraph['Location']))


        pyg_graph = from_networkx(edgeGraph)
        x = []
        for i in range(pyg_graph['num_nodes']):
            x.append([pyg_graph['pitchChange'][i], pyg_graph['onsetGap'][i], pyg_graph['endOnsetGap'][i]])

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

        # dataset.append(pyg_graph)


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
