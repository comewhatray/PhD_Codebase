from Utilities import ComeWhatRayUtil as CWR
from Utilities import BoundingGenerator as BG
from Utilities import datasetManagment as DM
from Utilities import Visualisations as VIS
from shapely.affinity import translate
import numpy as np

# MAKE SURE TO SAVE THE LOOKUPTABLE IF IT IS USED

import sys
this_module = sys.modules[__name__]

options = {
    "function": "totalPatternOverlapSimilarity",
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
    # Provide the location of a look up table
    "LookUpTable": None
}

# LookUpTable = CWR.openFile("Papers/Paper 2/dynamicSimilarityDictionary.json")


def startProcess(dataset, inputOptions):
    CWR.updateOldDictionaryEntriesWithNewDictionaryEntries(options, inputOptions)
    methodInstanciated = getattr(this_module, options['function'])

    methodInstanciated(dataset)




# Overlap Similarity measures (Essentially it is a modified Jaccard Similarity measure)
# ----------------------------------------------------------------------------------------------------------------------

def MaxOverlapSimilarity(dataset):

    correlationMatrix = generateEmptyMatrix(dataset)
    dataset = DM.convertDatasetToOldFormat(dataset)

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

                        sim = lookUpTable(pattern1, pattern2)
                        if sim == 0:
                            sim = modifiedJaccardSimilarityPatternMatching(eval(pattern1), eval(pattern2))
                            updateLookUpTable(pattern1, pattern2, sim)

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
    correlationMatrix = generateEmptyMatrix(dataset)
    dataset = DM.convertDatasetToOldFormat(dataset)

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

                    sim = lookUpTable(pattern1, pattern2)
                    if sim == 0:
                        sim = modifiedJaccardSimilarityPatternMatching(eval(pattern1), eval(pattern2))
                        updateLookUpTable(pattern1, pattern2, sim)
                        newPatterns += 1

                    # else:
                    #     sim = modifiedJaccardSimilarityPatternMatching(eval(pattern1), eval(pattern2))

                    totalPatternSim += sim * openedPiece[pattern1] * comparisonPiece[pattern2]

                print(f"Total Pattern Similarity: {totalPatternSim}")

                totalPieceSim += totalPatternSim

            print(f"Total Piece Similarity: {totalPieceSim}")

            # Normalise
            dot_product = sum(openedPiece[key1] * comparisonPiece[key2] for key1 in openedPiece for key2 in comparisonPiece)
            normalSim = totalPieceSim / dot_product

            print(f"Normalised Piece Similarity: {normalSim}")

            correlationMatrix[dataset.index(piece), dataset.index(comparedPiece)] = normalSim

            if options["LookUpTable"] is not None:
                CWR.saveFile("Papers/Paper_2/LookUpTables/SzetoClassicalTestEnd.json", options["LookUpTable"])

    return correlationMatrix
    # workspace = details["ExperimentDirectories"]["SimilarityWorkspace"]
    # CWR.saveFile(workspace + "/correlationMatrix.npy", correlationMatrix)
    # avgSymMatrix = generateAverageSimilarityMatrix(correlationMatrix, details)
    # CWR.saveFile(workspace + "/averageCorrelationMatrix.npy", avgSymMatrix)
    # CWR.saveFile("Papers/Paper 2/dynamicSimilarityDictionary.json", dynamicSimilarity)

def thresholdPatternOverlapSimilarity(dataset):

    threshold = options["threshold"]

    correlationMatrix = generateEmptyMatrix(dataset)
    dataset = DM.convertDatasetToOldFormat(dataset)
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

                    sim = lookUpTable(pattern1, pattern2)

                    if sim == 0:
                        sim = modifiedJaccardSimilarityPatternMatching(eval(pattern1), eval(pattern2))

                        updateLookUpTable(pattern1, pattern2, sim)
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

