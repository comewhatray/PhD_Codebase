from Utilities import ComeWhatRayUtil as CWR
from Utilities import datasetManagment as DM
from Utilities import Visualisations as VIS
import os
import heapq
import statistics
import numpy as np
import pandas as pd

import matplotlib as mpl
import matplotlib.pyplot as plt

import seaborn as sns


# fileLocation = "Papers/Paper_2/Extension/ExtensionWorkspace/ExperimentResults.json"
# fileLocation = "Papers/Paper_2/Extension/ExtensionWorkspace/Experiment7Results.json"
fileLocation = "Papers/Paper_2/Extension/ExtensionWorkspace/Experiment8Results.json"
# startFileLocation = "ExperimentResults/Experiment8/AllSimilarity"
# startFileLocation = "ExperimentResults/Experiment9 (BreathingRoom)/AllSimilarity"
# startFileLocation = "ExperimentResults/Experiment12 (membershipScale)/AllSimilarity"
# startFileLocation = "ExperimentResults/Experiment13 (FragmentisationCheck)/AllSimilarity"
# startFileLocation = "ExperimentResults/Experiment14 (FragAndMember)/AllSimilarity"
startFileLocation = "ExperimentResults/Experiment15 (BreathingRoom_Membership)/AllSimilarity"
# startFileLocation = "ExperimentResults/Experiment16 (Kyna_Membership)/AllSimilarity"
# startFileLocation = "ExperimentResults/Experiment17 (Default Overlap)/AllSimilarity"

# Membership 0.9
# ----------------------------------------------------------------------------------------------------------------------
# startFileLocation = "ExperimentResults/membership_0.9/Experiment14 (FragAndMember)/AllSimilarity"
# startFileLocation = "ExperimentResults/membership_0.9/Experiment15 (BreathingRoom_Membership)/AllSimilarity"
# startFileLocation = "ExperimentResults/membership_0.9/Experiment16 (Kyna_Membership)/AllSimilarity"
# ----------------------------------------------------------------------------------------------------------------------

# Membership 0.5
# ----------------------------------------------------------------------------------------------------------------------
# startFileLocation = "ExperimentResults/membership_0.5/Experiment14 (FragAndMember)/AllSimilarity"
# startFileLocation = "ExperimentResults/membership_0.5/Experiment15 (BreathingRoom_Membership)/AllSimilarity"
# startFileLocation = "ExperimentResults/membership_0.5/Experiment16 (Kyna_Membership)/AllSimilarity"
# ----------------------------------------------------------------------------------------------------------------------

# startFileLocation = "ExperimentResults/PolygonBoundingChanges_0.5_0.5/Experiment13 (FragmentisationCheck)/AllSimilarity"
# startFileLocation = "ExperimentResults/PolygonBoundingChanges_0.5_0.5/Experiment14 (FragAndMember)/AllSimilarity"
# startFileLocation = "ExperimentResults/PolygonBoundingChanges_0.5_0.5/Experiment15 (BreathingRoom_Membership)/AllSimilarity"
# startFileLocation = "ExperimentResults/PolygonBoundingChanges_0.5_0.5/Experiment16 (Kyna_Membership)/AllSimilarity"
# startFileLocation = "ExperimentResults/PolygonBoundingChanges_0.5_0.5/Experiment17 (Default Overlap)/AllSimilarity"


experimentName = startFileLocation.split("/")[1]
queryLocations = "LakhDataset/ExperimentDataset/Queries"
precissionAt = 10

showInter = True
showQuery = True

def main():
    # maxResults()
    # topXResults(1)
    # topXResults(4)
    thresholdResults(0.9)
    return


# Deprecated
def maxResults():
    results = CWR.openFile(fileLocation)

    highestResults = {}

    for label in results:
        highestResults[label] = {
            "grouping": "",
            "score": 0
        }
        for group in results[label]:
            average = 0
            for piece in results[label][group]:
                average += results[label][group][piece]
            average /= len(results[label][group])

            if average > highestResults[label]["score"]:
                highestResults[label]["grouping"] = group
                highestResults[label]["score"] = average

            print(f"{label}:{group} -> {average}")

    trueCount = 0
    falseCount = 0
    for label in highestResults:
        match = False
        if highestResults[label]["grouping"] == label:
            match = True

        if match:
            trueCount += 1
        else:
            falseCount += 1
        print(f"Highest Similarity: {label} -> {highestResults[label]['grouping']} | {match} : {highestResults[label]['score']}")

    print(f"True Count: {trueCount}")
    print(f"False Count: {falseCount}")


