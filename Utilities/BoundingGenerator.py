from shapely import MultiLineString
from shapely.geometry import Polygon, box, LineString, MultiPolygon, Point
from matplotlib.patches import Ellipse
from Utilities import Visualisations as VIS
from shapely.affinity import translate


def RectangleLineGenerator(note, dimensions):
    width = dimensions['width']
    height = dimensions["height"]
    shape = box(
        #  Bottom Left
        note['position'] - (width / 2),
        note['pitch'] - (height / 2),
        #  Top Right
        note['position'] + note['duration'] + (width / 2),
        note['pitch'] + (height / 2)
    )

    return shape


def RectanglePointGenerator(note, dimensions):
    width = dimensions['width']
    height = dimensions["height"]
    shape = box(
        #  Bottom Left
        note['position'] - width / 2,
        note['pitch'] - height / 2,
        #  Top Right
        note['position'] + width / 2,
        note['pitch'] + height / 2
    )

    return shape


def EllipsePointGenerator(note, dimensions):
    width = dimensions['width']
    height = dimensions["height"]
    shape = Ellipse((note['position'], note['pitch']), width, height)
    vertices = shape.get_verts()
    shape = vertices

    shape = Polygon(shape)

    return shape


#Requires a line string
def boundingPolygon(lineString, bufferSize=1):


    # line = lineString.buffer(bufferSize)


    # Alternatives to default
                                # Round flat Square     # round, mitre, bevel
    line = lineString.buffer(bufferSize, cap_style='square', join_style='bevel')

    # if line.geom_type == 'MultiPolygon':
    #     VIS.visualiseLineString(lineString)
    #     VIS.visualiseShape(line)


    return line


def overlappingPolygon(shape1, shape2):
    #
    # if shape1.geom_type == "MultiPolygon" or shape1.geom_type == "GeometryCollection":
    #     shape1 = MultiPolygon([Polygon([Point(xy) for xy in zip(*geom.exterior.xy) if not p.contains(Point(xy))]) for geom in shape1.geoms])
    #
    # if shape2.geom_type == "MultiPolygon" or shape2.geom_type == "GeometryCollection":
    #     shape2 = MultiPolygon([Polygon([Point(xy) for xy in zip(*geom.exterior.xy) if not p.contains(Point(xy))]) for geom in shape2.geoms])
    return shape1.intersection(shape2)


# Finds the best overlap of the polygons
def maxOverlappingPolygon(extract1, extract2, visualisation=False, bufferSize=1):
    pattern1Lines = generateLinesFromExtract(extract1)
    pattern2Lines = generateLinesFromExtract(extract2)

    initialLineStringSequence = generateLineStringFromExtract(extract1)

    initialPolygon = boundingPolygon(initialLineStringSequence, bufferSize)

    maxOverlap = 0

    output = {

    }

    # Going through each line in the initial extract
    for coordinate1 in pattern1Lines:

        # Going through each line in the comparison extract
        for coordinate2 in pattern2Lines:

            # This will generate the differences between the two line segments in order to translate the second extract
            # This is to see which translation gives the best overlap

            # Difference in X values
            durationDifference = coordinate1[0][0] - coordinate2[0][0]
            # Difference in Y values
            pitchDifference = coordinate1[0][1] - coordinate2[0][1]

            # This will be the second pattern translated by the x and y differences
            newPattern = []

            # Translating second patter coordinates
            for coordinate3 in pattern2Lines:

                newLine = [(coordinate3[0][0] + durationDifference , coordinate3[0][1] + pitchDifference),
                           (coordinate3[1][0] + durationDifference, coordinate3[1][1] + pitchDifference)]

                newPattern.append(newLine)

            newLineStringSequence = generateLineStringFromCoordinates(newPattern)

            newPolygon = boundingPolygon(newLineStringSequence, bufferSize)
            overlapPolygon = overlappingPolygon(initialPolygon, newPolygon)

            if overlapPolygon.area > maxOverlap:
                maxOverlap = overlapPolygon.area
                bestOverlappingPatternPolygon = newPolygon
                bestOverlapPolygon = overlapPolygon

                totalArea = initialPolygon.area + newPolygon.area
                overlapArea = bestOverlapPolygon.area

                output = {
                    "InitialPolygon": initialPolygon,
                    "ComparisonPolygon": bestOverlappingPatternPolygon,
                    "MaximalOverlap": bestOverlapPolygon,
                    "Ratio": round((overlapArea/(totalArea-overlapArea))*100,2)
                }

    # VIS.visualisePolygonOverlapComparison(initialPolygon, bestOverlappingPatternPolygon, bestOverlapPolygon)
    # VIS.visualisePolygon(bestOverlapPolygon)



    return output



