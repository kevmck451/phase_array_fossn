import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import QApplication, QFileDialog

# Use native macOS dialog via PyQt
app = QApplication(sys.argv)
file_path, _ = QFileDialog.getOpenFileName(None, "Select CSV File", "", "CSV Files (*.csv)")
app.exit()

if not file_path:
    print("No file selected.")
    sys.exit()

df = pd.read_csv(file_path)
frequencies = df.columns[1:]
data = df.iloc[:, 1:].to_numpy()
vmax = np.max(data)

plt.figure(figsize=(15, 20))
plt.imshow(data, aspect='auto', cmap='hot', origin='lower', vmax=vmax)
plt.colorbar(label='Value')
plt.xlabel('Frequency (Hz)')
plt.ylabel('Time (Frame Index)')
plt.xticks(ticks=np.arange(len(frequencies)), labels=frequencies, rotation=90)
plt.title('Time Series Heatmap of Frequencies')
plt.tight_layout(pad=0)
plt.show()
