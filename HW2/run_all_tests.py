import subprocess
import sys

def run_test(file_name):
    print(f"Running {file_name}...")
    result = subprocess.run([sys.executable, file_name], capture_output=True, text=True)
    if result.returncode == 0:
        print(f"{file_name} passed!")
        print(result.stdout)
    else:
        print(f"{file_name} failed!")
        print(result.stdout)
        print(result.stderr)
    print()

if __name__ == "__main__":
    test_files = [
        "test.py",
        "der_test.py",
        "sec_test.py",
        "address_test.py",
        "sec_parser_test.py"
    ]
    
    for test_file in test_files:
        run_test(test_file)
    
    print("All tests completed!")