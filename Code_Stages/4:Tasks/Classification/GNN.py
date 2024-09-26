from Utilities import ComeWhatRayUtil as CWR
from torch_geometric.utils.convert import from_networkx
import sys

options = {
    "method": "GNN",
}

this_module = sys.modules[__name__]

def startProcess(dataset, inputOptions):
    print("Calculating Cosine Similarity")
    CWR.updateOldDictionaryEntriesWithNewDictionaryEntries(options, inputOptions)

    methodInstanciated = getattr(this_module, options['method'])

    return methodInstanciated(dataset)

# ----------------------------------------------------------------------------------------------------------------------

# Default GNN
def GNN(dataset, inputOptions):
    print("Beginning GNN")



