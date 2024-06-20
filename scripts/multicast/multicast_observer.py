import os
import sys
import time
import json
import requests
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

def get_public_ip():
    try:
        response = requests.get('https://api.ipify.org')
        if response.status_code == 200:
            return response.text
        else:
            print("Failed to retrieve IP address. Status code:", response.status_code)
            sys.exit(1)
    except requests.RequestException as e:
        print("Error:", e)
        sys.exit(1)

public_ip = get_public_ip()
base_url = "http://" + public_ip + ":8054/"

scripts_dir = os.path.dirname(os.path.abspath(__file__))
csv_module_path = os.path.join(scripts_dir, 'csv')

if csv_module_path not in sys.path:
    sys.path.append(csv_module_path)
import send_rows_from_csv

class CSVChangeHandler(FileSystemEventHandler):
    def __init__(self, csv_file_path):
        self.csv_file_path = csv_file_path

    def on_modified(self, event):
        if event.src_path == self.csv_file_path:
            print(f"Detected changes in {self.csv_file_path}")
            self.process_csv()

    def process_csv(self):
        try:
            url = base_url + "connections"
            method = 'GET'
            response = make_http_request(url, method)

            if response and response.status_code == 200:
                try:
                    response_json = response.json()
                    completed_connections = [entry["connection_id"] for entry in response_json.get("results", []) if entry.get("rfc23_state") == "completed"]

                    # Get all rows in the CSV file
                    total_rows = send_rows_from_csv.get_number_of_rows(self.csv_file_path)
                    rows_to_send = [send_rows_from_csv.get_row(self.csv_file_path, row) for row in range(1, total_rows + 1)]

                    if rows_to_send:
                        send_rows(base_url, completed_connections, rows_to_send)
                    else:
                        print("No rows to send.")

                except json.JSONDecodeError as e:
                    print(f"Error decoding JSON: {e}")
        except Exception as e:
            print(f"Error processing CSV: {e}")

def make_http_request(url, method='GET', headers=None, body=None, verify=False):
    try:
        if method.upper() == 'GET':
            response = requests.get(url, headers=headers)
        elif method.upper() == 'POST':
            response = requests.post(url, headers=headers, data=body, verify=verify)
        else:
            print(f"Unsupported HTTP method: {method}")
            return None

        print(f"Response Code: {response.status_code}")
        return response

    except Exception as e:
        print(f"Error making HTTP request: {e}")
        return None

def send_rows(base_url, completed_connections, rows_to_send):
    try:
        for row_data in rows_to_send:
            content = {k: v for k, v in row_data.items()}
            print("Sending message:", content)
            body_dict = {"content": content}
            body = json.dumps(body_dict)
            method = 'POST'

            for connection in completed_connections:
                url = base_url + "connections/" + connection + "/send-message"
                response_post = make_http_request(url, method, body=body)
                print(response_post.status_code)
                print(response_post.text)
                if response_post.status_code != 200:
                    raise Exception("Unable to send message to connection " + connection)
    except Exception as e:
        print(f"Error sending rows: {e}")

if __name__ == "__main__":
    csv_directory = os.getenv('CSV_PATH')
    if not csv_directory:
      csv_directory = input("Enter the directory containing the CSV file: ")

    csv_file_path = os.path.join(os.path.abspath(csv_directory), 'eventlog.csv')
    print(f"Using CSV file path: {csv_file_path}")

    event_handler = CSVChangeHandler(csv_file_path)
    observer = Observer()
    observer.schedule(event_handler, path=os.path.dirname(csv_file_path), recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(0.5)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()
