"""
Flask web application for London Cocktail Week 2025.

This app loads bar and drink data from CSV files and displays
the number of entries found. If files are missing or cannot be read,
it handles the error gracefully.
"""

from flask import Flask, render_template_string, request
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
                    
                    .search-box {
                        padding: 0 0 1rem 0;
                    }
                </style>
            </head>
            <body>
                <h1>London Cocktail Week 2025!</h1>
                    <div class="search-box">
                        <form method="GET">
                            <input type="text" name="query" placeholder="Search bar name" value="{{ query }}">
                            <select name="preference">
                                <option value="" {% if preference == '' %}selected{% endif %}>All Preferences</option>
                                <option value="r" {% if preference == 'r' %}selected{% endif %}>R Preference</option>
                                <option value="f" {% if preference == 'f' %}selected{% endif %}>F Preference</option>
                                <option value="both" {% if preference == 'both' %}selected{% endif %}>Both</option>
                                <option value="none" {% if preference == 'none' %}selected{% endif %}>None</option>
                            </select>
                            <button type="submit">Search</button>
                            <a href="/" style="text-decoration:none;">
                                <button type="button">Reset</button>
                            </a>
                        </form>
                    </div>
                <div class="map-container">
                    {{ map_html|safe }}
                </div>
            </body>
        </html>
    """

    query = request.args.get("query", "").strip().lower()
    preference = request.args.get('preference', '')

    filtered_df = bars_df.copy()

    if query:
        filtered_df = filtered_df[filtered_df['Bar Name'].str.contains(query, case=False, na=False)]

    # Filter by preference
    if preference == 'r':
        filtered_df = filtered_df[filtered_df['R_Preference'] == True]
    elif preference == 'f':
        filtered_df = filtered_df[filtered_df['F_Preference'] == True]
    elif preference == 'both':
        filtered_df = filtered_df[(filtered_df['R_Preference'] == True) & (filtered_df['F_Preference'] == True)]
    elif preference == 'none':
        filtered_df = filtered_df[(filtered_df['R_Preference'] == False) & (filtered_df['F_Preference'] == False)]

    if not filtered_df.empty:
        map_center = [filtered_df['Latitude'].mean(), filtered_df['Longitude'].mean()]
    else:
        map_center = [filtered_df['Latitude'].mean(), filtered_df['Longitude'].mean()]

    bar_map = folium.Map(location=map_center, zoom_start=13, tiles="cartodb positron")

    for idx, row in filtered_df.iterrows():

        popup_html = f"""
            <b>{row['Bar Name']}</b><br>
            <a href="/bar/{idx}" target="_blank">View details</a>
        """

        r_preference = row['R_Preference']
        f_preference = row['F_Preference']

        if r_preference & f_preference:
            colour = 'red'
            icon = 'star'
        elif r_preference and not f_preference:
            colour = 'orange'
            icon = 'lemon'
        elif f_preference and not r_preference:
            colour = 'green'
            icon = 'cat'
        else:
            colour = 'lightgray'
            icon = 'face-frown'

        folium.Marker(
            location=[row['Latitude'], row['Longitude']],
            popup=popup_html,
            icon=folium.Icon(
                color=colour,
                icon=icon,
                prefix='fa'
            )
        ).add_to(bar_map)

    return render_template_string(
        html_template,
        query=query, preference=preference,
        map_html=bar_map._repr_html_()
    )

@app.route('/bar/<int:bar_id>')
def bar_details(bar_id):
    if bar_id not in bars_df.index:
        return "<h2>Bar not found</h2>", 404

    bar = bars_df.loc[bar_id]

    return f"""
        <!DOCTYPE html>
        <html>
            <head>
                <title>{bar['Bar Name']} - Details</title>
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        background: #f4f4f9;
                        margin: 0;
                        padding: 0;
                        display: flex;
                        justify-content: center;
                        align-items: center;
                        height: 100vh;
                    }}
                    .card {{
                        background: #fff;
                        padding: 20px 30px;
                        border-radius: 12px;
                        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
                        max-width: 400px;
                        width: 100%;
                    }}
                    .card h1 {{
                        margin-top: 0;
                        font-size: 24px;
                        color: #333;
                    }}
                    .card p {{
                        font-size: 16px;
                        color: #555;
                        margin: 8px 0;
                    }}
                    .card a {{
                        display: inline-block;
                        margin-top: 15px;
                        padding: 8px 16px;
                        background: #007BFF;
                        color: white;
                        text-decoration: none;
                        border-radius: 6px;
                        font-size: 14px;
                    }}
                    .card a:hover {{
                        background: #0056b3;
                    }}
                </style>
            </head>
            <body>
                <div class="card">
                    <h1>{bar['Bar Name']}</h1>
                    <p><b>Address:</b> {bar['Address']}</p>
                    <p><b>Phone Number:</b> {bar['Phone Number']}</p>
                    <p><b>Description:</b> {bar['Description']}</p>
                    <p><b>Neighbourhood:</b> {bar['Neighbourhood']}</p>
                    <p><b>District:</b> {bar['City District']}</p>
                    <h2>Opening Hours</h2>
                    <p><b>MON:</b> {bar['MON']}</p>
                    <p><b>TUE:</b> {bar['TUE']}</p>
                    <p><b>WED:</b> {bar['WED']}</p>
                    <p><b>THU:</b> {bar['THU']}</p>
                    <p><b>FRI:</b> {bar['FRI']}</p>
                    <p><b>SAT:</b> {bar['SAT']}</p>
                    <p><b>SUN:</b> {bar['SUN']}</p>
                    <a href="/">⬅ Back to map</a>
                </div>
            </body>
        </html>
    """

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
