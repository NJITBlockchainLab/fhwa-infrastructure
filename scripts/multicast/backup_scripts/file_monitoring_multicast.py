import os
import sys
import time
import json
import requests
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

scripts_dir = os.path.dirname(os.path.abspath(__file__))
csv_module_path = os.path.join(scripts_dir, 'csv')

if csv_module_path not in sys.path:
    sys.path.append(csv_module_path)

import pothole_csv

directory_to_watch = "/home/ubuntu/fhwa-infrastructure/scripts/multicast/csv/Files"  # Replace with the directory you want to monitor

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
        print("Response Text:", response.text)
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

class NewCSVHandler(FileSystemEventHandler):
    def __init__(self, processed_files):
        self.processed_files = processed_files

    def on_created(self, event):
        if not event.is_directory and event.src_path.endswith(".csv"):
            if event.src_path not in self.processed_files:
                self.processed_files.add(event.src_path)
                print(f"New CSV file detected: {event.src_path}")
                self.process_csv(event.src_path)

    def process_csv(self, csv_file_path):
        try:
            public_ip = get_public_ip()
            print(f"Public IP: {public_ip}")
            base_url = "http://" + public_ip + ":8054/"
            url = base_url + "connections"
            method = 'GET'
            response = make_http_request(url, method)
            if response and response.status_code == 200:
                try:
                    response_json = response.json()
                    completed_connections = [entry["connection_id"] for entry in response_json.get("results", []) if entry.get("rfc23_state") == "completed"]
                    print(f"Completed connections: {completed_connections}")

                    total_rows = pothole_csv.get_number_of_rows(csv_file_path)
                    print(f"Total rows in CSV: {total_rows}")
                    current_row = 1
                    rows_to_send_count = 10  # Adjust this as needed
                    while current_row <= total_rows:
                        rows_to_send = []
                        for _ in range(rows_to_send_count):
                            row_data = pothole_csv.get_row(csv_file_path, current_row)
                            if row_data:
                                rows_to_send.append(row_data)
                                current_row += 1
                            else:
                                break

                        if rows_to_send:
                            send_rows(base_url, completed_connections, rows_to_send)
                        else:
                            print("No more rows to send.")
                        time.sleep(1)  # Adjust the delay as needed
                except json.JSONDecodeError as e:
                    print(f"Error decoding JSON: {e}")
        except Exception as e:
            print(f"Error processing CSV file: {e}")

def process_existing_files(directory):
    processed_files = set()
    for filename in os.listdir(directory):
        if filename.endswith(".csv"):
            filepath = os.path.join(directory, filename)
            processed_files.add(filepath)
            print(f"Processing existing file: {filepath}")
            handler = NewCSVHandler(processed_files)
            handler.process_csv(filepath)
    return processed_files

if __name__ == "__main__":
    processed_files = process_existing_files(directory_to_watch)

    event_handler = NewCSVHandler(processed_files)
    observer = Observer()
    observer.schedule(event_handler, directory_to_watch, recursive=False)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