def topXResults(topX):

    queryLabels = os.listdir(startFileLocation)

    resultsTracking = {}

    for queryLabel in queryLabels:
        resultsTracking[queryLabel] = {}
        print(f"Analyzing Query: {queryLabel}")

        currentQueryLocation = os.path.join(startFileLocation, queryLabel)

        comparisonLabels = os.listdir(currentQueryLocation)

        for comparisonLabel in comparisonLabels:
            resultsTracking[queryLabel][comparisonLabel] = {
                "average": 0,
                "averageList": []
            }
            # print(comparisonLabel)
            currentComparisonLocation = os.path.join(currentQueryLocation, comparisonLabel)
            dataNames = os.listdir(currentComparisonLocation)

            for dataName in dataNames:
                dataLocation = os.path.join(currentComparisonLocation, dataName)
                data = CWR.openFile(dataLocation, printDisplay=False)
                topXResult = [i for i in heapq.nlargest(topX, data)]
                if topXResult:
                    # print(topXResult)
                    resultsTracking[queryLabel][comparisonLabel]["averageList"].append(statistics.mean(topXResult))

            resultsTracking[queryLabel][comparisonLabel]["average"] = statistics.mean(resultsTracking[queryLabel][comparisonLabel]["averageList"])

    trueCount = 0
    falseCount = 0
    for queryLabel in resultsTracking:

        highestComparison = queryLabel

        for comparisonLabel in resultsTracking[queryLabel]:


            if resultsTracking[queryLabel][comparisonLabel]["average"] > resultsTracking[queryLabel][highestComparison]["average"]:
                highestComparison = comparisonLabel


        match = False
        if highestComparison == queryLabel:
            match = True

        if match:
            trueCount += 1
        else:
            falseCount += 1
        print(f"Highest Similarity: {queryLabel} -> {highestComparison} | {match} : {resultsTracking[queryLabel][highestComparison]['average']}")

    print(f"True Count: {trueCount}")
    print(f"False Count: {falseCount}")
    return


