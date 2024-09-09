from Utilities import ComeWhatRayUtil as CWR
from Utilities import BoundingGenerator as BG
import numpy as np

# MAKE SURE TO SAVE THE LOOKUPTABLE IF IT IS USED

import sys
this_module = sys.modules[__name__]

options = {
    "task": "totalPatternOverlapSimilarity",
    "threshold": 0,
    # The distance from the line that the polygon is generated
    "shapeBuffer": 3,
    "polygon": {
            "type": "Rectangle",
            "dimensions": {
                "height": 4,
                "width": 4
            }
        },
    "LookUpTable": None
}

# LookUpTable = CWR.openFile("Papers/Paper 2/dynamicSimilarityDictionary.json")


def startProcess(dataset, inputOptions):
    CWR.updateOldDictionaryEntriesWithNewDictionaryEntries(options, inputOptions)

    methodInstanciated = getattr(this_module, options['method'])

    methodInstanciated(dataset)




# Overlap Similarity measures (Essentially it is a modified Jaccard Similarity measure)
# ----------------------------------------------------------------------------------------------------------------------

def MaxOverlapSimilarity(dataset):

    correlationMatrix = np.zeros((len(dataset), len(dataset)))

    for piece in dataset:
        openedPiece = CWR.openFile(piece['Location'])

        for comparedPiece in dataset[dataset.index(piece):]:

            totalSim = 0
            totalPatterns = len(openedPiece)
            patternCounter = 1

            comparisonPiece = CWR.openFile(comparedPiece["Location"])

            for pattern1 in openedPiece:
                maxSim = 0

                maxCount = 0
                maxComparison = ""
                print("Pattern: " + str(patternCounter) + "/" + str(totalPatterns))
                patternCounter += 1
                print("Compare:       " + pattern1)

                match = False

                # Quickly Checks for exact match
                match = False
                if pattern1 in comparisonPiece:
                    maxSim = 1
                    maxCount = openedPiece[pattern1] * comparisonPiece[pattern1]
                    maxComparison = pattern1
                    match = True

                if not match:

                    for pattern2 in comparisonPiece:

                        sim = 0

                        if options["LookUpTable"] is not None:

                            if pattern1 in options["LookUpTable"]:
                                if pattern2 in options["LookUpTable"][pattern1]:
                                    sim = options["LookUpTable"][pattern1][pattern2]

                            if pattern2 in options["LookUpTable"]:
                                if pattern1 in options["LookUpTable"][pattern2]:
                                    sim = options["LookUpTable"][pattern2][pattern1]

                        if sim == 0:
                            sim = modifiedJaccardSimilarityPatternMatching(eval(pattern1), eval(pattern2))

                            if options["LookUpTable"] is not None:

                                if pattern1 not in options["LookUpTable"]:
                                    options["LookUpTable"][pattern1] = {}

                                options["LookUpTable"][pattern1][pattern2] = sim

                        if sim > maxSim:
                            maxSim = sim
                            maxCount = openedPiece[pattern1] * comparisonPiece[pattern2]
                            maxComparison = pattern2

                print("Most Similar: " + str(maxComparison))
                print("Max Similarity: " + str(maxSim))

                totalSim += maxSim * maxCount

            # Normalising
            dot_product = sum(openedPiece[key1] * comparisonPiece[key2] for key1 in openedPiece for key2 in comparisonPiece)
            normalSim = totalSim / dot_product

            print(f"Normalised Piece Similarity: {normalSim}")

            correlationMatrix[dataset.index(piece), dataset.index(comparedPiece)] = normalSim

    return correlationMatrix

