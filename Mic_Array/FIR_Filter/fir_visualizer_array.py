
from Mic_Array.FIR_Filter.mic_coordinates import generate_mic_coordinates
from Mic_Array.FIR_Filter.time_delays import calculate_time_delays
from Mic_Array.FIR_Filter.fir_filter import create_fir_filters



from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from tkinter import ttk
import tkinter as tk


class FIRFilterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("FIR Filter Visualization")

        self.theta = 0  # elevation angle
        self.phi = 0  # azimuth angle
        self.temperature_F = 95  # temperature in Fahrenheit
        self.sample_rate = 48000
        self.num_taps = 151  # should be odd

        self.mic_coordinates = generate_mic_coordinates()

        self.setup_ui()
        self.root.after(200, self.update_plot)  # Initial plot update after a delay

    def setup_ui(self):
        self.figure = plt.figure(figsize=(24, 12))
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.root)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        self.theta_label = tk.Label(self.root, text="Theta (Elevation): 0")
        self.theta_label.pack(side=tk.LEFT, padx=5)

        self.theta_slider = ttk.Scale(self.root, from_=-90, to=90, orient=tk.HORIZONTAL)
        self.theta_slider.set(self.theta)
        self.theta_slider.pack(side=tk.LEFT, padx=10, pady=10)
        self.theta_slider.bind("<Motion>", self.on_slider_change)
        self.theta_slider.bind("<ButtonRelease-1>", self.on_slider_change)

        self.phi_label = tk.Label(self.root, text="Phi (Azimuth): 0")
        self.phi_label.pack(side=tk.RIGHT, padx=5)

        self.phi_slider = ttk.Scale(self.root, from_=-90, to=90, orient=tk.HORIZONTAL)
        self.phi_slider.set(self.phi)
        self.phi_slider.pack(side=tk.RIGHT, padx=10, pady=10)
        self.phi_slider.bind("<Motion>", self.on_slider_change)
        self.phi_slider.bind("<ButtonRelease-1>", self.on_slider_change)

    def on_slider_change(self, event):
        self.root.after(300, self.update_plot)  # Debounce the slider event

    def update_plot(self):
        theta = self.theta_slider.get()
        phi = self.phi_slider.get()
        if theta == self.theta and phi == self.phi:
            return  # No change in slider values

        self.theta = theta
        self.phi = phi

        # Update the labels with the current angles
        self.theta_label.config(text=f"Theta (Elevation): {self.theta:.2f}")
        self.phi_label.config(text=f"Phi (Azimuth): {self.phi:.2f}")

        time_delays = calculate_time_delays(self.mic_coordinates, self.theta, self.phi, self.temperature_F, self.sample_rate)
        fir_filter = create_fir_filters(time_delays, self.num_taps)

        num_rows = len(fir_filter)
        num_cols = len(fir_filter[0]) if num_rows > 0 else 0

        if not hasattr(self, 'axes'):
            self.axes = self.figure.subplots(num_rows, num_cols)

        for i, row in enumerate(fir_filter):
            for j, data in enumerate(row):
                ax = self.axes[i, j] if num_rows > 1 else self.axes[j]
                ax.clear()
                ax.plot(data)
                ax.set_title(f'Filter {i + 1}-{j + 1}')

        self.figure.tight_layout()
        self.canvas.draw()

if __name__ == '__main__':
    root = tk.Tk()
    app = FIRFilterApp(root)
    root.mainloop()
