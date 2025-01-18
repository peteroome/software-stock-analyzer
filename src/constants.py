# src/constants.py
import pandas as pd
from datetime import datetime

def load_universe():
    """Load the most recent universe file"""
    try:
        # Get most recent universe file (assuming format: software_universe_YYYYMMDD.csv)
        import glob
        universe_files = glob.glob('software_universe_*.csv')
        if not universe_files:
            raise FileNotFoundError("No universe file found")
            
        most_recent = max(universe_files)
        return pd.read_csv(most_recent)
    except Exception as e:
        print(f"Error loading universe: {e}")
        return pd.DataFrame()

# Shared configuration
MARKET_CAP_RANGE = (1_000_000_000, 70_000_000_000)  # $1B to $70B
MIN_VOLUME = 100_000