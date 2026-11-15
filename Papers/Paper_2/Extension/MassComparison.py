from Utilities import ComeWhatRayUtil as CWR
import os
import statistics
import numpy as np
from multiprocessing import Pool
import multiprocessing as mp
from tqdm import tqdm


comparisonStarts = {
    "Default": "DefaultExperiment", # Default
    "Membership": "membership_",  # Membership Only
    "Rhythm": "rhythm_ins", # Rhythm Only
    "MembershipRhythm": "-membership_", # This is for membership and rythmn
    "Scaling": "scale_"
}

ResultsLocation = "ExperimentResults/"

comparisons = {
    "Default": [],
    "Membership": [],
    "Rhythm": [],
    "MembershipRhythm": [],
    "Scaling": []
}

Threshold = 0.5
Binary = False
# Currently have removed the non diagona aspect of the nonbinary method
MULTI = True


# def main():
#     fileNames = os.listdir(ResultsLocation)
#
#
#     # Allocate the Names better
#     for fileName in fileNames:
#         if fileName.startswith(comparisonStarts["Default"]):
#             comparisons["Default"].append(fileName)
#
#         if fileName.startswith(comparisonStarts["Membership"]):
#             comparisons["Membership"].append(fileName)
#
#         if fileName.startswith(comparisonStarts["Rhythm"]):
#             comparisons["Rhythm"].append(fileName)
#
#         if fileName.startswith(comparisonStarts["MembershipRhythm"]):
#             comparisons["MembershipRhythm"].append(fileName)
#
#
#     resultsAverageTracking = []
#     for key in comparisons:
#         # print(comparisons[key])
#         # if key == "Default":
#         for comparison in comparisons[key]:
#
#             confusionMatrix = generateConfusionMatrix(os.path.join(ResultsLocation, comparison))
#
#             nameMapping = CWR.openFile("Papers/Paper_2/Datasets/NamingConvention.json")
#
#
#             remapedMatrix = {}
#             for query in confusionMatrix:
#
#                 remapedMatrix[nameMapping[query]] = {}
#                 for label in confusionMatrix[query]:
#
#                     averageScore = 0
#                     if isinstance(confusionMatrix[query][label]["average"] , (int, float)):
#                         averageScore = confusionMatrix[query][label]["average"]
#
#                     remapedMatrix[nameMapping[query]][nameMapping[label]] = averageScore
#
#             # Get dimensions
#             row_keys = sorted(remapedMatrix.keys(), key=int)
#             col_keys = sorted(set(k for row in remapedMatrix.values() for k in row.keys()), key=int)
#
#             # Create array
#             arrayConfusionMatrix = np.array([[remapedMatrix[r][c] for c in col_keys] for r in row_keys])
#
#             diagonal_avg = np.diag(arrayConfusionMatrix).mean()
#
#             resultsAverageTracking.append((comparison, diagonal_avg))
#
#
#     # print(resultsAverageTracking)
#
#     sortedAverageTracking = sorted(resultsAverageTracking, key=lambda x: x[1], reverse=True)
#
#     print(sortedAverageTracking)
#
#     CWR.saveFile("Papers/Paper_2/Extension/OnceOffStorage/BestResults.pkl", sortedAverageTracking)

