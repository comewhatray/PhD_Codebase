from Utilities import ComeWhatRayUtil as CWR
from Utilities import datasetManagment as DM
import os
import heapq
import statistics

# fileLocation = "Papers/Paper_2/Extension/ExtensionWorkspace/ExperimentResults.json"
# fileLocation = "Papers/Paper_2/Extension/ExtensionWorkspace/Experiment7Results.json"
fileLocation = "Papers/Paper_2/Extension/ExtensionWorkspace/Experiment8Results.json"
# startFileLocation = "ExperimentResults/Experiment8/AllSimilarity"
startFileLocation = "ExperimentResults/Experiment9 (BreathingRoom)/AllSimilarity"

def main():
    # maxResults()
    # topXResults(1)
    # topXResults(4)
    thresholdResults(.8)
    # return


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
                "averageList": []
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
                topXResult = [i for i in data["overlapScoreList"] if i >= threshold]

                # print(topXResult)
                # If the results aren't empty
                if topXResult:
                    # Normalise the results by getting their sum and dividing it by the length of the piece
                    normalisedResults = sum(topXResult) / data["pieceLength"]

                    # The normalised results get appended to a list
                    resultsTracking[queryLabel][comparisonLabel]["averageList"].append(normalisedResults)
                else:
                    resultsTracking[queryLabel][comparisonLabel]["averageList"].append(0)

            # if the average list is not empty
            if len(resultsTracking[queryLabel][comparisonLabel]["averageList"]) != 0:
                # print(resultsTracking[queryLabel][comparisonLabel]["averageList"])
                # get the average of those results
                resultsTracking[queryLabel][comparisonLabel]["average"] = statistics.mean(
                    resultsTracking[queryLabel][comparisonLabel]["averageList"])

    orderingDictionary = {

    }
    trueCount = 0
    falseCount = 0
    averagePosition = {}
    for queryLabel in resultsTracking:

        highestComparison = queryLabel

        orderingDictionary[queryLabel] = []

        averagePosition[queryLabel] = {}

        for comparisonLabel in resultsTracking[queryLabel]:

            averagePosition[queryLabel][comparisonLabel] = {
                "average": 0,
                "averagingList": []
            }

            if resultsTracking[queryLabel][comparisonLabel]["average"] > resultsTracking[queryLabel][highestComparison][
                "average"]:
                highestComparison = comparisonLabel

            for result in resultsTracking[queryLabel][comparisonLabel]["averageList"]:
                orderingDictionary[queryLabel].append((comparisonLabel, result))

        orderingDictionary[queryLabel] = sorted(
            orderingDictionary[queryLabel],
            key=lambda x: x[1],
            reverse=True
        )

        match = False
        if highestComparison == queryLabel:
            match = True

        if match:
            trueCount += 1
        else:
            falseCount += 1
        print(
            f"Highest Similarity: {queryLabel} -> {highestComparison} | {match} : {resultsTracking[queryLabel][highestComparison]['average']}")


        for tuple in orderingDictionary[queryLabel]:
            averagePosition[queryLabel][tuple[0]]["averagingList"].append(orderingDictionary[queryLabel].index(tuple))

        for comparison in averagePosition[queryLabel]:
            averagePosition[queryLabel][comparison]["average"] = statistics.mean(averagePosition[queryLabel][comparison]["averagingList"])




    print(f"True Count: {trueCount}")
    print(f"False Count: {falseCount}")

    lowestPositions = []

    for queryLabel in averagePosition:
        print(CWR.largeSpacer)
        lowestPosition = None
        lowestTuple = None

        for comparison in averagePosition[queryLabel]:
            if lowestPosition is None:
                lowestPosition = 10000


            comparisonAverage = averagePosition[queryLabel][comparison]['average']
            if comparisonAverage < lowestPosition:
                lowestTuple = (queryLabel, comparison, comparisonAverage)
                lowestPosition = comparisonAverage

            print(f"Average position {queryLabel} -> {comparison}: {comparisonAverage}")
        lowestPositions.append(lowestTuple)

    print(CWR.extraLargeSpacer)
    print("Lowest average positions")
    print(CWR.extraLargeSpacer)
    desiredOutcome = 0
    undesiredOutcome = 0
    for x in lowestPositions:
        # print(x)
        print(f"Lowest Position {x[0]} -> {x[1]}: {x[2]}")
        if x[0] == x[1]:
            desiredOutcome += 1
        else:
            undesiredOutcome += 1

    print(f"Desired Outcome: {desiredOutcome}")
    print(f"Undesired Outcome: {undesiredOutcome}")

    return


main()