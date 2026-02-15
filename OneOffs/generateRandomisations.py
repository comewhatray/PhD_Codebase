from Utilities import ComeWhatRayUtil as CWR
import random

outputLocation = "AriaDataset/configs/randomisations/randomisations.json"
# config = "AriaDataset/configs/periodConfigTotal.json"
config = "AriaDataset/configs/BalancedAriaConfig.json"
itterations = 10

output = {}

details = CWR.openFile(config)

total = 0
for label in details["Labels"]:
    print(f"{label}: {len(details["Labels"][label])}")
    total += len(details["Labels"][label])

print(total)

order = [i for i in range(total)]

for i in range(itterations):
    random.shuffle(order)
    output[i] = order[:]

# CWR.saveFile(outputLocation, output)