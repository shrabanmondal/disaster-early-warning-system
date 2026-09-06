# 🚨 Real-Time Disaster Early Warning System (PWA)

A lightweight, full-stack Progressive Web Application (PWA) that polls real-time seismic data from the USGS API, stores alerts in an SQLite database, and presents an interactive web interface with automatic native time zone detection, live map pins, and browser emergency alerts.

## 🌟 Features

- **FastAPI Backend**: Serves RESTful endpoints and manages static file hosting.
- **USGS Telemetry Ingestion**: Background script actively monitors active global seismic events.
- **Native Timezone Formatting**: Formats timestamps into the viewer's local time zone automatically.
- **PWA Installation**: Installable directly on desktop and mobile devices via Web Manifest and Service Worker (`sw.js`).
- **Interactive Mapping**: Visualizes earthquake locations using Leaflet.js.
- **Audio & Popup Notifications**: Triggers system alerts for seismic events $\ge 4.0$ magnitude.

## 🛠️ Tech Stack

- **Backend**: Python, FastAPI, Uvicorn, SQLite3, Requests
- **Frontend**: HTML5, CSS3, JavaScript (ES6+), Leaflet.js
- **PWA Architecture**: Web App Manifest, Service Workers, Browser Notification API

## 🚀 Getting Started

### Prerequisites

- Python 3.9+
- Git

### Installation & Setup

1. **Clone the Repository**
   ```bash
   git clone [https://github.com/YOUR_USERNAME/disaster-early-warning-app.git](https://github.com/YOUR_USERNAME/disaster-early-warning-app.git)
   cd disaster-early-warning-app