from Utilities import ComeWhatRayUtil as CWR
from Utilities import BoundingGenerator as BG
from Utilities import ShapeVisualisation as SV
import matplotlib.pyplot as plt

def main():


    pattern1 = (-20.0, 4.0, 1.0, 0.0, 2.0, 2.0, 2.0)
    pattern2 = (0.0, 26.0, 2.0, 1.0, 2.0, 2.0, 1.0)

    pattern1Line = extractLineStringFromPattern(extractLinesFromPattern(pattern1))
    SV.visualiseLineSeries(pattern1Line)
    bounding1 = BG.boundingPolygon(pattern1Line, 3)
    SV.visualisePolygon(bounding1)
    plt.show()

    pattern2Line = extractLineStringFromPattern(extractLinesFromPattern(pattern2))
    SV.visualiseLineSeries(pattern2Line)
    bounding2 = BG.boundingPolygon(pattern2Line, 3)
    SV.visualisePolygon(bounding2)
    plt.show()




    #
    # overlap = BG.overlappingPolygon(bounding1, bounding2)
    #
    # print(overlap.area)



def extractLineStringFromPattern(pattern):

    lineStringList = []

    for line in pattern:
        for point in line:
            lineStringList.append(point)

    return lineStringList

def extractLinesFromPattern(pattern):
    patternSize = (len(pattern) + 1) % 3
    # print(patternSize)

    points = [[(0, 0), (0, pattern[patternSize * 3])]]
    # print(len(pattern))

    previousPitch = 0
    previousDuration = 0

    for i in range(patternSize):
        startPitch = previousPitch + pattern[i]
        startDuration = previousDuration + pattern[i + patternSize]

        endPitch = startPitch
        endDuration = startDuration + pattern[i + (patternSize * 2) + 1]

        previousPitch = endPitch
        previousDuration = startDuration

        line = [(startPitch, startDuration), (endPitch, endDuration)]

        # points.append((startPitch, startDuration))
        # points.append((endPitch, endDuration))
        points.append(line)

    # print(points)
    return points

main()