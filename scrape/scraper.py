import requests
import json
from datetime import datetime
import os
from zoneinfo import ZoneInfo

SERVICE_ALERT_URL = "https://datamall2.mytransport.sg/ltaodataservice/TrainServiceAlerts"

def fetch(url = SERVICE_ALERT_URL):
    
    payload = {}
    headers = {
      'AccountKey': os.environ["API_KEY"] 
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    response.raise_for_status()

    return response.json()

def main():
    data = fetch()
    timestamp = datetime.now(ZoneInfo("Asia/Singapore")).strftime("%Y-%m-%dT%H-%M-%S")

    os.makedirs("data", exist_ok=True)

    log_path = "data/log.jsonl"
    with open(log_path, "a") as f: # append mode
        f.write(json.dumps({"timestamp": timestamp, "data": data})  + "\n")

if __name__ == "__main__": # when file is run directly
    main()