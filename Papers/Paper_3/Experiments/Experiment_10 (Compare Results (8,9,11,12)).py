from Utilities import ComeWhatRayUtil as CWR
import numpy as np
import pandas as pd
from sklearn.metrics import confusion_matrix
import os


ExperimentResultsDirectory = "ExperimentResults/Experiment10"
numExperiments = 7

options = ["TrainingStage", "TrainingTest", "TestStage"]
numClass = 5

# Approach = "Custom"
Approach = "Comparison"
fileIteration = "ExperimentResults2.json"
epoch = 100

def main():
    print("Experiment Start")
    # oneRun()
    # correctPercentage("HAHA")
    # answerDistribution()
    averageMain()



def oneRun():
    print("Experiment Start (One Run)")
    # fileLocation = CWR.appendDirectory(ExperimentResultsDirectory, [Approach, fileIteration])
    # experimentData = CWR.openFile(fileLocation)

    experimentData = CWR.openFile("ExperimentResults/Experiment10/CustomBalanced/results/ExperimentResults0.json")
    # closeCallTest(experimentData, 100)
    confusionMatrixTest(experimentData, 100)

    # closeCallTest(experimentData, epoch)
    # confusionMatrixTest(experimentData, epoch)

def averageMain():
    print("Experiment Start (Average)")

    comparisons = ["Custom", "Comparison", "CustomBalanced", "ComparisonBalanced"]

    storeResults = {}


    for comparison in comparisons:

        averageConfusion = np.zeros((numClass, numClass))
        averageCloseCall = np.zeros((numClass, numClass))
        averageCorrect = 0

        storeResults[comparison] = {}

        fileCount = len(os.listdir(f"{ExperimentResultsDirectory}/{comparison}/results"))
        print(fileCount)

        print("Comparing: " + comparison)
        for i in range(fileCount):
            fileIttr = f"ExperimentResults{i}.json"
            fileLocation = CWR.appendDirectory(ExperimentResultsDirectory, [comparison, "results", fileIttr])
            experimentData = CWR.openFile(fileLocation)

            averageCloseCall = np.add(averageCloseCall, closeCallTest(experimentData, epoch))
            averageConfusion = np.add(averageConfusion, confusionMatrixTest(experimentData, epoch, percentage=True))
            averageCorrect += correctPercentage(experimentData, epoch)

        averageCloseCall = np.divide(averageCloseCall, fileCount)
        averageConfusion = np.divide(averageConfusion, fileCount)
        averageCorrect = averageCorrect / fileCount

        storeResults[comparison]['averageCloseCall'] = averageCloseCall
        storeResults[comparison]['averageConfusion'] = averageConfusion
        storeResults[comparison]['averageCorrect'] = averageCorrect

    print(CWR.extraLargeSpacer)
    print("RESULTS")
    for comparison in comparisons:
        print(CWR.extraLargeSpacer)
        print(f"Results for {comparison} method:")
        print(f"Average Close Call: {comparison}")
        print(storeResults[comparison]['averageCloseCall'])
        print(convertToCSV(storeResults[comparison]['averageCloseCall']))
        print(f"Average Confusion: {comparison}")
        print(storeResults[comparison]['averageConfusion'])
        print(convertToCSV(storeResults[comparison]['averageConfusion']))
        print(f"Average Correct: {comparison}")
        print(storeResults[comparison]['averageCorrect'])

# Metrics
# ----------------------------------------------------------------------------------------------------------------------

# Correct Percentage
# ----------------------------------------------------------------------------------------------------------------------

def correctPercentage(experimentData, epoch):

    average = 0
    # experimentData = CWR.openFile("ExperimentResults/Experiment10/Custom/results/ExperimentResults0.json")

    results = experimentData["TestStage"][epoch]

    for result in results:
        print(result)
        # values.index(max(values))

        probs = result["Probabilities"]
        guess = np.argmax(probs)
        answer = result["Answer"][0]

        print(f"{guess}: {answer}")

        if guess == answer:
            average += 1

    average = average / len(results)

    print(f"Average Correct: {average}")
    return average


