import unittest
import sys
import os

sys.path.insert(0, os.path.abspath("."))

def run_suite():
    loader = unittest.TestLoader()
    start_dir = os.path.join(os.path.dirname(__file__))
    suite = loader.discover(start_dir, pattern="test_*.py")

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    if not result.wasSuccessful():
        sys.exit(1)

if __name__ == "__main__":
    run_suite()
