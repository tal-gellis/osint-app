import pytest
import sys
import os

# Add the parent directory to sys.path so tests can import from the main package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))) 