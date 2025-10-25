"""Test runner for the On-Device Assistant."""

import sys
import subprocess

def run_tests():
    """Run all tests."""
    print("=" * 60)
    print("Running On-Device Assistant Tests")
    print("=" * 60)
    print()
    
    # Run pytest
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/", "-v", "--tb=short"],
        capture_output=False
    )
    
    return result.returncode

if __name__ == "__main__":
    sys.exit(run_tests())
