
from Utilities import ComeWhatRayUtil as CWR
from Utilities import datasetManagment as DM
from Code_Stages import ExperimentProcess as EP
from torch_geometric.nn import GCNConv, Linear, global_add_pool, SAGEConv, SumAggregation, global_mean_pool, global_max_pool, max_pool, avg_pool
import torch.nn.functional as F
from torch_geometric.loader import DataLoader
from tabulate import tabulate
import os
import time

import torch
from torch_geometric.data import Dataset, download_url

globalDevice = "mps"

# Specifications for transforming the dataset
ExperimentDetails = {
    # Experiment Name left blank is just for experiments we don't want to store the results of
    "ExperimentName": "preprocessingDataset",
    "threading": True,
    "ExperimentSignifier": "",
    "Description": "Ensuring that everything is still working since I have a new computer",
    "WorkspaceLocation": "Papers/Paper_3/Extension/Workspace",
    "Dataset_Configuration": "AriaDataset/configs/periodConfigTotal.json",
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
    ]
}

# Specifications for transforming the dataset
aggregationDetails = {
    "threading": False,
    "Stages": [
        {
            "file": "Code_Stages/4:Tasks/Classification/GNN.py",
            "options": {
                "function": "graphClassificationUsingEdgeInformation",
                # "saveType": "",
                "threading": True,
                "saveLocation": None,
                "saveIntermediate": None,
                "saveType": ".pt",
            }
        }
    ]
}

# Class for the dataset
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

# GNN construction
class GraphSAGE(torch.nn.Module):
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

        # self.conv1 = self.conv1.to('cpu')
        # self.conv2 = self.conv2.to('mps')
        # self.conv3 = self.conv3.to('mps')
        # self.lin = self.lin.to('mps')

    def forward(self, x, edge_index, batch=None):
        # First conv block
        x = self.conv1(x, edge_index)
        x = F.relu(x)
        x = F.dropout(x, p=self.dropout, training=self.training)

        # Second conv block
        x = self.conv2(x, edge_index)
        x = F.relu(x)
        x = F.dropout(x, p=self.dropout, training=self.training)

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
        x = F.dropout(x, p=self.dropout, training=self.training)
        x = self.lin(x)

        return x  # Return raw logits (apply loss function separately)

# Old train method
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

# Old test Method
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


# New train method
def train_epoch(model, loader, optimizer, device=globalDevice):

    print("Training...")
    model.train()
    total_loss = 0
    correct = 0
    total = 0

    for batch in loader:
        batch = batch.to(device)
        optimizer.zero_grad()

        # IMPORTANT: Pass batch.batch for proper batching
        out = model(batch.x, batch.edge_index, batch.batch)

        # Use appropriate loss
        if dataset.num_classes > 1:
            loss = F.cross_entropy(out, batch.y)
            pred = out.argmax(dim=1)
            correct += (pred == batch.y).sum().item()
        else:
            loss = F.mse_loss(out.squeeze(), batch.y.float())

        loss.backward()
        optimizer.step()

        total_loss += loss.item() * batch.num_graphs
        total += batch.num_graphs

    return total_loss / total, correct / total if dataset.num_classes > 1 else 0

# New test method
@torch.no_grad()
def validate(model, loader, device=globalDevice):
    print("Validating...")
    model.eval()
    total_loss = 0
    correct = 0
    total = 0

    for batch in loader:
        batch = batch.to(device)

        # Forward pass with batch
        out = model(batch.x, batch.edge_index, batch.batch)

        if dataset.num_classes > 1:
            loss = F.cross_entropy(out, batch.y)
            pred = out.argmax(dim=1)
            correct += (pred == batch.y).sum().item()
        else:
            loss = F.mse_loss(out.squeeze(), batch.y.float())

        total_loss += loss.item() * batch.num_graphs
        total += batch.num_graphs

    return total_loss / total, correct / total if dataset.num_classes > 1 else 0

# Finds the optimal batch size
def find_optimal_batch_size_graphsage(dataset, model):
    """Test different batch sizes for GraphSAGE"""

    test_batch_sizes = [8, 16, 32, 64]
    device = globalDevice  # or 'mps' if it works

    results = []
    for batch_size in test_batch_sizes:
        try:
            loader = DataLoader(
                dataset[:min(500, len(dataset))],  # Test subset
                batch_size=batch_size,
                shuffle=False,
                num_workers=0
            )

            model.eval()
            start = time.time()

            with torch.no_grad():
                for batch in loader:
                    batch = batch.to(device)
                    out = model(batch.x, batch.edge_index, batch.batch)

            elapsed = time.time() - start
            samples_per_sec = min(500, len(dataset)) / elapsed

            print(f"Batch size {batch_size:3d}: {samples_per_sec:.1f} samples/sec")
            results.append((batch_size, samples_per_sec))

        except RuntimeError as e:
            if "out of memory" in str(e).lower():
                print(f"Batch size {batch_size:3d}: Out of memory")
                break
            else:
                print(f"Batch size {batch_size:3d}: Error - {e}")

    optimal = max(results, key=lambda x: x[1])
    print(f"\n🎯 Optimal batch size: {optimal[0]} ({optimal[1]:.1f} samples/sec)")
    return optimal[0]


