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
from mlx_graphs.nn import SAGEConv, global_add_pool, global_mean_pool, global_max_pool
import mlx.nn as F
import mlx.optimizers as optim

globalDevice = "mps"
fileSaveType = ".pt"

ExperimentDetails = {
    # Experiment Name left blank is just for experiments we don't want to store the results of
    "ExperimentName": "GNNExtension_experiment_1",
    "threading": True,
    "ExperimentSignifier": "",
    "Description": "Ensuring that everything is still working since I have a new computer",
    "WorkspaceLocation": "Papers/Paper_3/Extension/Workspace",
    "Dataset_Configuration": "GiantMidiDataset/subsets/configurations/5ComposersTest.json",
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
    "threading": False,
    "Stages": [
        {
            "file": "Code_Stages/4:Tasks/Classification/GNN.py",
            "options": {
                "function": "graphClassificationUsingEdgeInformation",
                "saveType": fileSaveType,
                "threading": False,
                "saveLocation": None,
                "saveIntermediate": None,
            }
        }
    ]
}


class MidiDataset(Dataset):
    def __init__(self, name, configurationLocation, processGuide):
        self.configurationLocation = configurationLocation
        self.processGuide = processGuide
        self.configuration = None
        super().__init__(name)

    @property
    def configName(self):
        return CWR.getFileNameFromPath(self.configurationLocation, includeExtension=True)

    # If the files presented here are found, we do not need to run the process function
    @property
    def processed_file_names(self):
        self.openConfig()

        dataTotal = 0
        for Label in self.configuration["Labels"]:
            dataTotal += len(self.configuration["Labels"][Label])

        return [f'data_{i}{fileSaveType}' for i in range(dataTotal)]

    # Not needed for my purpose
    def download(self):
        # Download to `self.raw_dir`.
        # path = download_url(url, self.raw_dir)

        CWR.moveFile(self.configurationLocation, os.path.join(self.raw_path, self.configName))
        pass

    # The process we should follow to turn data into something uselfull for the gnn
    def process(self):
        # ExperimentDetails
        # print(f"Raw Path: {self.raw_path}")

        # print(f"Raw FileNames: {self.configName}")
        self.processGuide["ExperimentDetails"]["Dataset_Configuration"] = CWR.appendDirectory(self.raw_path, self.configName)
        details = EP.batchExperiment(self.processGuide["ExperimentDetails"])

        self.processGuide["AggregationDetails"]["Stages"][0]["options"]["saveLocation"] = self.processed_path
        EP.aggregationExperiment(details, self.processGuide["AggregationDetails"])

    # How much data we have
    def __len__(self):
        return len(self.processed_file_names)

    # get a specific piece of data
    def get(self, idx):
        # data = torch.load(osp.join(self.processed_dir, processedFileName))
        data = CWR.openFile(os.path.join(self.processed_path, f'data_{idx}{fileSaveType}'))
        return data

    # Method to stop constantly opening the configuration file
    def openConfig(self):
        if self.configuration is None:
            self.configuration = CWR.openFile(CWR.appendDirectory(self.raw_dir, self.raw_file_names))


