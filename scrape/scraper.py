import requests
import json
from datetime import datetime
import os
from zoneinfo import ZoneInfo

ENDPOINTS = {
    "train_service_alerts": "https://datamall2.mytransport.sg/ltaodataservice/TrainServiceAlerts",
    "station_crowd_ccl": "https://datamall2.mytransport.sg/ltaodataservice/PCDRealTime?TrainLine=CCL",
    "station_crowd_cel": "https://datamall2.mytransport.sg/ltaodataservice/PCDRealTime?TrainLine=CEL",
    "station_crowd_cgl": "https://datamall2.mytransport.sg/ltaodataservice/PCDRealTime?TrainLine=CGL",
    "station_crowd_dtl": "https://datamall2.mytransport.sg/ltaodataservice/PCDRealTime?TrainLine=DTL",
    "station_crowd_ewl": "https://datamall2.mytransport.sg/ltaodataservice/PCDRealTime?TrainLine=EWL",
    "station_crowd_nel": "https://datamall2.mytransport.sg/ltaodataservice/PCDRealTime?TrainLine=NEL",
    "station_crowd_nsl": "https://datamall2.mytransport.sg/ltaodataservice/PCDRealTime?TrainLine=NSL",
    "station_crowd_bpl": "https://datamall2.mytransport.sg/ltaodataservice/PCDRealTime?TrainLine=BPL",
    "station_crowd_slrt": "https://datamall2.mytransport.sg/ltaodataservice/PCDRealTime?TrainLine=SLRT",
    "station_crowd_plrt": "https://datamall2.mytransport.sg/ltaodataservice/PCDRealTime?TrainLine=PLRT",
    "station_crowd_tel": "https://datamall2.mytransport.sg/ltaodataservice/PCDRealTime?TrainLine=TEL",
}

def fetch(url):
    
    payload = {}
    headers = {
      'AccountKey': os.environ["API_KEY"] 
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    response.raise_for_status()

    return response.json()

def main():
    timestamp = datetime.now(ZoneInfo("Asia/Singapore")).strftime("%Y-%m-%dT%H-%M-%S")

    os.makedirs("data", exist_ok=True)

    for name, url in ENDPOINTS.items():
        try:
            data = fetch(url)
        except requests.exceptions.RequestException as e:
            print(f"Failed to fetch {name}: {e}")
            continue

        log_path = f"data/{name}_log.jsonl"
        with open(log_path, "a") as f: # append mode
            f.write(json.dumps({"timestamp": timestamp, "data": data})  + "\n")

if __name__ == "__main__": # when file is run directly
    main()