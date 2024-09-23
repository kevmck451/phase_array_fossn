import numpy as np
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtWidgets
import pandas as pd
import os
from PyQt5.QtWidgets import QFileDialog

# Function to load data from CSV file
def load_data(file_path):
    try:
        data = pd.read_csv(file_path)
        return data
    except Exception as e:
        print(f"Error loading data: {e}")
        return pd.DataFrame()  # Return an empty DataFrame in case of error

# Function to find the latest CSV file based on the naming convention
def find_latest_log_file(anomaly_folder):
    files = [f for f in os.listdir(anomaly_folder) if f.startswith('anomalies_') and f.endswith('.csv')]
    if files:
        latest_file = max(files, key=lambda x: os.path.getctime(os.path.join(anomaly_folder, x)))
        return os.path.join(anomaly_folder, latest_file)
    else:
        return None

# Main PyQtGraph-based plotter class
class RealTimePlotter:
    def __init__(self, anomaly_folder):
        self.app = QtWidgets.QApplication([])  # PyQtGraph's app
        self.win = pg.GraphicsLayoutWidget(show=True)
        self.win.setWindowTitle('Real-Time Sliding Window Plot')

        # Create a 2D image plot
        self.plot = self.win.addPlot()
        self.img = pg.ImageItem()
        self.plot.addItem(self.img)
        self.plot.setLabel('left', 'Time (Last 30 slots)')
        self.plot.setLabel('bottom', 'Angles')

        # Set up the color map
        self.cmap = pg.colormap.get('viridis')  # Get the 'viridis' color map

        # Initialize the data array for the sliding window (30 time slots, 10 angles)
        self.time_window = 30
        self.data_window = np.zeros((self.time_window, 10))  # Assuming 10 angles for now
        self.anomaly_folder = anomaly_folder
        self.log_file = None
        self.timestamps = [f"{i + 1}s" for i in range(self.time_window)]  # Time slots labeled 1s to 30s

        # Start a timer to update the plot every second
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_plot)
        self.timer.start(1000)  # Update every 1 second

    def update_plot(self):
        # Check for the anomaly file
        if self.log_file is None:
            print("Looking for the anomaly file...")
            self.log_file = find_latest_log_file(self.anomaly_folder)
            if self.log_file is None:
                print("Anomaly file not found.")
                return

        # Load the latest data from the file
        df = load_data(self.log_file)
        if df.empty:
            print("Anomaly file is empty or failed to load.")
            return

        # Get the most recent row of data (or first row if only one exists)
        recent_data = df.tail(1)  # Only take the last row of data

        # If 'Timestamp' exists, drop it as we don't want it in the plot
        if 'Timestamp' in recent_data.columns:
            recent_data = recent_data.drop(columns=['Timestamp'])

        # Convert the data to numeric
        recent_data = recent_data.apply(pd.to_numeric, errors='coerce').fillna(0)

        # Update the sliding window by pushing old data out
        self.data_window = np.roll(self.data_window, -1, axis=0)
        self.data_window[-1] = recent_data.values[0]  # Insert the latest data into the last row

        # Update the plot with the new data
        self.img.setImage(self.data_window.T)  # Transpose to match angles on x-axis
        self.img.setLookupTable(self.cmap.getLookupTable())

        # Set the y-axis labels to reflect time (1s to 30s)
        self.plot.getAxis('left').setTicks([[(i, self.timestamps[i]) for i in range(self.time_window)]])

    def run(self):
        QtWidgets.QApplication.instance().exec_()

# Main logic to start the real-time plotter
def main():
    # Open folder selection dialog to select the anomaly folder
    app = QtWidgets.QApplication([])  # Need an app to show the dialog
    anomaly_folder = str(QFileDialog.getExistingDirectory(None, "Select Anomaly Folder"))
    if not anomaly_folder:
        print("No folder selected, exiting.")
        return

    print(f"Selected folder: {anomaly_folder}")

    plotter = RealTimePlotter(anomaly_folder)
    plotter.run()

if __name__ == '__main__':
    main()