def totalPatternOverlapSimilarity(dataset):
    correlationMatrix = np.zeros((len(dataset), len(dataset)))

    for piece in dataset:
        openedPiece = CWR.openFile(piece['Location'])

        for comparedPiece in dataset[dataset.index(piece):]:

            print(f"Comparing {piece['Name']} to {comparedPiece['Name']}")

            totalPieceSim = 0
            totalPatterns = len(openedPiece)
            patternCounter = 1
            newPatterns = 0

            comparisonPiece = CWR.openFile(comparedPiece["Location"])

            for pattern1 in openedPiece:
                totalPatternSim = 0

                print("Pattern: " + str(patternCounter) + "/" + str(totalPatterns))
                patternCounter += 1
                print("Compare: " + pattern1)

                for pattern2 in comparisonPiece:

                    sim = 0

                    if options["LookUpTable"] is not None:

                        if pattern1 in options["LookUpTable"]:
                            if pattern2 in options["LookUpTable"][pattern1]:
                                sim = options["LookUpTable"][pattern1][pattern2]

                        if pattern2 in options["LookUpTable"]:
                            if pattern1 in options["LookUpTable"][pattern2]:
                                sim = options["LookUpTable"][pattern2][pattern1]

                    if sim == 0:
                        sim = modifiedJaccardSimilarityPatternMatching(eval(pattern1), eval(pattern2))

                        if options["LookUpTable"] is not None:
                            if pattern1 not in options["LookUpTable"]:
                                options["LookUpTable"][pattern1] = {}

                            options["LookUpTable"][pattern1][pattern2] = sim
                            newPatterns += 1

                    else:
                        sim = modifiedJaccardSimilarityPatternMatching(eval(pattern1), eval(pattern2))

                    totalPatternSim += sim * openedPiece[pattern1] * comparisonPiece[pattern2]

                print(f"Total Pattern Similarity: {totalPatternSim}")

                totalPieceSim += totalPatternSim

            print(f"Total Piece Similarity: {totalPieceSim}")

            # Normalise
            dot_product = sum(openedPiece[key1] * comparisonPiece[key2] for key1 in openedPiece for key2 in comparisonPiece)
            normalSim = totalPieceSim / dot_product

            print(f"Normalised Piece Similarity: {normalSim}")

            correlationMatrix[dataset.index(piece), dataset.index(comparedPiece)] = normalSim

    return correlationMatrix
    # workspace = details["ExperimentDirectories"]["SimilarityWorkspace"]
    # CWR.saveFile(workspace + "/correlationMatrix.npy", correlationMatrix)
    # avgSymMatrix = generateAverageSimilarityMatrix(correlationMatrix, details)
    # CWR.saveFile(workspace + "/averageCorrelationMatrix.npy", avgSymMatrix)
    # CWR.saveFile("Papers/Paper 2/dynamicSimilarityDictionary.json", dynamicSimilarity)

def thresholdPatternOverlapSimilarity(dataset):

    threshold = options["threshold"]

    correlationMatrix = np.zeros((len(dataset), len(dataset)))
    averageThreshold = 0
    rawThreshold = 0
    numberofComparisons = 0
    partialMatches = 0
    for piece in dataset:
        openedPiece = CWR.openFile(piece['Location'])

        for comparedPiece in dataset[dataset.index(piece):]:

            print(f"Comparing {piece['Name']} to {comparedPiece['Name']}")


            totalPieceSim = 0
            totalPatterns = len(openedPiece)
            patternCounter = 1
            newPatterns = 0

            comparisonPiece = CWR.openFile(comparedPiece["Location"])

            for pattern1 in openedPiece:
                totalPatternSim = 0


                print("Pattern: " + str(patternCounter) + "/" + str(totalPatterns))
                patternCounter += 1
                print("Compare:       " + pattern1)

                match = False

                for pattern2 in comparisonPiece:

                    sim = 0

                    if options['LookUpTable'] is not None:

                        if pattern1 in options['LookUpTable']:
                            if pattern2 in options['LookUpTable'][pattern1]:
                                sim = options['LookUpTable'][pattern1][pattern2]

                        if pattern2 in options['LookUpTable']:
                            if pattern1 in options['LookUpTable'][pattern2]:
                                sim = options['LookUpTable'][pattern2][pattern1]

                    if sim == 0:
                        sim = modifiedJaccardSimilarityPatternMatching(eval(pattern1), eval(pattern2))

                        if options['LookUpTable'] is not None:
                            if pattern1 not in options['LookUpTable']:
                                options['LookUpTable'][pattern1] = {}

                            options['LookUpTable'][pattern1][pattern2] = sim
                            newPatterns += 1

                    numberofComparisons +=1
                    if sim >= threshold:
                        totalPatternSim += sim * openedPiece[pattern1] * comparisonPiece[pattern2]
                        averageThreshold += 1
                        rawThreshold += 1
                        if sim < 1:
                            partialMatches += 1



                print(f"Total Pattern Similarity: {totalPatternSim}")

                totalPieceSim += totalPatternSim

            print(f"Total Piece Similarity: {totalPieceSim}")

            # if newPatterns > 0:
            #     if options['LookUpTable'] is not None:
            #         CWR.saveFile("Papers/Paper 2/dynamicSimilarityDictionary.json", options['LookUpTable'])

            # Normalise
            dot_product = sum(openedPiece[key1] * comparisonPiece[key2] for key1 in openedPiece for key2 in comparisonPiece)
            normalSim = totalPieceSim / dot_product

            print(f"Normalised Piece Similarity: {normalSim}")

            correlationMatrix[dataset.index(piece), dataset.index(comparedPiece)] = normalSim
            averageThreshold /= len(openedPiece)* len(comparedPiece)


    return correlationMatrix, averageThreshold, rawThreshold, partialMatches
    # workspace = details["ExperimentDirectories"]["SimilarityWorkspace"]
    # CWR.saveFile(workspace + "/correlationMatrix.npy", correlationMatrix)
    # avgSymMatrix = generateAverageSimilarityMatrix(correlationMatrix, details)
    # CWR.saveFile(workspace + "/averageCorrelationMatrix.npy", avgSymMatrix)
    # averageThreshold /= len(dataset)
    # print(f'Average number of items included in a threshold is: {averageThreshold}')
    # print(f'Raw number of items included in a threshold is: {rawThreshold}')
    # print(f'Partial Matches raw count: {partialMatches}')
    # print(f'Total number of comparisons included in a threshold is: {numberofComparisons}')
    # print(f'Reduction rate of: {(numberofComparisons-rawThreshold) / numberofComparisons}')

