"""
Run all tests for the Math Chatbot project.
This script can be used locally to verify everything works before pushing to GitHub.
"""

import pytest
import sys
import os


def main():
    # Ensure we're running from the project root
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, root_dir)

    print("🔍 Running all Math Chatbot tests...")
    exit_code = pytest.main(["-q", "tests"])
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
