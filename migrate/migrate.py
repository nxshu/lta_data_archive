import json
import os
import psycopg2
import psycopg2.extras
from datetime import datetime
from zoneinfo import ZoneInfo

DATABASE_URL = os.environ["DATABASE_URL"]

def parse_ts(ts_str):
    dt = datetime.strptime(ts_str, "%Y-%m-%dT%H-%M-%S")
    return dt.replace(tzinfo = ZoneInfo("Asia/Singapore"))

def migrate_service_status(conn, filepath):
    rows = []
    with open(filepath) as f:
        for raw_line in f:
            raw_line = raw_line.strip()
            if not raw_line:
                continue
            record = json.loads(raw_line)
            scraped_at = parse_ts(record["timestamp"])
            status_data = record["data"].get("value", {})

            rows.append((
                scraped_at,
                status_data.get("Status"),
                json.dumps(status_data.get("AffectedSegments", [])),
                json.dumps(status_data.get("Message", [])),
                json.dumps(status_data)
            ))

    if not rows:
        print(f"No rows found in {filepath}")
        return

    with conn.cursor() as cur:
        psycopg2.extras.execute_values(
            cur,
            """
            INSERT INTO service_status (scraped_at, status, affected_segments, messages, raw)
            VALUES %s
            """,
            rows
        )

    conn.commit()
    print(f"Migrated {len(rows)} rows from {filepath} into service_status")


def migrate_crowd_file(conn, filepath, line_name):
    rows = []
    with open(filepath) as f:
        for raw_line in f:
            raw_line = raw_line.strip()
            if not raw_line:
                continue
            record = json.loads(raw_line)
            scraped_at = parse_ts(record["timestamp"])
            stations = record["data"].get("value", [])

            for station in stations:
                rows.append((
                    scraped_at,
                    line_name,
                    station.get("Station"),
                    station.get("StartTime"),
                    station.get("EndTime"),
                    station.get("CrowdLevel"),
                    json.dumps(station)
                ))

    if not rows:
        print(f"No rows found in {filepath}")
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
    print(f"Migrated {len(rows)} station-entries from {filepath} ({line_name})")

def main():
    conn = psycopg2.connect(DATABASE_URL)
    try:
        # migrate_service_status(conn, "data/train_service_alerts_log.jsonl")

        lines = ["bpl", "ccl", "cel", "cgl", "dtl", "ewl", "nel", "nsl", "plrt", "slrt", "tel"]

        crowd_files = {line.upper(): "data/station_crowd_" + line + "_log.jsonl" for line in lines}

        for line_name, filepath in crowd_files.items():
            if os.path.exists(filepath):
                migrate_crowd_file(conn, filepath, line_name)
            else:
                print(f"Skipping missed file: {filepath}")

    finally:
        conn.close()

if __name__ == "__main__":
    main()