def queryExperiment(dataset):

    queryDataLocation = dataset["querySet"]
    corpusLocation = dataset["dataSet"]
    queryLastLocation = dataset["queryLastLocation"]
    corpusLastLocation = dataset["datasetLastLocation"]
    labelCount = 1
    labelTotal = len(queryDataLocation[queryLastLocation])
    for label in queryDataLocation[queryLastLocation]:
        print(CWR.largeSpacer)
        print(f"Query Label: {label}")
        queryNumCount = 1
        queryNumTotal = len(queryDataLocation[queryLastLocation][label])
        for query in queryDataLocation[queryLastLocation][label]:
            print(CWR.largeSpacer)
            print(f"Query Location: {query}")
            groupingCount = 1
            groupingTotal = len(corpusLocation[corpusLastLocation])
            for grouping in corpusLocation[corpusLastLocation]:
                print(CWR.largeSpacer)
                print(f"Work Label: {grouping}")
                workCount = 1
                workTotal = len(corpusLocation[corpusLastLocation][grouping])
                for work in corpusLocation[corpusLastLocation][grouping]:
                    print(CWR.largeSpacer)
                    print(f"Work Location: {work}")

                    queryData = CWR.openFile(query)
                    workData = CWR.openFile(work)

                    queryCount = 1
                    querySize = len(queryData)

                    for queryPattern in queryData:
                        print(CWR.extraLargeSpacer)
                        print(f"Query Label: ({labelCount}/{labelTotal})")
                        print(f"Query: ({queryNumCount}/{queryNumTotal})")
                        print(f"Work Label: ({groupingCount}/{groupingTotal})")
                        print(f"Work: ({workCount}/{workTotal})")
                        print(f"Sub Query: ({queryCount}/{querySize})")
                        dataCount = 1
                        dataSize = len(workData)
                        for workPattern in workData:
                            # Updates Every X%
                            if dataCount % int(dataSize/5) == 0:
                                print(CWR.midSpacer)
                                print(f"Data ({dataCount}/{dataSize})")

                            skipTo = True
                            if skipTo:
                                if (    labelCount == 1 and
                                        queryNumCount == 1 and
                                        groupingCount == 1 and
                                        workCount == 1 and
                                        queryCount == 4):
                                    print(queryPattern)
                                    print(workPattern)
                                    patternSimilarity = modifiedJaccardSimilarityPatternMatching(queryPattern, workPattern)


                            else:
                                patternSimilarity = modifiedJaccardSimilarityPatternMatching(queryPattern, workPattern)
                            # print(f"Pattern Similarity: {patternSimilarity}")
                            dataCount += 1

                        queryCount += 1


                workCount += 1

            groupingCount += 1

        queryNumCount += 1

    labelCount += 1

    return

def overlapQueryExperiment(dataset):

    queryDataLocation = dataset["querySet"]
    corpusLocation = dataset["dataSet"]
    queryLastLocation = dataset["queryLastLocation"]
    corpusLastLocation = dataset["datasetLastLocation"]

    queryLabelCount = 1
    queryLabelTotal = len(queryDataLocation[queryLastLocation])
    for label in queryDataLocation[queryLastLocation]:
        print(CWR.largeSpacer)
        print(f"Query Label: {label}")
        queryNumCount = 1
        queryNumTotal = len(queryDataLocation[queryLastLocation][label])

        for query in queryDataLocation[queryLastLocation][label]:
            print(CWR.largeSpacer)
            print(f"Query Location: {query}")
            groupingCount = 1
            groupingTotal = len(corpusLocation[corpusLastLocation])

            queryData = CWR.openFile(query)
            queryMultiString = BG.convertGraphToMultiLineString(queryData)
            # print(queryPolygons)
            # VIS.visualiseShape(queryMultiString)
            queryLength = queryMultiString.bounds[2]

            for grouping in corpusLocation[corpusLastLocation]:
                print(CWR.largeSpacer)
                print(f"Work Label: {grouping}")
                workCount = 1
                workTotal = len(corpusLocation[corpusLastLocation][grouping])

                for work in corpusLocation[corpusLastLocation][grouping]:
                    print(CWR.largeSpacer)
                    print(f"Work Location: {work}")
                    workData = CWR.openFile(work)

                    print(CWR.extraLargeSpacer)
                    print(f"Query Label: ({queryLabelCount}/{queryLabelTotal})")
                    print(f"Query: ({queryNumCount}/{queryNumTotal})")
                    print(f"Work Label: ({groupingCount}/{groupingTotal})")
                    print(f"Work: ({workCount}/{workTotal})")
                    print(CWR.smallSpacer)
                    # print(f"Sub Query: ({queryCount}/{querySize})")

                    # turns a piece into a multiLineString Geomtery (All the lines are notes)
                    workMultiString = BG.generateMultiLineStringFromExtract(workData)

                    polygonList = workMultiString.geoms
                    queryCount = 0
                    queryTotal = len(polygonList)
                    maxScore = 0
                    maxQuery = None
                    maxComparison = None
                    maxOverlap = None
                    # Goes through each line
                    for lineNumber in range(len(polygonList)):
                        if queryCount % int(queryTotal/10) == 0:
                            print(f"Query: {queryCount}/{queryTotal}")
                            print(f"CurrentMaxScore: {maxScore}")
                        line = polygonList[lineNumber]

                        transX = line.xy[0][0]
                        transY = line.xy[1][0]

                        # Translates the query to the start of the line
                        currentQuery = translate(queryMultiString, xoff=transX, yoff=transY)
                        currentQuery = currentQuery.buffer(1)

                        intersectionList = []

                        for comparison in range(lineNumber, len(polygonList)):
                            comparisonLine = polygonList[comparison]

                            if comparisonLine.xy[0][0] > transX + queryLength:
                                break
                            else:
                                if currentQuery.intersects(comparisonLine) or currentQuery.contains(comparisonLine):
                                    intersectionList.append(comparisonLine)


                        comparisonLines = BG.convertLineStringSequenceToMultiLineString(intersectionList)
                        comparisonPolygon = comparisonLines.buffer(1)

                        totalArea = currentQuery.area + comparisonPolygon.area
                        overlapPolygon = currentQuery.intersection(comparisonPolygon)
                        overlapArea = overlapPolygon.area


                        # VIS.visualiseOverlappingPolygonsUsingData(currentQuery, comparisonPolygon, overlapPolygon)

                        similarity = overlapArea / (totalArea - overlapArea)
                        # print(similarity)
                        if similarity > maxScore:
                            maxScore = similarity
                            maxQuery = currentQuery
                            maxComparison = comparisonPolygon
                            maxOverlap = overlapPolygon


                    # VIS.visualiseShape(workString)
                        queryCount += 1
                    print(f"Max Score: {maxScore}")
                    VIS.visualiseShape(maxQuery)
                    VIS.visualiseShape(maxComparison)
                    VIS.visualiseOverlappingPolygonsUsingData(maxQuery, maxComparison, maxOverlap)
                    workCount += 1
                groupingCount += 1
            queryNumCount += 1
        queryLabelCount += 1


    # print(query)

    return

