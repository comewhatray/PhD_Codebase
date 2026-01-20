import torch
from torch_geometric.loader import DataLoader
import time


def benchmark_batch_sizes(dataset):
    """Show the massive difference batch size makes"""

    batch_sizes = [1, 8, 16, 32, 64, 128, 256]

    for batch_size in batch_sizes:
        loader = DataLoader(
            dataset,
            batch_size=batch_size,
            shuffle=False,
            num_workers=0
        )

        start = time.time()
        for i, batch in enumerate(loader):
            if i >= 100:  # Process 100 batches
                break
            # Simulate some work
            _ = batch.x.mean()

        elapsed = time.time() - start
        total_samples = min(100 * batch_size, len(dataset))
        time_per_sample = elapsed / total_samples

        print(f"Batch size {batch_size:3d}: {elapsed:.3f}s total, "
              f"{time_per_sample * 1000:.2f}ms per sample")


# Run this with your dataset
# benchmark_batch_sizes(your_dataset)

counter = 0

totalLength = 2400
itterationSize = 4
updateCounter = 0
otherCounter = 0
for i in range(0, totalLength, itterationSize):

    if counter % int(totalLength*0.1) < updateCounter:
        print(f"Completion Update: {counter}/{totalLength}")
        print(otherCounter)
        otherCounter += 1
        updateCounter = 0
    else:
        updateCounter += itterationSize


    counter += itterationSize