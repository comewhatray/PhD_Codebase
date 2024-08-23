from Utilities import ComeWhatRayUtil as CWR
import sys

# MUST USE A GRAPH REPRESENTATION

options = {
    "": ""
}

def generatePatterns(work, inputOptions=None):
    # Update Options with user input
    CWR.updateOldDictionaryEntriesWithNewDictionaryEntries(options, inputOptions)

    # Setting up python voodoo magic to let me use a sting to call a function
    this_module = sys.modules[__name__]
    methodInstanciated = getattr(this_module, options['method'])

    print(f"Pattern Extraction Approach: {options['method']}")
    extractedPatterns = methodInstanciated(work)

    return extractedPatterns