# Helper Methods
# ----------------------------------------------------------------------------------------------------------------------

# This converts a series of pattern differences into a set of coordinates
#                                                                           Pitch Dif| onsetDif | durations (this is for debug mode)
def convertDifferenceToCoordinates(pattern):
    numPoints = int((len(pattern)+2)/3)

    durations = pattern[-numPoints:]
    points = [[(0, 0), (durations[0], 0)]]
    previousOnset = 0
    previousPitch = 0

    for i in range(numPoints-1):
        # print(i)
        duration = durations[i+1]
        # [(x1,y1),(x2,y2)]
        x1Diff = pattern[i+numPoints-1] + previousOnset
        y1Diff = pattern[i] + previousPitch

        point = [(x1Diff, y1Diff), (x1Diff+duration, y1Diff)]

        previousOnset = x1Diff
        previousPitch = y1Diff

        points.append(point)

    return points

def generateLineStringFromCoordinates(coordinates):
    lineStringList = []

    for line in coordinates:
        for point in line:
            # lineStringList.append((point[1], point[0]))
            lineStringList.append([point[0], point[1]])
            # lineStringList.append(point)

    # print(lineStringList)
    return LineString(lineStringList)

def generateLineStringFromExtract(extract, absolutePosition=False):

    patternList = generateLinesFromExtract(extract, absolutePosition=absolutePosition)

    return generateLineStringFromCoordinates(patternList)

def generateLinesFromExtract(extract, absolutePosition=False):

    if not absolutePosition:
        # convert extract to start at 0
        updateExtractStartingPosition(extract)

        # First Coordinate will always be a line at [0,0] going to [0, duration of first note]
        #          x1, y1  x2, y2
        points = [[(0, 0), (extract[0]["duration"], 0)]]

        # previousPitch = extract[0]["pitch"]
        # previousEnd = extract[0]["duration"]

        originPitch = extract[0]["pitch"]

        for i in range(1, len(extract)):

            # Removing Rests
            if extract[i]["type"] != "Rest":
                currentPitch = extract[i]["pitch"]
                startPitch = currentPitch - originPitch
                startDuration = extract[i]["position"]

                endPitch = startPitch
                endDuration = startDuration + extract[i]["duration"]

                line = [(startDuration, startPitch), (endDuration, endPitch)]
                points.append(line)
    else:
        points = []

        for i in range(len(extract)):
            # Removing rests
            if extract[i]["type"] != "Rest":
                startPitch = extract[i]["pitch"]
                startDuration = extract[i]["position"]

                endPitch = startPitch
                endDuration = startDuration + extract[i]["duration"]

                line = [(startDuration, startPitch), (endDuration, endPitch)]
                points.append(line)

    # print(points)
    return points

def updateExtractStartingPosition(extract):

    difference = 0 - extract[0]["position"]

    for note in extract:
        note['position'] += difference

def removeInteriorShapes(shape):

    if shape.geom_type == 'Polygon':
        shape = removeInteriorPolygon(shape)

    if shape.geom_type == "MultiPolygon":
        shape = removeInteriorMultiPolygon(shape)

    if shape.geom_type == "GeometryCollection":
        shape = removeInteriorGeometryCollection(shape)

    return shape

def removeInteriorPolygon(shape):


    return Polygon(shape.exterior.coords)

def removeInteriorMultiPolygon(shape):

    return

