import requests
import json 
import time
import sys
import os


scripts_dir = os.path.dirname(os.path.abspath(__file__))
csv_module_path = os.path.join(scripts_dir,'csv')

if csv_module_path not in sys.path:
    sys.path.append(csv_module_path)


# Importing the eventlog_csv module
import eventlog_csv

# Define the directory and filename
directory = os.getcwd()
filename = "csv/Files/eventlog.csv"
csv_file_path = os.path.join(directory, filename)

# Function to get the public IP address
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

# Function to make HTTP request
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
        print("\n\n")
        return response

    except Exception as e:
        print(f"Error making HTTP request: {e}")
        return None

# Function to send rows
def send_rows(base_url, completed_connections, gps_data):
    try:
        for gps_value in gps_data:
            content = gps_value
            print("Sending message " + str(content[0]) + "," + str(content[1]))
            body_dict = {"content": content}
            body = json.dumps(body_dict)
            method = 'POST'
            for connection in completed_connections:
                url = base_url + "connections/" + connection + "/send-message"
                response_post = make_http_request(url, method, body=body)
                print(response_post.status_code)
                print(response_post.text)
                if(response_post.status_code != 200):
                    raise Exception("Unable to send message to connection " + connection)
    except Exception as e:
        print(f"Error sending rows: {e}")

# Main function
if __name__ == "__main__":
    longitude = input("Enter the longitude: ")
    latitude = input("Enter the latitude: ")

    # Getting public IP and base URL
    public_ip = get_public_ip()
    base_url = "http://" + public_ip + ":8054/"

    # Calling parse_gps_data function
    gps_data = eventlog_csv.parse_gps_data(csv_file_path, (float(longitude), float(latitude)))

    # Making HTTP request to get connections
    url = base_url + "connections"
    method = 'GET'
    response = make_http_request(url, method)

    if response and response.status_code == 200:
        try:
            response_json = response.json()
            completed_connections = [entry["connection_id"] for entry in response_json.get("results", []) if entry.get("rfc23_state") == "completed"]
            if gps_data:
                send_rows(base_url, completed_connections, gps_data)
            else:
                print("No GPS data found.")
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
