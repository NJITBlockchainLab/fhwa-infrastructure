import csv
import os
import math

# Function to calculate the bounding box coordinates from a fixed radius
def calculate_bounding_box(lat, lon, radius):
    # Earth's radius in meters
    earth_radius = 6371000

    # Convert latitude and longitude to radians
    lat_rad = math.radians(lat)
    lon_rad = math.radians(lon)

    # Calculate the distance in radians
    dist_rad = radius / earth_radius

    # Calculate the minimum and maximum latitudes
    min_lat = lat_rad - dist_rad
    max_lat = lat_rad + dist_rad

    # Calculate the minimum and maximum longitudes
    min_lon = lon_rad - dist_rad / math.cos(lat_rad)
    max_lon = lon_rad + dist_rad / math.cos(lat_rad)

    # Convert back to degrees
    min_lat = math.degrees(min_lat)
    max_lat = math.degrees(max_lat)
    min_lon = math.degrees(min_lon)
    max_lon = math.degrees(max_lon)

    return min_lat, max_lat, min_lon, max_lon

def parse_gps_data(csv_file, gps_location, radius=500):
    min_lat, max_lat, min_lon, max_lon = calculate_bounding_box(gps_location[0], gps_location[1], radius)

    data = {}

    with open(csv_file, "r") as csv_file:
        csv_reader = csv.reader(csv_file)

        header = next(csv_reader)

        for row in csv_reader:
            try:
                # Extract values from the row
                event, gps_str, speed, timestamp = row

                # Parse GPS coordinates
                lat, lon = eval(gps_str)

                # Check if the GPS coordinates fall within the bounding box
                if min_lat <= lat <= max_lat and min_lon <= lon <= max_lon:
                    data[(lat, lon)] = {'event': event, 'speed': float(speed), 'timestamp':str(timestamp)}

            except ValueError as e:
                continue

    return data

if __name__ == "__main__":
    # The directory where the CSV file is located
    directory = os.getcwd()

    # The file name
    filename = "/Files/eventlog.csv"

    csv_file_path = os.path.abspath(directory + filename)

    gps_location = (40.36043581976105, -74.59656142995496)  # Example GPS coordinates
    radius = 500  # Radius in meters

    data = parse_gps_data(csv_file_path, gps_location, radius)

    # Iterate over the data dictionary
    for gps_coords, event_data in data.items():
        lat, lon = gps_coords
        event = event_data['event']
        speed = event_data['speed']
        timestamp = event_data['timestamp']
        print("GPS Coordinates:", gps_coords)
        print("Event:", event)
        print("Speed:", speed)
        print("Timestamp:", timestamp)
        print()
