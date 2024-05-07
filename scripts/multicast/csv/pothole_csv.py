import csv
import os

# Example usage:
# The directory where the CSV file is located
directory = os.getcwd()
# The file name
filename = "Files/pothole.csv"

csv_file_path = os.path.join(directory, filename)


def get_number_of_rows(csv_file):
    with open(csv_file, mode='r') as file:
        csv_reader = csv.DictReader(file)
        return sum(1 for row in csv_reader)

def get_row(csv_file, row_number):
    with open(csv_file, mode='r') as file:
        csv_reader = csv.DictReader(file)
        for index, row in enumerate(csv_reader, start=1):
            if index == row_number:
                return row
    return None

def parse_gps_data(csv_file, row_number):
    row = get_row(csv_file, row_number)
    if row:
        gps_str = row.get('gps', '')
        if gps_str:
            gps_values = gps_str.strip('[]').split(',')
            gps_values = [float(value.strip()) for value in gps_values]
            if len(gps_values) == 2:
                return gps_values
    return None

if __name__ == "__main__":
    row_number = 1  # Row number
    gps_values = parse_gps_data(csv_file_path, row_number)
    if gps_values:
        print("GPS values for row", row_number, ":", gps_values)
    else:
        print("Row not found or GPS values could not be parsed.")
