from Utilities import ComeWhatRayUtil as CWR
import os
import numpy as np
from sklearn.metrics import confusion_matrix
import matplotlib.pyplot as plt

directory = "Experiment3Results/analysis"
startItteration = 0
numIterations = 3
epoch = 2999
# hotEncodingsLocation = "AriaHotEncodings.json"
hotEncodingsLocation = "GiantMidiHotEncodings.json"


# experimentNames = [
#     # "Kyna",
#     # "KynaDefault",
#     # "Szeto",
#     "SzetoDefault",
# ]
#
# classes = [
#     "baroque",
#     "classical",
#     "romantic",
#     "impressionist",
#     "contemporary",
#     "modern"
# ]

experimentNames = [
    # "KynaOld",
    # "KynaDefaultOld",
    # "SzetoOld",
    # "SzetoDefaultOld",
    # "KynaOldUnbalanced",
    # "KynaDefaultOldUnbalanced",
    # "SzetoOldUnbalanced",
    # "SzetoDefaultOldUnbalanced",
    "KynaDefaultOldUnbalancedMoreTime",
    # "SzetoDefaultOldUnbalancedMoreTime"
]

classes = [
    "Chopin",
    "Liszt",
    "Schubert",
    "Scarlatti",
    "Bach"
]

def main():
    averageConfusionMatrix()
    # averageCloseCall()
    # accuracyList()
    # outLiars("Experiment3Results/analysis/SzetoDefault/|Epoch99|Iteration4.json")
#

def averageConfusionMatrix():
    encodings = CWR.openFile(hotEncodingsLocation, printDisplay=False)
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
    encodings = CWR.openFile(hotEncodingsLocation, printDisplay=False)

    titleString = "|"
    for encode in encodings.keys():
        titleString = titleString + encode + "|"

    for experiment in experimentNames:
        print(f"Close Call for {experiment}")

        dataCollection = []

        for i in range(startItteration, numIterations):
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

        closeCallTest(dataTransformation, printIncorect=True)


def accuracyList():
    encodings = CWR.openFile(hotEncodingsLocation, printDisplay=False)

    titleString = "|"
    for encode in encodings.keys():
        titleString = titleString + encode + "|"

    for experiment in experimentNames:
        for iteration in range(numIterations):
            correctnessStorage = []

            print(f"ITTERATION {iteration}-----------------------------------------")
            for eopch in range(epoch):
                identifier = generateIdentifier(eopch, iteration)

                experimentLocation = os.path.join(directory, experiment)
                dataLocation = os.path.join(experimentLocation, identifier)

                data = CWR.openFile(dataLocation, printDisplay=False)
                results = confusionMatrixTest(data, percentage=True)

                average_confusion = results

                averageCorrectness = 0
                for i in range(len(average_confusion)):
                    averageCorrectness = averageCorrectness + average_confusion[i][i]

                correctnessStorage.append(averageCorrectness/len(average_confusion))

            accuracies = correctnessStorage

            # Create epochs array (0 to len(accuracies)-1)
            epochs = list(range(len(accuracies)))

            # Create the plot
            plt.figure(figsize=(10, 6))
            plt.scatter(epochs, accuracies, s=30, color='#378ADD', alpha=0.8, edgecolors='darkblue', linewidth=1)

            # Customize the plot
            plt.xlabel('Epoch', fontsize=12, fontweight='500')
            plt.ylabel('Accuracy (%)', fontsize=12, fontweight='500')
            plt.title(f'{experiment}: Average Accuracy', fontsize=14, fontweight='bold', pad=15)

            # Add grid for better readability
            plt.grid(True, alpha=0.3, linestyle='-', linewidth=0.5)

            # Set y-axis to start from 0
            plt.ylim([0, max(accuracies) + 5])

            # Show every 5th tick (change 5 to whatever interval you want)
            plt.xticks(range(0, len(epochs), 25), fontsize=10)
            plt.yticks(fontsize=10)

            # Add some styling
            plt.tight_layout()

            # Save and show
            plt.savefig('accuracy_dot_plot.png', dpi=300, bbox_inches='tight')
            plt.show()


def outLiars(testFile):

    tempEncodings = CWR.openFile(hotEncodingsLocation)
    hotEncodings = {}
    for key, value in tempEncodings.items():
        hotEncodings[value] = key

    results = CWR.openFile(testFile)
    predictions = results["TestStage"][0]["Predictions"]

    probsWrong = []

    for prediction in predictions:
        probs = prediction["Probabilities"]
        predict = np.argmax(probs)
        if predict != prediction["Answer"]:
            prob = probs[np.argmax(probs)]
            probsWrong.append((prob, hotEncodings[predict], hotEncodings[prediction["Answer"]]))

    probsWrong.sort(reverse=True)
    # print(hotEncodings)
    print(probsWrong)



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

    tempResultsStore = []
    for result in results:
        if printIncorect:
            print(result)
        # averageMatrix[result['actual']][result['prediction']] += (result['probAct'] - result['probPred'])
        difference = result['probPred'] - result['probAct']
        percentDiff = difference * 100 / abs(result['probAct'])
        averageMatrix[result['prediction']][result['actual']] += percentDiff

        if percentDiff > 100000:
            print("pause")

        tempResultsStore.append((percentDiff, result['prediction'], result['actual']))

    tempResultsStore.sort(reverse=True)
    print(tempResultsStore)


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

