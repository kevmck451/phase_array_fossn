

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from PIL import Image
import io


class Heatmap:
    def __init__(self, max_time_steps=120):
        self.max_time_steps = max_time_steps
        self.anomaly_matrix = None
        self.max_value_seen = 0
        self.current_thetas = []
        self.smoothing_window = 3

    def update(self, thetas, values):
        if len(thetas) != len(values):
            raise ValueError("Length of thetas and values must match")

        self.current_thetas = list(thetas)
        num_bins = len(thetas)

        new_row = np.zeros(num_bins)
        for i, val in enumerate(values):
            new_row[i] = val

        if self.anomaly_matrix is None:
            self.anomaly_matrix = np.zeros((self.max_time_steps, num_bins))

        self.anomaly_matrix = np.roll(self.anomaly_matrix, -1, axis=0)
        # self.anomaly_matrix[-1] = new_row
        # self.anomaly_matrix[-1] = (self.anomaly_matrix[-2] + new_row) / 2 if self.anomaly_matrix.any() else new_row
        if self.anomaly_matrix.shape[0] >= self.smoothing_window and self.anomaly_matrix.any():
            recent = self.anomaly_matrix[-self.smoothing_window:-1]
            self.anomaly_matrix[-1] = (np.sum(recent, axis=0) + new_row) / (self.smoothing_window)
        else:
            self.anomaly_matrix[-1] = new_row

        self.max_value_seen = max(self.max_value_seen, np.max(new_row))

    def render_heatmap_image(self, width=350, height=280):
        fig = Figure(figsize=(width / 100, height / 100), dpi=100)
        canvas = FigureCanvas(fig)
        ax = fig.add_subplot(111)

        if self.anomaly_matrix is None:
            return None

        vmax = self.max_value_seen if self.max_value_seen > 0 else 1

        ax.imshow(
            self.anomaly_matrix,
            aspect='auto',
            cmap='inferno',
            vmin=0,
            vmax=vmax,
            origin='upper',
            interpolation='gaussian',
            extent=(0, len(self.current_thetas), 0, self.max_time_steps)
        )

        ax.set_xticks(np.arange(len(self.current_thetas)) + 0.5)
        ax.set_xticklabels(self.current_thetas, rotation=45, fontsize=6)
        ax.set_yticks([])

        fig.tight_layout(pad=0)
        ax.axis('off')
        fig.subplots_adjust(left=0, right=1, top=1, bottom=0)

        buf = io.BytesIO()
        canvas.print_png(buf)
        buf.seek(0)
        image = Image.open(buf)

        return image

