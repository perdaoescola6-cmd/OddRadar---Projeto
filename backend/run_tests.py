#!/usr/bin/env python3
"""
BetStats Test Runner
Runs all tests and generates a summary report
"""
import subprocess
import sys
import os

def run_tests():
    """Run all tests and display results"""
    print("=" * 60)
    print("🧪 BetStats Test Suite")
    print("=" * 60)
    print()
    
    # Change to backend directory
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(backend_dir)
    
    # Run pytest with verbose output
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/", "-v", "--tb=short", "-x"],
        capture_output=False
    )
    
    print()
    print("=" * 60)
    if result.returncode == 0:
        print("✅ All tests passed!")
    else:
        print("❌ Some tests failed. Check output above.")
    print("=" * 60)
    
    return result.returncode


def run_parser_tests():
    """Run only parser tests"""
    print("🧪 Running Parser Tests...")
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/test_parser.py", "-v"],
        capture_output=False
    )
    return result.returncode


def run_resolver_tests():
    """Run only resolver tests"""
    print("🧪 Running Resolver Tests...")
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/test_resolver.py", "-v"],
        capture_output=False
    )
    return result.returncode


def run_e2e_tests():
    """Run only E2E tests"""
    print("🧪 Running E2E Tests...")
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/test_e2e.py", "-v"],
        capture_output=False
    )
    return result.returncode


if __name__ == "__main__":
    if len(sys.argv) > 1:
        test_type = sys.argv[1]
        if test_type == "parser":
            sys.exit(run_parser_tests())
        elif test_type == "resolver":
            sys.exit(run_resolver_tests())
        elif test_type == "e2e":
            sys.exit(run_e2e_tests())
        else:
            print(f"Unknown test type: {test_type}")
            print("Usage: python run_tests.py [parser|resolver|e2e]")
            sys.exit(1)
    else:
        sys.exit(run_tests())
