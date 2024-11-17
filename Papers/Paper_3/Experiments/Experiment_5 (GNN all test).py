import os

from Utilities import ComeWhatRayUtil as CWR
from Code_Stages import ExperimentProcess as EP
from torch_geometric.nn import GCNConv, Linear, global_add_pool, SAGEConv, SumAggregation, global_mean_pool, global_max_pool, max_pool, avg_pool
import torch.nn.functional as F
from torch_geometric.loader import DataLoader
from tabulate import tabulate


import os.path as osp

import torch
from torch_geometric.data import Dataset, download_url

ExperimentDetails = {
    # Experiment Name left blank is just for experiments we don't want to store the results of
    # "ExperimentName": "GNN All Preperation",
    "Description": "Initial exploration of GNN learning for paper 3",
    "WorkspaceLocation": "Papers/Paper_3/Experiments/ExperimentsWorkspace",
    # "Dataset_Configuration": "Papers/Paper_3/Datasets/ClassicalComposersDataset/Configurations/3x3_Sample.json",
    "Dataset_Configuration": "Papers/Paper_3/Datasets/ClassicalComposersDataset/Configurations/All.json",
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
                "function": "graphClassificationUsingEdgeInformation",
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
        super().__init__(root, transform, pre_transform, pre_filter)
        # self.configuration = CWR.openFile(CWR.appendDirectory(self.raw_dir, configurationLocation))


    @property
    def raw_file_names(self):
        return self.configurationLocation

    # If the files presented here are found, we do not need to run the process function
    @property
    def processed_file_names(self):
        if self.configuration is None:
            self.configuration = CWR.openFile(CWR.appendDirectory(self.raw_dir, self.raw_file_names))

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
        self.processGuide["Dataset_Configuration"] = CWR.appendDirectory(self.raw_dir, self.raw_file_names)
        details = EP.batchExperiment(ExperimentDetails)

        aggregationDetails["Stages"][0]["options"]["saveLocation"] = self.processed_dir
        EP.aggregationExperiment(details, aggregationDetails)

    # How much data we have
    def len(self):
        return len(self.processed_file_names)

    # # How many classes there are
    # def num_classes(self):
    #     configuration = CWR.openFile(CWR.appendDirectory(self.raw_dir, self.raw_file_names))
    #     return len(configuration["Labels"])

    # get a specific piece of data
    def get(self, idx):
        # data = torch.load(osp.join(self.processed_dir, processedFileName))
        data = torch.load(osp.join(self.processed_dir, f'data_{idx}.pt'))
        return data


# class MidiGCN(torch.nn.Module):
#     # You get to specify what you need to use
#     def __init__(self, in_channels, hidden_channels, out_channels):
#         super(MidiGCN, self).__init__()
#         self.conv1 = GCNConv(in_channels, hidden_channels[0])
#         self.conv2 = GCNConv(hidden_channels[0], hidden_channels[1])
#         self.lin = Linear(hidden_channels[1], out_channels)
#
#     # This is what does the work
#     # You specify how to use what you defined above
#     def forward(self, x, edge_index, batch):
#         x = F.dropout(x, p=0.5, training=self.training)
#         x = self.conv1(x, edge_index).relu()
#         x = F.dropout(x, p=0.5, training=self.training)
#         x = self.conv2(x, edge_index).relu()
#
#         # This is an aggregation step to represent a whole graph as a single vector?
#         x = global_add_pool(x, batch)
#         x = self.lin(x)
#
#         return x


class GraphSAGE(torch.nn.Module):
    def __init__(self, in_dim, hidden_dim, out_dim, dropout=0.2):
        super().__init__()
        self.dropout = dropout
        self.conv1 = SAGEConv(in_dim, hidden_dim)
        self.conv2 = SAGEConv(hidden_dim, hidden_dim)
        self.conv3 = SAGEConv(hidden_dim, hidden_dim)
        self.lin = Linear(hidden_dim, out_dim)

    def forward(self, data):
        x = self.conv1(data.x, data.edge_index)
        # x = F.elu(x)
        x = F.relu(x)
        x = F.dropout(x, p=self.dropout)

        x = self.conv2(x, data.edge_index)
        # x = F.elu(x)
        x = F.relu(x)
        x = F.dropout(x, p=self.dropout)

        x = self.conv3(x, data.edge_index)
        # x = F.elu(x)
        x = F.relu(x)
        x = F.dropout(x, p=self.dropout)

        #Default
        # return
        #
        # x = torch.log_softmax(x, dim=-1)

        # x = x.mean(dim=1)

        # x = max

        # Attempt 1
        x = self.lin(x)
        # x = F.softmax(x, dim=0)
        x = F.softmax(x, dim=-1)

        x = x.mean(dim=0)

        # Attempt 2

        return x


def train(train_loader):
    model.train()

    totalLoss = 0
    dataCount = 0
    for data in train_loader:
        # if dataCount % 4 == 0:
        #     print(f"Sanity Check: {dataCount}")

        data = data.to(device)
        optimiser.zero_grad()

        out = model(data)
        desiredOutput = torch.zeros(train_loader.num_classes)
        desiredOutput[data.y] = 1
        loss = F.cross_entropy(out, desiredOutput)
        loss.backward()
        optimiser.step()
        totalLoss += float(loss) * train_loader.len()
        dataCount += 1

    return float(totalLoss / len(train_loader))

@torch.no_grad()
def test(loader):
    model.eval()
    total_correct = 0

    for data in loader:
        data = data.to(device)
        out = model(data)
        pred = out.argmax()

        if torch.eq(pred, data.y):
            total_correct += 1
        # total_correct +=

    return round(total_correct / len(loader), 4)
    #
    # accs = []
    #
    # return accs





if __name__ == '__main__':

    rawConfiguration = "All.json"
    fileRoot = "Papers/Paper_3/Datasets/ClassicalComposersDataset/MidiTensors"
    # fileRoot = ExperimentDetails["WorkspaceLocation"]
    CWR.ensureDirectory(fileRoot)
    trainTestSplit = .8
    hiddenLayers = 300
    learn = True
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    dataset = MidiDataset(fileRoot, rawConfiguration, ExperimentDetails)

    dataSplit = int(dataset.len() * trainTestSplit)

    print(dataset.get_summary())
    dataset = dataset.shuffle()
    # print(dataset[0])
    # print(dataset[0])
    print(dataset.num_classes)
    model = GraphSAGE(dataset.num_features, hiddenLayers ,dataset.num_classes).to(device)
    optimiser = torch.optim.Adam(model.parameters(), lr=0.001)

    print(model)

    # split_idx = dataset.get_idx_split()
    # print(split_idx)


    # todo need to randomise the dataset

    # Batch size is by default 1
    # train_loader = DataLoader(dataset[:testTrainRation], shuffle=True)
    # test_loader = DataLoader(dataset[testTrainRation:], shuffle=True)

    trainSplit = dataset[:dataSplit]
    testSplit = dataset[dataSplit:]

    for x in range(len(trainSplit)):
        print(x)

    epochs = 51
    times = []
    if learn:
        print(CWR.largeSpacer)
        for epoch in range(epochs):

            print(f"Epoch: {epoch}")


            train(trainSplit)

            train_acc= test(trainSplit)
            test_acc = test(testSplit)

            print(f"{epoch=} | {train_acc=} | {test_acc=}")

            print(CWR.largeSpacer)

            if epoch % 10 == 0:
                times.append([epoch, train_acc, test_acc])

    for stamp in times:
        print(f"Epoch: {stamp[0]} | Train Accuracy: {stamp[1]} | Test Accuracy: {stamp[2]}")


        # loss = train(data)
        # result = test(data, evaluator)
        # logger.add_result(run, result)
        # if epoch % 10 == 0:
        #     train_acc, valid_acc, test_acc = result
        #     print(f'Epoch: {epoch}/{epochs}, '
        #           f'Loss: {loss:.4f}, '
        #           f'Train: {100 * train_acc:.2f}%, '
        #           f'Valid: {100 * valid_acc:.2f}% '
        #           f'Test: {100 * test_acc:.2f}%')



    # print(dataset.get(0))
    # print(dataset.shuffle())
    # print(dataset.get(0))
    # test = dataset.shuffle()



    # for i in range(5):
    #     print(test.get(i))


    # print(test.get(0))
