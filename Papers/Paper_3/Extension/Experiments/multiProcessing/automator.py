import subprocess
import sys
import os


def run_python_files_sequentially(file_list):
    """
    Run a list of Python files one after the other.

    Args:
        file_list (list): List of paths to Python files
    """
    for i, file_path in enumerate(file_list, 1):
        print(f"\n{'=' * 50}")
        print(f"Running file {i}/{len(file_list)}: {file_path}")
        print(f"{'=' * 50}")

        # Check if file exists
        if not os.path.exists(file_path):
            print(f"ERROR: File not found - {file_path}")
            continue

        try:
            # Run the Python file and wait for completion
            subprocess.run([sys.executable, file_path], check=True)
            print(f"✅ Completed: {file_path}")

        except subprocess.CalledProcessError as e:
            print(f"❌ Error running {file_path}: Return code {e.returncode}")

        except KeyboardInterrupt:
            print(f"\n⚠️  Interrupted while running {file_path}")
            break

    print(f"\n{'=' * 50}")
    print("All files completed!")


# Your list of Python files to run
python_files = [
    # "Papers/Paper_3/Extension/Experiments/multiProcessing/CurrentKyna/kynaDefaultPeriod.py",
    # "Papers/Paper_3/Extension/Experiments/multiProcessing/CurrentKyna/kynaPeriod.py"


    # "Papers/Paper_3/Extension/Experiments/multiProcessing/KynaOld/Balanced/KynaDefaultOld.py",
    # "Papers/Paper_3/Extension/Experiments/multiProcessing/KynaOld/Balanced/kynaOld.py",

    # "Papers/Paper_3/Extension/Experiments/multiProcessing/KynaOld/Unbalanced/KynaDefaultOldUnbalanced.py",
    # "Papers/Paper_3/Extension/Experiments/multiProcessing/KynaOld/Unbalanced/KynaUnbalancedOld.py",
    # "Papers/Paper_3/Extension/Experiments/multiProcessing/SzetoOld/Balanced/SzetoDefaultOld.py",
    # "Papers/Paper_3/Extension/Experiments/multiProcessing/SzetoOld/Balanced/SzetoOld.py",
    # "Papers/Paper_3/Extension/Experiments/multiProcessing/SzetoOld/Unbalanced/DefaultUnbalanced.py",
    # "Papers/Paper_3/Extension/Experiments/multiProcessing/SzetoOld/Unbalanced/NoteDiffUnbalanced.py"
    # "Papers/Paper_3/Extension/Experiments/multiProcessing/moreTime/KynaMoreTime.py",
    # "Papers/Paper_3/Extension/Experiments/multiProcessing/moreTime/SzetoMoreTime.py"
    # "Papers/Paper_3/Extension/Experiments/multiProcessing/abstract.py",
    # "Papers/Paper_3/Extension/Experiments/multiProcessing/SzetoOld/Balanced/SzetoDefaultOld.py"
]

# Run the files
run_python_files_sequentially(python_files)