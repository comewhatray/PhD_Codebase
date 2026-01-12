from Utilities import ComeWhatRayUtil as CWR
import os

metadata = CWR.openFile("AriaDataset/metadata.json")


def constructName(number):
    totalDigits = 6
    baseName = str(number)

    digitsToAdd = totalDigits - len(baseName)

    paddingZeros = "0"*digitsToAdd

    filename = paddingZeros+baseName+"_0.mid"

    return filename

periodCounter = 0
periodTracer = {}
for piece in metadata:

    mData = metadata[piece]["metadata"]


    if "music_period" in mData:
        periodCounter += 1

        if not mData["music_period"] in periodTracer:
            periodTracer[mData["music_period"]] = {
                "count": 1,
                "subset": [constructName(piece)]
            }

        else:
            periodTracer[mData["music_period"]]["count"] += 1
            periodTracer[mData["music_period"]]["subset"].append(constructName(piece))


print(f"Number of Pieces that have a Period Attribute: {periodCounter}")

config = {
    "Title": "",
    "Directory": "",
    "Labels": {}
}

for label in periodTracer:
    config["Labels"][label] = periodTracer[label]["subset"]


configName = "AriaDataset/configs/periodConfigTotal.json"
if not os.path.exists(configName):
    CWR.saveFile("AriaDataset/configs/periodConfigTotal.json", config)


locations = CWR.exploreDirectory('AriaDataset/data')

for location in locations:
    fileName = CWR.getFileNameFromPath(location, includeExtension=True)
    if not os.path.exists(fileName):
        CWR.moveFile(location,f"AriaDataset/dataMonolith/{fileName}")

