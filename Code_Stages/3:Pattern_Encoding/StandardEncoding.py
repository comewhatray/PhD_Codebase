from Utilities import ComeWhatRayUtil as CWR
import sys

options = {
    "method": None
}

def startProcess(work, inputOptions=None):
    CWR.updateOldDictionaryEntriesWithNewDictionaryEntries(options,inputOptions)
    work = CWR.openFile(work)
    this_module = sys.modules[__name__]
    if options["method"] is not None:
        methodInstanciated = getattr(this_module, options['method'])
        print(f"Pattern Encoding Approach: {options['method']}")
        extractedPatterns = methodInstanciated(work)

    else:
        extractedPatterns = work

    return extractedPatterns

# Encoding Methods
#-----------------------------------------------------------------------------------------------------------------------