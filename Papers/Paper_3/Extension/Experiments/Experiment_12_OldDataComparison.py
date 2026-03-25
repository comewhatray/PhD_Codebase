from Utilities import ComeWhatRayUtil as CWR
import os
import numpy as np
from sklearn.metrics import confusion_matrix

directory = "Experiment3Results/analysis"
numIterations = 3
epoch = 99

experimentNames = [
    "KynaOld",
    "KynaDefaultOld",
]

classes = [
    "Bach",
    "Liszt",
    "Scarlatti",
    "Schubert",
    "Chopin",
]

def main():
    averageConfusionMatrix()
    # averageCloseCall()


def averageConfusionMatrix():
    encodings = CWR.openFile("tempHotEncodings.json")
    titleString = "|"
    for encode in encodings.keys():
        titleString = titleString + encode + "|"



    for experiment in experimentNames:
        print(f"Average ConfusionMatrix for {experiment}")

        matrixStorage = []

        for iteration in range(numIterations):

            identifier = generateIdentifier(epoch, iteration)

            experimentLocation = os.path.join(directory, experiment)
            dataLocation = os.path.join(experimentLocation, identifier)

            data = CWR.openFile(dataLocation, printDisplay=False)
            results = confusionMatrixTest(data, percentage=True)

            matrixStorage.append(results)


        print(titleString)
        average_confusion = np.mean(matrixStorage, axis=0)
        print(average_confusion)

        averageCorrectness = 0
        for i in range(len(average_confusion)):
            averageCorrectness = averageCorrectness + average_confusion[i][i]

        print(averageCorrectness/len(average_confusion))

        # print(confusionMatrixTest(data, percentage=True))




    return


def averageCloseCall():
    encodings = CWR.openFile("tempHotEncodings.json")

    titleString = "|"
    for encode in encodings.keys():
        titleString = titleString + encode + "|"

    for experiment in experimentNames:
        print(f"Close Call for {experiment}")

        dataCollection = []

        for i in range(numIterations):
            identifier = generateIdentifier(epoch, i)

            experimentLocation = os.path.join(directory, experiment)
            dataLocation = os.path.join(experimentLocation, identifier)

            data = CWR.openFile(dataLocation, printDisplay=False)
            dataCollection.append(data)

        dataTransformation = {
            "TestStage": [
                {
                    'Epoch': epoch,
                    'Predictions': []}
                ]
        }
        for data in dataCollection:
            dataTransformation["TestStage"][0]["Predictions"].extend(data["TestStage"][0]["Predictions"])

        closeCallTest(dataTransformation, printIncorect=False)



#  Analysis Methods
# ----------------------------------------------------------------------------------------------------------------------

def confusionMatrixTest(experimentData, percentage=False):
    # print("Confusion Matrix Test")

    experimentDataTest = experimentData["TestStage"]


    totalCount = [0 for _ in range(len(classes))]


    pred, actual = getConfusionInputs(experimentDataTest)
    countResults(totalCount, actual)

    confusion = confusion_matrix(actual, pred)


    confPercent = np.zeros((len(confusion), len(confusion)))

    for row in range(len(confusion)):
        for value in range(len(confusion[row])):
            confPercent[row][value] =  confusion[row][value] / totalCount[row]
            confPercent[row][value] = round(confPercent[row][value] * 100, 2)


    if percentage:
        return confPercent
    else:
        return confusion


# Check where it went wrong in cases where the predictionas are incorect
def closeCallTest(experimentData, printIncorect=True):
    print("Close Call Test")
    numClass = len(classes)

    experimentDataTest = experimentData["TestStage"][0]["Predictions"]

    results = getIncorectPredictions(experimentDataTest)

    averageMatrix = np.zeros((numClass, numClass))

    for result in results:
        if printIncorect:
            print(result)
        # averageMatrix[result['actual']][result['prediction']] += (result['probAct'] - result['probPred'])
        difference = result['probPred'] - result['probAct']
        percentDiff = difference * 100 / abs(result['probAct'])
        averageMatrix[result['prediction']][result['actual']] += percentDiff


    for x in range(numClass):
        for y in range(numClass):
            averageMatrix[x][y] = averageMatrix[x][y] / len(results)



    print(f"Incorrect Predictions: {len(results)}")
    print("Average difference between Prediction and Actual when wrong")
    print(averageMatrix)

    return averageMatrix

#  Helper Methods
# ----------------------------------------------------------------------------------------------------------------------

# Helper function for generating file names
def generateIdentifier(epoch, iteration):
    return f"|Epoch{epoch}|Iteration{iteration}.json"

# Get the number of results per class
def countResults(counter, actual):

    for i in range(len(classes)):
        count = actual.count(i)
        # print(f"{i}: {count}")
        counter[i] += count

# Helper function for getting the confusion matrix
def getConfusionInputs(results):
    pred = []
    actual = []

    for result in results[0]["Predictions"]:

        pred.append(np.argmax(result['Probabilities']))

        actual.append(result["Answer"])

    return pred, actual

# Get a list of every prediction that was wrong
def getIncorectPredictions(results):

    closeCalls = []
    numClass = len(classes)

    for result in results:

        prediction = np.argmax(result['Probabilities'])
        actual = result["Answer"]
        otherOrdering = []
        others = []

        for i in range(numClass):
            if i != prediction and i != actual:
                otherOrdering.append(i)
                others.append(result['Probabilities'][i])


        if prediction != actual:
            data = {
                "actual": actual,
                "prediction": prediction,
                "probAct": result['Probabilities'][actual],
                "probPred": result['Probabilities'][prediction],
                "otherOrdering": otherOrdering,
                "otherProb": others

            }
            closeCalls.append(data)

    return closeCalls


if __name__ == '__main__':
    main()

