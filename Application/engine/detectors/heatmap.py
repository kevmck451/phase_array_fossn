
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from PIL import Image
import pandas as pd
import numpy as np
import glob
import os
import io


class Heatmap:
    def __init__(self, max_time_steps=120):
        self.max_time_steps = max_time_steps
        self.anomaly_matrix = None
        self.max_value_seen_global = 0
        self.max_value_seen = 0
        self.current_thetas = []
        self.smoothing_window = 3
        self.update_counter = 0
        self.should_log = False
        self.matrix_filled_once = False
        self.raw_input_buffer = []

    def update(self, thetas, values, max_value_seen_setting='global'):
        if len(thetas) != len(values):
            raise ValueError("Length of thetas and values must match")

        self.current_thetas = list(thetas)
        num_bins = len(thetas)
        new_row = np.array(values)

        # Initialize all tracking on first run or dimension change
        if (
                not hasattr(self, "anomaly_matrix")
                or self.anomaly_matrix is None
                or self.anomaly_matrix.shape[1] != num_bins
        ):
            self.anomaly_matrix = np.zeros((0, num_bins))
            self.raw_input_buffer = []
            self.matrix_filled_once = False
            self.update_counter = 0
            self.should_log = False

        # Keep raw input history
        self.raw_input_buffer.append(new_row)
        if len(self.raw_input_buffer) > self.smoothing_window:
            self.raw_input_buffer.pop(0)

        # Compute smoothed row
        if len(self.raw_input_buffer) >= self.smoothing_window:
            smoothed_row = np.mean(self.raw_input_buffer, axis=0)
        else:
            smoothed_row = new_row

        # Stack the new row
        smoothed_row = smoothed_row.reshape(1, -1)  # ensure shape (1, N)
        self.anomaly_matrix = np.vstack([self.anomaly_matrix, smoothed_row])

        # Trim to rolling window
        if self.anomaly_matrix.shape[0] > self.max_time_steps:
            self.anomaly_matrix = self.anomaly_matrix[1:]

        # Log logic
        if self.anomaly_matrix.shape[0] == self.max_time_steps:
            if not self.matrix_filled_once:
                self.matrix_filled_once = True
                self.update_counter = 0
                self.should_log = True
                self.raw_input_buffer = []
            else:
                self.update_counter += 1
                if self.update_counter >= self.max_time_steps:
                    self.should_log = True
                    self.update_counter = 0
                else:
                    self.should_log = False
        else:
            self.should_log = False

        self.max_value_seen_global = max(self.max_value_seen, np.max(new_row))
        if max_value_seen_setting == 'global':
            self.max_value_seen = self.max_value_seen_global
        elif max_value_seen_setting == 'local':
            self.max_value_seen = np.max(self.anomaly_matrix)

    def render_heatmap_image(self, cmap, vert_max, scale_factor=1, width=550, height=440):
        if self.anomaly_matrix is None or self.anomaly_matrix.shape[0] == 0:
            return None

        fig = Figure(figsize=(width / 100, height / 100), dpi=100)
        canvas = FigureCanvas(fig)
        ax = fig.add_subplot(111)

        if self.anomaly_matrix is None:
            return None

        # vert_max ranges from 1 to 200
        sensitivity = int(vert_max)

        # prevent divide-by-zero or overflow
        if self.max_value_seen <= 0:
            vmax = 1
        else:
            # Higher sensitivity lowers vmax (more sensitive to lower values)
            # Lower sensitivity raises vmax (darker image, only strong stuff visible)
            # Map 1–200 to a scale where 100 means normal, <100 is more cutoff, >100 is more exposure
            scale = (100 / sensitivity) ** scale_factor
            vmax = self.max_value_seen * scale

        # cubehelix # hot # inferno # gist_heat # bone # gist_earth # gnuplot2  # viridis
        if cmap == "Visual 1": cmap = 'gnuplot2'
        elif cmap == "Visual 2": cmap = 'cubehelix'
        elif cmap == "Visual 3": cmap = 'inferno'
        else: cmap = 'hot'

        ax.imshow(
            self.anomaly_matrix,
            aspect='auto',
            cmap=cmap,
            vmin=0,
            vmax=vmax,
            origin='upper',
            interpolation='gaussian',
            extent=(0, len(self.current_thetas), 0, self.max_time_steps)
        )

        tick_positions = np.arange(len(self.current_thetas)) + 0.5
        ax.set_xticks(tick_positions)
        ax.set_xticklabels(
            self.current_thetas,
            fontsize=6,
            color='white',
            va='top'
        )
        ax.tick_params(axis='x', colors='white', direction='in', pad=-10, length=0)

        ax.set_yticks(np.linspace(0, self.max_time_steps, 10))  # or any number of horizontal divisions
        ax.xaxis.grid(True, which='both', color='white', linewidth=0.3, alpha=0.04)
        ax.yaxis.grid(False)

        fig.tight_layout(pad=0)
        # ax.axis('off')
        ax.tick_params(left=False, bottom=False, labelleft=False)
        fig.subplots_adjust(left=0, right=1, top=1, bottom=0)

        buf = io.BytesIO()
        canvas.print_png(buf)
        buf.seek(0)
        image = Image.open(buf)
        image.load()  # Force full load before buffer closes
        buf.close()

        return image


def generate_full_heatmap(folder_path, cmap, vert_max, scale_factor):
    csv_files = glob.glob(os.path.join(folder_path, "*.csv"))
    if len(csv_files) != 1:
        raise ValueError("Expected exactly one CSV file in the folder.")

    csv_path = csv_files[0]
    df = pd.read_csv(csv_path)
    if 'Timestamp' in df.columns:
        df = df.drop(columns=['Timestamp'])
    thetas = list(df.columns)
    values = df.to_numpy()

    heatmap = Heatmap(max_time_steps=len(df))

    for row in values:
        heatmap.update(thetas, row.tolist(), max_value_seen_setting='global')

    height = int((len(df) / 120) * 440)
    image = heatmap.render_heatmap_image(
        cmap=cmap,
        vert_max=vert_max,
        scale_factor=scale_factor,
        width=550,
        height=height
    )

    if image:
        base, _ = os.path.splitext(csv_path)
        output_path = base + "_heatmap.png"
        image.save(output_path)
