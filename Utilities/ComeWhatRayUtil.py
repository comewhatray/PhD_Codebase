import os

import itertools
import shutil
import numpy as np
# Save File Imports
import pandas as pd
# import torch
import pickle
import json

# Pretty Things
# ----------------------------------------------------------------------------------------------------

extraLargeSpacer =  "--------------------------------------------------------------------------------"
largeSpacer =       "----------------------------------------"
midSpacer =         "--------------------"
smallSpacer =       "----------"


def printCounter(startText, current, total):
    print(startText + ": " + str(current) + " / " + str(total))

#File Operations
# ----------------------------------------------------------------------------------------------------

# Function to save files (Append file types as necessary )
def saveFile(fileLocation, file, delimiter=None, printDisplay=True):
    if printDisplay:
        print(midSpacer)
    if "." in fileLocation:
        if printDisplay:
            print("Saving File: " + fileLocation)
    else:
        print("No file Type Specified in: " + fileLocation)
    if printDisplay:
        print(midSpacer)

    # Json files
    if ".json" in fileLocation:
        with open(fileLocation, "w+") as f:
            json.dump(file, f)

    # Pickle Files
    if ".gpickle" in fileLocation:
        with open(fileLocation, "wb") as f:
            pickle.dump(file, f, pickle.HIGHEST_PROTOCOL)

    # Numpy
    if ".npy" in fileLocation:
        with open(fileLocation, "wb") as f:
            np.save(f, file)

    # if ".pt" in fileLocation:
        # torch.save(file, fileLocation)

    # Of note, this needs to be a pandas dataframe
    if ".csv" in fileLocation:
        if delimiter is not None:
            file.to_csv(fileLocation, sep=delimiter)
        file.to_csv(fileLocation)

# Function to open files (Append file types as necessary)
def openFile(fileLocation, delimiter=None, printDisplay=True):
    if printDisplay:
        print(midSpacer)
        print("Opening File: " + fileLocation)
        print(midSpacer)

    # Json files
    if ".json" in fileLocation:
        with open(fileLocation, "r") as f:
            return json.load(f)

    # Pickle Files
    if ".gpickle" in fileLocation:
        with open(fileLocation, "rb") as f:
            return pickle.load(f)

    if ".npy" in fileLocation:
        with open(fileLocation, "rb") as f:
            return np.load(f)

    # if ".pt" in fileLocation:
        # return torch.load(fileLocation)

    if ".csv" in fileLocation:
        if delimiter is not None:
            return pd.read_csv(fileLocation, delimiter=delimiter ,on_bad_lines="warn")

        return pd.read_csv(fileLocation,on_bad_lines="warn")


def moveFile(fileLocation, newLocation, duplication=True):
    if duplication:
        shutil.copyfile(fileLocation, newLocation)
    else:
        shutil.move(fileLocation, newLocation)


def directoryExists(directory):
    return os.path.exists(directory)

# Checks if directory Exists
def ensureDirectory(directory):
    if not directoryExists(directory):
        os.makedirs(directory, exist_ok=True)

# Given a dictionary of parameters return a name
def createParameterisedDirectory(initDirectory, parameters):
    if parameters:

        directoryAppendage = dictionaryToFileName(parameters)

        fileLocation = initDirectory + os.sep + directoryAppendage

        ensureDirectory(fileLocation)

        return fileLocation
    else:
        print("No Parameters to create a directory from")

# If you have a directory return the file name at the end of it
def getFileNameFromPath(directory, includeExtension=False):
    fileName = os.path.basename(os.path.normpath(directory))

    if includeExtension:
        return fileName

    else:
        return fileName.split('.')[0]

# Appends a directory to a File Path
def appendDirectory(path, appendage):
    if isinstance(appendage, list):
        for item in appendage:
            path = appendDirectory(path, item)
    else:
        return os.path.join(path, appendage)
    return path

# Deletes a directory and all of its contents
def deleteDirectory(directory):
    if directoryExists(directory):
        shutil.rmtree(directory)

# String Modification Methods
# ----------------------------------------------------------------------------------------------------------------------

# Given a dictionary of parameters create a string summarising those details
def dictionaryToFileName(parameters):

    directoryAppendage = ""
    directoryList = []

    for param in parameters:
        directoryList.append(param)

    directoryList.sort()

    for param in parameters:
        directoryAppendage += "|" + str(param) + "_" + str(parameters[param])

    return directoryAppendage

def removeExtension(directory):
    return directory.rsplit('.', 1)[0]


# Iteration Methods
# ----------------------------------------------------------------------------------------------------------------------

def nCr(array, r):
    return list(itertools.combinations(array, r))

# File Structure Utilities
# ----------------------------------------------------------------------------------------------------------------------

# Updates the default options in a
def updateOldDictionaryEntriesWithNewDictionaryEntries(oldDictionary, newDictionary):
    # Provided that the target dictionary is not empty
    if newDictionary is not None:

        # go through each option in the new dictionary
        for option in newDictionary:

            # If the current option is in the old dictionary change it
            if option in oldDictionary:

                # if that option leeds to a sub dictionary go through and update those values
                if isinstance(oldDictionary[option], dict):

                    # Update the oldSubDictionary
                    for subOption in oldDictionary[option]:
                        if subOption in newDictionary[option]:
                            oldDictionary[option][subOption] = newDictionary[option][subOption]

                # Otherwise just update the old value with the new one
                else:
                    oldDictionary[option] = newDictionary[option]

    else:
        print("Dictionary is None")

