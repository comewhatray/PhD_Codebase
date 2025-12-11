from shapely import MultiLineString, MultiPolygon
from scipy.stats import wasserstein_distance
from scipy.special import expit
from Utilities import ComeWhatRayUtil as CWR
from Utilities import BoundingGenerator as BG
from Utilities import datasetManagment as DM
from Utilities import Visualisations as VIS
from shapely.affinity import translate
import copy
import numpy as np
import os


# Temp Printing out values
import fcntl
recordRhythm = False

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
    "LookUpTable": None,
    "interimSave": True,
    "queryType": "graphQueryTuneComparison",
    "inspectionBuffer": 1,
    "comparisonBuffer": 1,
    "saveResultsLabel": "DefaultPath",
    "debugging": False,
    "simplifiedSave": True,
    "threading": True,
    "visualiseProcess": False,
    "additionalParameters": {
        "minimumOverlap": 0,
        "fragmentationCheck": 0,
        "fragments": None,
        # Default of a number that can't be achieved so it doesn't run by default
        # "similarityThreshold": 1,
        "rhythmThresholdCheck":1,
        "insertionPenalty": 1,
        "deletionPenalty": 1,
    }
}


# LookUpTable = CWR.openFile("Papers/Paper 2/dynamicSimilarityDictionary.json")


def startProcess(dataset, inputOptions):
    CWR.updateOldDictionaryEntriesWithNewDictionaryEntries(options, inputOptions)
    methodInstanciated = getattr(this_module, options['function'])

    results = methodInstanciated(dataset)

    return results


# Overlap Similarity measures (Essentially it is a modified Jaccard Similarity measure)
# ----------------------------------------------------------------------------------------------------------------------

def MaxOverlapSimilarity(dataset):
    correlationMatrix = generateEmptyMatrix(dataset)
    dataset = DM.convertDatasetToOldFormat(dataset)

    for piece in dataset:
        openedPiece = CWR.openFile(piece['Location'], printDisplay=not options["threading"])

        for comparedPiece in dataset[dataset.index(piece):]:

            totalSim = 0
            totalPatterns = len(openedPiece)
            patternCounter = 1

            comparisonPiece = CWR.openFile(comparedPiece["Location"], printDisplay=not options["threading"])

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
            dot_product = sum(
                openedPiece[key1] * comparisonPiece[key2] for key1 in openedPiece for key2 in comparisonPiece)
            normalSim = totalSim / dot_product

            print(f"Normalised Piece Similarity: {normalSim}")

            correlationMatrix[dataset.index(piece), dataset.index(comparedPiece)] = normalSim

    return correlationMatrix


