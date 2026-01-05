import sys
import os

defaultExperiment = "Papers/Paper_2/Extension/Experiment_17_Default_Overlap.py"

if __name__ == '__main__':

    additionalConfig = None
    if len(sys.argv) > 1:
        configuration = [sys.argv[i] for i in range(1, len(sys.argv))]
        additionalConfig = configuration[0]
        print(additionalConfig)
        os.system(f"python3 {defaultExperiment} {additionalConfig}")

    os.system(f"python3 {defaultExperiment} ")