def thresholdResults(threshold):
    queryLabels = os.listdir(startFileLocation)

    resultsTracking = {}

    # Go through each query
    for queryLabel in queryLabels:

        # Updating the results tracker
        resultsTracking[queryLabel] = {}
        print(f"Analyzing Query: {queryLabel}")

        # Give the file location where all the data is stored for the current query
        currentQueryLocation = os.path.join(startFileLocation, queryLabel)

        # Gets the labels of all the comparisons it needs to do
        comparisonLabels = os.listdir(currentQueryLocation)

        # Goes through each comparison label
        for comparisonLabel in comparisonLabels:
            # Update the results tracker
            resultsTracking[queryLabel][comparisonLabel] = {
                "average": 0,
                "stdDev": 0,
                "averageList": [],
                "total": 0
            }
            # print(comparisonLabel)
            # Gets the list of files contained within the current comparison label
            currentComparisonLocation = os.path.join(currentQueryLocation, comparisonLabel)
            dataNames = os.listdir(currentComparisonLocation)

            # Goes through each piece within that comparison label
            for dataName in dataNames:
                dataLocation = os.path.join(currentComparisonLocation, dataName)
                data = CWR.openFile(dataLocation, printDisplay=False)

                # Gets the comparisons above a specified threshold


                topXResult = []
                if (
                        "fragmentedScoreList" in data and
                        len(data["fragmentedScoreList"]) > 0 and
                        isinstance(data["fragmentedScoreList"][0], list)
                ):

                    for i in range(len(data["overlapScoreList"])):
                        tempScore = 0
                        tempScore += data["overlapScoreList"][i]
                        modifier = statistics.mean(data["fragmentedScoreList"][i])
                        tempScore *= modifier
                        if tempScore > threshold:
                            topXResult.append(tempScore)

                else:
                    topXResult = [i for i in data["overlapScoreList"] if i >= threshold]

                # print(topXResult)
                # If the results aren't empty
                # if topXResult and data["pieceLength"] != 0:
                if topXResult:
                    # Normalise the results by getting their sum and dividing it by the length of the piece
                    normalisedResults = sum(topXResult) / data["pieceLength"]
                    # normalScores = []
                    # for topResult in topXResult:
                    #     normalResult = topResult / data["pieceLength"]
                    #     normalScores.append(normalResult)
                    # normalisedResults = sum(normalScores)/len(normalScores)
                    # print(f"Normalised Results: {normalisedResults}")

                    # The normalised results get appended to a list
                    resultsTracking[queryLabel][comparisonLabel]["averageList"].append(normalisedResults)
                # Experimenting removing this
                # else:
                ##     If there is no data we just default the similarity to 0
                    # resultsTracking[queryLabel][comparisonLabel]["averageList"].append(0)

            # if the average list is not empty
            if len(resultsTracking[queryLabel][comparisonLabel]["averageList"]) != 0:
                # print(resultsTracking[queryLabel][comparisonLabel]["averageList"])
                # get the average of those results
                resultsTracking[queryLabel][comparisonLabel]["total"] = len(dataNames)
                resultsTracking[queryLabel][comparisonLabel]["average"] = statistics.mean(
                    resultsTracking[queryLabel][comparisonLabel]["averageList"])
                # Get the standard deviation of those results
                if len(resultsTracking[queryLabel][comparisonLabel]["averageList"]) > 1:
                    resultsTracking[queryLabel][comparisonLabel]["stdDev"] = statistics.stdev(resultsTracking[queryLabel][comparisonLabel]["averageList"])
                else:
                    resultsTracking[queryLabel][comparisonLabel]["stdDev"] = "NA"

            else:
                resultsTracking[queryLabel][comparisonLabel]["average"] = "NA"
                resultsTracking[queryLabel][comparisonLabel]["stdDev"] = "NA"
                resultsTracking[queryLabel][comparisonLabel]["total"] = len(dataNames)


    nameMapping = CWR.openFile("Papers/Paper_2/Datasets/NamingConvention.json")

    for query in resultsTracking:

        dataFrameData = {}
        for label in resultsTracking[query]:
            # dataFrameData[nameMapping[query]] = {labelMapping[label]: resultsTracking[query][label]["averageList"]}
            dataFrameData[nameMapping[label]] = resultsTracking[query][label]["averageList"]

        # df = pd.DataFrame(dataFrameData)

        queries = os.listdir(queryLocations)

        for queryLoc in queries:
            if query in queryLoc:
                if showInter and showQuery:
                    VIS.visualiseMIDIAsLines(queryLocations+"/"+queryLoc)



        if showInter:
            sns.stripplot(dataFrameData)
            plt.xticks(rotation=90)
            plt.title(f"Recall: {len(dataFrameData[nameMapping[query]])}/{resultsTracking[query][query]['total']}")
            plt.suptitle(f"Query {nameMapping[query]}: {query}")
            plt.show()
            print(dataFrameData)



    orderingDictionary = {
        # Going to contain keys of dictionaries with a list containing tuples of labels and scores
    }
    trueCount = 0
    falseCount = 0
    averagePosition = {
        # Going to contain keys of dictionaries with its best result
    }
    # for every label
    for queryLabel in resultsTracking:

        # Assume the highest comparison will be with itself
        highestComparison = queryLabel

        # Creates an entry in the dictionary for this label
        orderingDictionary[queryLabel] = []

        # creates an entry in the dictionary for this label
        # averagePosition[queryLabel] = {}

        # averagePosition[queryLabel] = {
        #     "label": highestComparison,
        #     "average": 0,  # Overall average
        #     "stdDev": 0,  # Overall standard deviation
        #     "averagingList": [],  # list of  comparisons
        #     "total": 0  # N number of total copies
        # }

        # For each label in the results for the current label
        for comparisonLabel in resultsTracking[queryLabel]:

            # # Create a default best entry into the average position dictionary between the query label and the tune label


            # This checks if the query and the tune label from the average results is greater than the current best average
            # if not isinstance(resultsTracking[queryLabel][comparisonLabel]["average"], str):
            #     if resultsTracking[queryLabel][comparisonLabel]["average"] > resultsTracking[queryLabel][highestComparison]["average"]:
            #         # if it is we change what the label that the current query best matches
            #         highestComparison = comparisonLabel
            #         averagePosition[queryLabel]["label"] = comparisonLabel
            #         averagePosition[queryLabel]["average"] = resultsTracking[queryLabel][comparisonLabel]["average"]
            #         averagePosition[queryLabel]["stdDev"] = resultsTracking[queryLabel][comparisonLabel]["stdDev"]
            #         averagePosition[queryLabel]["averagingList"] = resultsTracking[queryLabel][comparisonLabel]["averageList"]
            #         averagePosition[queryLabel]["total"] = resultsTracking[queryLabel][comparisonLabel]["total"]

            # Make note of the of how each tune and its label and the score it received
            for result in resultsTracking[queryLabel][comparisonLabel]["averageList"]:
                orderingDictionary[queryLabel].append((comparisonLabel, result))

        # Orders the dictionary
        orderingDictionary[queryLabel] = sorted(
            orderingDictionary[queryLabel],
            key=lambda x: x[1],
            reverse=True
        )

        rankings = {

        }

    # For each query
    for query in orderingDictionary:
        rankings[query] = {}
        # For each label
        for label in orderingDictionary:
            rankings[query][label] = {
                "rank": [],
                "average": None,
                "stdDev": None
            }
            # Tally the rank of all the labels in a query
            for i in range(len(orderingDictionary[query])):
                value = orderingDictionary[query][i]
                if value[0] == label:
                    rankings[query][label]["rank"].append(i)

            if len(rankings[query][label]["rank"]) > 0:
                rankings[query][label]["average"] = statistics.mean(rankings[query][label]["rank"])
            if len(rankings[query][label]["rank"]) > 1:
                rankings[query][label]["stdDev"] = statistics.stdev(rankings[query][label]["rank"])

    matchCount = 0
    precisionDict = {}
    for query in rankings:

        match = False
        precissionMatches = 0

        finalPrecisionLength = min(len(orderingDictionary[query]), precissionAt)

        for i in range(finalPrecisionLength):
            if orderingDictionary[query][i][0] == query:
                precissionMatches += 1


        lowestAverage = None
        lowestStdDev = None
        lowestLabel = None

        for label in rankings[query]:

            if rankings[query][label]["average"] is not None:

                if lowestAverage is None:
                    lowestAverage = rankings[query][label]["average"]
                    lowestStdDev = rankings[query][label]["stdDev"]
                    lowestLabel = label

                elif rankings[query][label]["average"] < lowestAverage:
                    lowestAverage = rankings[query][label]["average"]
                    lowestStdDev = rankings[query][label]["stdDev"]
                    lowestLabel = label

        if query == lowestLabel:
            match = True
            matchCount += 1

        if lowestLabel is not None:
            lowestLabel = nameMapping[lowestLabel]
        else:
            lowestLabel = None

        print(f"Lowest Rank {nameMapping[query]} -> {lowestLabel} | Match: {match} | AVG: {lowestAverage} | stdDev: {lowestStdDev}")
        print(f"Precision of {query} @ {precissionAt}: {precissionMatches}/{finalPrecisionLength}")
        precisionDict[query] = (precissionMatches, finalPrecisionLength)

    print(f"True Count: {matchCount}/{len(resultsTracking)}")


    precisionTransform = []
    for query in precisionDict:
        precisionTransform.append((nameMapping[query], precisionDict[query][0]))

    df = pd.DataFrame(precisionTransform, columns=["Label", "Precision"])

    plt.suptitle(experimentName)
    plt.title(f"Precision at {precissionAt}")
    sns.barplot(x="Label", y="Precision", data=df)
    plt.xticks(rotation=90)

    plt.show()

    print(nameMapping)



    return


main()