def totalPatternOverlapSimilarity(dataset):
    correlationMatrix = generateEmptyMatrix(dataset)
    dataset = DM.convertDatasetToOldFormat(dataset)

    for piece in dataset:
        openedPiece = CWR.openFile(piece['Location'], printDisplay=not options["threading"])

        for comparedPiece in dataset[dataset.index(piece):]:

            print(f"Comparing {piece['Name']} to {comparedPiece['Name']}")

            totalPieceSim = 0
            totalPatterns = len(openedPiece)
            patternCounter = 1
            newPatterns = 0

            comparisonPiece = CWR.openFile(comparedPiece["Location"], printDisplay=not options["threading"])

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
            dot_product = sum(
                openedPiece[key1] * comparisonPiece[key2] for key1 in openedPiece for key2 in comparisonPiece)
            normalSim = totalPieceSim / dot_product

            print(f"Normalised Piece Similarity: {normalSim}")

            correlationMatrix[dataset.index(piece), dataset.index(comparedPiece)] = normalSim

            if options["LookUpTable"] is not None:
                CWR.saveFile("Papers/Paper_2/LookUpTables/SzetoClassicalTestEnd.json", options["LookUpTable"],
                             printDisplay=not options["threading"])

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
        openedPiece = CWR.openFile(piece['Location'], printDisplay=not options["threading"])

        for comparedPiece in dataset[dataset.index(piece):]:

            print(f"Comparing {piece['Name']} to {comparedPiece['Name']}")

            totalPieceSim = 0
            totalPatterns = len(openedPiece)
            patternCounter = 1
            newPatterns = 0

            comparisonPiece = CWR.openFile(comparedPiece["Location"], printDisplay=not options["threading"])

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

                    numberofComparisons += 1
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
            dot_product = sum(
                openedPiece[key1] * comparisonPiece[key2] for key1 in openedPiece for key2 in comparisonPiece)
            normalSim = totalPieceSim / dot_product

            print(f"Normalised Piece Similarity: {normalSim}")

            correlationMatrix[dataset.index(piece), dataset.index(comparedPiece)] = normalSim
            averageThreshold /= len(openedPiece) * len(comparedPiece)

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

                    queryData = CWR.openFile(query, printDisplay=not options["threading"])
                    workData = CWR.openFile(work, printDisplay=not options["threading"])

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
                            if dataCount % int(dataSize / 5) == 0:
                                print(CWR.midSpacer)
                                print(f"Data ({dataCount}/{dataSize})")

                            skipTo = True
                            if skipTo:
                                if (labelCount == 1 and
                                        queryNumCount == 1 and
                                        groupingCount == 1 and
                                        workCount == 1 and
                                        queryCount == 4):
                                    print(queryPattern)
                                    print(workPattern)
                                    patternSimilarity = modifiedJaccardSimilarityPatternMatching(queryPattern,
                                                                                                 workPattern)


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

    experimentResults = {}

    # For each label in the query
    for label in queryDataLocation[queryLastLocation]:
        if not options['threading']:
            print(CWR.largeSpacer)
            print(f"Query Label: {label}")
        queryNumCount = 1
        queryNumTotal = len(queryDataLocation[queryLastLocation][label])

        if label not in experimentResults:
            experimentResults[label] = {}

        # For each query example of that label
        for query in queryDataLocation[queryLastLocation][label]:
            if not options['threading']:
                print(CWR.largeSpacer)
                print(f"Query Location: {query}")
            groupingCount = 1
            groupingTotal = len(corpusLocation[corpusLastLocation])

            queryData = CWR.openFile(query, printDisplay=not options["threading"])

            # For each label in the dataset (hae to use grouping to avoid duplicated names)
            for grouping in corpusLocation[corpusLastLocation]:
                if not options['threading']:
                    print(CWR.largeSpacer)
                    print(f"Work Label: {grouping}")
                workCount = 1
                workTotal = len(corpusLocation[corpusLastLocation][grouping])

                if grouping not in experimentResults[label]:
                    experimentResults[label][grouping] = {}

                # For each data in the dataset of that label
                for work in corpusLocation[corpusLastLocation][grouping]:
                    if not options['threading']:
                        print(CWR.largeSpacer)
                        print(f"Work Location: {work}")
                    workData = CWR.openFile(work, printDisplay=not options["threading"])

                    if not options['threading']:
                        print(CWR.extraLargeSpacer)
                        print(f"Query Label: ({queryLabelCount}/{queryLabelTotal})")
                        print(f"Query: ({queryNumCount}/{queryNumTotal})")
                        print(f"Work Label: ({groupingCount}/{groupingTotal})")
                        print(f"Work: ({workCount}/{workTotal})")
                        print(CWR.smallSpacer)
                    workCount += 1

                    saveDirectory = f"ExperimentResults/{options['saveResultsLabel']}/AllSimilarity/{label}/{grouping}"
                    currentFile = CWR.getFileNameFromPath(work)

                    # If the data already exists we can move on to the next one
                    if os.path.exists(f"{saveDirectory}/{currentFile}.json"):
                        if not options["threading"]:
                            print("Data already exists")
                        continue

                    resultsStats = {
                        "queryCount": 0,
                        "queryTotal": len(workData),
                        "maxScore": 0,
                        "transformedQuery": None,
                        "maxQuery": None,
                        "maxComparison": None,
                        "maxOverlap": None,
                        "pieceLength": 0,
                        "overlapScoreList": [],
                        "fragmentedScoreList": []
                    }

                    if len(workData) == 0:
                        if not options["threading"]:
                            print("No data")

                    else:
                        methodInstanciated = getattr(this_module, options['queryType'])
                        methodInstanciated(queryData, workData, resultsStats)

                    if len(workData) != 0:
                        if not options['threading']:
                            print(f"Max Score: {resultsStats['maxScore']}")
                            # VIS.visualiseShape(resultsStats["maxQuery"])
                            # VIS.visualiseShape(resultsStats["maxComparison"])
                            # VIS.visualiseOverlappingPolygonsUsingData(resultsStats['maxQuery'], resultsStats["maxComparison"], resultsStats["maxOverlap"])

                    if options["interimSave"]:
                        CWR.ensureDirectory(saveDirectory)
                        simplifiedStats = {
                            "queryCount": resultsStats["queryCount"],
                            "queryTotal": resultsStats["queryTotal"],
                            "maxScore": resultsStats["maxScore"],
                            "pieceLength": resultsStats["pieceLength"],
                            "overlapScoreList": resultsStats["overlapScoreList"],
                            "fragmentedScoreList": resultsStats["fragmentedScoreList"]

                        }
                        if options["simplifiedSave"]:
                            CWR.saveFile(f"{saveDirectory}/{currentFile}.json", simplifiedStats,
                                         printDisplay=not options["threading"])

                        else:
                            CWR.saveFile(f"{saveDirectory}/{currentFile}.json", resultsStats,
                                         printDisplay=not options["threading"])

                groupingCount += 1
            queryNumCount += 1
        queryLabelCount += 1

    return experimentResults


