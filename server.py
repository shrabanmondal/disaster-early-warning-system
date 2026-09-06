import sqlite3
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import requests

app = FastAPI(title="Disaster Warning System API")

# Enable CORS for cross-origin web access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_NAME = "disaster_alerts.db"

@app.get("/")
def read_root():
    """Serves the PWA dashboard at http://localhost:8000/"""
    return FileResponse("index.html")

@app.get("/manifest.json")
def get_manifest():
    """Serves the PWA manifest"""
    return FileResponse("manifest.json")

@app.get("/sw.js")
def get_service_worker():
    """Serves the Service Worker script"""
    return FileResponse("sw.js", media_type="application/javascript")

@app.get("/alerts")
def get_stored_alerts():
    """Fetch stored earthquake records from SQLite database"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT event_id, place, mag, event_time FROM alerts ORDER BY event_time DESC LIMIT 20")
    rows = cursor.fetchall()
    conn.close()
    
    alerts = []
    for row in rows:
        alerts.append({
            "event_id": row[0],
            "place": row[1],
            "magnitude": row[2],
            "event_time": row[3]
        })
    return {"alerts": alerts}

@app.get("/live-usgs")
def get_live_usgs(min_magnitude: float = 2.0):
    """Fetch live seismic telemetry directly from USGS API"""
    url = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_hour.geojson"
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        
        events = []
        for feature in data.get("features", []):
            mag = feature["properties"]["mag"]
            if mag and mag >= min_magnitude:
                events.append({
                    "id": feature["id"],
                    "place": feature["properties"]["place"],
                    "magnitude": mag,
                    "time": feature["properties"]["time"],
                    "coordinates": feature["geometry"]["coordinates"]
                })
        return {"events": events}
    except Exception as e:
        return {"error": str(e), "events": []}