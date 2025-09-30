from Utilities import ComeWhatRayUtil as CWR
from Utilities import BoundingGenerator as BG
import sys
import networkx as nx
from shapely.geometry import Point, LineString
from scipy.spatial.distance import euclidean
import numpy as np

# It is assumed that all input is a set of points derived from MIDI_Extraction.py

options = {
    "function": "GraphLineRepresentation",
    "polygon": {
        "type": "Rectangle",
        "dimensions": {
            "height": 4,
            "width": 4
        }
    },
    "distanceAttempts": 100,
    "pruningMethod": None,
    "pitchWeighting" : 0.5,
    "rounding": 2,
    "edgeAttributes": False,
    "selfLoop": False,
    "testing": False,
    "shortestConsecutiveEvent": False,
    "threading": True,
    "re-label": True # This corresponds to updating all the nodes such that the deleated node numbers get replaced

}

# The Coordinates returned by MIDI_Extraction.py is the geometric representation
def startProcess(work, inputOptions=None):
    # Updating Options
    CWR.updateOldDictionaryEntriesWithNewDictionaryEntries(options, inputOptions)

    # print(options['pitchWeighting'])
    # work = CWR.openFile(work)

    # Setting up python voodoo magic to let me use a sting to call a function
    this_module = sys.modules[__name__]
    methodInstanciated = getattr(this_module, options['function'])

    if not options["threading"]:
        print(f"Pattern Extraction Approach: {options['function']}")

    proximityGraphRepresentation = methodInstanciated(work)

    if options['pruningMethod'] is not None:
        pruningMethod = getattr(this_module, options['pruningMethod'])
        proximityGraphRepresentation = pruningMethod(proximityGraphRepresentation)

    return proximityGraphRepresentation

# The Coordinates returned by MIDI_Extraction.py is the geometric representation



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
    tuneGraph = graphModifications(tuneGraph)

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
        tuneGraph.nodes[counter]['barBeat'] = note['barBeat']
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
    tuneGraph = graphModifications(tuneGraph)

    return tuneGraph


def SzetoGraphRepresentation(work):

    counter = 0
    updateCounter = 0

    work = CWR.openFile(work)

    tuneGraph = nx.empty_graph(len(work))

    # Going through each point in the piece
    for note in work:

        # Encoding each node with the notes relevant information
        tuneGraph.nodes[counter]['pitch'] = note['pitch']
        tuneGraph.nodes[counter]['position'] = note['position']
        tuneGraph.nodes[counter]['duration'] = note['duration']
        tuneGraph.nodes[counter]['pos'] = (note['position'], note['pitch'])

        # Update Counter
        if counter > ((len(work) / 10) * updateCounter):
            # print(str(counter) + '/' + str(len(points)))
            print('Number of Points: ' + str(len(work)))
            updateCounter += 1
            print(str(counter) + '/' + str(len(work)))

        # Setup for comparison code goes here

        beginScan = work.index(note)
        currentSequentialIndex = -1
        failureCount = 0

        # compare current note to notes that occur after it
        for x in work[beginScan:]:

            # Ends if the points is too far away
            #todo edit calculation to end loop
            # if x['position'] > note['position'] + options["polygon"]["dimensions"]["width"]:
            #     break

            # Comparison code goes here
            # if the notes are simultaneous add an edge
            if simultaneousEventCheck(note, work[work.index(x)]):
                tuneGraph.add_edge(counter, work.index(x))

            else:
                # if there is no point of comparison yet set the proposed sequential event equal to the first non-simultaneous event
                if currentSequentialIndex == -1:
                    currentSequentialIndex = work.index(x)
                else:
                    # Check if the current note is closer to the original note
                    if interEventDistance(note, work[currentSequentialIndex]) > interEventDistance(note, work[work.index(x)]):
                        currentSequentialIndex = work.index(x)

                    # This is just some optimisation such that it doesn't go through the whole piece
                    # As the further the process goes on, the less likely it will be closer
                    else:
                        failureCount += 1
                        if failureCount > options["distanceAttempts"]:
                            break



        # Each note can only have one sequential event, so it finds the closest one that is simultaneous
        if not currentSequentialIndex == -1:
            tuneGraph.add_edge(counter, currentSequentialIndex)

        counter += 1


    # Removes all self loops if any are created
    tuneGraph = graphModifications(tuneGraph)


    return tuneGraph