# Helper Methods
# ----------------------------------------------------------------------------------------------------------------------

# Calculates the similarity between two patterns
def modifiedJaccardSimilarityPatternMatching(pattern1, pattern2):
    if isinstance(pattern1, str):
        pattern1 = eval(pattern1)
    if isinstance(pattern2, str):
        pattern2 = eval(pattern2)
    pattern1Line = extractLineStringFromPattern(extractLinesFromPattern(pattern1))
    pattern2Line = extractLineStringFromPattern(extractLinesFromPattern(pattern2))
    patter1Bounding = BG.boundingPolygon(pattern1Line, options["ShapeBuffer"])
    patter2Bounding = BG.boundingPolygon(pattern2Line, options["ShapeBuffer"])
    totalArea = patter1Bounding.area + patter2Bounding.area
    overlapShape = patternAreaComparison(pattern1, pattern2)
    overlapArea = overlapShape.area

    # Jaccard Similarity (mainly for sets being applied to overlapping polygon areas
    similarity = overlapArea/(totalArea-overlapArea)

    return similarity


def extractLineStringFromPattern(pattern):

    lineStringList = []

    for line in pattern:
        for point in line:
            lineStringList.append(point)

    return lineStringList


def extractLinesFromPattern(pattern):
    patternSize = (len(pattern) + 1) % 3
    # print(patternSize)

    points = [[(0, 0), (0, pattern[patternSize * 3])]]
    # print(len(pattern))

    previousPitch = 0
    previousDuration = 0

    for i in range(patternSize):
        startPitch = previousPitch + pattern[i]
        startDuration = previousDuration + pattern[i + patternSize]

        endPitch = startPitch
        endDuration = startDuration + pattern[i + (patternSize * 2) + 1]

        previousPitch = endPitch
        previousDuration = startDuration

        line = [(startPitch, startDuration), (endPitch, endDuration)]

        # points.append((startPitch, startDuration))
        # points.append((endPitch, endDuration))
        points.append(line)

    # print(points)
    return points


# Finds the best overlap of the polygons
def patternAreaComparison(pattern1, pattern2, visualisation=False):
    pattern1Lines = extractLinesFromPattern(pattern1)
    pattern2Lines = extractLinesFromPattern(pattern2)

    initialLineStringSequence = extractLineStringFromPattern(pattern1Lines)

    initialPolygon = BG.boundingPolygon(initialLineStringSequence, options["ShapeBuffer"])

    maxOverlap = 0

    for coordinate1 in pattern1Lines:
        for coordinate2 in pattern2Lines:
            pitchDifference = coordinate1[0][0] - coordinate2[0][0]
            durationDifference = coordinate1[0][1] - coordinate2[0][1]
            newPattern = []

            for coordinate3 in pattern2Lines:

                newLine = [(coordinate3[0][0] + pitchDifference, coordinate3[0][1] + durationDifference),
                           (coordinate3[1][0] + pitchDifference, coordinate3[1][1] + durationDifference)]

                newPattern.append(newLine)

            newLineStringSequence = extractLineStringFromPattern(newPattern)

            newPolygon = BG.boundingPolygon(newLineStringSequence, options["ShapeBuffer"])
            overlapPolygon = BG.overlappingPolygon(initialPolygon, newPolygon)

            if overlapPolygon.area > maxOverlap:
                maxOverlap = overlapPolygon.area
                bestOverlappingPatternPolygon = newPolygon
                bestOverlapPolygon = overlapPolygon

    # VIS.visualisePolygonOverlapComparison(initialPolygon, bestOverlappingPatternPolygon, bestOverlapPolygon)
    # VIS.visualisePolygon(bestOverlapPolygon)

    return bestOverlapPolygon