class GraphSAGE(MessagePassing):
    def __init__(self, in_dim, hidden_dim, out_dim, dropout=0.2, aggregation='mean'):
        super().__init__()
        self.dropout = dropout
        self.aggregation = aggregation

        # GraphSAGE layers
        self.conv1 = SAGEConv(in_dim, hidden_dim)
        self.conv2 = SAGEConv(hidden_dim, hidden_dim)
        self.conv3 = SAGEConv(hidden_dim, hidden_dim)

        # Final classifier
        self.lin = Linear(hidden_dim, out_dim)

    def forward(self, x, edge_index, batch=None):
        # First conv block
        x = self.conv1(x, edge_index)
        x = F.relu(x)
        # x = F.dropout(x, p=self.dropout, training=self.training)

        # Second conv block
        x = self.conv2(x, edge_index)
        x = F.relu(x)
        # x = F.dropout(x, p=self.dropout, training=self.training)

        # Third conv block
        x = self.conv3(x, edge_index)
        x = F.relu(x)

        # CRITICAL: Pool nodes to graph-level representation
        if batch is not None:
            # For batched graphs (REQUIRED for batch_size > 1)
            if self.aggregation == 'mean':
                x = global_mean_pool(x, batch)
            elif self.aggregation == 'max':
                x = global_max_pool(x, batch)
            elif self.aggregation == 'add':
                x = global_add_pool(x, batch)
        else:
            # For single graph (batch_size=1 or node classification)
            if self.aggregation == 'mean':
                x = x.mean(dim=0, keepdim=True)
            elif self.aggregation == 'max':
                x = x.max(dim=0)[0].unsqueeze(0)

        # Final dropout and linear layer
        # x = F.dropout(x, p=self.dropout, training=self.training)
        x = self.lin(x)

        return x  # Return raw logits (apply loss function separately)

def loss_fn(y_hat, y, parameters=None):
    return mx.mean(F.losses.cross_entropy(y_hat, y))

def forward_fn(model, graph, labels):
    y_hat = model(graph.edge_index, graph.node_features, graph.batch_indices)
    loss = loss_fn(y_hat, labels, model.parameters())
    return loss, y_hat



def train(train_loader):
    loss_sum = 0.0
    for graph in train_loader:

        (loss, y_hat), grads = loss_and_grad_fn(
            model=model,
            graph=graph,
            labels=graph.graph_labels,
        )
        optimizer.update(model, grads)
        mx.eval(model.parameters(), optimizer.state)
        loss_sum += loss.item()
    return loss_sum / len(train_loader.dataset)

def test(loader):
    acc = 0.0
    for graph in loader:
        y_hat = model(graph.edge_index, graph.node_features, graph.batch_indices)
        y_hat = y_hat.argmax(axis=1)
        acc += (y_hat == graph.graph_labels).sum().item()

    return acc / len(loader.dataset)

def epoch(train_loader, test_loader):
    loss = train(train_loader)
    train_acc = test(train_loader)
    test_acc = test(test_loader)
    return loss, train_acc, test_acc




if __name__ == '__main__':

    # Configuration Data
    epochs = 100
    trainTestSplit = .7
    hiddenLayers = 75
    learn = False
    batchSize = 64

    # Dataset Code
    processLists = {
        "ExperimentDetails": ExperimentDetails,
        "AggregationDetails": aggregationDetails
    }

    dataset = MidiDataset("MLXTEST", ExperimentDetails["Dataset_Configuration"], processLists)
    dataSplit = int(len(dataset) * trainTestSplit)
    print(dataset)
    dataset = dataset


    model = GraphSAGE(dataset.num_features, hiddenLayers ,dataset.num_classes)
    print(model)

    trainSplit = dataset[:dataSplit]
    testSplit = dataset[dataSplit:]

    if batchSize is not None:
        trainSplit = Dataloader(trainSplit, batch_size=batchSize, shuffle=True)
        testSplit = Dataloader(testSplit, batch_size=batchSize, shuffle=True)


    times = []

    analysis = {
        "TrainingStage": [],
        "TrainingTest": [],
        "TestStage": []
    }

    mx.eval(model.parameters())

    optimizer = optim.Adam(learning_rate=0.01)
    loss_and_grad_fn = F.value_and_grad(model, forward_fn)

    epochs = 30
    best_test_acc = 0.0

    if learn:
        print(CWR.largeSpacer)

        for e in range(epochs):
            loss, train_acc, test_acc = epoch(trainSplit, testSplit)
            best_test_acc = max(best_test_acc, test_acc)

            print(
                " | ".join(
                    [
                        f"Epoch: {e:3d}",
                        f"Train loss: {loss:.3f}",
                        f"Train acc: {train_acc:.3f}",
                        f"Test acc: {test_acc:.3f}",
                    ]
                )
            )
        print(f"\n==> Best test accuracy: {best_test_acc:.3f}")




