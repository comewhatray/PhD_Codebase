from Utilities import ComeWhatRayUtil as CWR
from operator import itemgetter
import os
import ast
import math
import sys
import warnings

options = {
    "method": "NoEncoding",
    "patternSize": 3,
    "precision": 3,
    "topN": 4
}

pitchEncodingDict = {
    'A': 9,
    'B': 11,
    'C': 0,
    'D': 2,
    'E': 4,
    'F': 5,
    'G': 7,
}

def startProcess(work, inputOptions = None):
    CWR.updateOldDictionaryEntriesWithNewDictionaryEntries(options, inputOptions)
    work = CWR.openFile(work)

    warnings.warn("Please recheck some methods in doraisamy encoding file and remove this warning and the import")

    this_module = sys.modules[__name__]
    methodInstanciated = getattr(this_module, options['method'])

    print(f"Pattern Encoding Approach: {options['method']}")
    extractedPatterns = methodInstanciated(work)

    return extractedPatterns


# Encoding Methods
# -----------------------------------------------------

def NoEncoding(work):
    print("no encoding")

# Calculating the duration separately
def DoraisamyEncoding(dataset, workspace):

    doraisamyProgenitorEncoding(dataset, workspace, durationDistributionCalculator, durationEncoding)


# Calculating the Duration, as a ratio as Doraisamy Intended
def DoraisamyRatioEncoding(dataset, workspace):

    doraisamyProgenitorEncoding(dataset, workspace, ratioDurationDistributionCalculator, ratioDurationEncoding)


# Dry method allowing for each progeny to use it as needed
def doraisamyProgenitorEncoding(dataset, workspace, durationCalculator, durationEncoder):
    # pitchDist = intervalDistribution(dataset)
    durationPeaks = durationPeaksDiscovery(dataset, durationCalculator)

    fileCounter = 1
    numFiles = len(dataset)

    for work in dataset:

        print("Name: " + work["Name"])
        CWR.printCounter("Work", fileCounter, numFiles)

        # Details for saving the new file
        fileName = work["Name"] + ".json"
        savedFileLocation = CWR.appendDirectory(workspace, fileName)

        encodedDictionary = {}

        patternList = CWR.openFile(work["Location"])

        if not os.path.exists(savedFileLocation):

            for pattern in patternList:

                encodedPattern = encodePattern(pattern, durationPeaks, durationEncoder)

                if encodedPattern in encodedDictionary:
                    encodedDictionary[encodedPattern] += patternList[pattern]

                else:
                    encodedDictionary[encodedPattern] = patternList[pattern]

            CWR.saveFile(savedFileLocation, encodedDictionary)

        else:
            print("File already exists")

        # print(encodedDictionary)

        fileCounter += 1
        print(CWR.smallSpacer)


# Function to encode the patterns using doraisamys approach
# -----------------------------------------------------

# how to encode a pattern
def encodePattern(pattern, durationPeaks, encodingMethod):
    # TODO Update to be like the pattern extraction class such that the encoding step is modular?

    pattern = ast.literal_eval(pattern)

    # Duration Encoding Setup
    # -------------------

    bucketBreakpointsList = []

    # All buckets not in the extreme (The middle buckets)
    durationPeakKeys = list(durationPeaks.keys())
    for i in range(len(durationPeaks) - 1):
        # Calculates teh middle distance between the peaks
        bucketBreakpointsList.append(round((durationPeakKeys[i] + durationPeakKeys[i+1])/2, options["precision"]))

    # Calculates the distance between the first and last frequently occuring point and the middle distance of the previous value
    startDiff = durationPeakKeys[0] - bucketBreakpointsList[0]
    endDiff = durationPeakKeys[-1] - bucketBreakpointsList[-1]

    # Creates a new point that is a distance defined above in front of the beginning
    # and after the end to encapsulate the extremes
    startPoint = round(durationPeakKeys[0] + startDiff, options["precision"])
    endPoint = round(durationPeakKeys[-1] + endDiff, options["precision"])

    # The list containing the start point, the end point and the middle of the list
    bucketBreakpoints = [startPoint] + bucketBreakpointsList + [endPoint]
    # print(finalBucketList)

    bucketEncodings = bucketEncoding(bucketBreakpoints)

    # Pitch Encoding Setup
    # -------------------

    # Per the paper
    constantX = 27
    constantY = 24

    encodingString = ""

    # Encoding Step
    # -------------------

    # The first N values of the string are the pitch encodings
    for i in range(options["patternSize"]-1):

        # Using curve to define how the pitch values are encoded
        intervalEncoding = int(constantX * math.tanh(pattern[i]/constantY))
        encodingString += pitchEncodingDict[intervalEncoding]

    # The last N values of the string are the duration (Assumption) encodings
    encodingString += encodingMethod(bucketBreakpoints, bucketEncodings, pattern)

    # for i in range(defaultValues["patternSize"] - 1, defaultValues["patternSize"]-1 + defaultValues["patternSize"]-1):
    #
    #     # Using our extensive math to find out how the durations are encoded
    #     encodingString += durationEncoding(bucketBreakpoints, bucketEncodings, pattern[i])

    return encodingString


