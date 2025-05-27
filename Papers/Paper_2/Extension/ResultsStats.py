from Utilities import ComeWhatRayUtil as CWR
from Utilities import datasetManagment as DM
import os
import heapq
import statistics

# fileLocation = "Papers/Paper_2/Extension/ExtensionWorkspace/ExperimentResults.json"
# fileLocation = "Papers/Paper_2/Extension/ExtensionWorkspace/Experiment7Results.json"
fileLocation = "Papers/Paper_2/Extension/ExtensionWorkspace/Experiment8Results.json"
startFileLocation = "ExperimentResults/Experiment8/AllSimilarity"

def main():
    # maxResults()
    topXResults(1)
    # topXResults(4)
    # thresholdResults(.5)
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
                topXResult = [i for i in data if i >= threshold]
                # print(topXResult)
                if topXResult:

                    resultsTracking[queryLabel][comparisonLabel]["averageList"].append(statistics.mean(topXResult))

            if len(resultsTracking[queryLabel][comparisonLabel]["averageList"]) != 0:
                # print(resultsTracking[queryLabel][comparisonLabel]["averageList"])
                resultsTracking[queryLabel][comparisonLabel]["average"] = statistics.mean(
                    resultsTracking[queryLabel][comparisonLabel]["averageList"])


    trueCount = 0
    falseCount = 0
    for queryLabel in resultsTracking:

        highestComparison = queryLabel

        for comparisonLabel in resultsTracking[queryLabel]:

            if resultsTracking[queryLabel][comparisonLabel]["average"] > resultsTracking[queryLabel][highestComparison][
                "average"]:
                highestComparison = comparisonLabel

        match = False
        if highestComparison == queryLabel:
            match = True

        if match:
            trueCount += 1
        else:
            falseCount += 1
        print(
            f"Highest Similarity: {queryLabel} -> {highestComparison} | {match} : {resultsTracking[queryLabel][highestComparison]['average']}")

    print(f"True Count: {trueCount}")
    print(f"False Count: {falseCount}")
    return


main()