# When wrong, how much was it wrong by
# ----------------------------------------------------------------------------------------------------------------------
def closeCallTest(experimentData, epoch):
    print("Close Call Test")

    experimentDataTest = experimentData["TestStage"][epoch]

    results = getCloseCalls(experimentDataTest)

    averageMatrix = np.zeros((numClass, numClass))
    # print(averageMatrix)

    for result in results:
        print(result)
        # averageMatrix[result['actual']][result['prediction']] += (result['probAct'] - result['probPred'])
        averageMatrix[result['prediction']][result['actual']] += (result['probPred'] - result['probAct'])


    for x in range(numClass):
        for y in range(numClass):
            averageMatrix[x][y] = averageMatrix[x][y] / len(results)



    print(f"Incorrect Predictions: {len(results)}")
    print("Average Difference between Prediction and Actual")
    print(averageMatrix)

    return averageMatrix

def getCloseCalls(results):

    closeCalls = []

    for result in results:

        prediction = np.argmax(result['Probabilities'])
        actual = result["Answer"][0]
        otherOrdering = []
        others = []

        for i in range(numClass):
            if i != prediction and i != actual:
                otherOrdering.append(i)
                others.append(result['Probabilities'][0][i])


        if prediction != actual:
            data = {
                "actual": actual,
                "prediction": prediction,
                "probAct": result['Probabilities'][0][actual],
                "probPred": result['Probabilities'][0][prediction],
                "otherOrdering": otherOrdering,
                "otherProb": others

            }
            closeCalls.append(data)

    return closeCalls

def answerDistribution():

    experimentData = CWR.openFile("ExperimentResultsBalanced_1.json")


    trainDistribution = {}
    testDistribution = {}

    experimentDataTrain = experimentData["TrainingStage"][epoch]


    for result in experimentDataTrain:

        numberAnswer = result['Answer'][0]

        if numberAnswer not in trainDistribution:
            trainDistribution[numberAnswer] = 0
        else:
            trainDistribution[numberAnswer] += 1

    experimentDataTrain = experimentData["TestStage"][epoch]

    for result in experimentDataTrain:

        numberAnswer = result['Answer'][0]
        if numberAnswer not in testDistribution:
            testDistribution[numberAnswer] = 0
        else:
            testDistribution[numberAnswer] += 1

    print(trainDistribution)
    print(testDistribution)


# Confusion Matrix stuff
# ----------------------------------------------------------------------------------------------------------------------

def confusionMatrixTest(experimentData, epoch, percentage=False):
    print("Confusion Matrix Test")

    experimentDataTest = experimentData["TestStage"][epoch]
    # experimentDataTrain = experimentData["TrainingTest"][epoch]

    # print(len(experimentData["TestStage"]))
    # print(experimentData["TestStage"])

    totalCount = [0 for _ in range(5)]

    # pred, actual = getConfusionInputs(experimentDataTrain)
    # countResults(totalCount, actual)

    pred, actual = getConfusionInputs(experimentDataTest)
    countResults(totalCount, actual)
    # print(totalCount)

    confusion = confusion_matrix(actual, pred)
    # print(confusion)

    # Percentage Confusion
    # print(confusion[0])

    # confusion.astype(np.float32)

    confPercent = np.zeros((len(confusion), len(confusion)))

    for row in range(len(confusion)):
        for value in range(len(confusion[row])):
            confPercent[row][value] =  confusion[row][value] / totalCount[row]
            confPercent[row][value] = round(confPercent[row][value] * 100, 2)

    # print(confPercent)

    if percentage:
        return confPercent
    else:
        return confusion

    # return confusion, confPercent

def getConfusionInputs(results):
    pred = []
    actual = []

    for result in results:
        # print(counter)
        # print(result)
        # print(result['Probabilities'])
        # print(np.argmax(result['Probabilities']))
        pred.append(np.argmax(result['Probabilities']))
        # print(result["Answer"][0])
        actual.append(result["Answer"][0])

    return pred, actual

def countResults(counter, actual):

    for i in range(5):
        count = actual.count(i)
        print(f"{i}: {count}")
        counter[i] += count


# Utility
# ----------------------------------------------------------------------------------------------------------------------
def convertToCSV(array):

    composerList = ["Chopin", "Liszt", "Schubert", "Scarlatti", "Bach"]

    count = 0

    topString = ""
    for composer in composerList:
        topString += f", {composer}"


    print(topString)
    for row in array:
        outString = f"{composerList[count]}"
        for value in row:
            outString += str(f", {round(value, 2)}")

        print(outString)

        count += 1







if __name__ == '__main__':
    main()