def removeInteriorGeometryCollection(shape):


    return

def convertGraphToMultiPolygon(graph, buffer=1):

    lines = convertGraphToMultiLineString(graph)

    return lines.buffer(buffer, cap_style='square', join_style='bevel')

# Joins the lines together
def convertGraphToMultiLineString(graph, absoluteValue=False):

    # VIS.visualiseSpatialGraph(graph, withLabels=True)

    joinList = []

    for edge in graph.adj:
        # print(f"{edge} -> {graph.adj[edge]}")
        for key in graph.adj[edge]:
            if ((graph.adj[edge][key]["label"] == "ConsecutiveEvent" or
                 graph.adj[edge][key]["label"] == "ImpliedConsecutiveEvent")
                    and key > edge):

                joinPair = (edge,key)
                joinList.append(joinPair)
                # print(joinPair)

    # print(joinList)

    multiLinesList = []
    for joinPair in joinList:
        if len(multiLinesList) == 0:

            multiLinesList.append([joinPair[0], joinPair[1]])
        else:

            present = False

            for linestring in multiLinesList:

                if joinPair[0] in linestring:
                    present = True
                    linestring.append(joinPair[1])

            if not present:
                multiLinesList.append([joinPair[0], joinPair[1]])

    # print(multiLinesList)

    multiLineStringList = []
    for linestring in multiLinesList:
        tempLine = []
        for point in linestring:
            tempLine.append(graph.nodes[point])

        currentLinestring = generateLineStringFromExtract(tempLine, absolutePosition=True)
        multiLineStringList.append(currentLinestring)

    # print(multiLineStringList)

    lines = MultiLineString(multiLineStringList)

    if not absoluteValue:
        xoff = 0 - lines.geoms[0].xy[0][0] # First x coordinate
        yoff = 0 - lines.geoms[0].xy[1][0] # First y coordinate

        lines = translate(lines, xoff=xoff, yoff=yoff)
    #
    # print(lines)

    # VIS.visualiseShape(lines)
    # lines = lines.buffer(1, cap_style='square', join_style='bevel')
    # VIS.visualiseShape(lines)

    # VIS.visualiseLineString(multiLineStringList[0])

    return lines

# This makes them all individual lines
def generateMultiLineListFromGraph(graph, absoluteValue=False):

    lineStringList = []
    startNode = list(graph.nodes)[0]
    xoff = graph.nodes[startNode]["position"]
    yoff = graph.nodes[startNode]["pitch"]

    for node in graph.nodes:
        nodeData = graph.nodes[node]
        xcoords = [nodeData["position"], nodeData["position"]+nodeData["duration"]]
        ycoords = [nodeData["pitch"], nodeData["pitch"]]
        lineStringList.append(LineString([xcoords, ycoords]))

    multiLineString = MultiLineString(lineStringList)

    if not absoluteValue:
        translate(multiLineString, xoff=xoff, yoff=yoff)

    return multiLineString

def generateMultiLineStringFromExtract(extract):

    return MultiLineString(generateLinesFromExtract(extract, absolutePosition=True))

def convertLineStringSequenceToMultiLineString(sequence):

    # print(sequence)

    multiLineStringCoordinateList = []

    for line in sequence:
        x1 = line.coords[0][0]
        y1 = line.coords[0][1]
        x2 = line.coords[1][0]
        y2 = line.coords[1][1]

        append = True

        if not multiLineStringCoordinateList:
            multiLineStringCoordinateList.append([[x1, y1], [x2, y2]])
        else:
            for newSequence in multiLineStringCoordinateList:
                if newSequence[-1][0] <= x1 and append:
                    newSequence.append([x1, y1])
                    newSequence.append([x2, y2])
                    append = False
            if append:
                multiLineStringCoordinateList.append([[x1, y1], [x2, y2]])

    lineStrings = []

    for line in multiLineStringCoordinateList:
        lineStrings.append(LineString(line))


    output = MultiLineString(lineStrings)

    # VIS.visualiseShape(output)

    return output



