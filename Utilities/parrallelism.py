from networkx.algorithms.core import core_number

from Code_Stages import ExperimentProcess as EP
# from concurrent.futures import ProcessPoolExecutor
from parallelbar import progress_map


maxWorkers = 24


def singleComparison(args):
    query = args[0]
    datum = args[1]
    config = args[2]

    EP.queryAggregationExperiment(query, datum, config)

def threadedAnalysis(allQuery, allData, config):

    query_keys = [k for k in allQuery.keys() if k != 'directory']
    dataset_keys = [k for k in allData.keys() if k != 'directory']

    queryLabelList = []
    # Getting all the queries for an individual label
    for label in allQuery['Initial']:

        singleQuery = {
            'directory': allQuery['directory']
        }

        for query_key in query_keys:
            singleQuery[query_key] = {label: allQuery[query_key][label]}

        queryLabelList.append(singleQuery)

    # Getting all data for each label
    datasetLabelList = []
    for label in allData['Initial']:

        singleData = {
            'directory': allData['directory']
        }

        for query_key in dataset_keys:
            singleData[query_key] = {label: allData[query_key][label]}

        datasetLabelList.append(singleData)

    comparison_args = []

    for query in queryLabelList:
        for data in datasetLabelList:
            comparisonData = (query, data, config)
            comparison_args.append(comparisonData)

    # For running the program without showing a progress bar
    # with ProcessPoolExecutor(max_workers=maxWorkers) as executor:
    #     results = list(executor.map(singleComparison, comparison_args))

    # For running a program while running showing a progress bar
    results = progress_map(singleComparison, comparison_args, n_cpu=maxWorkers, chunk_size=1)


    print(f"Completed all comparisons!")