def graphQueryTuneComparison(queryGraph, tuneGraph, scorebord):
    lengthStart = tuneGraph.nodes[0]['position']
    endPosition = tuneGraph.nodes[len(tuneGraph.nodes) - 1]
    lengthEnd = endPosition['position'] + endPosition['duration']
    scorebord["pieceLength"] = lengthEnd - lengthStart

    if scorebord["transformedQuery"] is None:
        # TODO choose one line or the other
        scorebord["transformedQuery"] = BG.convertGraphToMultiLineString(queryGraph)
        # scorebord["transformedQueryNoAttachments"] = BG.generateMultiLineListFromGraph(queryGraph)
        scorebord["queryLength"] = scorebord["transformedQuery"].bounds[2]

    for lineNumber in range(scorebord["queryTotal"]):
        if not options['threading']:
            if scorebord["queryCount"] % int(scorebord["queryTotal"] / 10) == 0:
                print(f"Query: {scorebord['queryCount']}/{scorebord['queryTotal']}")
                print(f"CurrentMaxScore: {scorebord['maxScore']}")

        line = tuneGraph.nodes[lineNumber]

        transX = line["position"]
        transY = line["pitch"]

        # Translates the query to the start of the line
        currentQuery = translate(scorebord["transformedQuery"], xoff=transX, yoff=transY)
        # currentQueryLinesNoAttachment = translate(scorebord["transformedQueryNoAttachments"], xoff=transX, yoff=transY)
        currentQueryInspetion = BG.boundingPolygon(currentQuery, options["inspectionBuffer"])

        intersectionList = []
        graphPositionList = []

        # ----------------------------------------------------------------------------------------------------------------------
        # This gets the node numbers on the graph not the lines themselves
        for comparison in range(lineNumber, scorebord["queryTotal"]):
            comparisonLine = tuneGraph.nodes[comparison]
            comparisonLineString = BG.generateLineStringFromExtract([comparisonLine], absolutePosition=True)

            if comparisonLine["position"] > transX + scorebord['queryLength']:
                break
            else:
                if currentQueryInspetion.intersects(comparisonLineString) or currentQueryInspetion.contains(
                        comparisonLineString):
                    intersectionList.append(comparisonLineString)
                    graphPositionList.append((comparison, comparisonLineString))

        # comparisonLines = BG.convertLineStringSequenceToMultiLineString(intersectionList)

        membershipList = minimumOverlap(intersectionList, currentQueryInspetion)

        # allignmentSimilarity(scorebord["transformedQuery"], MultiLineString(intersectionList))

        subGraphList = []
        for position in graphPositionList:
            for member in membershipList:
                if member.equals(position[1]):
                    subGraphList.append(position[0])
                    break

        subGraph = tuneGraph.subgraph(subGraphList)
        fragmentedScores = 0
        if options["additionalParameters"]["fragmentationCheck"] > 0:
            fragmentedScores = fragmentedSimilarity(queryGraph, scorebord["queryLength"], subGraph, transX, transY)

        # ----------------------------------------------------------------------------------------------------------------------

        # VIS.visualiseSpatialGraph(subGraph)
        # TODO choose one line or the other
        comparisonLines = BG.convertGraphToMultiLineString(subGraph, absoluteValue=True)
        comparisonPolygon = BG.boundingPolygon(comparisonLines, options['comparisonBuffer'])
        # comparisonLines = BG.generateMultiLineListFromGraph(subGraph, absoluteValue=True)

        currentQueryComparison = BG.boundingPolygon(currentQuery, options["comparisonBuffer"])

        if options["debugging"]:
            VIS.visualiseShape(comparisonLines)
            VIS.visualiseShape(comparisonPolygon)
            VIS.visualiseShape(currentQuery)
            VIS.visualiseShape(currentQueryComparison)

        totalArea = currentQueryComparison.area + comparisonPolygon.area
        overlapPolygon = currentQueryComparison.intersection(comparisonPolygon)
        overlapArea = overlapPolygon.area

        # VIS.visualiseOverlappingPolygonsUsingData(currentQuery, comparisonPolygon, overlapPolygon)

        similarity = overlapArea / (totalArea - overlapArea)
        scorebord['overlapScoreList'].append(similarity)
        scorebord["fragmentedScoreList"].append(fragmentedScores)

        # print(similarity)
        if similarity > scorebord['maxScore']:
            scorebord['maxScore'] = similarity
            scorebord['maxQuery'] = currentQueryComparison
            scorebord['maxComparison'] = comparisonPolygon
            scorebord['maxOverlap'] = overlapPolygon

        # VIS.visualiseShape(workString)
        scorebord["queryCount"] += 1

    return


