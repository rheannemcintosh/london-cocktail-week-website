"""
Flask web application for London Cocktail Week 2025.

This app loads bar and drink data from CSV files and displays
the number of entries found. If files are missing or cannot be read,
it handles the error gracefully.
"""

from flask import Flask
import pandas as pd
import os

app = Flask(__name__)

@app.route('/')
def index():
    """
    Handle requests to the root URL ('/').

    Returns:
        str: Application title with data loading summary.
    """
    bars_df, drinks_df, error_message = load_data()

    if error_message:
        # Return a friendly error message instead of breaking
        return f"⚠️ London Cocktail Week 2025! {error_message}"

    return (
        f"London Cocktail Week 2025! "
        f"Bars loaded: {bars_df.shape[0]}. "
        f"Drinks loaded: {drinks_df.shape[0]}."
    )

def load_data():
    """
    Load bar and drink data from CSV files safely.

    Returns:
        tuple:
            pd.DataFrame: The bar data (empty if load failed).
            pd.DataFrame: The drink data (empty if load failed).
            str: Error message if files are missing or unreadable.
    """
    bars_file = 'data/bars.csv'
    drinks_file = 'data/drinks.csv'

    bars_df = pd.DataFrame()
    drinks_df = pd.DataFrame()

    try:
        if not os.path.exists(bars_file):
            raise FileNotFoundError(f"File not found: {bars_file}")
        if not os.path.exists(drinks_file):
            raise FileNotFoundError(f"File not found: {drinks_file}")

        bars_df = pd.read_csv(bars_file)
        drinks_df = pd.read_csv(drinks_file)

        return bars_df, drinks_df, None

    except FileNotFoundError as e:
        return bars_df, drinks_df, f"Missing data file — {e}"
    except pd.errors.EmptyDataError as e:
        return bars_df, drinks_df, f"Data file is empty — {e}"
    except Exception as e:
        return bars_df, drinks_df, f"Unexpected error loading data — {e}"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