def process_comparison(args):
    """Process a single comparison"""
    comparison, ResultsLocation, nameMapping = args

    confusionMatrix = generateConfusionMatrix(os.path.join(ResultsLocation, comparison))

    # Rest of the code stays the same...
    remapedMatrix = {}

    if not Binary:
        for query in confusionMatrix:
            remapedMatrix[nameMapping[query]] = {}
            # if not Binary:
            for label in confusionMatrix[query]:
                averageScore = 0
                if isinstance(confusionMatrix[query][label]["average"], (int, float)):
                    averageScore = confusionMatrix[query][label]["average"]

                remapedMatrix[nameMapping[query]][nameMapping[label]] = averageScore
            # else:
            #     # Get the label with the highest average
            #     highestLabel = query #The query is set as the default highest label
            #     highestScore = 0
            #     for label in confusionMatrix[query]:
            #         averageScore = 0
            #         if isinstance(confusionMatrix[query][label]["average"], (int, float)):
            #             averageScore = confusionMatrix[query][label]["average"]
            #
            #         if averageScore > highestScore:
            #             highestLabel = label
            #             highestScore = averageScore
            #
            #     for label in confusionMatrix[query]:
            #         if label == highestLabel:
            #             remapedMatrix[nameMapping[query]][nameMapping[label]] = 1
            #         else:
            #             remapedMatrix[nameMapping[query]][nameMapping[label]] = 0


    else:
        # Create the binary matrix
        binaryMatrix = np.zeros((len(confusionMatrix.keys()), len(confusionMatrix.keys())))

        # Go through each label
        for label in confusionMatrix:

            # We now want to go through each entry in that label to find which query gave that entry the highest score
            for entry in range(len(confusionMatrix[label][label])):

                highestQuery = ""
                highestScore = 0
                for query in confusionMatrix:
                    score = confusionMatrix[query][label]["averageList"][entry]
                    if score > highestScore:
                        highestQuery = query
                        highestScore = score

                if highestQuery != "":
                    binaryMatrix[int(nameMapping[highestQuery])][int(nameMapping[label])] += 1



    row_keys = sorted(remapedMatrix.keys(), key=int)
    col_keys = sorted(set(k for row in remapedMatrix.values() for k in row.keys()), key=int)
    arrayConfusionMatrix = np.array([[remapedMatrix[r][c] for c in col_keys] for r in row_keys])

    if not Binary:
        diagonal_avg = np.diag(arrayConfusionMatrix).mean()
        nonDiagonalAvg = avgNonDiagonal(arrayConfusionMatrix)

    # number of times correct vs number of time incorrect
    else:
        # We are about the sum of differences here
        diagonal_avg = np.diag(binaryMatrix).sum()
        nonDiagonalAvg = binaryMatrix.sum() - diagonal_avg

    # avgDifference = diagonal_avg - nonDiagonalAvg
    avgDifference = diagonal_avg

    return (comparison, avgDifference)


def avgNonDiagonal(matrix):
    # Create mask for diagonal
    mask = ~np.eye(matrix.shape[0], dtype=bool)

    # Get average of each row excluding diagonal
    row_averages = np.array([matrix[i][mask[i]].mean() for i in range(len(matrix))])

    return row_averages.mean()


