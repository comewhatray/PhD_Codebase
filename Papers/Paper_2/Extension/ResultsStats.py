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
import matplotlib.cm as cm

from scipy import stats

import seaborn as sns


# batchLocation = "yScal4Mem5"
# batchName = "scale_x1_y5-membership_0.7" # Top at 0.7
# batchName = "scale_x1_y5_BestResults_0.7-membership_0.9-rhythm_ins_0.8_del_0.2" # 2nd at 0.7
# batchName = "scale_x1_y5_BestResults_0.7-membership_0.9-rhythm_ins_1_del_0.2"
# batchName = "scale_x1_y6-membership_0.7"
# batchName = "scale_x1_y5_BestResults_0.7-membership_0.9-rhythm_ins_0.4_del_0.2"

batchName = "-membership_0.9-rhythm_ins_0.4_del_0.4"
# batchName = "-membership_0.9-rhythm_ins_0.4_del_0.4_TEST"
# batchName = "-membership_0.9-rhythm_ins_0.8_del_0.4"

# batchName = "scale_x1_y6-membership_0.9" # Top at 0.8
# batchName = "scale_x1_y7-membership_0.9" # Top at 0.9


# batchName = "test"

batchLocation = f"ExperimentResults/{batchName}"
ExperimentNames = [
    "Experiment15 (BreathingRoom_Membership)",
    "Experiment17 (Default Overlap)",
    "Experiment18 (Membership_Rhythmn)",
    "Experiment19 (Membership_Rhythmn_No_Deletion)"
]

experimentSubset = "AllSimilarity"

# experimentName = startFileLocation.split("/")[1]
queryLocations = "LakhDataset/ExperimentDataset/Queries"
precissionAt = 20
# Percentages for threshold values
minThreshold = 50
thresholdInterval = 2

showInter = False
showQuery = False
showMain = False

def main():

    for experimentName in ExperimentNames:
        startFileLocation = CWR.appendDirectory(batchLocation, [experimentName, experimentSubset])

        if os.path.exists(startFileLocation):

            print(f"{startFileLocation} exists")

            # stats = thresholdResults(startFileLocation, 0.85)
            # plotPrecisionRecallGraph(startFileLocation)

            queryStatsPerformance(startFileLocation, 0.8)

            # combinedStatsPerformance(startFileLocation, 0.85)

        else:
            print(f"{experimentName} does not exist")




    return


# Deprecated
def maxResults(fileLocation):
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

# Deprecated
def topXResults(topX, startFileLocation):

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


def thresholdResults(startFileLocation, threshold):

    experimentName = startFileLocation.split("/")[2]

    queryLabels = os.listdir(startFileLocation)

    resultsTracking = {}

    recallStats = []

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

        # recallStats.append((nameMapping[query], len(dataFrameData[nameMapping[query]]) / resultsTracking[query][query]['total']))



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
        recallMatches = 0

        # This gets whichever is lowest, the number of returned results or the precision value
        finalPrecisionLength = min(len(orderingDictionary[query]), precissionAt)

        for i in range(finalPrecisionLength):
            if orderingDictionary[query][i][0] == query:
                precissionMatches += 1
                recallMatches += 1

        recallStats.append((nameMapping[query], recallMatches/ resultsTracking[query][query]['total']))


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

    if showMain:
        plt.suptitle(experimentName)
        plt.title(f"Precision at {precissionAt}")
        sns.barplot(x="Label", y="Precision", data=df)
        plt.xticks(rotation=90)

        plt.show()

    # print(nameMapping)



    precisionStats = []


    for query in precisionTransform:
        precisionStats.append((query[0], query[1]/precissionAt))

    return (precisionStats, recallStats)


def plot_precision_recall_vs_threshold(data: dict):
    """
    Plot precision and recall vs threshold for each entry in the dictionary.

    Args:
        data: dict where each key is an entry ID and each value contains:
              'Precision': list of (threshold, precision) tuples
              'Recall':    list of (threshold, recall) tuples
    """
    n = len(data)
    ncols = 3
    nrows = (n + ncols - 1) // ncols

    fig, axes = plt.subplots(nrows, ncols, figsize=(ncols * 4.5, nrows * 3.2))
    axes = axes.flatten()
    fig.suptitle(f"Precision and Recall vs Threshold: {batchName}")
    colors = cm.tab10(np.linspace(0, 1, 10))

    for idx, (entry_id, metrics) in enumerate(data.items()):
        ax = axes[idx]

        p_thresholds, p_values = zip(*metrics['Precision'])
        r_thresholds, r_values = zip(*metrics['Recall'])

        ax.plot(p_thresholds, p_values, marker='o', markersize=4,
                label='Precision', color='#378ADD', linewidth=1.8)
        ax.plot(r_thresholds, r_values, marker='s', markersize=4,
                label='Recall', color='#D85A30', linewidth=1.8, linestyle='--')

        ax.set_title(f'Query {entry_id}', fontsize=11, fontweight='medium')
        ax.set_xlabel('Threshold', fontsize=9)
        ax.set_ylabel('Score', fontsize=9)
        ax.set_ylim(-0.05, 1.1)
        ax.set_xlim(-0.02, max(max(p_thresholds), max(r_thresholds)) + 0.05)
        ax.grid(True, linestyle='--', alpha=0.4)
        ax.tick_params(labelsize=8)
        ax.legend(fontsize=8, loc='center right')
        ax.spines[['top', 'right']].set_visible(False)

    # Hide unused subplots
    for idx in range(n, len(axes)):
        axes[idx].set_visible(False)

    fig.suptitle('Precision & Recall vs Threshold', fontsize=14,
                 fontweight='medium', y=1.01)
    plt.tight_layout()
    plt.savefig(f'Papers/Paper_2/Visualisations/Extension/Figures/{batchName}-precision_recall_plot.png', dpi=150, bbox_inches='tight')
    plt.show()
    print("Plot saved to precision_recall_plot.png")


