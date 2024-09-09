from matplotlib.pyplot import savefig

from Utilities import ComeWhatRayUtil as CWR
import sys
import networkx as nx
import matplotlib.pyplot as plt

options = {
    "function": None,
    "toSave": False,


}

def startProcess(work, inputOptions=None):
    # Updating Options
    CWR.updateOldDictionaryEntriesWithNewDictionaryEntries(options, inputOptions)
    # work = CWR.openFile(work)

    # Setting up python voodoo magic to let me use a sting to call a function

    if options["function"] is not None:
        this_module = sys.modules[__name__]
        methodInstanciated = getattr(this_module, options['function'])

        print(f"Visualisation Approach: {options['function']}")
        methodInstanciated(work)


# given a file location to a graph, visualise it with the relevant positional data
def visualiseSpatialGraph(work):
    graph = CWR.openFile(work)

    positions = nx.get_node_attributes(graph, 'pos')
    nx.draw(graph, positions)
    plt.show()

    if options["toSave"]:
        savefig()