def generateConfusionMatrix(experimentLocation):

    # print(f"Examining: {experimentLocation}")
    ExperimentName = os.listdir(experimentLocation)[0]

    experimentLocation = os.path.join(experimentLocation, ExperimentName)
    experimentLocation = os.path.join(experimentLocation, "AllSimilarity")

    queries = os.listdir(experimentLocation)
    resultsTracking = {}

    for query in queries:

        # print(f"Query: {query}")

        resultsTracking[query] = {}

        currentQueryLocation = os.path.join(experimentLocation, query)
        comparisonLabels = os.listdir(currentQueryLocation)

        # Goes through each comparison label
        for comparisonLabel in comparisonLabels:
            # Update the results tracker
            resultsTracking[query][comparisonLabel] = {
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
                        if tempScore > Threshold:
                            topXResult.append(tempScore)

                else:
                    topXResult = [i for i in data["overlapScoreList"] if i >= Threshold]

                if topXResult: # Normalise the results by getting their sum and dividing it by the length of the piece
                    normalisedResults = sum(topXResult) / data["pieceLength"]

                    # The normalised results get appended to a list
                    resultsTracking[query][comparisonLabel]["averageList"].append(normalisedResults)

                    # So in the event that there is no similarity, ew want the value to be 0
                elif Binary:
                    resultsTracking[query][comparisonLabel]["averageList"].append(0)


            # if the average list is not empty
            if len(resultsTracking[query][comparisonLabel]["averageList"]) != 0:
                # get the average of those results
                resultsTracking[query][comparisonLabel]["total"] = len(dataNames)
                resultsTracking[query][comparisonLabel]["average"] = statistics.mean(resultsTracking[query][comparisonLabel]["averageList"])

                # Get the standard deviation of those results
                if len(resultsTracking[query][comparisonLabel]["averageList"]) > 1:
                    resultsTracking[query][comparisonLabel]["stdDev"] = statistics.stdev(resultsTracking[query][comparisonLabel]["averageList"])
                else:
                    resultsTracking[query][comparisonLabel]["stdDev"] = "NA"

            else:
                resultsTracking[query][comparisonLabel]["average"] = "NA"
                resultsTracking[query][comparisonLabel]["stdDev"] = "NA"
                resultsTracking[query][comparisonLabel]["total"] = len(dataNames)


    # print(resultsTracking)
    return resultsTracking

def calculateEffectiveness():

    # Load nameMapping once
    nameMapping = CWR.openFile("Papers/Paper_2/Datasets/NamingConvention.json")

    fileNames = os.listdir(ResultsLocation)

    for fileName in fileNames:
        if fileName.startswith(comparisonStarts["Default"]):
            comparisons["Default"].append(fileName)

        if fileName.startswith(comparisonStarts["Membership"]):
            comparisons["Membership"].append(fileName)

        if fileName.startswith(comparisonStarts["Rhythm"]):
            comparisons["Rhythm"].append(fileName)

        if fileName.startswith(comparisonStarts["MembershipRhythm"]):
            comparisons["MembershipRhythm"].append(fileName)

        if fileName.startswith(comparisonStarts["Scaling"]):
            comparisons["Scaling"].append(fileName)




    resultsAverageTracking = []

    for key in comparisons:
        comparison_args = [(comparison, ResultsLocation, nameMapping)
                           for comparison in comparisons[key]]

        if MULTI:
            # Multi Process approach
            with Pool(processes=mp.cpu_count()) as pool:
                # Use imap instead of map for progress tracking
                results = list(tqdm(
                    pool.imap(process_comparison, comparison_args),
                    total=len(comparison_args),
                    desc=f"Processing {key}"
                ))

        else:
        # # Non multi Processed approach
            results = []
            for comparison in comparison_args:
                results.append(process_comparison(comparison))


        resultsAverageTracking.extend(results)

    sortedAverageTracking = sorted(resultsAverageTracking, key=lambda x: x[1], reverse=True)
    print(sortedAverageTracking)
    CWR.saveFile(f"Papers/Paper_2/Extension/OnceOffStorage/BestResults_{Threshold}_{Binary}.pkl", sortedAverageTracking)


def listTopXResults(topX):

    listings = CWR.openFile(f"Papers/Paper_2/Extension/OnceOffStorage/BestResults_{Threshold}.pkl")

    listings = listings[:topX]

    for listing in listings:
        print(listing)

if __name__ == '__main__':

    # calculateEffectiveness()
    # listTopXResults(100)


    # resultsLocation = "Papers/Paper_2/Extension/OnceOffStorage/BestResults_0.5_True.pkl"
    # resultsLocation = "Papers/Paper_2/Extension/OnceOffStorage/BestResults_0.6_True.pkl"
    # resultsLocation = "Papers/Paper_2/Extension/OnceOffStorage/BestResults_0.7_True.pkl"
    resultsLocation = "Papers/Paper_2/Extension/OnceOffStorage/BestResults_0.8_True.pkl"
    # resultsLocation = "Papers/Paper_2/Extension/OnceOffStorage/BestResults_0.9_True.pkl"
    # resultsLocation = "Papers/Paper_2/Extension/OnceOffStorage/BestResults_1_True.pkl"

    # resultsLocation = "Papers/Paper_2/Extension/OnceOffStorage/BestResults_0.5_False.pkl"
    # resultsLocation = "Papers/Paper_2/Extension/OnceOffStorage/BestResults_0.6_False.pkl"
    # resultsLocation = "Papers/Paper_2/Extension/OnceOffStorage/BestResults_0.7_False.pkl"
    # resultsLocation = "Papers/Paper_2/Extension/OnceOffStorage/BestResults_0.8_False.pkl"
    # resultsLocation = "Papers/Paper_2/Extension/OnceOffStorage/BestResults_0.9_False.pkl"
    # resultsLocation = "Papers/Paper_2/Extension/OnceOffStorage/BestResults_1_False.pkl"

    # resultsLocation = "Papers/Paper_2/Extension/OnceOffStorage/BestResults_0.5.pkl"
    # resultsLocation = "Papers/Paper_2/Extension/OnceOffStorage/BestResults_0.6.pkl"
    # resultsLocation = "Papers/Paper_2/Extension/OnceOffStorage/BestResults_0.7.pkl"
    # resultsLocation = "Papers/Paper_2/Extension/OnceOffStorage/BestResults_0.8.pkl"
    # resultsLocation = "Papers/Paper_2/Extension/OnceOffStorage/BestResults_0.9.pkl"
    # resultsLocation = "Papers/Paper_2/Extension/OnceOffStorage/BestResults_1.pkl"

    print(CWR.openFile(resultsLocation))





