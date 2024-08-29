from Utilities import ComeWhatRayUtil as CWR
from sklearn.feature_extraction import DictVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.metrics.pairwise import cosine_similarity
import sys
import numpy as np


options = {
    "method": "CosineSimilarity",
    "weightingScheme": None
}

this_module = sys.modules[__name__]

def similarityCalculation(dataset, inputOptions):
    print("Calculating Cosine Similarity")
    CWR.updateOldDictionaryEntriesWithNewDictionaryEntries(options, inputOptions)

    methodInstanciated = getattr(this_module, options['method'])

    return methodInstanciated(dataset)




def CosineSimilarity(dataset):
    sparseMatrix = vectorizeDataset(dataset)
    symMatrix = cosine_similarity(sparseMatrix)
    return symMatrix
    # print(symMatrix)
    # toVisualiseSymMatrix(symMatrix, details)
    # avgSymMatrix = generateAverageSimilarityMatrix(symMatrix, details)
    # toVisualiseAverageSymMatrix(avgSymMatrix, details)

    # workspace = details["ExperimentDirectories"]["SimilarityWorkspace"]
    # CWR.saveFile(workspace + "/experimentDetails.json", details)


# def CosineWithTFIDFSimilarity(dataset, details):
#     sparseMatrix = TFIDFTransformDataset(dataset)
#     symMatrix = cosine_similarity(sparseMatrix)
#     # toVisualiseSymMatrix(symMatrix, details)
#     # avgSymMatrix = generateAverageSimilarityMatrix(symMatrix, details)
#     # toVisualiseAverageSymMatrix(avgSymMatrix, details)
#
#     workspace = details["ExperimentDirectories"]["SimilarityWorkspace"]
#     CWR.saveFile(workspace + "/experimentDetails.json", details)

def averageCosineSimilarity(dataset):
    cosineDataset = cosine_similarity(dataset)
    return generateAverageSimilarityMatrix(symMatrix, details)


# Weighting Schemes
# ----------------------------------------------------------------------------------------------------------------------

# TF-IDF Weighting
def TFIDFTransformation(sparseMatrix):

    tfidf_transformer = TfidfTransformer()
    tfidf_transformer.fit(sparseMatrix)
    tf_idf_matrix = tfidf_transformer.transform(sparseMatrix)

    return tf_idf_matrix


# Helper Functions
# ----------------------------------------------------------------------------------------------------------------------

# Turns the data I have into a sparse matrix
def vectorizeDataset(dataset):

    print("TODO: THIS FUNCTION MAY BE SLOW WITH TOO MANY FILES")

    vectorizer = DictVectorizer(sparse=True)

    filePatternCollection = []

    for work in dataset:
        patterns = CWR.openFile(work["Location"])

        filePatternCollection.append(patterns)

    sparseMatrix = vectorizer.fit_transform(filePatternCollection)

    if options["weightingScheme"] is not None:
        weightingScheme = getattr(this_module, options['weightingScheme'])
        sparseMatrix = weightingScheme(sparseMatrix)

    return sparseMatrix

def generateAverageSimilarityMatrix(symMatrix, plotDetails):
    labels = [label["Label"] for label in plotDetails["Dataset"]["Files"]]

    uniqueLabels = list(dict.fromkeys(labels))
    groupingCount = [labels.count(x) for x in uniqueLabels]

    print(groupingCount)

    uniqueCount = []
    total = 0

    for x in range(0, len(uniqueLabels)):
        total += groupingCount[x]
        uniqueCount.append(total)

    print(uniqueCount)

    avgMatrix = np.zeros((len(groupingCount), len(groupingCount)))

    previousXcount = 0

    for xContainer in range(len(uniqueCount)):
        previousYcount = 0
        for yContainer in range(len(uniqueCount)):

            print("X Container: " + str(xContainer))
            print("Y Container: " + str(yContainer))

            for xValue in range(previousXcount, uniqueCount[xContainer]):
                for yValue in range(previousYcount, uniqueCount[yContainer]):
                    symMatrix[yValue, xValue] = symMatrix[xValue, yValue]
                    avgMatrix[xContainer, yContainer] += symMatrix[xValue, yValue]

            avgMatrix[xContainer, yContainer] /= (groupingCount[xContainer] * groupingCount[yContainer])

            print(avgMatrix[xContainer, yContainer])

            previousYcount = uniqueCount[yContainer]
            print("Previous y: " + str(previousYcount))
        previousXcount = uniqueCount[xContainer]
        print("Previous x: " + str(previousXcount))

    return avgMatrix