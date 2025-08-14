from Utilities import ComeWhatRayUtil as CWR

# Comparison at 100 epochs | Time: 9763.408041905612 | Accuracy: 0.5725490196078431
# resultsLocation = "ExperimentResults/Experiment14/results/ExperimentResults5.json"

# Comparison at 700 Epochs | Time: 65034.81740236655 | Accuracy: 0.6471
# resultsLocation = "ExperimentResults/Experiment14/ExperimentResults5(700).json"

# Custom at 100 Epochs | Time: 59948.63273018412 | Accuracy:
resultsLocation = "ExperimentResults/Experiment13/results/ExperimentResults5.json"


epoch = 99
# epoch = 699

def main():

    correct = 0
    incorrect = 0

    results = CWR.openFile(resultsLocation)

    resultEpoch = results["TestStage"][epoch]

    for result in resultEpoch:
        answer = result["Answer"][0]
        resultProbs = result["Probabilities"][0]
        guess = resultProbs.index(max(resultProbs))

        if answer == guess:
            correct += 1
        else:
            incorrect += 1

    accuracy = correct / len(resultEpoch)

    print(f"Accuracy: {accuracy}")


    return

main()