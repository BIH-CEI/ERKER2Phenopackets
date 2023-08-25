import os
import sys

# Get the path to the parent directory of the current file
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.join(current_dir, '..')

# Add the parent directory to sys.path temporarily
sys.path.append(parent_dir)

from src import Foo

# Remove the parent directory from sys.path to avoid potential issues
sys.path.remove(parent_dir)
