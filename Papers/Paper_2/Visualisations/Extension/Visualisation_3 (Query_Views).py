import os

import matplotlib.pyplot as plt

from Utilities import ComeWhatRayUtil as CWR
from Utilities import Visualisations as VIS
from Utilities import BoundingGenerator as BG
import numpy

nameMapping = CWR.openFile("Papers/Paper_2/Datasets/NamingConvention.json")

dataLocation = "Papers/Paper_2/Extension/ExtensionWorkspace/Experiment15 (BreathingRoom_Membership)"
# dataLocation = "Papers/Paper_2/Extension/ExtensionWorkspace/Experiment14 (FragAndMember)"
# dataLocation = "Papers/Paper_2/Extension/ExtensionWorkspace/Experiment13 (FragmentisationCheck)"
# dataLocation = "Papers/Paper_2/Extension/ExtensionWorkspace/Experiment12 (membershipScale)"
# dataLocation = "Papers/Paper_2/Extension/ExtensionWorkspace/Experiment16 (Kyna_Membership)"

finalQuery = "convertMidiToPoints"
# finalQuery = "karystinaiosModification"

def main():

    for query in os.listdir(dataLocation):
        loc = os.path.join(dataLocation, query)
        loc = os.path.join(loc, finalQuery)
        for file in os.listdir(loc):
            if "query" in file:
                queryCon = CWR.openFile(os.path.join(loc,file))

                startPosition = queryCon[0]["position"]
                endPosition = queryCon[-1]["position"]+ queryCon[0]["duration"]
                xRange = endPosition - startPosition

                lowest = queryCon[0]["pitch"]
                highest = queryCon[0]["pitch"]
                pitchRange = []
                for note in queryCon:
                    pitchRange.append(note["pitch"])
                    if note["pitch"] < lowest:
                        lowest = note["pitch"]
                    if note["pitch"] > highest:
                        highest = note["pitch"]

                yRange = highest - lowest

                print(f"Query_{nameMapping[query]}")
                print(f"xRange = {xRange}")
                print(f"Size = {len(queryCon)}")
                print(f"yRange = {yRange}")
                print(f"Highest = {highest}")
                print(f"Lowest = {lowest}")

                avg = numpy.average(pitchRange)
                std = numpy.std(pitchRange)
                print(f"yAvg: {avg}")
                print(f"yStd: {std}")


                if finalQuery == "convertMidiToPoints":
                    # plt.title(f"Query_{nameMapping[query]}")
                    # VIS.visualiseJsonAsLines(queryCon)

                    queryTemp = BG.generateMultiLineStringFromExtract(queryCon)
                    plt.title(f"Query_{nameMapping[query]}")
                    VIS.plotJsonAsLines(queryCon)
                    VIS.plotShape(BG.boundingPolygon(queryTemp,1), color="RED")
                    VIS.showPlot()
                    # VIS.visualiseShape(BG.boundingPolygon(queryTemp,1))

                elif finalQuery == "karystinaiosModification":
                    plt.title(f"Query_{nameMapping[query]}")
                    VIS.visualiseSpatialGraph(queryCon)
                    bounding = BG.convertGraphToMultiPolygon(queryCon)
                    plt.title(f"Query_{nameMapping[query]}")
                    VIS.visualiseShape(bounding)



    return

main()