def KarystinaiosRepresentation(work):

    work = CWR.openFile(work, printDisplay= not options['threading'])
    tuneGraph = nx.empty_graph(len(work))

    counter = 0
    updateCounter = 0

    # Encode note information
    if not options['threading']:
        print("Encoding note information")
    for note in work:
        tuneGraph.nodes[counter]['type'] = note["type"]
        tuneGraph.nodes[counter]['pitch'] = note['pitch']
        tuneGraph.nodes[counter]['position'] = note['position']
        tuneGraph.nodes[counter]['duration'] = note['duration']
        tuneGraph.nodes[counter]['pos'] = (note['position'], note['pitch'])

        counter += 1


    # Setup for comparison code goes here
    if not options['threading']:
        print("Scanning for edge creation")
    for node in range(len(work)):

    # Visualisation of Progress

        if node > ((len(work) / 10) * updateCounter):
            # print(str(counter) + '/' + str(len(points)))
            if not options['threading']:
                print('Number of Points: ' + str(len(work)))
            updateCounter += 1
            if not options['threading']:
                print(str(node) + '/' + str(len(work)-1))


        # compare current note to notes that occur after it
        for x in range(node+1, len(work)):

            comparisonIndex = x

            noteEvent = karystinaiosEventCheck(tuneGraph.nodes[node], tuneGraph.nodes[comparisonIndex])

            if noteEvent is not None:
                tuneGraph.add_edge(node, comparisonIndex, label=noteEvent)

    # Removes all self loops if any are created
    tuneGraph = graphModifications(tuneGraph)

    return tuneGraph

# We are basically just transferring connsecutive edges to rests to the next available note
def karystinaiosModification(work):

    initialGraph = KarystinaiosRepresentation(work)
    # Stores the rests in a graph
    toRemove = []

    # Transfer consecutive connections from rests to join the notes before and after them
    for node in range(len(initialGraph.nodes)):

        # Get all rests from a graph
        # Transfer their consecutive connections
        if initialGraph.nodes[node]["type"] == "Rest":

            toRemove.append(node)
            # print(f"rest: {node}")
            # print(initialGraph.edges(node))
            toJoinList = []

            # Check all rests for their consecutive events
            for edge in initialGraph.edges(node):
                # print(initialGraph[edge[0]][edge[1]])
                if initialGraph[edge[0]][edge[1]]["label"] == "ConsecutiveEvent" or initialGraph[edge[1]][edge[0]]["label"] == "ImpliedConsecutiveEvent":
                    if edge[1] < edge[0]:
                        toJoinList.append(edge[1])

            # add an edge between the consecutive connections before the rest to the ones after it
            for edge in initialGraph.edges(node):
                    if edge[1] > edge[0]:
                        if initialGraph[edge[0]][edge[1]]["label"] == "ConsecutiveEvent" or initialGraph[edge[1]][edge[0]]["label"] == "ImpliedConsecutiveEvent":
                            for tempNode in toJoinList:
                                initialGraph.add_edge(tempNode, edge[1], label="ImpliedConsecutiveEvent")

    # Removes rests from graph
    initialGraph.remove_nodes_from(toRemove)

    # Only maintain the shortest consecutive edges
    if options["shortestConsecutiveEvent"]:
        for node in initialGraph:
            shortestPath = None
            shortestDistance = None
            # Calculates which path is shortest among consecutive edges for a node
            for edge in initialGraph.edges(node):
                if initialGraph[edge[0]][edge[1]]["label"] == "ConsecutiveEvent" or initialGraph[edge[1]][edge[0]]["label"] == "ImpliedConsecutiveEvent":
                    if edge[1] > edge[0]:
                        if shortestPath is None:
                            shortestPath = edge[1]
                            originNote = initialGraph.nodes[node]
                            comparisonNote = initialGraph.nodes[shortestPath]
                            shortestDistance = interEventDistance(originNote, comparisonNote)
                        else:
                            originNote = initialGraph.nodes[node]
                            comparisonNote = initialGraph.nodes[edge[1]]
                            distanceCheck = interEventDistance(originNote, comparisonNote)
                            if distanceCheck < shortestDistance:
                                shortestPath = edge[1]
                                shortestDistance = distanceCheck

            removeEdgeList = []
            for edge in initialGraph.edges(node):
                if initialGraph[edge[0]][edge[1]]["label"] == "ConsecutiveEvent" or initialGraph[edge[1]][edge[0]]["label"] == "ImpliedConsecutiveEvent":
                    if edge[1] > edge[0]:
                        if edge[1] != shortestPath:
                            removeEdgeList.append(edge[1])

            for edge in removeEdgeList:
                initialGraph.remove_edge(node, edge)

    if options["re-label"]:

        remapping = {}
        remainingList = list(initialGraph.nodes)
        for node in range(len(remainingList)):
            remapping[remainingList[node]] = node

        initialGraph = nx.relabel_nodes(initialGraph, remapping)

    endGraph = graphModifications(initialGraph)

    return endGraph


