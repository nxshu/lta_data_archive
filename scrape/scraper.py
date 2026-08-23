import requests
import json
import os
import psycopg2
import psycopg2.extras
from datetime import datetime
from zoneinfo import ZoneInfo

SERVICE_URL = "https://datamall2.mytransport.sg/ltaodataservice/TrainServiceAlerts"
CROWD_URL = "https://datamall2.mytransport.sg/ltaodataservice/PCDRealTime?TrainLine"

LINES = ["CCL", "CEL", "CGL", "DTL", "EWL", "NEL", "NSL", "BPL", "SLRT", "PLRT", "TEL"]

def fetch(url):
    
    payload = {}
    headers = {
      'AccountKey': os.environ["API_KEY"] 
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    response.raise_for_status()

    return response.json()

def get_connection():
    return psycopg2.connect(os.environ["DATABASE_URL"])

def save_service_data(conn, data):
    now = datetime.now(ZoneInfo("Asia/Singapore"))

    status_data = data.get("value", {})

    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO service_status (scraped_at, status, affected_segments, messages, raw)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (
                now,
                status_data.get("Status"),
                json.dumps(status_data.get("AffectedSegments", [])),
                json.dumps(status_data.get("Message", [])),
                json.dumps(status_data)
            )
        )

    conn.commit()

def save_crowd_data(conn, line, data):
    now = datetime.now(ZoneInfo("Asia/Singapore"))
    stations = data.get("value", [])

    rows = []
    for station in stations:
        rows.append((
            now,
            line,
            station.get("Station"),
            station.get("StartTime"),
            station.get("EndTime"),
            station.get("CrowdLevel"),
            json.dumps(station)
        ))

    if not rows:
        return

    with conn.cursor() as cur:
        psycopg2.extras.execute_values(
            cur,
            """
            INSERT INTO crowd_data_station (scraped_at, line, station_code, start_time, end_time, crowd_level, raw)
            VALUES %s
            ON CONFLICT (line, station_code, start_time) DO NOTHING
            """,
            rows
        )

    conn.commit()

def main():
    conn = get_connection()
    try:
        service_data = fetch(SERVICE_URL)
        save_service_data(conn, service_data)

        for line in LINES:
            crowd_data = fetch(CROWD_URL + "=" + line)
            save_crowd_data(conn, line, crowd_data)

    finally:
        conn.close()

if __name__ == "__main__": # when file is run directly
    main()