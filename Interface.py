#!/usr/bin/env python3

import sys
import os


def run_dtest(sys1, sys2, file1, file2, test_name, pmq_tol, interop_tol):
    print("=== Running DTest ===")
    print(f"System 1 ID: {sys1}")
    print(f"System 2 ID: {sys2}")
    print(f"File 1: {file1}")
    print(f"File 2: {file2}")
    print(f"Test Name: {test_name}")
    print(f"PMQ Tolerance: {pmq_tol}")
    print(f"Tolerance: {interop_tol}")

    # Validate input files
    if not os.path.isfile(file1):
        print(f"Error: File not found: {file1}")
        return
    if not os.path.isfile(file2):
        print(f"Error: File not found: {file2}")
        return

    #  Add the PMQ analysis command
    print("Running interoperability and PMQ analysis...")
    # Write the Output file
    print("Test completed successfully.")


def main():
    if len(sys.argv) != 8:
        print("Usage: ./DTest <sys1> <sys2> <file1> <file2> <test_name> <pmq_tol> <interop_tol>")
        sys.exit(1)

    try:
        sys1 = int(sys.argv[1])
        sys2 = int(sys.argv[2])
        file1 = sys.argv[3]
        file2 = sys.argv[4]
        test_name = sys.argv[5]
        pmq_tol = float(sys.argv[6])
        interop_tol = float(sys.argv[7])
    except ValueError as e:
        print(f"Error parsing arguments: {e}")
        sys.exit(1)

    run_dtest(sys1, sys2, file1, file2, test_name, pmq_tol, interop_tol)


if __name__ == "__main__":
    main()