# Quick test to show the speedup
def compare_batch_sizes(train_dataset, model):
    """Compare batch_size=1 vs optimal - FIXED VERSION"""

    # Check what device the model is on
    device = next(model.parameters()).device
    print(f"Model is on device: {device}")

    model.eval()
    test_samples = 320  # Test with fixed number of samples

    # Test batch_size=1 (your old setup)
    loader_1 = DataLoader(
        train_dataset[:test_samples],
        batch_size=1,
        shuffle=False,
        num_workers=0
    )

    start = time.time()
    with torch.no_grad():
        for batch in loader_1:
            # CRITICAL: Move batch to same device as model!
            batch = batch.to(device)
            _ = model(batch.x, batch.edge_index, batch.batch)
    time_batch_1 = time.time() - start

    # Test batch_size=64
    loader_64 = DataLoader(
        train_dataset[:test_samples],
        batch_size=64,
        shuffle=False,
        num_workers=0
    )

    start = time.time()
    with torch.no_grad():
        for batch in loader_64:
            # CRITICAL: Move batch to same device as model!
            batch = batch.to(device)
            _ = model(batch.x, batch.edge_index, batch.batch)
    time_batch_64 = time.time() - start

    print(f"\nProcessing {test_samples} samples:")
    print(f"Batch size  1: {time_batch_1:.2f}s ({test_samples / time_batch_1:.1f} samples/sec)")
    print(f"Batch size 64: {time_batch_64:.2f}s ({test_samples / time_batch_64:.1f} samples/sec)")
    print(f"Speedup: {time_batch_1 / time_batch_64:.1f}x 🚀")




if __name__ == '__main__':

    # Configuration Data
    epochs = 100
    trainTestSplit = .7
    hiddenLayers = 75
    learn = False
    batchSize = 8

    torch.set_num_threads(os.cpu_count() // 2)

    # What device to process stuff
    device = torch.device(globalDevice)

    # Dataset Configurations and such
    fileRoot, rawConfiguration = DM.GNNStructureCreation(ExperimentDetails)
    processLists = {
        "ExperimentDetails": ExperimentDetails,
        "AggregationDetails": aggregationDetails
    }

    # Create the dataset object
    dataset = MidiDataset(fileRoot, rawConfiguration, processLists)

    #Define the dataset split
    dataSplit = int(len(dataset) * trainTestSplit)

    # Print a summary of the dataset
    print(dataset.get_summary())

    # Shuffle the dataset
    dataset = dataset.shuffle()

    # Create the GNN
    model = GraphSAGE(dataset.num_features, hiddenLayers ,dataset.num_classes).to(device)

    # The optimiser does optimiser stuff
    optimiser = torch.optim.Adam(model.parameters(), lr=0.001)

    # Print out the model details
    print(model)

    # Create the train and test dataset divisions
    trainSplit = dataset[:dataSplit]
    testSplit = dataset[dataSplit:]

    # print(trainSplit)
    # print(testSplit)

    # Function to find optimal batch size (it was 8)
    # batchSize = find_optimal_batch_size_graphsage(dataset, model)

    # Batch sizing for improved performance
    # if batchSize is not None:
    train_loader = DataLoader(trainSplit, batch_size=batchSize, shuffle=True, num_workers=0, drop_last=False)
    val_loader = DataLoader(testSplit, batch_size=batchSize, shuffle=True, num_workers=0, drop_last=False)



    # Summary metric storage
    analysis = {
        "TrainingStage": [],
        "TrainingTest": [],
        "TestStage": []
    }

    # The learning Process
    if learn:

        best_val_acc = 0
        for epoch in range(epochs):
            print(CWR.largeSpacer)
            start = time.time()

            # Train
            train_loss, train_acc = train_epoch(model, train_loader, optimiser, globalDevice)

            # Validate
            val_loss, val_acc = validate(model, val_loader, globalDevice)

            epoch_time = time.time() - start

            print(f"Epoch {epoch:3d}: Train Loss: {train_loss:.4f}, "
                  f"Train Acc: {train_acc:.3f}, Val Loss: {val_loss:.4f}, "
                  f"Val Acc: {val_acc:.3f}, Time: {epoch_time:.2f}s")

            if val_acc > best_val_acc:
                best_val_acc = val_acc
                torch.save(model.state_dict(), 'best_model.pt')