# Helper Methods
# ----------------------------------------------------------------------------------------------------------------------

# Calculates the similarity between two patterns
def modifiedJaccardSimilarityPatternMatching(pattern1, pattern2):
    if isinstance(pattern1, str):
        pattern1 = eval(pattern1)
    if isinstance(pattern2, str):
        pattern2 = eval(pattern2)
    patternCOORDS1 = BG.convertDifferenceToCoordinates(pattern1)
    patternCOORDS2 = BG.convertDifferenceToCoordinates(pattern2)
    pattern1Line = BG.generateLineStringFromCoordinates(patternCOORDS1)
    pattern2Line = BG.generateLineStringFromCoordinates(patternCOORDS2)
    patter1Bounding = BG.boundingPolygon(pattern1Line, options["shapeBuffer"])
    patter2Bounding = BG.boundingPolygon(pattern2Line, options["shapeBuffer"])
    totalArea = patter1Bounding.area + patter2Bounding.area
    overlapShape = patternAreaComparison(pattern1, pattern2)
    overlapArea = overlapShape.area

    # Jaccard Similarity (mainly for sets being applied to overlapping polygon areas
    similarity = overlapArea/(totalArea-overlapArea)

    return similarity

# Finds the best overlap of the polygons
def patternAreaComparison(pattern1, pattern2, visualisation=False):
    pattern1Lines = BG.convertDifferenceToCoordinates(pattern1)
    pattern2Lines = BG.convertDifferenceToCoordinates(pattern2)
    visualisation = visualisation

    initialLineStringSequence = BG.generateLineStringFromCoordinates(pattern1Lines)

    initialPolygon = BG.boundingPolygon(initialLineStringSequence, options["shapeBuffer"])

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

            newLineStringSequence = BG.generateLineStringFromCoordinates(newPattern)
            newPolygon = BG.boundingPolygon(newLineStringSequence, options["shapeBuffer"])

            # TODO find way to handle multipolygons
            if newPolygon.geom_type != 'MultiPolygon' and initialPolygon.geom_type != 'MultiPolygon':
                overlapPolygon = BG.overlappingPolygon(initialPolygon, newPolygon)

                if overlapPolygon.area > maxOverlap:
                    maxOverlap = overlapPolygon.area
                    bestOverlappingPatternPolygon = newPolygon
                    bestOverlapPolygon = overlapPolygon
            else:
                print(initialPolygon)
                print(newPolygon)



    if visualisation:
        VIS.visualiseOverlappingPolygonsUsingData(initialPolygon, bestOverlappingPatternPolygon, bestOverlapPolygon)
        VIS.visualisePolygon(bestOverlapPolygon)



    return bestOverlapPolygon

# Generates the correct size matrix for the dataset
def generateEmptyMatrix(dataset):
    print("Generating empty matrix")

    totalLength = 0

    for label in dataset:
        totalLength += len(dataset[label])


    return np.zeros((totalLength, totalLength))

# Gets the division of the dataset
def getDatasetDivisions(dataset):

    divisions = []
    for label in dataset:
        divisions.append(len(dataset[label]))

    return divisions

# Searches Lookup Table
def lookUpTable(pattern1, pattern2):

    sim = 0

    if options["LookUpTable"] is not None:
        if pattern1 in options["LookUpTable"]:
            if pattern2 in options["LookUpTable"][pattern1]:
                sim = options["LookUpTable"][pattern1][pattern2]

        if pattern2 in options["LookUpTable"]:
            if pattern1 in options["LookUpTable"][pattern2]:
                sim = options["LookUpTable"][pattern2][pattern1]

    return sim

# Updates Lookup Table
def updateLookUpTable(pattern1, pattern2, sim):

    if options["LookUpTable"] is not None:
        if pattern1 not in options["LookUpTable"]:
            options["LookUpTable"][pattern1] = {}

        options["LookUpTable"][pattern1][pattern2] = sim

# Transforms new dataset format into old one
# def convertDataset(dataset):
#     oldFormat = []
#     for label in dataset:
#
#         for piece in dataset[label]:
#
#             Name = CWR.getFileNameFromPath(piece)
#             Label = label
#             Location = piece
#
#             oldFormat.append({
#                 "Name": Name,
#                 "Label": Label,
#                 "Location": Location
#             })
#
#     return oldFormat
