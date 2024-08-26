from Utilities import ComeWhatRayUtil as CWR
from Utilities import BoundingGenerator as BG
import sys
import networkx as nx
from shapely.geometry import Point, LineString

# It is assumed that all input is a set of points derived from MIDI_Extraction.py

options = {
    "method": "GraphLineRepresentation",
    "polygon": {
        "type": "Rectangle",
        "dimensions": {
            "height": 4,
            "width": 4
        }
    },
    "pruningMethod": ""
}

# The Coordinates returned by MIDI_Extraction.py is the geometric representation
def generateRepresentation(work, inputOptions=None):
    # Updating Options
    CWR.updateOldDictionaryEntriesWithNewDictionaryEntries(options, inputOptions)

    # Setting up python voodoo magic to let me use a sting to call a function
    this_module = sys.modules[__name__]
    methodInstanciated = getattr(this_module, options['method'])

    print(f"Pattern Extraction Approach: {options['method']}")
    proximityGraphRepresentation = methodInstanciated(work)

    return proximityGraphRepresentation

# Graph Representations
# ----------------------------------------------------------------------------------------------------------------------

def GraphPointRepresentation(work):
    work = CWR.openFile(work)
    counter = 0
    updateCounter = 0

    # Selects the appropriate shape generator
    shapeGenerator = getattr(BG, options["polygon"]["type"]+"PointGenerator")

    # Creates a graph containing a node for each note
    tuneGraph = nx.empty_graph(len(work))

    # Going through each note in the piece
    for note in work:

        # Update Counter
        if counter > ((len(work) / 10) * updateCounter):
            print('Number of Points: ' + str(len(work)))
            updateCounter += 1
            print(str(counter) + '/' + str(len(work)))

        # Encoding each node with the notes relevant information
        tuneGraph.nodes[counter]['pitch'] = note['pitch']
        tuneGraph.nodes[counter]['position'] = note['position']
        tuneGraph.nodes[counter]['pos'] = (note['position'], note['pitch'])

        # Generates the coordinates for the shape
        shape = shapeGenerator(note, options["polygon"]["dimensions"])

        # Tells the index of where the current note is
        beginScan = work.index(note)

        # Checks which notes are within the shape of the note
        for x in work[beginScan:]:
            # Ends if the points is too far away
            if x['position'] > note['position'] + options["polygon"]["dimensions"]["width"]:
                break

            noteRep = Point(x['position'], x['pitch'])

            # Checks if the shape and the point/line have any points in common
            if shape.intersects(noteRep):
                tuneGraph.add_edge(counter, work.index(x))

        counter += 1

        # TODO improve this so that it doesn't happen to begin with
    tuneGraph.remove_edges_from(nx.selfloop_edges(tuneGraph))
    return tuneGraph


def GraphLineRepresentation(work):
    counter = 0
    updateCounter = 0

    work = CWR.openFile(work)

    # Selects the appropriate shape generator
    shapeGenerator = getattr(BG, options["polygon"]["type"]+"LineGenerator")

    tuneGraph = nx.empty_graph(len(work))

    # Going through each point in the piece
    for note in work:

        # Update Counter
        if counter > ((len(work) / 10) * updateCounter):
            # print(str(counter) + '/' + str(len(points)))
            print('Number of Points: ' + str(len(work)))
            updateCounter += 1
            print(str(counter) + '/' + str(len(work)))

        # Encoding each node with the notes relevant information
        tuneGraph.nodes[counter]['pitch'] = note['pitch']
        tuneGraph.nodes[counter]['position'] = note['position']
        tuneGraph.nodes[counter]['duration'] = note['duration']
        tuneGraph.nodes[counter]['pos'] = (note['position'], note['pitch'])

        # Generates the coordinates for the shape
        shape = shapeGenerator(note, options["polygon"]["dimensions"])

        # Tells the index of where the current note is
        beginScan = work.index(note)

        # Checks which notes are within the shape of the note
        for x in work[beginScan:]:
            # Ends if the points is too far away
            if x['position'] > note['position'] + options["polygon"]["dimensions"]["width"]:
                break

            # Makes line or point depending on parameters
            # if graphDuration:
            pointStart = Point(x['position'], x['pitch'])
            pointEnd = Point(x['position'] + x['duration'], x['pitch'])

            noteRep = LineString([pointStart, pointEnd])

            # else:
            #     noteRep = Point(x['position'], x['pitch'])

            # Checks if the shape and the point/line have any points in common
            if shape.intersects(noteRep):
                tuneGraph.add_edge(counter, work.index(x))

        counter += 1

    # TODO improve this so that it doesn't happen to begin with
    tuneGraph.remove_edges_from(nx.selfloop_edges(tuneGraph))

    prunedGraph = tuneGraph

    # graphTransitivityPruning(tuneGraph)
    # prunedGraph = pruningtwo(tuneGraph)
    # prunedGraph = pruningThree(tuneGraph)

    return prunedGraph


# Pruning Methods #TODO Implement
# ----------------------------------------------------------------------------------------------------------------------