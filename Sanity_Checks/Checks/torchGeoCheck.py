from Utilities import ComeWhatRayUtil as CWR

import torch
# import torch_geometric as tgo
from torch_geometric.utils.convert import from_networkx
import torch_geometric.transforms as T


# import graphmuse.nn as gmnn

# fileLocation = "Sanity_Checks/SanityGraphs/MotzartExtractGraphExample.gpickle"
fileLocation = "Sanity_Checks/SanityGraphs/MozartExtraphWithGraphEdgeAttributes.gpickle"


graph = CWR.openFile(fileLocation)

print(graph)

pygraph = from_networkx(graph)

# pygraph = tgo.utils.to_undirected(pygraph.edge_index, pygraph.edge_attr)

print(pygraph)

# This results in the same graph
# transform = T.Compose([T.ToUndirected()])
# data = transform(pygraph)
# print(data)




