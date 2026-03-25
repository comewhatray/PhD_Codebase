import os

from Utilities import ComeWhatRayUtil as CWR
from statsmodels.stats.contingency_tables import mcnemar

# Kyna Comparisons
filesLocationNew = "Experiment3Results/analysis/Kyna"
filesLocationOld = "Experiment3Results/analysis/KynaDefault"

#Szeto Comparisons

filesLocationOld = "Experiment3ResultsBackups/analysis/Szeto"

# NoteDiff Comparisons

filesLocationNew = "Experiment3Results/analysis/KynaOldUnbalanced"
filesLocationOld = "Experiment3Results/analysis/KynaDefaultOldUnbalanced"

# Szeto Old Comparison on blanced data
# filesLocationOld = "Experiment3Results/analysis/SzetoOld"
# filesLocationNew = "Experiment3Results/analysis/SzetoDefaultOld"

# filesLocationOld = "Experiment3Results/analysis/SzetoOldUnbalanced"
# filesLocationNew = "Experiment3Results/analysis/SzetoDefaultOldUnbalanced"

numIterations = 3
epoch = 99

def main():

    approach1Summary = mcNemarPrep(filesLocationNew, epoch)
    approach2Summary = mcNemarPrep(filesLocationOld, epoch)
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
    for iteration in range(numIterations):
        location = os.path.join(approachLocation, constructName(iteration, epoch))
        results = CWR.openFile(location)
        for result in results["TestStage"][0]["Predictions"]:
            answer = result["Answer"]
            resultProbs = result["Probabilities"]
            guess = resultProbs.index(max(resultProbs))

            summary.append([answer, guess])


    return summary

def constructName(iteration, epoch):


    return f"|Epoch{epoch}|Iteration{iteration}.json"


main()