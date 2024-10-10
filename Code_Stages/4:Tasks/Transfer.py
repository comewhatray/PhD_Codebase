from Utilities import ComeWhatRayUtil as CWR
import sys


options = {
    "function": "torchTransfer",
    "newLocation": "",
    # "counter": 0 Counter doesn't work
}



def startProcess(work, inputOptions=None):
    # Updating Options
    CWR.updateOldDictionaryEntriesWithNewDictionaryEntries(options, inputOptions)

    # Setting up python voodoo magic to let me use a sting to call a function
    this_module = sys.modules[__name__]
    methodInstanciated = getattr(this_module, options['function'])

    print(f" Tensor Representations: {options['function']}")
    proximityGraphRepresentation = methodInstanciated(work)

    return proximityGraphRepresentation

def torchTransfer(work):

    # CWR.

    pass

