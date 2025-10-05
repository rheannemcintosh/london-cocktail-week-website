"""
Flask web application for London Cocktail Week 2025.

This app loads bar and drink data from CSV files and displays
the number of entries found. If files are missing or cannot be read,
it handles the error gracefully.
"""

from flask import Flask, render_template_string
import folium
import pandas as pd
import os

app = Flask(__name__)

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


bars_df, drinks_df, error_message = load_data()

@app.route('/')
def index():
    """
    Handle requests to the root URL ('/').

    Returns:
        str: Application title with data loading summary.
    """

    if error_message:
        # Return a friendly error message instead of breaking
        return f"⚠️ London Cocktail Week 2025! {error_message}"

    html_template = """
        <!DOCTYPE html>
        <html>
            <head>
                <title>Bar Map</title>
                <style>
                    html, body {
                        height: 100%;
                        margin: 0;
                        padding: 0;
                        font-family: Arial, sans-serif;
                    }
                    
                    body{
                        display: flex;
                        flex-direction: column;
                        padding: 1rem;
                        box-sizing: border-box;
                    }

                    h1 {
                        text-align: center;
                        margin: 0 0 1rem 0;
                        flex-shrink: 0; 
                    }

                    .map-container {
                        flex: 1;
                        width: 100%;
                        max-width: 100%;
                        overflow: hidden;
                        position: relative;
                        display: flex;
                    }
                    
                    .map-container iframe {
                        flex: 1;
                        border: 1px solid #ccc;
                        border-radius: 8px;
                    }
                </style>
            </head>
            <body>
                <h1>London Cocktail Week 2025!</h1>
                <div class="map-container">
                    {{ map_html|safe }}
                </div>
            </body>
        </html>
    """

    df = bars_df.copy()

    if not df.empty:
        map_center = [df['Latitude'].mean(), df['Longitude'].mean()]
    else:
        map_center = [df['Latitude'].mean(), df['Longitude'].mean()]

    bar_map = folium.Map(location=map_center, zoom_start=13, tiles="cartodb positron")

    for idx, row in df.iterrows():
        popup_html = f"""
            <b>{row['Bar Name']}</b><br>
        """

        folium.Marker(
            location=[row['Latitude'], row['Longitude']],
            popup=popup_html,
            icon=folium.Icon()
        ).add_to(bar_map)

    return render_template_string(
        html_template,
        map_html=bar_map._repr_html_()
    )




if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