# Only use the base line segments for constructing polygon, no lined lines
def linesQueryTuneComparison(queryLines, tuneLines, scorebord):
    sanityList = []

    lengthStart = tuneLines[0]['position']
    lengthEnd = tuneLines[-1]['position'] + tuneLines[-1]['duration']
    scorebord["pieceLength"] = lengthEnd - lengthStart

    # First transoforms the query to start at the origin
    # The is none part prevents it from performing this step more than once
    if scorebord["transformedQuery"] is None:
        scorebord["transformedQuery"] = BG.generateMultiLineStringFromExtract(queryLines)
        # Translate to origin
        tempTransX = 0 - queryLines[0]['position']
        tempTransY = 0 - queryLines[0]['pitch']
        scorebord["transformedQuery"] = translate(scorebord["transformedQuery"], xoff=tempTransX, yoff=tempTransY)
        scorebord["queryLength"] = scorebord["transformedQuery"].bounds[2]

    if options["visualiseProcess"]:
        VIS.plotShape(BG.boundingPolygon(scorebord["transformedQuery"], options["inspectionBuffer"]), color="Red")
        VIS.plotShape(scorebord["transformedQuery"])
        VIS.showPlot()

    # Makes a list of all the notes as linestrings
    notesLineList = []
    for note in range(scorebord["queryTotal"]):
        notesLineList.append(BG.generateLineStringFromExtract([tuneLines[note]], absolutePosition=True))

    # The main loop
    # going through all the notes
    for lineNumber in range(scorebord["queryTotal"]):
        # Print statemesnts for progress clarity

        if scorebord["queryCount"] % int(scorebord["queryTotal"] / 10) == 0:
            if not options["threading"]:
                print(f"Query: {scorebord['queryCount']}/{scorebord['queryTotal']}")
                print(f"CurrentMaxScore: {scorebord['maxScore']}")
        # line = BG.generateLineStringFromCoordinates(tuneLines[lineNumber])

        # Gets the coordinates of the current line
        line = tuneLines[lineNumber]

        # Gets the details needed to transform the query to the current coordinates
        transX = line["position"]
        transY = line["pitch"]
        if options["debugging"]:
            if transX > 144:
                print("Start Looking here")

        # Translates the query to the start of the line
        currentQuery = translate(scorebord["transformedQuery"], xoff=transX, yoff=transY)
        # Creates the polygon which will inspect intersections
        currentQueryInspection = BG.boundingPolygon(currentQuery, options["inspectionBuffer"])

        if options["visualiseProcess"]:
            VIS.plotShape(currentQueryInspection, color="red")
            VIS.plotJsonAsLines(tuneLines)
            VIS.showPlot()

        # This loop will find all lines in the piece that intersect the current query
        intersectionList = []
        for comparison in range(lineNumber, scorebord["queryTotal"]):

            comparisonLine = tuneLines[comparison]
            comparisonLineString = notesLineList[comparison]

            # This if statements is for effeciency, it restarts the loop if the note being examined occurs after the end of the query
            if comparisonLine["position"] > transX + scorebord['queryLength']:
                break
            else:
                # if it doesnt it checks if the note is in the query polygon or intersects it
                if currentQueryInspection.intersects(comparisonLineString) or currentQueryInspection.contains(
                        comparisonLineString):
                    intersectionList.append(comparisonLineString)

        # Getting the bounding of the query

        # Similarity Calculation
        similarity, similarityCalculation = calculateSimilarity(currentQuery, intersectionList)
        scorebord['overlapScoreList'].append(similarity)

        # Just some stats being stored and updates
        if similarity > scorebord['maxScore']:
            scorebord['maxScore'] = similarity
            scorebord['maxQuery'] = similarityCalculation[0]
            scorebord['maxComparison'] = similarityCalculation[1]
            scorebord['maxOverlap'] = similarityCalculation[2]

        if options["debugging"]:
            if similarity > 0.9:
                sanityList.append(
                    (similarityCalculation[0], similarityCalculation[1], similarityCalculation[2], similarity))

        # VIS.visualiseShape(workString)
        # Counter incremented
        scorebord["queryCount"] += 1
    if options["debugging"]:
        print(f"Sanity Length: {len(sanityList)}")
        for result in sanityList:
            VIS.visualiseOverlappingPolygonsUsingData(result[0], result[1], result[2])
            print(f"Similarity: {result[3]}")

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
    similarity = overlapArea / (totalArea - overlapArea)

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


