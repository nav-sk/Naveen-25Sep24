import io
import json
import time

import pandas as pd
import requests

# Base URL for the API
URL = "http://localhost:8000/"


def trigger_report() -> str | None:
    """Trigger the report generation and return the report ID."""
    path = "trigger_report/"
    response = requests.get(URL + path)
    if response.status_code == 200:
        try:
            parsed_data = json.loads(response.text)
            return parsed_data["report_id"]
        except json.JSONDecodeError:
            print("Error parsing JSON")
            return None
    else:
        print(f"Error: {response.status_code}")
        return None


def get_report(report_id: str) -> None:
    """Get the report data for the given report ID."""
    path = f"get_report/?report_id={report_id}"
    start_time = time.time()
    while True:
        time.sleep(5)  # Setting the polling interval as 5 seconds
        response = requests.get(URL + path)
        if response.status_code == 200:
            try:
                parsed_data = json.loads(response.text)
                # If the report is complete, print the report data
                if parsed_data["status"] == "Complete":
                    df = pd.read_csv(io.StringIO(parsed_data["report"]))
                    df.to_csv("report.csv", index=False)
                    print(df)
                    break
                # If the report is still running, print the time elapsed
                elif parsed_data["status"] == "Running":
                    print(
                        "Report is still running. Time elapsed: %d s"
                        % int(time.time() - start_time),
                    )
            except json.JSONDecodeError:
                print("Error parsing JSON")
                break
        else:
            print(f"Error: {response.status_code}")
            break


if __name__ == "__main__":
    # Trigger the report generation
    report_id = trigger_report()
    print("Report ID: ", report_id)
    # If the report ID is generated, get the report data
    if report_id:
        get_report(report_id)
