
from Utilities import ComeWhatRayUtil as CWR
from Utilities import datasetManagment as DM
from Code_Stages import ExperimentProcess as EP
from torch_geometric.nn import GCNConv, Linear, global_add_pool, SAGEConv, SumAggregation, global_mean_pool, global_max_pool, max_pool, avg_pool
import torch.nn.functional as F
from torch_geometric.loader import DataLoader
from tabulate import tabulate
import os

import torch
from torch_geometric.data import Dataset, download_url

ExperimentDetails = {
    # Experiment Name left blank is just for experiments we don't want to store the results of
    "ExperimentName": "Giant5Test",
    "ExperimentSignifier": "",
    "Description": "Initial exploration of GNN learning for paper 3",
    "WorkspaceLocation": "Papers/Paper_3/Experiments/ExperimentsWorkspace",
    "Dataset_Configuration": "GiantMidiDataset/subsets/configurations/5ComposersComparison.json",
    # "Dataset_Configuration": "Papers/Paper_3/Datasets/ClassicalComposersDataset/Configurations/All.json",
    "Stages": [
        # First Extract the midi file into points
        {
            "file": "Code_Stages/0:MIDI_Interface/MIDI_Extraction.py",
            "options": {
                "function": "convertMidiToPoints",
                "saveType": ".json",
            }
        },
        # Then transform it into a more usable representation
        {
            "file": "Code_Stages/1:MIDI_Representations/ProximityGraphRepresentation.py",
            "options": {
                "function": "SzetoGraphRepresentation",
                "saveType": ".gpickle",
                "edgeAttributes": True
            }
        },
        # Transform Again
        # TODO fix this up
        # {
        #     "file": "Code_Stages/1:MIDI_Representations/TensorRespresentation.py",
        #     "options": {
        #         "function": "edgeToNodeTensorEncoding",
        #         "saveType": ".pt",
        #         "edgeAttributes": True
        #     }
        # },
    ]
}

aggregationDetails = {
    "Stages": [
        {
            "file": "Code_Stages/4:Tasks/Classification/GNN.py",
            "options": {
                "function": "graphClassificationUsingNodeInformation",
                # "saveType": "",
                "saveLocation": None
            }
        }
    ]
}


class MidiDataset(Dataset):
    def __init__(self, root, configurationLocation, processGuide, transform=None, pre_transform=None, pre_filter=None):
        self.configurationLocation = configurationLocation
        self.processGuide = processGuide
        self.configuration = None
        self.customOrdering = None
        super().__init__(root, transform, pre_transform, pre_filter)

    @property
    def raw_file_names(self):
        return self.configurationLocation

    # If the files presented here are found, we do not need to run the process function
    @property
    def processed_file_names(self):
        self.openConfig()

        dataTotal = 0
        for Label in self.configuration["Labels"]:
            dataTotal += len(self.configuration["Labels"][Label])

        return [f'data_{i}.pt' for i in range(dataTotal)]

    # Not needed for my purpose
    def download(self):
        # Download to `self.raw_dir`.
        # path = download_url(url, self.raw_dir)
        pass

    # The process we should follow to turn data into something uselfull for the gnn
    def process(self):
        # ExperimentDetails
        self.processGuide["ExperimentDetails"]["Dataset_Configuration"] = CWR.appendDirectory(self.raw_dir, self.raw_file_names)
        details = EP.batchExperiment(self.processGuide["ExperimentDetails"])

        self.processGuide["AggregationDetails"]["Stages"][0]["options"]["saveLocation"] = self.processed_dir
        EP.aggregationExperiment(details, self.processGuide["AggregationDetails"])

    # How much data we have
    def len(self):
        return len(self.processed_file_names)

    # get a specific piece of data
    def get(self, idx):
        # data = torch.load(osp.join(self.processed_dir, processedFileName))
        if self.customOrdering is not None:
            idx = self.customOrdering[idx]

        data = torch.load(os.path.join(self.processed_dir, f'data_{idx}.pt'))
        return data

    # Method to stop constantly opening the configuration file
    def openConfig(self):
        if self.configuration is None:
            self.configuration = CWR.openFile(CWR.appendDirectory(self.raw_dir, self.raw_file_names))

    def customOrdering(self, ordering):
        self.customOrdering = ordering



class GraphSAGE(torch.nn.Module):
    def __init__(self, in_dim, hidden_dim, out_dim, dropout=0.2):
        super().__init__()
        # All the Layers
        self.dropout = dropout
        self.conv1 = SAGEConv(in_dim, hidden_dim)
        self.conv2 = SAGEConv(hidden_dim, hidden_dim)
        self.conv3 = SAGEConv(hidden_dim, hidden_dim)
        self.lin = Linear(hidden_dim, out_dim)

    def forward(self, data, batch=None):
        #What happens at each processing of data
        #

        # Input Layer
        # --------------------------------------------------------------------------------
        # Stage 1
        # ----------------------------------------
        x = self.conv1(data.x, data.edge_index)
        # x = F.elu(x)
        x = F.relu(x)
        x = F.dropout(x, p=self.dropout)

        # HIDDEN LAYERS
        # --------------------------------------------------------------------------------
        # Stage 2
        # ----------------------------------------
        x = self.conv2(x, data.edge_index)
        # x = F.elu(x)
        x = F.relu(x)
        x = F.dropout(x, p=self.dropout)

        # Stage 3
        # ----------------------------------------
        x = self.conv3(x, data.edge_index)
        # x = F.elu(x)
        x = F.relu(x)
        # x = F.dropout(x, p=self.dropout)

        #Default
        # return
        #
        # x = torch.log_softmax(x, dim=-1)

        # x = x.mean(dim=1)

        # x = max

        # Batching stage
        # ----------------------------------------
        if batch is not None:
            x = global_mean_pool(x, batch)

        # Output LAYER
        # --------------------------------------------------------------------------------
        # Get output
        #----------------------------------------
        # Attempt 1
        x = F.dropout(x, p=self.dropout)
        x = self.lin(x)
        # x = F.softmax(x, dim=0)
        # x = F.softmax(x, dim=-1)

        # x = x.mean(dim=0)

        # Attempt 2

        return x



