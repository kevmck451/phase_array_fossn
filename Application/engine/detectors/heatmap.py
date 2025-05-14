

import numpy as np
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
        self.update_counter = 0
        self.should_log = False
        self.matrix_filled_once = False
        self.raw_input_buffer = []

    def update(self, thetas, values):
        if len(thetas) != len(values):
            raise ValueError("Length of thetas and values must match")

        self.current_thetas = list(thetas)
        num_bins = len(thetas)
        new_row = np.array(values)

        if self.anomaly_matrix is None:
            self.anomaly_matrix = np.zeros((self.max_time_steps, num_bins))
            self.matrix_filled_once = False
            self.update_counter = 0
            self.should_log = False
            self.raw_input_buffer = []

        # Roll the matrix to make room for new row at the bottom
        self.anomaly_matrix = np.roll(self.anomaly_matrix, -1, axis=0)

        # Maintain raw input buffer
        self.raw_input_buffer.append(new_row)
        if len(self.raw_input_buffer) > self.smoothing_window:
            self.raw_input_buffer.pop(0)

        # Compute smoothed row from raw input only
        if len(self.raw_input_buffer) == self.smoothing_window:
            smoothed_row = np.mean(self.raw_input_buffer, axis=0)
        else:
            smoothed_row = new_row

        self.anomaly_matrix[-1] = smoothed_row

        # Detect when matrix has completely filled (top row no longer all zeros)
        if not self.matrix_filled_once and not np.all(self.anomaly_matrix[0] == 0):
            self.matrix_filled_once = True
            self.update_counter = 1  # first full frame just happened
            self.should_log = True
        elif self.matrix_filled_once:
            self.update_counter += 1
            if self.update_counter >= self.max_time_steps:
                self.should_log = True
                self.update_counter = 0
            else:
                self.should_log = False
        else:
            self.should_log = False

        self.max_value_seen = max(self.max_value_seen, np.max(new_row))

    def render_heatmap_image(self, width=350, height=280):
        if self.anomaly_matrix is None or self.anomaly_matrix.shape[0] == 0:
            return None

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
        image.load()  # Force full load before buffer closes
        buf.close()

        return image

