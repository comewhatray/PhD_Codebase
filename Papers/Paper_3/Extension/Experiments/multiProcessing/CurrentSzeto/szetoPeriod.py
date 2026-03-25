from Papers.Paper_2.Extension.Experiment_15_Breathing_membership import workspace
from Utilities import ComeWhatRayUtil as CWR
import subprocess
import time


configuration = "AriaDataset/configs/randomisations/randomisations.json"
experiment = "Papers/Paper_3/Extension/Experiments/Experiment_4_preprocessingDataset.py"


if __name__ == '__main__':

    # itters = len(CWR.openFile(configuration))
    identifier = "szetoLogs"
    workspace = "Papers/Paper_3/Extension/Workspace"
    CWR.ensureDirectory(f"{workspace}/{identifier}")

    processes = []
    for i in range(3):
        cmd = ["python3", experiment, configuration, str(i)]
        log_file = open(f'{workspace}/{identifier}/log_{i}.txt', 'w')
        p = subprocess.Popen(cmd, stdout=log_file, stderr=subprocess.STDOUT)
        processes.append(p)

    startTime = time.time()
    while any(p.poll() is None for p in processes):

        running = sum(1 for p in processes if p.poll() is None)
        completed = len(processes) - running
        print(f"Time: {round(time.time() - startTime, 2)}, Running: {running}, Completed: {completed}")
        time.sleep(60)

    print(f"\nAll {len(processes)} processes completed!")
