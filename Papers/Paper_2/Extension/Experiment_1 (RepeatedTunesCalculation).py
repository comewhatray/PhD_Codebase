from Utilities import ComeWhatRayUtil as CWR
import os
import shutil
import pandas as pd

rootdir = 'LakhDataset/lmd_matched'

midiCount = {

}

for subdir, dirs, files in os.walk(rootdir):
    for file in files:

        tune = subdir.split('/')[-1]

        if tune not in midiCount:
            midiCount[tune] = 1
        else:
            midiCount[tune] += 1


        # print(os.path.join(subdir, file))

sorted_data_values = {k: v for k, v in sorted(midiCount.items(), key=lambda item: item[1]) if 29 < v < 57}

sum = 0
number = 0

output = {

}

keyList = []

for key, value in sorted_data_values.items():
    sum += value
    number += 1
    output[key] = {
        "count": value,
        "Label": ""
    }
    keyList.append(key)

print(sorted_data_values)

print(sum)
print(number)
print(output)

# CWR.saveFile("labeling.json", output)

chosenDirectories = []
for subdir, dirs, files in os.walk(rootdir):
    # print(subdir)
    for key in keyList:
        if key in subdir:
            chosenDirectories.append(subdir)

print(chosenDirectories)
print(len(chosenDirectories))

for dir in chosenDirectories:
    ID = dir.split('/')[-1]
    newDirectory = f"LakhDataset/Subset/{ID}"
    CWR.ensureDirectory(newDirectory)
    print(ID)
    print(newDirectory)

    for file in os.listdir(dir):

        print(file)

        src = os.path.join(dir, file)
        dst = os.path.join(newDirectory, file)

        shutil.copyfile(src, dst)

# after manual inspection file TRNRMXA128F42598AC is the last one to have the same tunes in its file
#Bohemian rhapsody contains cruel angels thesis and shes leaving home

