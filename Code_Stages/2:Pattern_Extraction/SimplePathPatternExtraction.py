from Utilities import ComeWhatRayUtil as CWR
import sys
import json

# MUST USE A GRAPH REPRESENTATION

options = {
    "method": "SimplePathGraphDurationExtraction",
    "patternSize": 3,
    "precision": 3
}

def startProcess(work, inputOptions=None):
    # Update Options with user input
    CWR.updateOldDictionaryEntriesWithNewDictionaryEntries(options, inputOptions)
    work = CWR.openFile(work)

    # Setting up python voodoo magic to let me use a sting to call a function
    this_module = sys.modules[__name__]
    methodInstanciated = getattr(this_module, options['method'])

    print(f"Pattern Extraction Approach: {options['method']}")
    extractedPatterns = methodInstanciated(work)

    return extractedPatterns


# Pattern Extraction methods
#-----------------------------------------------------------------------------------------------------------------------

def SimplePathGraphPointSetExtraction(work):
    hashingMethod = pointSetHashingMethod
    return simplePathGraphProgenitor(work, hashingMethod)


def SimplePathGraphDurationExtraction(work):
    hashingMethod = durationHashingMethod
    return simplePathGraphProgenitor(work, hashingMethod)


# Progenitor Method
#-----------------------------------------------------------------------------------------------------------------------

def simplePathGraphProgenitor(work, hashingMethod):
    patternHash = {}
    noteCombinations = {}

    for x in range(work.number_of_nodes()):
        patterns = generatePatternsContainingNode(work, x, options["patternSize"] - 1)

        for combination in patterns:
            combination.sort()

            strTemp = str(combination)

            if strTemp not in noteCombinations:
                noteCombinations[strTemp] = 1

    for eKey in noteCombinations:
        eList = json.loads(eKey)
        tempList = []

        for point in eList:
            # print(tuneGraph.nodes[point])
            tempList.append(work.nodes[point])

        inputPatternListToHash(patternHash, [tempList], hashingMethod)

    return patternHash

# Hashing Methods
#-----------------------------------------------------------------------------------------------------------------------

# PointSet Hashing Method
def pointSetHashingMethod(pattern):
    tempPitch = []
    tempPosition = []
    previousPitch = -1
    previousPosition = -1
    for p in pattern:

        if previousPitch != -1 and previousPosition != -1:
            tempPitch.append(round(p['pitch'] - previousPitch, options["precision"]))
            tempPosition.append(round(p['position'] - previousPosition, options["precision"]))
            previousPitch = p['pitch']
            previousPosition = p['position']
        else:
            previousPitch = p['pitch']
            previousPosition = p['position']

    return str(tuple(tempPitch + tempPosition))

# Inludes the durations in the hashing method
def durationHashingMethod(pattern):
    tempPitch = []
    tempPosition = []
    durations = []
    previousPitch = -1
    previousPosition = -1
    for p in pattern:

        if previousPitch != -1 and previousPosition != -1:
            tempPitch.append(round(p['pitch'] - previousPitch, options["precision"]))
            tempPosition.append(round(p['position'] - previousPosition, options["precision"]))

            durations.append(p['duration'])

            previousPitch = p['pitch']
            previousPosition = p['position']
        else:
            previousPitch = p['pitch']
            previousPosition = p['position']
            durations.append(p['duration'])

                    #  0, 1,        2 ,3,         4,5,6
    return str(tuple(tempPitch + tempPosition + durations))


# Helper Methods
#-----------------------------------------------------------------------------------------------------------------------

# Given a graph, a node and a path length get all pathes of that length begining with the node
def generatePatternsContainingNode(tuneGraph, node, length, excludeSet=None):

    if excludeSet == None:
        excludeSet = set([node])
    else:
        excludeSet.add(node)
    if length == 0:
        return [[node]]
    paths = [[node] + path for neighbor in tuneGraph.neighbors(node) if neighbor not in excludeSet for path in
             generatePatternsContainingNode(tuneGraph, neighbor, length - 1, excludeSet)]

    excludeSet.remove(node)

    return paths

# Takes a list of Patterns and inputs it into a dictionary
def inputPatternListToHash(patternsHash, patternList, hashingMethod):

    for pattern in patternList:
        pHash = hashingMethod(pattern)
        if pHash not in patternsHash:
            patternsHash[pHash] = 1

        else:
            patternsHash[pHash] += 1