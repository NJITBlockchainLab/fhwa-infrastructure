import requests
import json 
import time
import sys
import os

scripts_dir = os.path.dirname(os.path.abspath(__file__))
csv_module_path = os.path.join(scripts_dir,'csv')

if csv_module_path not in sys.path:
    sys.path.append(csv_module_path)


import pothole_csv
directory = os.getcwd()
# Specify the file name
filename = "/home/ubuntu/fhwa-infrastructure/scripts/multicast/csv/Files/eventlog.csv"

csv_file_path = filename #os.path.join(directory, filename)

def get_public_ip():
    try:
        # Using a free API to get the public IP address
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
        # Construct the request
        if method.upper() == 'GET':
            response = requests.get(url, headers=headers)
        elif method.upper() == 'POST':
            response = requests.post(url, headers=headers, data=body, verify=verify)
        else:
            print(f"Unsupported HTTP method: {method}")
            return None

        # Print the response
        print(f"Response Code: {response.status_code}")
        
        print("\n\n")

        return response

    except Exception as e:
        print(f"Error making HTTP request: {e}")
        return None

def send_rows(base_url, completed_connections, rows_to_send):
    try:
        for row_data in rows_to_send:
            # Convert row_data dictionary to a JSON-compatible dictionary
            content = {k: v for k, v in row_data.items()}
            print("Sending message:", content)
            body_dict = {"content": content}
            body = json.dumps(body_dict)
            method = 'POST'
            # Print the result
            for connection in completed_connections:
                url = base_url + "connections/" + connection + "/send-message"
                response_post = make_http_request(url, method, body=body)
                print(response_post.status_code)
                print(response_post.text)
                if(response_post.status_code != 200):
                    raise Exception("Unable to send message to connection " + connection)
    except Exception as e:
        print(f"Error sending rows: {e}")

# Example usage:
if __name__ == "__main__":
    frequency = input("Enter the wait time in seconds: ")
    rows_to_send_count = int(input("Enter the number of rows to send simultaneously: "))

    total_rows = pothole_csv.get_number_of_rows(csv_file_path)
    current_row = 1

    while current_row <= total_rows:
        public_ip = get_public_ip()
        base_url = "http://" + public_ip + ":8054/"
        url = base_url + "connections"
        
        method = 'GET'
        response = make_http_request(url, method)

        if response and response.status_code == 200:
            try:
                response_json = response.json()
                completed_connections = [entry["connection_id"] for entry in response_json.get("results", []) if entry.get("rfc23_state") == "completed"]

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

            except json.JSONDecodeError as e:
                print(f"Error decoding JSON: {e}")
        
        time.sleep(int(frequency))
