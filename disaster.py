import json
import os
import sqlite3
import time
from datetime import datetime
from dotenv import load_dotenv
import requests

load_dotenv()

# Configuration Settings
USGS_API_URL = os.getenv(
    "USGS_API_URL",
    "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_hour.geojson",
)
MAGNITUDE_THRESHOLD = float(os.getenv("MAGNITUDE_THRESHOLD", "4.0"))
POLL_INTERVAL_SECONDS = int(os.getenv("POLL_INTERVAL_SECONDS", "30"))
DB_NAME = os.getenv("DB_NAME", "disaster_alerts.db")


def init_db():
    """Initializes local SQLite database."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS alerts (
            event_id TEXT PRIMARY KEY,
            place TEXT,
            magnitude REAL,
            timestamp INTEGER
        )
    """
    )
    conn.commit()
    conn.close()


def fetch_disaster_data():
    """Fetches real-time earthquake data from USGS API."""
    try:
        response = requests.get(
            USGS_API_URL,
            headers={"User-Agent": "DisasterWarningSystem/1.0"},
            timeout=10,
        )
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print(f"[{datetime.now()}] Error fetching data: {e}")
    return None


def send_alert(event_id, place, mag, event_time):
    """Outputs disaster alert notification."""
    formatted_time = datetime.fromtimestamp(event_time / 1000).strftime(
        "%Y-%m-%d %H:%M:%S UTC"
    )
    message = (
        f"🚨 EMERGENCY WARNING 🚨\n"
        f"Severity: High (Magnitude {mag})\n"
        f"Location: {place}\n"
        f"Time: {formatted_time}"
    )

    print("\n" + "=" * 50)
    print(message)
    print("=" * 50 + "\n")


def process_events():
    """Processes fetched disaster events and checks thresholds."""
    data = fetch_disaster_data()
    if not data or "features" not in data:
        return

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    for feature in data["features"]:
        properties = feature["properties"]
        event_id = feature["id"]
        mag = properties.get("mag")
        place = properties.get("place")
        event_time = properties.get("time")

        if mag is None or mag < MAGNITUDE_THRESHOLD:
            continue

        cursor.execute(
            "SELECT event_id FROM alerts WHERE event_id = ?", (event_id,)
        )
        if cursor.fetchone() is None:
            cursor.execute(
                "INSERT INTO alerts VALUES (?, ?, ?, ?)",
                (event_id, place, mag, event_time),
            )
            conn.commit()
            send_alert(event_id, place, mag, event_time)

    conn.close()


def main():
    init_db()
    print(
        f"Monitoring active... Scanning for earthquakes > Magnitude {MAGNITUDE_THRESHOLD}"
    )
    try:
        while True:
            process_events()
            time.sleep(POLL_INTERVAL_SECONDS)
    except KeyboardInterrupt:
        print("\nSystem shut down safely.")


if __name__ == "__main__":
    main()