# intakes a series of lines and a query that is a polygon
def minimumOverlap(patternList, query):
    membershipList = []

    # Checks that each line that intersects has a minimum overlap with the query
    if options["additionalParameters"]["minimumOverlap"] != 0:
        for line in patternList:
            membershipTest = BG.boundingPolygon(line, options["comparisonBuffer"])
            membershipOverlap = membershipTest.intersection(query)

            if options["debugging"]:
                print(f"Test Area: {membershipTest.area}")
                print(f"Overlap Area: {membershipOverlap.area}")
                VIS.visualiseOverlappingPolygonsUsingData(membershipTest, query, membershipOverlap)

            # Currently the overlap needs to be over half the area of the total bounding
            if (membershipTest.area * options["additionalParameters"]["minimumOverlap"]) < membershipOverlap.area:
                membershipList.append(line)
    # if there is no minimum just send the entire list on though
    else:
        membershipList = patternList

    return membershipList

#                            (graph, number   , graph, number, number)
def fragmentedSimilarity(queryGraph, queryLength, pattern, transX, transY):
    fragmentScores = None
    numFragments = options["additionalParameters"]["fragmentationCheck"]

    if numFragments > 0:
        intervalSize = queryLength / numFragments

        # transform the values of the query graph
        transformGraph = copy.deepcopy(queryGraph)
        xDiff = transX - transformGraph.nodes[0]["position"]
        yDiff = transY - transformGraph.nodes[0]["pitch"]
        for node in transformGraph.nodes:
            transformGraph.nodes[node]["position"] = transformGraph.nodes[node]["position"] + xDiff
            transformGraph.nodes[node]["pitch"] = transformGraph.nodes[node]["pitch"] + yDiff
            transformGraph.nodes[node]["pos"] = (transformGraph.nodes[node]["position"],
                                                 transformGraph.nodes[node]["pitch"])

        # Fragmenting part
        if options["debugging"]:
            VIS.visualiseShape(BG.boundingPolygon(BG.convertGraphToMultiLineString(transformGraph)))
            VIS.visualiseShape(BG.boundingPolygon(BG.convertGraphToMultiLineString(pattern)))

        oldStart = transformGraph.nodes[0]["position"]
        newEnd = oldStart + intervalSize

        fragmentScores = []

        while newEnd <= transformGraph.nodes[0]["position"] + queryLength:

            queryFragment = []
            for node in transformGraph.nodes:
                if isBetween(transformGraph.nodes[node], oldStart, newEnd):
                    queryFragment.append(node)

            patternFragment = []
            for node in pattern.nodes:
                if isBetween(pattern.nodes[node], oldStart, newEnd):
                    patternFragment.append(node)

            querySubFragment = transformGraph.subgraph(queryFragment)
            patternSubFragment = pattern.subgraph(patternFragment)

            queryLines = BG.convertGraphToMultiLineString(querySubFragment, absoluteValue=True)
            queryBounds = BG.boundingPolygon(queryLines, options["comparisonBuffer"])
            patternLines = BG.convertGraphToMultiLineString(patternSubFragment, absoluteValue=True)
            patternBounds = BG.boundingPolygon(patternLines, options["comparisonBuffer"])

            totalArea = queryBounds.area + patternBounds.area
            overlapPolygon = queryBounds.intersection(patternBounds)
            overlapArea = overlapPolygon.area

            if options["debugging"]:
                VIS.visualiseShape(queryBounds)
                VIS.visualiseShape(patternBounds)
                VIS.visualiseOverlappingPolygonsUsingData(queryBounds, patternBounds, overlapPolygon)

            similarity = 0
            if totalArea - overlapArea != 0:
                similarity = overlapArea / (totalArea - overlapArea)

            fragmentScores.append(similarity)

            oldStart = newEnd
            newEnd = newEnd + intervalSize
    if options["debugging"]:
        print(f"Fragmented Similarity: {fragmentScores}")
    return fragmentScores


