import sqlite3
import requests
from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import os

app = FastAPI(title="Disaster Early Warning System")

# Enable CORS for cross-origin mobile and web access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_FILE = "disaster_alerts.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS alerts (
            id TEXT PRIMARY KEY,
            place TEXT,
            magnitude REAL,
            time INTEGER,
            url TEXT,
            longitude REAL,
            latitude REAL
        )
    ''')
    conn.commit()
    conn.close()

init_db()

def fetch_usgs_data():
    url = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_hour.geojson"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            for feature in data.get("features", []):
                eq_id = feature["id"]
                props = feature["properties"]
                geom = feature["geometry"]
                place = props.get("place", "Unknown location")
                mag = props.get("mag", 0.0)
                eq_time = props.get("time", 0)
                eq_url = props.get("url", "")
                lon, lat = geom["coordinates"][0], geom["coordinates"][1]

                cursor.execute('''
                    INSERT OR IGNORE INTO alerts (id, place, magnitude, time, url, longitude, latitude)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (eq_id, place, mag, eq_time, eq_url, lon, lat))
            conn.commit()
            conn.close()
    except Exception as e:
        print(f"Error fetching telemetry: {e}")

@app.get("/api/telemetry")
def get_telemetry(background_tasks: BackgroundTasks):
    background_tasks.add_task(fetch_usgs_data)
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT id, place, magnitude, time, url, longitude, latitude FROM alerts ORDER BY time DESC LIMIT 50")
    rows = cursor.fetchall()
    conn.close()

    alerts = []
    for r in rows:
        alerts.append({
            "id": r[0],
            "place": r[1],
            "magnitude": r[2],
            "time": r[3],
            "url": r[4],
            "longitude": r[5],
            "latitude": r[6]
        })
    return {"status": "success", "alerts": alerts}

# Serve root PWA application
@app.get("/")
@app.get("/index.html")
def read_root():
    return FileResponse("index.html")

# Serve manifest and service worker
@app.get("/manifest.json")
def get_manifest():
    return FileResponse("manifest.json")

@app.get("/sw.js")
def get_sw():
    return FileResponse("sw.js", media_type="application/javascript")

# Serve PWA icons
@app.get("/icon-192.png")
def get_icon192():
    return FileResponse("icon-192.png", media_type="image/png")

@app.get("/icon-512.png")
def get_icon512():
    return FileResponse("icon-512.png", media_type="image/png")