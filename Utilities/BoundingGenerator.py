from shapely.geometry import Polygon, box, LineString
from matplotlib.patches import Ellipse
from Utilities import Visualisations as VIS


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
    shape = Ellipse((note['position'], note['pitch']), width, height, 0)
    vertices = shape.get_verts()
    shape = vertices

    shape = Polygon(shape)

    return shape


#Requires a line string
def boundingPolygon(lineString, bufferSize):


    line = lineString.buffer(bufferSize)

    # Alternatives to default
                                # Round flat Square     # round, mitre, bevel
    # line = line.buffer(bufferSize, cap_style='square', join_style='mitre')

    return line


def overlappingPolygon(shape1, shape2):
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

def generateLineStringFromCoordinates(coordinates):
    lineStringList = []

    for line in coordinates:
        for point in line:
            # lineStringList.append((point[1], point[0]))
            lineStringList.append([point[0], point[1]])
            # lineStringList.append(point)

    # print(lineStringList)
    return LineString(lineStringList)

def generateLineStringFromExtract(extract):

    patternList = generateLinesFromExtract(extract)

    return generateLineStringFromCoordinates(patternList)

def generateLinesFromExtract(extract):

    # convert extract to start at 0
    updateExtractStartingPosition(extract)

    # First Coordinate will always be a line at [0,0] going to [0, duration of first note]
    #          x1, y1  x2, y2
    points = [[(0, 0), (extract[0]["duration"], 0)]]

    # previousPitch = extract[0]["pitch"]
    # previousEnd = extract[0]["duration"]

    originPitch = extract[0]["pitch"]

    for i in range(1, len(extract)):

        currentPitch = extract[i]["pitch"]
        startPitch = currentPitch - originPitch
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



