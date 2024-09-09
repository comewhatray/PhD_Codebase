from shapely.geometry import Polygon, box, LineString
from matplotlib.patches import Ellipse


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


def boundingPolygon(lineString, bufferSize):

    line = LineString(lineString)

    line = line.buffer(bufferSize)

    return line


def overlappingPolygon(shape1, shape2):
    return shape1.intersection(shape2)
