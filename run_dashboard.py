"""
Convenience script to launch the Felix Monitor dashboard.

Run this script to start the Streamlit web interface:
    python run_dashboard.py
"""
import subprocess
import sys
import os

if __name__ == "__main__":
    # Ensure we're in the project directory
    project_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(project_dir)
    
    # Run streamlit
    subprocess.run([
        sys.executable,
        "-m",
        "streamlit",
        "run",
        "felix_monitor/app.py",
        "--theme.base=dark",
        "--theme.primaryColor=#00d4ff",
        "--theme.backgroundColor=#0f0f23",
        "--theme.secondaryBackgroundColor=#1a1a2e",
        "--theme.textColor=#ffffff",
    ])

