import os
import sys
import glob
import subprocess

TEST_DIR = os.path.dirname(os.path.abspath(__file__))

def run_all_tests():
    test_files = glob.glob(os.path.join(TEST_DIR, 'test_*.py'))
    failed = False
    for test_file in test_files:
        print(f"Running {os.path.basename(test_file)}...")
        result = subprocess.run([sys.executable, test_file], capture_output=True, text=True)
        print(result.stdout)
        if result.returncode != 0:
            print(f"FAILED: {os.path.basename(test_file)}")
            print(result.stderr)
            failed = True
    if not failed:
        print("All tests passed.")
    else:
        print("Some tests failed.")

if __name__ == "__main__":
    run_all_tests()
