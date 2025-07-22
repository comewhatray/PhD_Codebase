import os

from Utilities import ComeWhatRayUtil as CWR
from statsmodels.stats.contingency_tables import mcnemar


def main():
    epoch = 99
    approach1Summary = mcNemarPrep("ExperimentResults/Experiment13/results", epoch)
    approach2Summary = mcNemarPrep("ExperimentResults/Experiment14/results", epoch)
    rightWrongRatio(approach1Summary)
    rightWrongRatio(approach2Summary)

    resultsTable = mcNemarTest(approach1Summary, approach2Summary)
    print(resultsTable)

    print(mcnemar(resultsTable, exact=False))





def mcNemarTest(approach1, approach2):

    bothRight = 0
    bothWrong = 0
    oneRight = 0
    twoRight = 0

    for i in range(len(approach1)):
        oneComp = approach1[i]
        twoComp = approach2[i]

        if isCorrect(oneComp) and isCorrect(twoComp):
            bothRight += 1

        elif not isCorrect(oneComp) and not isCorrect(twoComp):
            bothWrong += 1

        elif isCorrect(oneComp) and not isCorrect(twoComp):
            oneRight += 1

        elif isCorrect(twoComp) and not isCorrect(oneComp):
            twoRight += 1

    results = [[bothRight, oneRight], [twoRight, bothWrong]]



    return results

def isCorrect(itteration):

    if itteration[0] == itteration[1]:
        return True
    else:
        return False

def rightWrongRatio(summaryList):
    correctCount = 0
    wrongCount = 0
    for result in summaryList:
        if isCorrect(result):
            correctCount += 1
        else:
            wrongCount += 1

    print(f"right/wrong: {correctCount}/{wrongCount}")

def mcNemarPrep(approachLocation, epoch):

    summary = []
    for filename in os.listdir(approachLocation):
        results = CWR.openFile(os.path.join(approachLocation, filename))
        for result in results["TestStage"][epoch]:
            answer = result["Answer"][0]
            resultProbs = result["Probabilities"][0]
            guess = resultProbs.index(max(resultProbs))

            summary.append([answer, guess])


    return summary


main()