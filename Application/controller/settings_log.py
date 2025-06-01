
from datetime import datetime
from dataclasses import asdict, is_dataclass
import json
import os



class Settings_Log:

    def __init__(self, save_directory):
        self.save_directory = save_directory
        self.all_settings = {}
        self.use_external_calibration = None
        self.temp_sensor = None
        self.mic_array = None
        self.audio_loaded = None
        self.beam_mixes = None
        self.array_type = None
        self.sample_rate = None
        self.chunk_size_seconds = None

        # Beamforming
        self.thetas = None
        self.phis = None
        self.beam_mix = None

        # Processor
        self.processing_chain = None
        self.nr_std_threshold = None
        self.bottom_cutoff_frequency = None
        self.norm_percent = None
        self.new_sample_rate = None

        # PCA Calculator
        self.nperseg = None
        self.num_components = None

        # Detector
        self.max_value = None
        self.anomaly_threshold = None
        self.num_channels = None
        self.num_pca_components = None
        self.num_samples = None

        # Anomaly Filter
        self.anomaly_filter_on_off = None
        self.bias_scale_factor = None
        self.bias_margin = None
        self.bias_theta_ratio = None
        self.edge_width = None
        self.suppression_factor = None
        self.targeted = None

        # Heatmap
        self.max_value_seen_global = None
        self.smoothing_window = None
        self.vert_max = None
        self.sensitivity_factor = None

    def log_data(self):
        current_time = datetime.now().strftime('%-I.%M%p').lower()
        filename = os.path.join(self.save_directory, f"settings_{current_time}.json")

        self.all_settings = {
            "use_external_calibration": self.use_external_calibration,
            "temp_sensor": self.temp_sensor,
            "mic_array": self.mic_array,
            "audio_loaded": self.audio_loaded,
            "beam_mixes": self.beam_mixes,
            "array_type": self.array_type,
            "sample_rate": self.sample_rate,
            "chunk_size_seconds": self.chunk_size_seconds,

            "beamforming": {
                "thetas": self.thetas,
                "phis": self.phis,
                "beam_mix": asdict(self.beam_mix) if self.beam_mix else None,
                "beam_mixes": self.beam_mixes,
            },

            "processor": {
                "processing_chain": self.processing_chain,
                "nr_std_threshold": self.nr_std_threshold,
                "bottom_cutoff_frequency": self.bottom_cutoff_frequency,
                "norm_percent": self.norm_percent,
                "new_sample_rate": self.new_sample_rate,
            },

            "pca_calculator": {
                "nperseg": self.nperseg,
                "num_components": self.num_components,
            },

            "detector": {
                "max_value": self.max_value,
                "anomaly_threshold": self.anomaly_threshold,
                "num_channels": self.num_channels,
                "num_pca_components": self.num_pca_components,
                "num_samples": self.num_samples,
            },

            "anomaly_filter": {
                "anomaly_filter_on_off": self.anomaly_filter_on_off,
                "bias_scale_factor": self.bias_scale_factor,
                "bias_margin": self.bias_margin,
                "bias_theta_ratio": self.bias_theta_ratio,
                "edge_width": self.edge_width,
                "suppression_factor": self.suppression_factor,
                "targeted": self.targeted,
            },

            "heatmap": {
                "max_value_seen_global": self.max_value_seen_global,
                "smoothing_window": self.smoothing_window,
                "vert_max": self.vert_max,
                "sensitivity_factor": self.sensitivity_factor,
            }
        }

        with open(filename, "w") as f:
            json.dump(self.all_settings, f, indent=4)