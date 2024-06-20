import os
import json
import time
import sys
import asyncio
import aiohttp
from flask import Flask, request, jsonify
import requests
scripts_dir = os.path.dirname(os.path.abspath(__file__))
csv_module_path = os.path.join(scripts_dir,'csv')

if csv_module_path not in sys.path:
    sys.path.append(csv_module_path)

import pothole_csv  

app = Flask(__name__)

# Global variables for frequency and rows_to_send_count
frequency = None
rows_to_send_count = None

# Function to get public IP
def get_public_ip():
    try:
        response = requests.get('https://api.ipify.org')
        if response.status_code == 200:
            return response.text.strip()
        else:
            print("Failed to retrieve IP address. Status code:", response.status_code)
            return None
    except requests.RequestException as e:
        print("Error:", e)
        return None

# Function to send rows asynchronously
async def send_rows_async(base_url, completed_connections, rows_to_send):
    async with aiohttp.ClientSession() as session:
        tasks = []
        for row_data in rows_to_send:
            content = {k: v for k, v in row_data.items()}
            body_dict = {"content": content}
            body = json.dumps(body_dict)
            method = 'POST'
            for connection in completed_connections:
                url = base_url + "connections/" + connection + "/send-message"
                tasks.append(asyncio.create_task(make_http_request_async(session, url, method, body)))
        await asyncio.gather(*tasks)

# Asynchronous HTTP request function
async def make_http_request_async(session, url, method='GET', headers=None, body=None, verify=False):
    try:
        if method.upper() == 'GET':
            async with session.get(url, headers=headers) as response:
                return await response.json(), response.status
        elif method.upper() == 'POST':
            async with session.post(url, headers=headers, data=body, ssl=verify) as response:
                return await response.json(), response.status
        else:
            return None, None
    except Exception as e:
        print(f"Error making HTTP request: {e}")
        return None, None

# Flask route to handle CSV upload and processing
@app.route('/csv', methods=['POST'])
def handle_csv_upload():
    try:
        global frequency, rows_to_send_count
        
        if 'file' not in request.files:
            return jsonify({"error": "No file part in the request"}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No selected file"}), 400

        # Save the uploaded CSV file temporarily
        filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filename)

        # Process the CSV file
        rows_to_send = pothole_csv.process_csv(filename)

        if not rows_to_send:
            return jsonify({"message": "No data found in the CSV"}), 400

        # Asynchronously send rows
        asyncio.create_task(send_rows_async(base_url, completed_connections, rows_to_send))  # Use create_task for non-blocking call

        return jsonify({"message": f"Rows sent to connections asynchronously"}), 200

    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

# Function to periodically send rows
async def send_rows_periodically(csv_file_path):
    global frequency, rows_to_send_count

    while True:
        if frequency and rows_to_send_count:
            total_rows = pothole_csv.get_number_of_rows(csv_file_path)
            current_row = 1

            while current_row <= total_rows:
                public_ip = get_public_ip()
                base_url = "http://" + public_ip + ":8054/"
                url = base_url + "connections"

                method = 'GET'
                response, status_code = await make_http_request_async(aiohttp.ClientSession(), url, method)

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
                            await send_rows_async(base_url, completed_connections, rows_to_send)
                        else:
                            print("No more rows to send.")

                    except json.JSONDecodeError as e:
                        print(f"Error decoding JSON: {e}")

            await asyncio.sleep(int(frequency))

# Set up asyncio loop and start sending rows periodically
if __name__ == "__main__":
    app.config['UPLOAD_FOLDER'] = '/path/to/upload/folder'  # Adjust this path
    frequency = input("Enter the wait time in seconds: ")
    rows_to_send_count = int(input("Enter the number of rows to send simultaneously: "))
    csv_file_path = "/home/ubuntu/fhwa-infrastructure/scripts/test.csv"  # Adjust this path

    asyncio.run(send_rows_periodically(csv_file_path))
