# Functions for utilities

import csv


class CSVFile:
    def __init__(self, file_path):
        self.file_path = str(file_path)
        self.header, self.data = self._read_csv_file()

    def _read_csv_file(self):
        with open(self.file_path, 'r', encoding='utf-8-sig') as csvfile:
            csvreader = csv.reader(csvfile)
            data = list(csvreader)
        header = [column.strip('\ufeff') for column in data[0]]  # Remove the BOM character from the first column
        return header, data[1:]

    def print_entries(self):
        for row in self.data:
            print(', '.join(row))

    def get_column(self, column_name):
        column_index = self.header.index(column_name)
        column_data = [row[column_index] for row in self.data]
        return column_data

    def filter_rows(self, condition):
        filtered_data = [row for row in self.data if condition(row)]
        return filtered_data

    def csv_entries(self):
        csv_list = []
        with open(self.file_path, 'r') as csvfile:
            csvreader = csv.reader(csvfile)
            for row in csvreader:
                csv_list.append(', '.join(row))
                # print(', '.join(row))
        return csv_list

    def sorted_csv_entries(self, sort_column):
        sorted_data = []
        with open(self.file_path, 'r') as csvfile:
            csvreader = csv.reader(csvfile)
            header = next(csvreader)  # Read the header row
            header = [column.strip('\ufeff') for column in header]
            column_index = header.index(sort_column)
            sorted_rows = sorted(csvreader, key=lambda row: row[column_index].lstrip('\ufeff'))

            for row in sorted_rows:
                sorted_data.append([', '.join(row)])

        return sorted_data

    def get_value(self, sample_name, header_name):
        sample_index = self.header.index(header_name)
        for row in self.data:
            if row[0] == sample_name:
                return row[sample_index]
        return None

    def update_value(self, sample_name, header_name, value):
        sample_index = self.header.index(header_name)
        for row in self.data:
            if row[0] == sample_name:
                row[sample_index] = value
                break

    def add_column(self, header_name, column_data):
        self.header.append(header_name)
        for i in range(len(self.data)):
            self.data[i].append(column_data[i] if i < len(column_data) else "")

    def replace_column(self, header_name, new_column_data):
        column_index = self.header.index(header_name)
        for i in range(len(self.data)):
            self.data[i][column_index] = new_column_data[i] if i < len(new_column_data) else ""

    def rename_headers(self, new_headers):
        if len(new_headers) != len(self.header):
            raise ValueError("The number of new headers must match the number of existing headers.")
        self.header = new_headers

        # Write the modified data back to the CSV file
        with open(self.file_path, 'w', newline='', encoding='utf-8-sig') as csvfile:
            csvwriter = csv.writer(csvfile)
            csvwriter.writerow(self.header)
            csvwriter.writerows(self.data)

    def save_changes(self):
        with open(self.file_path, 'w', newline='', encoding='utf-8-sig') as csvfile:
            csvwriter = csv.writer(csvfile)
            csvwriter.writerow(self.header)
            csvwriter.writerows(self.data)