# Measure the distance between rhythms
def rhythmicSimilarity(query, comparison):
    # Get onset values for query
    queryOnsets = []
    for line in query.geoms:
        queryOnsets.append(line.bounds[0])

    # Get onset values of comparison
    comparisonOnsets = []
    for line in comparison:
        comparisonOnsets.append(line.bounds[0])

    # 1 good, 0 bad
    penalty = 1

    # Insertions required
    if len(queryOnsets) > len(comparisonOnsets):

        # Number of insertions required
        numInsertions = len(queryOnsets) - len(comparisonOnsets)

        # Note if two possible
        allignment = {}

        # Itterate through comparison onsets
        for cOnset in comparisonOnsets:

            distance = None
            index = None

            # Compare them to query onsets
            for i in range(len(queryOnsets)):
                # for qOnset in queryOnsets:
                qOnset = queryOnsets[i]
                tempDistance = abs(cOnset - qOnset)

                # If the distance is 0 we can end the loop
                # if tempDistance == 0:
                #     index = i

                if distance is None:
                    distance = tempDistance
                    index = i

                # Makes it so the first smallest value is selected
                # To change to last smallest value change to <=
                elif tempDistance < distance:
                    distance = tempDistance
                    index = i
                    distance = tempDistance

            # allignment.append(index)
            allignment[index] = cOnset

        insertedComparisonOnsets = []

        for i in range(len(queryOnsets)):

            if i in allignment:
                insertedComparisonOnsets.append(allignment[i])

            else:
                insertedComparisonOnsets.append(queryOnsets[i])

        #
        penalty = 1 - ((numInsertions/len(queryOnsets)) * options["additionalParameters"]["insertionPenalty"])
        comparisonOnsets = insertedComparisonOnsets

    # Deletions required
    elif len(queryOnsets) < len(comparisonOnsets):

        numDeletions = len(comparisonOnsets) - len(queryOnsets)

        allignment = {}

        for i in range(len(queryOnsets)):

            qOnset = queryOnsets[i]

            distance = None
            value = None

            for cOnset in range(len(comparisonOnsets)):

                tempDistance = abs(qOnset - comparisonOnsets[cOnset])

                if distance is None:
                    distance = tempDistance
                    value = cOnset

                # Makes it so the first smallest value is selected
                # To change to last smallest value change to <=
                elif tempDistance < distance:
                    distance = tempDistance
                    value = cOnset

            allignment[i] = comparisonOnsets[value]

        deletedComparisonOnsets = []
        for i in range(len(queryOnsets)):
            deletedComparisonOnsets.append(allignment[i])

        penalty = 1 - ((numDeletions/len(comparisonOnsets)) * options["additionalParameters"]["deletionPenalty"])
        comparisonOnsets = deletedComparisonOnsets

    # Earth movers distance between the two rhythm onset vectors
    # TODO I'm not sure what on earth I should actually do here
    rhythmicDist = wasserstein_distance(queryOnsets, comparisonOnsets)

    # Currently similarity measure (Colm mentioned an approach were I would divide the distance by N (i'm not sure what N refers too
    rhythmicSim = 1 - rhythmicDist

    # Open file in append mode and write with locking
    if recordRhythm:
        with open('results.txt', 'a') as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_EX)  # Exclusive lock
            f.write(f"{rhythmicDist}\n")
            fcntl.flock(f.fileno(), fcntl.LOCK_UN)  # Unlock


    # rhythmicSim = 1/1+rhythmicDist

    rhythmicSim *= penalty

    return rhythmicSim