# Helper Methods
# ----------------------------------------------------------------------------------------------------------------------

# Checks if two notes would be connected by a sequential edge (Melody) or simultaneous edge (Harmony).
def eventType(note1, note2):

    if simultaneousEventCheck(note1, note2):
        return "SimultaneousEvent"
    else:
        return "SequentialEvent"

# Checks if notes are sequential events (ie they do not share any overlapping time
def sequentialEventCheck(note1, note2):
    return not simultaneousEventCheck(note1, note2)

# Checks if two notes are simultaneous
def simultaneousEventCheck(note1, note2):

    # if the start of note 1 is between

    note1RelevantTime = [note1['position'], note1['position'] + note1['duration']]
    note2RelevantTime = [note2['position'], note2['position'] + note2['duration']]

    return timeOverlapCheck(note1RelevantTime, note2RelevantTime)

# Time Overlap Check.
def timeOverlapCheck(relevantTime1, relevantTime2):

    if (
            (relevantTime2[0] <= relevantTime1[0] < relevantTime2[1])
            or
            (relevantTime2[0] < relevantTime1[1] <= relevantTime2[1])
    ):
        return True

    elif (
            (relevantTime1[0] <= relevantTime2[0] < relevantTime1[1])
            or
            (relevantTime1[0] < relevantTime2[1] <= relevantTime1[1])
    ):

        return True

    return False

# Gets the distance between two notes (the distance is infinite if they are simultaneous)
def interEventDistance(note1, note2):
                # End of the first note (x)         , pitch of first note (y)
    point1 = [note1['position'] + note1['duration'], note1['pitch']]

             # start of the second note (x)   , pitch of first note (y)
    point2 = [note2['position'], note2['pitch']]

    distance = euclidean(point1, point2, w=[1, options['pitchWeighting']])

    return distance


# Checks which of the three karystinaios defined edge types two notes are
def karystinaiosEventCheck(note1, note2):

    if onsetEventCheck(note1, note2):
        return "OnsetEvent"

    elif consecutiveEventCheck(note1, note2):
        return "ConsecutiveEvent"

    elif simultaneousEventCheck(note1, note2):
        return "SimultaneousEvent"

    return None

# Do the notes start at the same time
def onsetEventCheck(note1, note2):

    if note1['position'] == note2['position']:
        return True

    return False

# Does a note start as another ends
def consecutiveEventCheck(note1, note2):

    if note1['position'] + note1['duration'] == note2['position'] or note2['position'] + note2['duration'] == note1['position'] :
        return True
    return False


# Modifications on the graph
def graphModifications(graph):

    # Remove or keep self loops
    if not options["selfLoop"]:
        graph.remove_edges_from(nx.selfloop_edges(graph))

    # if options["re-label"]:
    #     for node in range(len(graph.nodes)):
    #         graph.nodes[node]['label'] = node

    # Adds relevant attributes to the edges in a graph
    if options["edgeAttributes"]:
        attributes = {
            "pitchChange": 0,
            "distanceChange": 0
        }

        for edge in graph.edges():

            if options["testing"]:
                print(f"{edge[0]} -> {edge[1]}")

            attributes = {
                "pitchChange": round(graph.nodes[edge[1]]['pitch'] - graph.nodes[edge[0]]['pitch'], options['rounding']),
                "onsetGap": round(graph.nodes[edge[1]]['position'] - graph.nodes[edge[0]]['position'], options['rounding']),
                "endOnsetGap": round(graph.nodes[edge[1]]['position'] - (
                            graph.nodes[edge[0]]['position'] + graph.nodes[edge[0]]['duration']), options['rounding']),
            }

            if options["testing"]:
                print(attributes)

            graph.edges[edge[0], edge[1]].update(attributes)
            if options["testing"]:
                print(f"Pitch Change: {graph.edges[edge[0], edge[1]]['pitchChange']}")
                print(f"Onset Gap: {graph.edges[edge[0], edge[1]]['onsetGap']}")
                print(f"End Onset Gap: {graph.edges[edge[0], edge[1]]['endOnsetGap']}")




    return graph

# Pruning Methods #TODO Implement
# ----------------------------------------------------------------------------------------------------------------------