def plotPrecisionRecallGraph(startFileLocation):
    individualStorage = {}
    for i in range(minThreshold, 101, thresholdInterval):
        theshold = i / 100

        results = thresholdResults(startFileLocation, theshold)

        for query in range(len(results[0])):
            if query not in individualStorage:
                individualStorage[query] = {
                    "Precision": [(theshold, results[0][query][1])],
                    "Recall": [(theshold, results[1][query][1])]
                }
            else:
                individualStorage[query]["Precision"].append((theshold, results[0][query][1]))
                individualStorage[query]["Recall"].append((theshold, results[1][query][1]))

    plot_precision_recall_vs_threshold(individualStorage)

def queryStatsPerformance(startFileLocation, threshold):

    importantStats = ["numNotes", "noteDensity", "xRange", "yRange", "standardDeviationPitch"]

    statsDictionary = CWR.openFile("Papers/Paper_2/Extension/OnceOffStorage/QueryCharacteristics.json")
    nameMapping = CWR.openFile("Papers/Paper_2/Datasets/NamingConvention.json")
    reverseMapping  = {v: k for k, v in nameMapping.items()}

    metricName = "Average Precision/Recall"
    # metricName = "Precision"
    # metricName = "Recall"

    tempResults = []
    for stat in importantStats:

        statResults = []
        results = thresholdResults(startFileLocation, threshold)


        for i in range(len(results[0])):

            # Average of precision and recall)
            metric = (results[0][i][1] + results[1][i][1])/ 2

            # Precision
            # metric = results[0][i][1]

            # Recall
            # metric = results[1][i][1]

            queryStatValue = statsDictionary[reverseMapping[f"{i}"]][stat]
            statResults.append((queryStatValue, metric))


        x, y = zip(*statResults)
        plt.title(f"{metricName} @ {precissionAt} vs {stat} @ threshold: {threshold}")
        plt.xlabel(f"{stat}")
        plt.ylabel(f"{metricName}")
        plt.scatter(x, y)
        plt.show()

        rho, p = stats.spearmanr(x, y)
        tempResults.append((stat, rho, p))
        # print(f"Stat {stat}")
        # print(f"P: {p}")
        # print(f"rho: {rho}")
    for results in tempResults:
        print(results)


def combinedStatsPerformance(startFileLocation, threshold):

    importantStats = ["numNotes", "noteDensity", "xRange", "yRange", "standardDeviationPitch"]

    statsDictionary = CWR.openFile("Papers/Paper_2/Extension/OnceOffStorage/QueryCharacteristics.json")
    nameMapping = CWR.openFile("Papers/Paper_2/Datasets/NamingConvention.json")
    reverseMapping = {v: k for k, v in nameMapping.items()}

    # stat1 = "numNotes"
    # stat2 = "noteDensity"
    metricName = "Average Precision/Recall"


    results = thresholdResults(startFileLocation, threshold)


    for k in range(len(importantStats)):
        stat1 = importantStats[k]
        for j in range(k+1, len(importantStats)):
            stat2 = importantStats[j]

            statResults = []

            for i in range(len(results[0])):
                # Average of precision and recall)
                metric = (results[0][i][1] + results[1][i][1]) / 2

                # Precision
                # metric = results[0][i][1]

                # Recall
                # metric = results[1][i][1]

                queryStatValue1 = statsDictionary[reverseMapping[f"{i}"]][stat1]
                queryStatValue2 = statsDictionary[reverseMapping[f"{i}"]][stat2]
                statResults.append((queryStatValue1, queryStatValue2, metric))


            fig = plt.figure()
            ax = fig.add_subplot(111, projection='3d')

            # points = [(1, 2, 3), (4, 5, 6), (7, 8, 9)]

            x, y, z = zip(*statResults)
            ax.scatter(x, y, z)

            ax.set_title(f"{stat1} + {stat2} | {metricName} @ {precissionAt} vs {threshold}")
            ax.set_xlabel(f"{stat1}")
            ax.set_ylabel(f"{stat2}")
            ax.set_zlabel(f"{metricName}")

            plt.show()



main()