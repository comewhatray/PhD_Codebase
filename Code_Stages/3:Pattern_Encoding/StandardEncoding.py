from Utilities import ComeWhatRayUtil as CWR
import sys

options = {
    "method": "NoEncoding"
}

def encodePatterns(patternList, inputOptions=None):
    CWR.updateOldDictionaryEntriesWithNewDictionaryEntries(options,inputOptions)
    this_module = sys.modules[__name__]
    methodInstanciated = getattr(this_module, options['method'])

    print(f"Pattern Encoding Approach: {options['method']}")
    extractedPatterns = methodInstanciated(patternList)

    return extractedPatterns

# Encoding Methods
#-----------------------------------------------------------------------------------------------------------------------

# Does what it says on the tin
def NoEncoding(work):
    return work