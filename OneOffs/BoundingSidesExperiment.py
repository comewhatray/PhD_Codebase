from Utilities import ComeWhatRayUtil as CWR
from Code_Stages import ExperimentProcess as EP

from Utilities import BoundingGenerator as BG
from Utilities import Visualisations as VIS

ExperimentDetails = {
    # "ExperimentName": "Name left blank on purpose",
    "Description": "For running a sanity check on the Line Proximity graph representation method",
    "WorkspaceLocation": "Sanity_Checks/SanityWorkSpace",
    "Dataset_Configuration": "Extracts/Configs/LisztExtractConfig.json",
    "Stages": [
        {
            "file": "Code_Stages/0:MIDI_Interface/MIDI_Extraction.py",
            "options": {
                "function": "convertMidiToPoints",
                "saveType": ".json",
            }
        }
    ]

}

if __name__ == '__main__':
    details = EP.batchExperiment(ExperimentDetails)

    FileLocation = CWR.openFile(
        "Sanity_Checks/SanityWorkSpace/Testing/Default/convertMidiToPoints/LiebestraumExtract.json")

    lines = BG.generateMultiLineStringFromExtract(FileLocation)

    polygons = BG.boundingPolygon(lines,yScale=5)

    VIS.plotShape(polygons)
    VIS.plotShape(lines, color="red")
    VIS.showPlot()





