import numpy as np
import matplotlib.pyplot as plt



# This will visualise a pattern that has a duration
def visualiseLineSeries(pattern, color="black"):

    for num in range(0, len(pattern), 2):
        startx = pattern[num][0]
        starty = pattern[num][1]
        endx = pattern[num+1][0]
        endy = pattern[num+1][1]

        liney = np.array([startx, endx])
        linex = np.array([starty, endy])

        plt.plot(linex, liney, c=color)


def visualisePolygon(shape, color='black'):

    y, x = shape.exterior.xy
    plt.plot(x, y, color=color)

    # Retrieve and plot x and y coordinates of interior
    for interior in shape.interiors:
        y, x = interior.xy
        plt.plot(x, y, color=color)