"""
Felix Monitor - Streamlit Cloud Entry Point

This is the main entry point for Streamlit Cloud deployment.
It imports and runs the main application from the felix_monitor package.
"""

# Add the current directory to Python path to ensure package can be imported
import sys
from pathlib import Path

# Get the directory containing this script
root_dir = Path(__file__).parent
sys.path.insert(0, str(root_dir))

# Now import and run the main app
from felix_monitor.app import main

if __name__ == "__main__":
    main()

