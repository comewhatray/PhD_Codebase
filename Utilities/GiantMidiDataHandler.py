from Utilities import ComeWhatRayUtil as CWR
from os import listdir
from os.path import isfile, join
import unidecode

def main():

    giantCSV = CWR.openFile("GiantMidiDataset/Music Similarity Piano Solo.csv", delimiter="\t")

    print(len(giantCSV))
    print(giantCSV.columns)

    usedMidis = giantCSV[giantCSV["giant_midi_piano"] == 1]

    lisztData = usedMidis[(usedMidis["surname"] == "Liszt") & (usedMidis["firstname"] == "Franz")]
    ScarlattiData = usedMidis[(usedMidis["surname"] == "Scarlatti") & (usedMidis["firstname"] == "Domenico")]
    BachData = usedMidis[(usedMidis["surname"] == "Bach") & (usedMidis["firstname"] == "Johann Sebastian")]
    SchubertData = usedMidis[(usedMidis["surname"] == "Schubert") & (usedMidis["firstname"] == "Franz")]
    ChopinData = usedMidis[(usedMidis["surname"] == "Chopin") & (usedMidis["firstname"] == "Frédéric")]

    dataHolder = ChopinData

    print("Franz Liszt MIDIS")
    print(CWR.largeSpacer)
    # print(lisztData)
    print(len(dataHolder))
    print(dataHolder.to_string())
    # for i in range(len(ScarlattiData)):
    #     print(ScarlattiData.)
    # for data in ScarlattiData:
    #     print(data)

    # subsets = [lisztData, ScarlattiData, BachData, SchubertData, ChopinData]

    print("All MIDIS")
    print(CWR.largeSpacer)
    # print(usedMidis)

    # mypath = "GiantMidiDataset/Midis/surname_checked_midis"
    mypath = "GiantMidiDataset/Midis/midis"
    endPath = "GiantMidiDataset/Midis/5ComposerTest/Chopin"
    # chosenData = ChopinData

    # onlyfiles = [f for f in listdir(mypath)]

    # print(onlyfiles)

    # for file in onlyfiles:
    #     print(file)

    # for index, row in chosenData.iterrows():
    #     trackID = row["audio_name"]
    #     splitType = row["split"]
    #
    #
    #
    #     print(CWR.largeSpacer)
    #     print(f"Track Name: {trackID} | {splitType}")
    #     for fileName in onlyfiles:
    #         if unidecode.unidecode(trackID) in unidecode.unidecode(fileName):
    #             print(f"MIDI Name: {fileName}")
    #
    #             origin = CWR.appendDirectory(mypath, fileName)
    #             destination = CWR.appendDirectory(endPath, fileName)
    #
    #             CWR.moveFile(origin, destination)
    #
    #
    #
    #
    #
    #     # print(record["youtube_id"])



    # for subset in subsets:

        # trainMidis = subset[subset["split"] == "train"]
        # testMidis = subset[subset["split"] == "test"]
        # validationMidis = subset[subset["split"] == "validation"]
        #
        #
        #
        # print("Train MIDIS")
        # print(CWR.largeSpacer)
        # print(len(trainMidis))
        #
        # print("Test MIDIS")
        # print(CWR.largeSpacer)
        # print(len(testMidis))
        #
        # print("Validation MIDIS")
        # print(CWR.largeSpacer)
        # print(len(validationMidis))


main()