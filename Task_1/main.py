"""
main.py - Application entry point.

Run with:
    python3 main.py

Assumes the dataset CSV is in the same directory (or set DATASET_PATH below).
"""

import sys
import os
import tkinter as tk
from tkinter import messagebox

from load_dataset_module import DataLoader
from statistics_module import StatisticsModule
from query_module import QueryModule
from user_interface_module import launch_ui
from load_dataset_module import DataLoader, BaseModule, DataLoadError

# Dataset path 
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_PATH = os.path.join(BASE_DIR, "..", "data.csv")

class AppError(Exception):
    """Custom exception for application startup failures"""
    pass

def _show_error(message):
    """Shows error as popup or prints to terminal."""
    try:
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("Application Error", message)
        root.destroy()
    except Exception:
        print(f"[ERROR] {message}")

def main():
    # 1. Load the dataset
    loader = DataLoader(DATASET_PATH)
    
    try:
        success = loader.load()
    except DataLoadError as e:
        _show_error(f"Dataset error:\n{e}")
        sys.exit(1)

    if not success:
        _show_error(
            f"Failed to load dataset from:\n{DATASET_PATH}\n\n"
            "Please check the file path and try again."
        )
        sys.exit(1)

    try:
        # 2. Initialise modules
        dataframe = loader.get_dataframe()
        stats_module = StatisticsModule()
        query_module = QueryModule(dataframe)
        
        # 3. Launch GUI
        launch_ui(query_module, stats_module, dataframe)

    except Exception as e:
        _show_error(f"Application failed to start:\n{e}")
        sys.exit(1)

if __name__ == "__main__":
    main()












