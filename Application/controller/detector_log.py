import csv
import os
from datetime import datetime


class Detector_Log:
    def __init__(self, save_directory, angles_list):
        self.save_directory = save_directory
        self.angles_list = angles_list
        self.file_path = self.create_csv_file()

    def create_csv_file(self):
        # Generate the timestamp for the filename
        current_time = datetime.now().strftime('%-I.%M%p').lower()
        file_name = f'anomalies_{current_time}.csv'
        file_path = os.path.join(self.save_directory, file_name)

        # Create the file and write the header
        with open(file_path, mode='w', newline='') as file:
            writer = csv.writer(file)
            header = ['Timestamp'] + self.angles_list
            writer.writerow(header)

        return file_path

    def log_data(self, data):
        # Get current timestamp
        current_timestamp = datetime.now().strftime('%-I.%M%p').lower()

        # Convert numeric data to string for concatenation with the timestamp
        str_data = [str(x) for x in data]

        # Combine timestamp with the data
        row = [current_timestamp] + str_data

        # Write the data to the CSV file
        with open(self.file_path, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(row)
