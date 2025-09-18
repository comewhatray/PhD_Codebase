from Utilities import ComeWhatRayUtil as CWR
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
import importlib
from Utilities import BoundingGenerator as BG
from Utilities.ShapeVisualisation import visualisePolygon
extraction =  "Code_Stages/0:MIDI_Interface/MIDI_Extraction.py"
geometry = "Code_Stages/1:MIDI_Representations/GeometricRepresentation.py"

plotDetails = {
    "alternateColours": None
}

def visualiseMIDIAsLines(midiLocation):


    processName = CWR.removeExtension(extraction)
    processName = processName.replace('/', '.')

    stage = importlib.import_module(processName)
    results = stage.startProcess(midiLocation, "convertMidiToPoints")

    # processName = CWR.removeExtension(geometry)
    # processName = processName.replace('/', '.')
    # stage = importlib.import_module(processName)
    # results = stage.startProcess(midiLocation, "convertMidiToPoints")



    visualiseJsonAsLines(results)

    return results

# Intakes json of points
# [{"pitch": 67.0, "position": 0.5, "duration": 0.5, "barBeat": 0.5}, {"pitch": 67.0, "position": 1.0, "duration": 0.5, "barBeat": 1.0}, ...]
def visualiseJsonAsPoints(json, saveTo=None):
    plotJsonAsPoints(json)
    if saveTo is not None:
        toSave(saveTo)
    plt.show()

# Intakes json of points
# [{"pitch": 67.0, "position": 0.5, "duration": 0.5, "barBeat": 0.5}, {"pitch": 67.0, "position": 1.0, "duration": 0.5, "barBeat": 1.0}, ...]
def visualiseJsonAsLines(json, plotRequirements=None, saveTo=None):
    plotJsonAsLines(json, plotRequirements)
    if saveTo is not None:
        toSave(saveTo)
    plt.show()


# This includes the constructed lines between notes
def visualiseLineStringFromJson(json, saveTo=None):
    plotLineStringFromJson(json)
    # plotLineString(lineString)
    if saveTo is not None:
        toSave(saveTo)
    plt.show()

# This includes the constructed lines between notes
def visualiseLineString(lineString, saveTo=None):
    # plotLineStringFromJson(json)
    plotLineString(lineString)
    if saveTo is not None:
        toSave(saveTo)
    plt.show()

# Visualise the boundary of a lineString
def visualiseLineStringBounding(json, boundary=1, saveTo=None):
    lineString = BG.generateLineStringFromExtract(json)
    bounding = BG.boundingPolygon(lineString, boundary)
    plotPolygon(bounding)
    if saveTo is not None:
        toSave(saveTo)
    plt.show()

# Visualise a lineString and its boundary
def visualiseLineStringWithBoundary(json, boundary=1, saveTo=None):
    plotLineStringFromJson(json)
    lineString = BG.generateLineStringFromExtract(json)
    bounding = BG.boundingPolygon(lineString, boundary)
    plotPolygon(bounding)
    if saveTo is not None:
        toSave(saveTo)
    plt.show()

# Visualise two polygons and their overlap Input is the json data and boundary data
def visualiseOverlappingPolygons(json1, json2, boundary=1, saveTo=None):
    lineString1 = BG.generateLineStringFromExtract(json1)
    lineString2 = BG.generateLineStringFromExtract(json2)

    boundary1 = BG.boundingPolygon(lineString1, boundary)
    boundary2 = BG.boundingPolygon(lineString2, boundary)

    plotPolygon(boundary1, color="Red")
    plotPolygon(boundary2, color="Blue")

    overlap = BG.overlappingPolygon(boundary1, boundary2)
    plotShape(overlap, color="Black")
    if saveTo is not None:
        toSave(saveTo)
    plt.show()

def visualiseOverlappingPolygonsUsingData(polygon1, polygon2, overlapPolygon, saveTo=None):
    # plotPolygon(polygon1, color="Red")
    # plotPolygon(polygon2, color="Blue")
    plotShape(polygon1, color="Red")
    plotShape(polygon2, color="Blue")
    plotShape(overlapPolygon, color="Black")

    if saveTo is not None:
        toSave(saveTo)
    plt.show()


# without care of positioning of points
def visualiseGraph(graph, withLabels=False, size=300, color="Blue"):
    nx.draw(graph, with_labels=withLabels, node_size=size, node_color=color)
    plt.show()

# with care of positioning of points (MUST HAVE pos attribute)
def visualiseSpatialGraph(graph, toSave=None,  withLabels=False, size=300, color="Blue"):
    # graph = CWR.openFile(work)

    positions = nx.get_node_attributes(graph, 'pos')
    nx.draw(graph, positions, with_labels=withLabels, node_size=size, node_color=color)
    plt.show()
    #
    if toSave is not None:
        return

def visualiseShape(shape, color="Black"):
    plotShape(shape, color=color)
    plt.show()

# Plotting Details
# ----------------------------------------------------------------------------------------------------------------------

# Given a json file of notes, plot the notes onset value and pitch
def plotJsonAsPoints(json):
    pointList = json

    xList = []
    yList = []
    for num in range(0, len(pointList)):
        xList.append(pointList[num]["position"])
        yList.append(pointList[num]["pitch"])

    plt.scatter(xList, yList)

# Given a json file of notes, plot the notes
def plotJsonAsLines(json, plotRequirements=None):
    linesList = json

    colour = "Black"

    for num in range(0, len(linesList)):
        startx = linesList[num]["position"]
        starty = linesList[num]["pitch"]
        endx = linesList[num]["position"] + linesList[num]["duration"]
        endy = linesList[num]["pitch"]

        linex = np.array([startx, endx])
        liney = np.array([starty, endy])

        if plotRequirements is not None:
            CWR.updateOldDictionaryEntriesWithNewDictionaryEntries(plotDetails, plotRequirements)
            if plotDetails["alternateColours"] is not None:
                if num % 2 == 0:
                    colour = plotDetails["alternateColours"][0]
                else:
                    colour = plotDetails["alternateColours"][1]

        plt.plot(linex, liney, c=colour)

# Given a json file plot the notes as a continues line string, gaps between notes being connected by a line
def plotLineStringFromJson(json, color="black"):
    lineString = BG.generateLineStringFromExtract(json)
    return plotLineString(lineString, color=color)


def plotLineString(lineString, color="black"):

    x, y = lineString.coords.xy
    plt.plot(x, y, color=color)
    return lineString



# Given a polygon object draw it
def plotPolygon(shape, color="Black"):

    x, y = shape.exterior.xy
    plt.plot(x, y, color=color)

    # Retrieve and plot x and y coordinates of interior
    for interior in shape.interiors:
        x, y = interior.xy


# Helper Methods
# ----------------------------------------------------------------------------------------------------------------------

# A recursive call for shapes with multiple shapes in them
def plotShape(shape, color='black'):
    if shape is not None:
        if shape.geom_type == "MultiPolygon" or shape.geom_type == "GeometryCollection" or shape.geom_type == "MultiLineString":
            for geom in shape.geoms:
                plotShape(geom, color)

        elif shape.geom_type == "Polygon":
            plotPolygon(shape, color)

        elif shape.geom_type == "LineString":
            plotLineString(shape, color)

def toSave(location):
    plt.savefig(location)

