from OneOffs.GnnPerformanceDiagnostics import totalLength
from Utilities import ComeWhatRayUtil as CWR

fileLocation = "GiantMidiDataset/randomisations/oldBalancedRandomisations.json"
totalLength = 1024

randomisations = CWR.openFile(fileLocation)




for randomisation in randomisations:
    remaining = [i for i in range(totalLength)]
    for counter in randomisations[randomisation]:
        if counter in remaining:
            remaining.remove(counter)

    print(remaining)

