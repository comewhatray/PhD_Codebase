import os

from Utilities import ComeWhatRayUtil as CWR
from Code_Stages import ExperimentProcess as EP
from torch_geometric.nn import GCNConv, Linear, global_add_pool
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


class MidiGCN(torch.nn.Module):
    def __init__(self, in_channels, hidden_channels, out_channels):
        super(MidiGCN, self).__init__()
        self.conv1 = GCNConv(in_channels, hidden_channels[0])
        self.conv2 = GCNConv(hidden_channels[0], hidden_channels[1])
        self.lin = Linear(hidden_channels[1], out_channels)

    def forward(self, x, edge_index, batch):
        x = F.dropout(x, p=0.5, training=self.training)
        x = self.conv1(x, edge_index).relu()
        x = F.dropout(x, p=0.5, training=self.training)
        x = self.conv2(x, edge_index).relu()

        # This is an aggregation step to represent a whole graph as a single vector?
        x = global_add_pool(x, batch)
        x = self.lin(x)

        return x

    def message(self, edge_index, edge_weight):
        return


def train():
    model.train()

    totalLoss = 0
    dataCount = 0
    for data in train_loader:
        if dataCount % 25 == 0:
            print(f"Sanity Check: {dataCount}")
        data = data.to(device)
        optimiser.zero_grad()

        out = model(data.x, data.edge_index, data.batch)
        loss = F.cross_entropy(out, data.y)
        loss.backward()
        optimiser.step()
        totalLoss += float(loss) * data.num_graphs
        dataCount += 1

    return float(totalLoss / len(train_loader.dataset))

@torch.no_grad()
def test(loader):
    model.eval()
    total_correct = 0

    for data in loader:
        data = data.to(device)
        out = model(data.x, data.edge_index, data.batch)
        pred = out.argmax(dim=-1)
        total_correct += int((pred == data.y).sum())

    return total_correct / len(loader.dataset)

    accs = []

    return accs



if __name__ == '__main__':

    rawConfiguration = "All.json"
    fileRoot = "Papers/Paper_3/Datasets/ClassicalComposersDataset/MidiTensors"
    hiddenLayers = [300, 50]
    testTrainRation = 120
    learn = True
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    dataset = MidiDataset(fileRoot, rawConfiguration, ExperimentDetails)

    print(dataset.get_summary())
    dataset = dataset.shuffle()
    # print(dataset[0])
    # print(dataset[0])

    model = MidiGCN(dataset.num_features, hiddenLayers ,dataset.num_classes).to(device)



    optimiser = torch.optim.Adam(model.parameters(), lr=0.001)

    print(model)

    # todo need to randomise the dataset

    # Batch size is by default 1
    train_loader = DataLoader(dataset[:testTrainRation], shuffle=True)
    test_loader = DataLoader(dataset[testTrainRation:], shuffle=True)

    epochs = 51
    # times = []
    if learn:
        for epoch in range(epochs):
            print(f"Epoch: {epoch}")
            print(CWR.largeSpacer)

            loss = train()

            train_acc= test(train_loader)
            test_acc = test(test_loader)

            if epoch % 10 == 0:
                print(f"{epoch=} | {train_acc=} | {test_acc=}")



    # print(dataset.get(0))
    # print(dataset.shuffle())
    # print(dataset.get(0))
    # test = dataset.shuffle()



    # for i in range(5):
    #     print(test.get(i))


    # print(test.get(0))
