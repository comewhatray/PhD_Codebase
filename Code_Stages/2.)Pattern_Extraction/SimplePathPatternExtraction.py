from Utilities import ComeWhatRayUtil as CWR
import sys
import itertools

# MUST USE A GRAPH REPRESENTATION

options = {
    "method": "SlidingWindowMelodyExtraction",
    "patternSize": 3,
    "gaps": 0,
    "precision": 3
}

def generatePatterns(work, inputOptions=None):
    # Update Options with user input
    CWR.updateOldDictionaryEntriesWithNewDictionaryEntries(options, inputOptions)

    # Setting up python voodoo magic to let me use a sting to call a function
    this_module = sys.modules[__name__]
    methodInstanciated = getattr(this_module, options['method'])

    print(f"Pattern Extraction Approach: {options['method']}")
    extractedPatterns = methodInstanciated(work)

# Sliding Window Approaches
# -----------------------------------------------------------

def SlidingWindowAllExtraction(work):
    initialFunction = slidingWindowAllInitial
    loopFunction = slidingWindowAllLoop
    return slidingWindowProgenitor(work, initialFunction, loopFunction)

def SlidingWindowMelodyExtraction(work):
    initialFunction = slidingWindowMelodyInitial
    loopFunction = slidingWindowMelodyLoop
    return slidingWindowProgenitor(work, initialFunction, loopFunction)

def SlidingWindowMelodyTriadExtraction(work):
    initialFunction = slidingWindowMelodyTriadInitial
    loopFunction = slidingWindowMelodyTriadLoop
    return slidingWindowProgenitor(work, initialFunction, loopFunction)

def SlidingWindowDoraisamyExtraction(work):
    initialFunction = slidingWindowDoraisamyInitial
    loopFunction = slidingWindowDoraisamyLoop
    return slidingWindowProgenitor(work, initialFunction, loopFunction)

# Sliding Window Aggregator Function
# -----------------------------------------------------------

# To reduce code duplication as all sliding window methods follow a similar process
def slidingWindowProgenitor(pointSet, initialFunction, loopFunction):

    # First Unique List Creation
    pieceHash = {}

    initialList = []
    uniquelist = []

    counter = 0
    # Initial setup of unique list
    while counter < len(pointSet) and \
            (len(uniquelist) < (options["patternSize"] + options["gaps"])
             or initialList[len(initialList) - 1]['position'] == pointSet[counter]['position']):
        initialList.append(pointSet[counter])

        if pointSet[counter]['position'] not in uniquelist:
            uniquelist.append(pointSet[counter]['position'])
        counter += 1

    # Add first to output
    initialFunction(initialList, pieceHash)

    # Now Clearning and begining the loop
    updateCounter = 0
    while counter < len(pointSet):

        # Remove all things with first position
        firstPos = uniquelist[0]
        uniquelist.remove(firstPos)

        removeCount = 0
        for note in initialList:
            if note['position'] == firstPos:
                removeCount += 1

        initialList = initialList[removeCount:]

        beforeList = initialList.copy()
        nextList = []
        while counter < len(pointSet) \
                and (len(uniquelist) < (options["patternSize"] + options["gaps"])
                     or initialList[len(initialList) - 1]['position'] == pointSet[counter]['position']):

            initialList.append(pointSet[counter])
            nextList.append(pointSet[counter])

            if pointSet[counter]['position'] not in uniquelist:
                uniquelist.append(pointSet[counter]['position'])

            counter += 1

        # Loop funciton input
        loopFunction(beforeList, nextList, pieceHash)

        beforeList.clear()
        nextList.clear()

        # Console Update Code
        if counter > ((len(pointSet) / 10) * updateCounter):
            print(str(counter) + '/' + str(len(pointSet)))
            # TODO Update to remove overarching patternHash
            print('Number of Patterns: ' + str(len(pieceHash)))

            updateCounter += 1

    initialList.clear()
    uniquelist.clear()

    return pieceHash

# Sliding Window Assistance Functions
# -----------------------------------------------------------

# Sliding window All initial setup
def slidingWindowAllInitial(initialList, pieceHash):
    patternList = CWR.nCr(initialList, options["patternSize"])
    inputPatternListToHash(pieceHash, patternList, pointSetHashingMethod)


# Sliding window All after initial step the recursion step
def slidingWindowAllLoop(beforeList, nextList, pieceHash):
    patternList = combine2Lists(beforeList, nextList)
    inputPatternListToHash(pieceHash, patternList, pointSetHashingMethod)


# Sliding window Melody Triad initial setup
def slidingWindowMelodyInitial(initialList, pieceHash):
    patternList = melodyTriadDiscovery(initialList, enableTriads=False)
    inputPatternListToHash(pieceHash, patternList, pointSetHashingMethod)


# Sliding window Melody Triad after initial step the recursion step
def slidingWindowMelodyLoop(beforeList, nextList, pieceHash):
    patternList = melodyTriadDiscoveryOptimisation(beforeList, nextList, enableTriads=False)
    inputPatternListToHash(pieceHash, patternList, pointSetHashingMethod)