# Types of Encoding for duration
# -------------------------------

# Encode each duration seperately
def durationEncoding(buckets, encoding, pattern):

    durationEncodingSegment = ""

    for i in range(options["patternSize"] - 1, options["patternSize"]-1 + options["patternSize"]-1):

        # Using our extensive math to find out how the durations are encoded
        # encodingString += durationEncoding(bucketBreakpoints, bucketEncodings, pattern[i])
        duration = pattern[i]

        if duration != 0:
            durationLog = math.log(duration)

            durationEncodingSegment += durationEncodingHelper(buckets, encoding, durationLog)

        else:
            durationEncodingSegment += '0'

    return durationEncodingSegment


# Encode the durations as the average of all of them
def ratioDurationEncoding(buckets, encoding, pattern):
    durationEncodingSegment = ""

    ratioValue = calculateDurationRatioValue(pattern)

    if ratioValue != 0:
        durationLog = math.log(ratioValue)

        for i in range(len(buckets)):
            if durationLog < buckets[i]:
                return encoding[i]
        durationEncodingSegment += encoding[-1]
    else:
        durationEncodingSegment += '0'

    return durationEncodingSegment


# Distribution calculation related methdos
# -------------------------------

# Function to determine where the bucket breakpoints are
def durationPeaksDiscovery(dataset, durationCalculator):

    ratioDistribution = durationAssumptionDistribution(dataset, durationCalculator)

    roundedResults = {round(key, options["precision"]): 0 for key in ratioDistribution}

    # rdf = pd.DataFrame(roundedResults.items(), columns=['Log', 'Frequency'])
    # print(rdf)

    # Round to two deimcal places kadding all the results it combined this way
    for key in ratioDistribution:
        if roundedResults[round(key, options["precision"])] < ratioDistribution[key]:
            roundedResults[round(key, options["precision"])] += ratioDistribution[key]

    roundedResults = dict(sorted(roundedResults.items()))
    # rdf = pd.DataFrame(roundedResults.items(), columns=['Log', 'Frequency'])
    # print(rdf.to_string())

    # Now check if items are .01 away to continue to avoid to similar items

    correctionDict = {}
    correctionCheck = 0.01

    for key in roundedResults:
        if round(key + correctionCheck, 2) not in correctionDict and round(key - correctionCheck,
                                                                           2) not in correctionDict:
            correctionDict[key] = roundedResults[key]
        else:
            if round(key + correctionCheck, 2) in correctionDict:
                correctionDict[round(key + correctionCheck, 2)] += roundedResults[key]
            elif round(key - correctionCheck, 2) in correctionDict:
                correctionDict[round(key - correctionCheck, 2)] += roundedResults[key]

    correctionDict = dict(sorted(correctionDict.items()))
    # cdf = pd.DataFrame(correctionDict.items(), columns=['Log', 'Frequency'])
    # print(cdf.to_string())

    parseDictionary = correctionDict

    positiveResults = {key: parseDictionary[key] for key in parseDictionary if key >= 0}
    negativeResults = {key: parseDictionary[key] for key in parseDictionary if key < 0}

    topPosRes = dict(sorted(positiveResults.items(), key=itemgetter(1), reverse=True)[:options["topN"]+1])
    topNegRes = dict(sorted(negativeResults.items(), key=itemgetter(1), reverse=True)[:options["topN"]])

    topPosRes = dict(sorted(topPosRes.items()))
    topNegRes = dict(sorted(topNegRes.items(), reverse=True))

    topResults = topPosRes | topNegRes

    topResults = dict(sorted(topResults.items()))

    # tdf = pd.DataFrame(topResults.items(), columns=['Log', 'Frequency'])

    # print(tdf)

    return topResults


