import csv
import os
from datetime import datetime


class Detector_Log:
    def __init__(self, save_directory, angles_list, anomaly_threshold_value_list):
        self.save_directory = save_directory
        self.angles_list = angles_list
        self.anomaly_threshold_value_list = [int(x) for x in anomaly_threshold_value_list]
        self.file_paths = self.create_csv_file()

    def create_csv_file(self):
        # Generate the timestamp for the filename
        current_time = datetime.now().strftime('%-I.%M%p').lower()
        filepath_lists = []

        for value in self.anomaly_threshold_value_list:
            file_name = f'anomalies_{value}_{current_time}.csv'
            file_path = os.path.join(self.save_directory, file_name)

            # Create the file and write the header
            with open(file_path, mode='w', newline='') as file:
                writer = csv.writer(file)
                header = ['Timestamp'] + self.angles_list
                writer.writerow(header)

            filepath_lists.append(file_path)

        return filepath_lists

    def log_data(self, data):

        for filepath, std_data in zip(self.file_paths, data):
            # Get current timestamp
            current_timestamp = datetime.now().strftime('%-I.%M%p').lower()

            # Convert numeric data to string for concatenation with the timestamp
            str_data = [str(x) for x in std_data]

            # Combine timestamp with the data
            row = [current_timestamp] + str_data

            # Write the data to the CSV file
            with open(filepath, mode='a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(row)
