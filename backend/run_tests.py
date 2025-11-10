#!/usr/bin/env python
"""
Test runner script for the FinTech forecasting application

Usage:
    python run_tests.py                    # Run all tests
    python run_tests.py --unit             # Run only unit tests
    python run_tests.py --integration       # Run only integration tests
    python run_tests.py --model             # Run only model evaluation tests
    python run_tests.py --coverage          # Run with coverage report
"""
import sys
import subprocess
import argparse


def run_tests(test_type=None, coverage=False):
    """Run pytest with appropriate arguments"""
    cmd = ["python", "-m", "pytest"]
    
    if coverage:
        cmd.extend(["--cov=backend", "--cov-report=html", "--cov-report=term"])
    
    if test_type == "unit":
        cmd.extend(["-m", "unit"])
    elif test_type == "integration":
        cmd.extend(["-m", "integration"])
    elif test_type == "model":
        cmd.extend(["-m", "model"])
    
    cmd.append("tests/")
    
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd)
    return result.returncode


def main():
    parser = argparse.ArgumentParser(description="Run tests for FinTech forecasting application")
    parser.add_argument("--unit", action="store_true", help="Run only unit tests")
    parser.add_argument("--integration", action="store_true", help="Run only integration tests")
    parser.add_argument("--model", action="store_true", help="Run only model evaluation tests")
    parser.add_argument("--coverage", action="store_true", help="Generate coverage report")
    
    args = parser.parse_args()
    
    test_type = None
    if args.unit:
        test_type = "unit"
    elif args.integration:
        test_type = "integration"
    elif args.model:
        test_type = "model"
    
    exit_code = run_tests(test_type, args.coverage)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()