# Calculate the interval distribution
def intervalDistribution(dataset):
    print("Getting the distribution of intervals")

    intervalDistributionDict = {}

    # Going through each file
    for work in dataset:

        patternList = CWR.openFile(work["Location"])

        # For each pattern in a file
        for pattern in patternList:

            pattern = ast.literal_eval(pattern)

            # Add it to the list
            for i in range(options["patternSize"] - 1):
                if pattern[i] not in intervalDistributionDict:
                    intervalDistributionDict[pattern[i]] = 1
                else:
                    intervalDistributionDict[pattern[i]] += 1

    # print(intervalDistributionDict)

    # plt.bar(intervalDistributionDict.keys(), intervalDistributionDict.values(), color='g')
    # plt.show()

    # The way this is ploted makes it not symetrical
    # Because we only consider intervals in the positive direction

    return intervalDistributionDict


# Calculate the duration distribution
def durationAssumptionDistribution(dataset, durationCalculator):
    print("Getting the distribution of durations")

    ratioDistribution = {
        # "zero": 0
    }

    logCount = []

    for work in dataset:

        patternsList = CWR.openFile(work["Location"])

        for pattern in patternsList:

            pattern = ast.literal_eval(pattern)

            # Extracts all the intervals from the patterns
            # Given the provided method
            durationCalculator(ratioDistribution, pattern)


    # df = pd.DataFrame(ratioDistribution.items(), columns=['Log', 'Frequency'])
    # print(df)
    # TODO Change plt type
    # plt.figure(figsize=(10, 5))
    # plt.title('Log of Ratio Distirbution')
    # plt.ylabel('Frequency')
    # plt.xlabel('Log(Ratio)')
    # plt.ylim(0, 50000)
    # sns.histplot(data=logCount)
    # plt.xticks(np.arange(-3, 4, 1))
    # plt.show()

    return ratioDistribution


# Duration Calculators
# ------------------------------------------------

# Calculates the ratio of durations
def ratioDurationDistributionCalculator(ratioDistribution, pattern):

    ratio = calculateDurationRatioValue(pattern)

    if ratio != 0:
        if math.log(ratio) not in ratioDistribution:
            ratioDistribution[math.log(ratio)] = 1
        else:
            ratioDistribution[math.log(ratio)] += 1


# Calculates all of the durations
def durationDistributionCalculator(ratioDistribution, pattern):

    for j in range(options["patternSize"], options["patternSize"] - 1 + options["patternSize"] - 1):

        # Can't get log of zero so that is encoded seperately
        if pattern[j] != 0:
            # logCount.append(math.log(pattern[j]))

            if math.log(pattern[j]) not in ratioDistribution:
                ratioDistribution[math.log(pattern[j])] = 1
            else:
                ratioDistribution[math.log(pattern[j])] += 1


# Helper Methods
# ------------------------------------------------

# Just a helper function to keep things dry
def calculateDurationRatioValue(pattern):
    ratio = 0
    for j in range(options["patternSize"], options["patternSize"] - 1 + options["patternSize"] - 1):
        ratio += pattern[j]

    return round(ratio / options["patternSize"], options["precision"])


# Function to encode the text values into buckets
def bucketEncoding(encodingBreakPoints):

    # To encapsulate the pitches that end up in the extreme
    bucketEncodings = ['y']

    numBuckets = len(encodingBreakPoints)

    # Populates the encoding table with the encoding values
    for i in range(int(numBuckets/2)-numBuckets+1, int(numBuckets/2)):
        if i == 0:
            bucketEncodings.append('Z')
        else:
            bucketEncodings.append(pitchEncodingDict[i])

    # To encapsulate the pitches that end up in the extreme
    bucketEncodings.append('Y')

    return bucketEncodings


# Cheap and cheerful way to get desired effect
def durationEncodingHelper(buckets, encoding, logValue):
    for i in range(len(buckets)):
        if logValue < buckets[i]:
            return encoding[i]

    return encoding[-1]
