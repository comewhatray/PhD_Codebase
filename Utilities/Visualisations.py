from Utilities import ComeWhatRayUtil as CWR
import networkx as nx
import matplotlib.pyplot as plt


def visualiseGraph(graph):


def visualiseSpatialGraph(work):
    graph = CWR.openFile(work)


    positions = nx.get_node_attributes(graph, 'pos')
    nx.draw(graph, positions)
    plt.show()
    #
    # if options["toSave"]:
    #     savefig()