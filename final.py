import requests
from datetime import datetime, timedelta, timezone
import sqlite3
from flask import Flask, render_template
import json

# Meteomatics API credentials and parameters

# Read configuration from file
with open('config.json', 'r') as config_file:
    config = json.load(config_file)

# Now you can access your credentials as follows:
username = config['meteomatics']['username']
password = config['meteomatics']['password']

locations = {
    'Kastoria': '40.5193,21.2682',
    'Athens': '37.9838,23.7275',
    'Thessaloniki': '40.6401,22.9444'
}

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('weather.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with sqlite3.connect('weather.db') as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS locations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE,
                coordinates TEXT UNIQUE
            );
        """)
        for name, coords in locations.items():
            cursor.execute("INSERT OR IGNORE INTO locations (name, coordinates) VALUES (?, ?)", (name, coords))
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS forecasts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                location_id INTEGER,
                forecast_date DATE,
                temperature REAL,
                precipitation REAL,
                wind_speed REAL,
                FOREIGN KEY (location_id) REFERENCES locations(id)
            );
        """)
        conn.commit()

def count_unique_locations():
    with sqlite3.connect('weather.db') as conn:
        cursor = conn.cursor()
        count = cursor.execute("SELECT COUNT(DISTINCT name) FROM locations").fetchone()[0]
        return count


def fetch_forecasts():
    forecasts = {}
    for name, coords in locations.items():
        start_date = datetime.now(timezone.utc).replace(microsecond=0).strftime('%Y-%m-%dT%H:%M:%SZ')
        end_date = (datetime.now(timezone.utc) + timedelta(days=6)).replace(microsecond=0).strftime('%Y-%m-%dT%H:%M:%SZ')
        url = f"https://api.meteomatics.com/{start_date}--{end_date}:P1D/t_2m:C,precip_1h:mm,wind_speed_10m:ms/{coords}/csv"
        response = requests.get(url, auth=(username, password))
        if response.status_code == 200:
            forecast_data = [line.split(';') for line in response.text.strip().split('\n')[1:]]  # Skip header
            forecasts[name] = forecast_data
        else:
            print(f"Error fetching data for location {name}: {response.text}")
    return forecasts

def store_forecasts(forecasts):
    with sqlite3.connect('weather.db') as conn:
        cursor = conn.cursor()
        for name, forecast_data in forecasts.items():
            location_id = cursor.execute("SELECT id FROM locations WHERE name = ?", (name,)).fetchone()[0]
            for data_line in forecast_data:
                date, temp, precip, wind_speed = data_line
                exists = cursor.execute("""
                SELECT id FROM forecasts WHERE location_id = ? AND forecast_date = ?
                """, (location_id, date)).fetchone()
                if not exists:
                    cursor.execute("""
                    INSERT INTO forecasts (location_id, forecast_date, temperature, precipitation, wind_speed)
                    VALUES (?, ?, ?, ?, ?)
                    """, (location_id, date, temp, precip, wind_speed))
        conn.commit()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/locations', methods=['GET'])
def list_locations():
    conn = get_db_connection()
    locations = conn.execute('SELECT * FROM locations').fetchall()
    conn.close()
    return render_template('locations.html', locations=locations)

@app.route('/forecasts', methods=['GET'])
def list_forecasts():
    conn = get_db_connection()
    forecasts_by_city = {}
    cities = conn.execute('SELECT * FROM locations').fetchall()
    for city in cities:
        forecasts = conn.execute('SELECT * FROM forecasts WHERE location_id = ?', (city['id'],)).fetchall()
        forecasts_by_city[city['name']] = forecasts
    conn.close()
    return render_template('forecasts.html', forecasts_by_city=forecasts_by_city)

@app.route('/latest_forecasts', methods=['GET'])
def list_latest_forecasts():
    conn = get_db_connection()
    latest_forecasts_by_city = {}
    cities = conn.execute('SELECT * FROM locations').fetchall()
    for city in cities:
        latest_forecasts = conn.execute(
            'SELECT * FROM (SELECT * FROM forecasts WHERE location_id = ? ORDER BY forecast_date DESC) GROUP BY forecast_date',
            (city['id'],)
        ).fetchall()
        latest_forecasts_by_city[city['name']] = latest_forecasts
    conn.close()
    return render_template('latest_forecasts.html', latest_forecasts_by_city=latest_forecasts_by_city)

def process_forecasts(forecasts):
    from collections import defaultdict
    # Organize forecasts into a dictionary where each key is a date
    # and each value is a list of temperatures recorded on that date
    temps_by_date = defaultdict(list)
    for forecast in forecasts:
        date = forecast['forecast_date'][:10]  # Extract just the date part
        temps_by_date[date].append(forecast['temperature'])

    # For each date, calculate the average of the last three forecasts
    avg_temps = {}
    for date, temps in temps_by_date.items():
        # Ensure we consider only the last three temperatures
        relevant_temps = temps[-3:]
        avg_temps[date] = sum(relevant_temps) / len(relevant_temps) if relevant_temps else None

    return avg_temps

@app.route('/average_temperatures', methods=['GET'])
def list_average_temperatures():
    conn = get_db_connection()
    avg_temp_by_city = {}
    cities = conn.execute('SELECT * FROM locations').fetchall()

    for city in cities:
        # Fetch temperature forecasts for this location, sorted by date and time
        forecasts = conn.execute(
            'SELECT forecast_date, temperature FROM forecasts WHERE location_id = ? ORDER BY forecast_date',
            (city['id'],)
        ).fetchall()

        # Process these forecasts in Python to compute the desired averages
        processed_forecasts = process_forecasts(forecasts)
        avg_temp_by_city[city['name']] = processed_forecasts
    
    conn.close()
    return render_template('average_temperatures.html', avg_temp_by_city=avg_temp_by_city)

@app.route('/top_locations/<metric>/', methods=['GET'])
def list_dynamic_top_locations(metric):
    n = count_unique_locations()  # Get the dynamic count of locations
    if metric not in ['temperature', 'precipitation', 'wind_speed']:
        return "Invalid metric", 400
    conn = get_db_connection()
    top_locations = conn.execute(
        f'SELECT l.name, AVG(f.{metric}) as avg_metric FROM forecasts f JOIN locations l ON f.location_id = l.id GROUP BY l.name ORDER BY avg_metric DESC LIMIT ?',
        (n,)
    ).fetchall()
    conn.close()
    return render_template('top_locations.html', top_locations=top_locations, metric=metric)


def main():
    init_db()
    forecast_data = fetch_forecasts()
    store_forecasts(forecast_data)

if __name__ == '__main__':
    main()
    app.run(debug=True)