#              node, num, num
def isBetween(query, start, end):
    if query["position"] + query["duration"] > start and query["position"] < end:
        return True
    else:
        return False


def calculateSimilarity(query, comparison):
    # Generate a bounding around the query
    queryBounding = BG.boundingPolygon(query, options["comparisonBuffer"])

    # Check if each member of the comparison has a minimum overlap with the query
    comparison = minimumOverlap(comparison, queryBounding)

    # Creates a multiLinestring of the lines that intersect
    comparisonMultiLine = MultiLineString(comparison)

    # Creates a polygon around those notes
    comparisonBounding = BG.boundingPolygon(comparisonMultiLine, options['comparisonBuffer'])

    # get the area, the overlap
    totalArea = queryBounding.area + comparisonBounding.area
    overlapPolygon = queryBounding.intersection(comparisonBounding)
    overlapArea = overlapPolygon.area

    # similarity is determined by the overlapping area divided by the difference in total area - the overlapping area
    similarity = overlapArea / (totalArea - overlapArea)

    if options["visualiseProcess"]:
        VIS.plotOverlappingPolygonsUsingData(queryBounding, comparisonBounding, overlapPolygon)
        VIS.plotShape(comparisonMultiLine, color="green")
        VIS.showPlot()
        print(similarity)

    if similarity > options["additionalParameters"]["rhythmThresholdCheck"]:
        modifier = rhythmicSimilarity(query, comparison)

        similarity *= modifier

    return similarity, (queryBounding, comparisonBounding, overlapPolygon)
