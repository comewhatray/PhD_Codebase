import os

from Utilities import ComeWhatRayUtil as CWR
from Code_Stages import ExperimentProcess as EP
from torch_geometric.nn import GCNConv


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
        {
            "file": "Code_Stages/1:MIDI_Representations/TensorRespresentation.py",
            "options": {
                "function": "edgeToNodeTensorEncoding",
                "saveType": ".pt",
                "edgeAttributes": True
            }
        },
    ]
}


class MidiDataset(Dataset):
    def __init__(self, root, configuration, processGuide, transform=None, pre_transform=None, pre_filter=None):
        self.configuration = configuration
        self.processGuide = processGuide
        super().__init__(root, transform, pre_transform, pre_filter)


    @property
    def raw_file_names(self):
        return self.configuration

    # If the files presented here are found, we do not need to run the process function
    @property
    def processed_file_names(self):
        configuration = CWR.openFile(CWR.appendDirectory(self.raw_dir, self.raw_file_names))
        dataTotal = 0
        for Label in configuration["Labels"]:
            dataTotal += len(configuration["Labels"][Label])

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
        EP.batchExperiment(ExperimentDetails)

        # aggregationDetails["Stages"][0]["options"]["saveLocation"] = self.processed_dir
        # EP.aggregationExperiment(details, aggregationDetails)

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


class MidiGNN(torch.nn.Module):
    def __init__(self, in_channels, hidden_channels, out_channels):
        super(MidiGNN, self).__init__()
        self.conv1 = GCNConv(in_channels, hidden_channels)
        self.conv2 = GCNConv(hidden_channels, out_channels)

    def forward(self, x, edge_index):
        x = self.conv1(x, edge_index).relu()
        x = self.conv2(x, edge_index)
        return x

    def message(self, edge_index, edge_weight):
        return



if __name__ == '__main__':

    rawConfiguration = "All.json"
    fileRoot = "Papers/Paper_3/Datasets/ClassicalComposersDataset/MidiTensors"
    hiddenLayers = 16

    dataset = MidiDataset(fileRoot, rawConfiguration, ExperimentDetails)

    model = MidiGNN(dataset.num_features, hiddenLayers ,dataset.num_classes)

    print(dataset.get(0))
