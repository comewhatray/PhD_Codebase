from Utilities import ComeWhatRayUtil as CWR
from Utilities import datasetManagment as DM
from Code_Stages import ExperimentProcess as EP

import os
import time

import mlx.core as mx
from mlx_graphs.loaders import Dataloader
from mlx_graphs.datasets import Dataset
from mlx_graphs.nn.linear import Linear
from mlx_graphs.nn.message_passing import MessagePassing
from mlx_graphs.nn import SAGEConv


class MidiDataset(Dataset):
    def __init__(self, root, configurationLocation, processGuide, transform=None, pre_transform=None, pre_filter=None):
        self.configurationLocation = configurationLocation
        self.processGuide = processGuide
        self.configuration = None
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
        print(self.raw_dir)
        print(self.raw_file_names)
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
        data = torch.load(os.path.join(self.processed_dir, f'data_{idx}.pt'), weights_only=False)
        return data

    # Method to stop constantly opening the configuration file
    def openConfig(self):
        if self.configuration is None:
            self.configuration = CWR.openFile(CWR.appendDirectory(self.raw_dir, self.raw_file_names))