from Utilities import ComeWhatRayUtil as CWR

dataSet = CWR.openFile("AriaDataset/metadata.json")
period = "contemporary"
composers = {

}
for data in dataSet:
    data = dataSet[data]["metadata"]
    if "music_period" in data and "composer" in data:
        if data["music_period"] == period:
            if data["composer"] in composers:
                composers[data["composer"]] += 1
            else:
                composers[data["composer"]] = 1

# print(composers)
d = composers
for w in sorted(d, key=d.get, reverse=True):
    print(w, d[w])