# Sliding window Melody Triad initial setup
def slidingWindowMelodyTriadInitial(initialList, pieceHash):
    patternList = melodyTriadDiscovery(initialList)
    inputPatternListToHash(pieceHash, patternList, pointSetHashingMethod)


# Sliding window Melody Triad after initial step the recursion step
def slidingWindowMelodyTriadLoop(beforeList, nextList, pieceHash):
    patternList = melodyTriadDiscoveryOptimisation(beforeList, nextList, options["patternSize"])
    inputPatternListToHash(pieceHash, patternList, pointSetHashingMethod)


# Sliding window Doraisamy initial setup
def slidingWindowDoraisamyInitial(initialList, pieceHash):
    patternList = melodyTriadDiscovery(initialList, enableTriads=False)
    inputPatternListToHash(pieceHash, patternList, doraisamyHashingMethod)


# Sliding window Doraisamy after initial step the recursion step
def slidingWindowDoraisamyLoop(beforeList, nextList, pieceHash):
    patternList = melodyTriadDiscoveryOptimisation(beforeList, nextList, options["patternSize"], enableTriads=False)
    inputPatternListToHash(pieceHash, patternList, doraisamyHashingMethod)

# Extraction Methods
# ----------------------------------------------------------------------------------------------------

def triadDiscovery(array, patternsList):
    if len(array) >= 3:
        tempList = CWR.nCr(array, 3)

        for value in tempList:
            patternsList.append(value)


def melodyDiscovery(array, n):
    buckets = []
    temp = []

    patternsList = []
    for note in array:
        if not temp:
            temp.append(note)
        elif temp[0]['position'] == note['position']:
            temp.append(note)
        else:
            buckets.append(temp.copy())
            temp.clear()
            temp.append(note)

    buckets.append(temp)

    tempList = nCrOnePerList(buckets, n)

    for sample in tempList:
        for subSample in sample:
            patternsList.append(subSample)

    return patternsList


def melodyTriadDiscovery(array, enableTriads=True):

    buckets = []
    temp = []

    patternsList = []
    for note in array:
        if not temp:
            temp.append(note)
        elif temp[0]['position'] == note['position']:
            temp.append(note)
        else:
            buckets.append(temp.copy())
            temp.clear()
            temp.append(note)

    buckets.append(temp)

    # Searching for Triads
    if enableTriads:
        for bucket in buckets:
            triadDiscovery(bucket, patternsList)

    tempList = nCrOnePerList(buckets, options["patternSize"])

    for sample in tempList:
        for subSample in sample:
            patternsList.append(subSample)

    return patternsList


def melodyTriadDiscoveryOptimisation(beforeList, afterList, enableTriads=True):

    n = options["patternSize"]

    totalCombinations = []

    combinationLists = CWR.nCr(beforeList, n-1)
    tempListConversion = []
    for combList in combinationLists:
        tempListConversion.append(list(combList) + afterList)

    for combList in tempListConversion:
        totalCombinations += melodyDiscovery(combList, n)

    if enableTriads:
        triadDiscovery(afterList, totalCombinations)

    return totalCombinations


# Hashing Methods
# ----------------------------------------------------------------------------------------------------

# pointSet Hashing Method
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


# Doraisamy Hashing Method
def doraisamyHashingMethod(pattern):
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

    ratio = round(tempPosition[1]/tempPosition[0], options["precision"])

    return str(tuple(tempPitch + [ratio]))


#Inludes the durations in the hashing method
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
# ----------------------------------------------------------------------------------------------------

# n chose r with the exception only one element can be chosen from each list
def nCrOnePerList(arrays, r):

    listCombinations = CWR.nCr(arrays, r)

    combinations = []

    for listComb in listCombinations:

        combinations.append([p for p in itertools.product(*listComb)])

    return combinations


# A more efficient helper method for combining two lists
def combine2Lists(beforeList, afterList):

    totalCombinations = []
    for x in range(1, options["patternSize"] + 1):

        if x > len(afterList):
            break

        afterCombinations = CWR.nCr(afterList, x)
        beforeCombinations = CWR.nCr(beforeList, options["patternSize"] - x)

        for beforeComb in beforeCombinations:
            for afterComb in afterCombinations:
                totalCombinations.append(beforeComb + afterComb)

        beforeCombinations.clear()
        afterCombinations.clear()

    return totalCombinations


# Takes a list of Patterns and inputs it into a dictionary
def inputPatternListToHash(patternsHash, patternList, hashingMethod):

    for pattern in patternList:
        pHash = hashingMethod(pattern)
        if pHash not in patternsHash:
            patternsHash[pHash] = 1

        else:
            patternsHash[pHash] += 1


# Given a graph, a node and a path length get all pathes of that length begining with the node
def generatePatternsContainingNode(tuneGraph, node, length, excludeSet=None):

    if excludeSet is None:
        excludeSet = set([node])
    else:
        excludeSet.add(node)
    if length == 0:
        return [[node]]
    paths = [[node] + path for neighbor in tuneGraph.neighbors(node) if neighbor not in excludeSet for path in
             generatePatternsContainingNode(tuneGraph, neighbor, length - 1, excludeSet)]

    excludeSet.remove(node)

    return paths