def train(train_loader, logging):
    model.train()

    totalLoss = 0
    dataCount = 0
    for data in train_loader:
        # if dataCount % 4 == 0:
        #     print(f"Sanity Check: {dataCount}")

        data = data.to(device)
        optimiser.zero_grad()

        # out = model(data)
        out = model(data, data.batch)

        logging.append({
            "Probabilities": out.tolist(),
            "Answer": data.y.tolist()
        })

        # desiredOutput = torch.zeros(train_loader.num_classes)
        # desiredOutput[data.y] = 1
        # loss = F.cross_entropy(out, desiredOutput)
        loss = F.cross_entropy(out, data.y)
        loss.backward()
        optimiser.step()
        # totalLoss += float(loss) * train_loader.len()
        dataCount += 1

    # return float(totalLoss / len(train_loader))

@torch.no_grad()
def test(loader, logging):
    model.eval()
    # total_correct = 0
    #
    # for data in loader:
    #     data = data.to(device)
    #     out = model(data)
    #     pred = out.argmax()
    #
    #     if torch.eq(pred, data.y):
    #         total_correct += 1

    # return round(total_correct / len(loader), 4)

    correct = 0
    for data in loader:  # Iterate in batches over the training/test dataset.
        out = model(data, data.batch)
        logging.append({
            "Probabilities": out.tolist(),
            "Answer": data.y.tolist()
        })
        pred = out.argmax(dim=1)  # Use the class with highest probability.
        correct += int((pred == data.y).sum())  # Check against ground-truth labels.
    return round(correct / len(loader.dataset), 4)








if __name__ == '__main__':

    # Configuration Data
    epochs = 100
    trainTestSplit = .7
    hiddenLayers = 75
    learn = True
    batchSize = 1 # None or size of batch

    # What device to process stuff
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    experimentLocation = "ExperimentResults/Experiment14/"
    resultsLocation = experimentLocation + "results/"
    modelLocation = experimentLocation + "model/"
    permutationDatasetLocation = "Papers/Paper_3/Experiments/ExperimentsWorkspace/DatasetPermutations"

    CWR.ensureDirectory(resultsLocation)
    CWR.ensureDirectory(modelLocation)
    resultsCount = len(os.listdir(resultsLocation))
    modelCount = len(os.listdir(modelLocation))




    # Dataset Code
    fileRoot, rawConfiguration = DM.GNNStructureCreation(ExperimentDetails)
    processLists = {
        "ExperimentDetails": ExperimentDetails,
        "AggregationDetails": aggregationDetails
    }
    dataset = MidiDataset(fileRoot, rawConfiguration, processLists)
    dataSplit = int(len(dataset) * trainTestSplit)
    print(dataset.get_summary())
    # dataset = dataset.shuffle()

    orderingObject = CWR.openFile(os.path.join(permutationDatasetLocation, f'Perm{resultsCount}.json'))
    dataset.customOrdering = orderingObject["ordering"]
    #
    # print(f"Number of Classes: {dataset.num_classes}")
    #
    model = GraphSAGE(dataset.num_features, hiddenLayers ,dataset.num_classes).to(device)
    optimiser = torch.optim.Adam(model.parameters(), lr=0.001)
    print(model)

    trainSplit = dataset[:dataSplit]
    testSplit = dataset[dataSplit:]

    # torch.save(trainSplit, os.path.join(fileRoot, 'trainPerm0.pt'))
    # torch.save(testSplit, os.path.join(fileRoot, 'testPerm0.pt'))

    # trainSplit = torch.load(os.path.join(permutationDatasetLocation, f'trainPerm{resultsCount}.pt'))
    # testSplit = torch.load(os.path.join(permutationDatasetLocation, f'testPerm{resultsCount}.pt'))

    if batchSize is not None:
        trainSplit = DataLoader(trainSplit, batch_size=batchSize, shuffle=True)
        testSplit = DataLoader(testSplit, batch_size=batchSize, shuffle=True)


    times = []

    analysis = {
        "TrainingStage": [],
        "TrainingTest": [],
        "TestStage": []
    }

    if learn:
        print(CWR.largeSpacer)
        for epoch in range(epochs + 1):

            print(f"Epoch: {epoch}")
            trainStageLog = []
            trainTestStageLog = []
            testStageLog = []


            train(trainSplit, trainStageLog)

            train_acc = test(trainSplit, trainTestStageLog)
            test_acc = test(testSplit, testStageLog)

            analysis["TrainingStage"].append(trainStageLog)
            analysis["TrainingTest"].append(trainTestStageLog)
            analysis["TestStage"].append(testStageLog)

            print(f"{epoch=} | {train_acc=} | {test_acc=}")

            print(CWR.largeSpacer)

            if epoch % 10 == 0:
                times.append([epoch, train_acc, test_acc])

    for stamp in times:
        print(f"Epoch: {stamp[0]} | Train Accuracy: {stamp[1]} | Test Accuracy: {stamp[2]}")


    resultsLocation += f"ExperimentResults{resultsCount}.json"
    modelLocation += f"newModel{modelCount}.pt"

    CWR.saveFile(resultsLocation, analysis)
    torch.save(model.state_dict(), modelLocation)
