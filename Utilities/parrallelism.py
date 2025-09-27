from Code_Stages import ExperimentProcess as EP
from concurrent.futures import ProcessPoolExecutor
import multiprocessing as mp
from Utilities import ComeWhatRayUtil as CWR

maxWorkers = 25

def threadedAnalysis(allQuery, allData, config):

    global progress_counter, total_comparisons

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

    progress_counter = mp.Value('i', 0)
    total_comparisons = len(comparison_args)



    with ProcessPoolExecutor(max_workers=maxWorkers) as executor:
        results = list(executor.map(singleComparison, comparison_args))

    print(f"Completed all {total_comparisons} comparisons!")


def singleComparison(args):

    query = args[0]
    datum = args[1]
    config = args[2]

    EP.queryAggregationExperiment(query, datum, config)

    with progress_counter.get_lock():
        progress_counter.value += 1
        current = progress_counter.value

        # Print progress every 1 completions (adjust frequency as needed)
        if current % 100 == 0:
            percentage = (current / total_comparisons) * 1
            print(CWR.extraLargeSpacer)
            print(f"Completed {current}/{total_comparisons} ({percentage:.1f}%)")
            print(CWR.extraLargeSpacer)

