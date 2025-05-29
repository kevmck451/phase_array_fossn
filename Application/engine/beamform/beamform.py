

from Application.engine.beamform.time_delays import calculate_time_delays
from Application.engine.beamform.fir_filter import create_fir_filters

from concurrent.futures import ThreadPoolExecutor
from scipy.signal import convolve
from queue import Queue
import numpy as np


class Beamform:
    def __init__(self, thetas, phis, initial_temp, array_config, beam_mix):
        self.array_config = array_config
        self.beam_mix = beam_mix
        self.num_mics = self.beam_mix.num_mics
        self.sample_rate = self.array_config.sample_rate
        self.mic_coordinates = None
        self.thetas = thetas
        self.phis = phis
        self.temperature = int(initial_temp)
        self.temperature_current = int(initial_temp)
        self.num_taps = self.beam_mix.num_taps
        self.fir_coeffs = None
        self.desired_channels = None
        self.num_coeffs = None
        self.generate_mic_coordinates()
        self.compile_all_fir_coeffs()

        self.queue = Queue()
        self.data_list = []
        self.tag_index = 2

        self.send_to_external_audio_stream = False
        self.external_audio_queue = Queue()

    def update_parameters(self, beam_mix):
        self.beam_mix = beam_mix
        self.num_mics = beam_mix.num_mics
        self.num_taps = beam_mix.num_taps
        self.generate_mic_coordinates()
        self.compile_all_fir_coeffs()

    def generate_mic_coordinates(self):
        '''
            these grid coordinate are from the perspective of in front the array with (0,0) at the top left
            the reference is from the center of the array
        '''

        rows = self.beam_mix.rows
        cols = self.beam_mix.cols
        mic_spacing = self.beam_mix.mic_spacing  # meters - based on center freq
        num_mics = self.beam_mix.num_mics
        mic_coords = np.zeros((num_mics, 3))  # Initialize coordinates array

        idx = 0
        for row in range(rows):
            for col in range(cols):
                # Calculate the position centered around (0, 0)
                x = (col - (cols - 1) / 2) * mic_spacing
                y = ((rows - 1) / 2 - row) * mic_spacing  # Flip the sign to correct y-coordinate
                z = 0  # For a 2D array, z is always 0
                mic_coords[idx] = [x, y, z]
                idx += 1

        # print(mic_coords)
        self.mic_coordinates = mic_coords

    def compile_all_fir_coeffs(self):
        print('Generating FIR Coeffs')
        fir_coeffs_list = []
        for phi in self.phis:
            for theta in self.thetas:
                fir_coeffs = self.generate_fir_coeffs(self.mic_coordinates, theta, phi, self.temperature_current, self.array_config, self.beam_mix)
                # print(f'FIR C Shape: {fir_coeffs.shape}')
                fir_coeffs_list.append(fir_coeffs)

        fir_coeffs_stack = np.stack(fir_coeffs_list, axis=0)

        self.desired_channels = fir_coeffs_stack.shape[0]
        self.num_coeffs = fir_coeffs_stack.shape[3]
        self.fir_coeffs = fir_coeffs_stack

    def map_channels_to_positions(self, data):
        num_samples = data.shape[1]

        mapped_data = np.zeros((self.array_config.rows, self.array_config.cols, num_samples))

        for ch_index in range(self.beam_mix.num_mics):
            mic_x, mic_y = self.array_config.mic_positions[ch_index]
            mapped_data[mic_x, mic_y, :] = data[ch_index, :]
            # print(f'MX{mic_x} | MY{mic_y} -> ch{ch_index+1}')

        return mapped_data

    def map_channels_to_beam_mix(self, mapped_array_data):

        if self.array_config.title == 'Line Array':
            num_samples = mapped_array_data.shape[2]
            mapped_data = np.zeros((self.beam_mix.rows, self.beam_mix.cols, num_samples))

            if len(self.beam_mix.mics_to_use) != self.beam_mix.rows * self.beam_mix.cols:
                raise ValueError("Mismatch between mics_to_use and beam mix shape.")

            for i, (src_x, src_y) in enumerate(self.beam_mix.mics_to_use):
                dest_x = i // self.beam_mix.cols
                dest_y = i % self.beam_mix.cols
                mapped_data[dest_x, dest_y, :] = mapped_array_data[src_x, src_y, :]
                # print(f'FROM ({src_x}, {src_y}) -> TO ({dest_x}, {dest_y}) [ch {i + 1}]')

        else:
            num_samples = mapped_array_data.shape[2]
            mapped_data = np.zeros((self.beam_mix.rows, self.beam_mix.cols, num_samples))

            if len(self.beam_mix.mics_to_use) != self.beam_mix.rows * self.beam_mix.cols:
                raise ValueError("Mismatch between mics_to_use and beam mix shape.")

            for i, (src_x, src_y) in enumerate(self.beam_mix.mics_to_use):
                dest_x = i // self.beam_mix.cols
                dest_y = i % self.beam_mix.cols
                mapped_data[dest_x, dest_y, :] = mapped_array_data[src_x, src_y, :]
                # print(f'FROM ({src_x}, {src_y}) -> TO ({dest_x}, {dest_y}) [ch {i + 1}]')


        return mapped_data

    def beamform_data(self, data):

        if self.temperature != self.temperature_current:
            print(f'Temp Changed => old: {self.temperature} | new: {self.temperature_current}')
            self.compile_all_fir_coeffs()
            self.temperature = self.temperature_current

        mapped_audio_data = self.map_channels_to_positions(data)
        mapped_audio_data = self.map_channels_to_beam_mix(mapped_audio_data)

        rows, cols, num_samples = mapped_audio_data.shape
        assert rows * cols == self.fir_coeffs.shape[1] * self.fir_coeffs.shape[2], "Mismatch between audio data and FIR coefficients shape."

        beamformed_data_all_channels = np.zeros((self.desired_channels, num_samples + self.num_coeffs - 1))

        # Use parallel processing
        with ThreadPoolExecutor() as executor:
            futures = [executor.submit(self.beamform_channel, channel, mapped_audio_data, self.fir_coeffs) for channel in range(self.desired_channels)]
            for channel, future in enumerate(futures):
                beamformed_data_all_channels[channel] = future.result()

        # Trim the extra samples to match the original input length
        trim_amount = (beamformed_data_all_channels.shape[1] - num_samples) // 2
        trimmed_result = beamformed_data_all_channels[:, trim_amount: -trim_amount]

        self.queue.put(trimmed_result)

        if self.send_to_external_audio_stream:
            self.external_audio_queue.put(trimmed_result)

    def beamform_channel(self, channel, mapped_audio_data, fir_coeffs):
        num_samples = mapped_audio_data.shape[2]
        beamformed_data = np.zeros(num_samples + self.num_coeffs - 1)

        # print(f'Mapped Data Shape: {mapped_audio_data.shape}')

        for row_index in range(mapped_audio_data.shape[0]):
            for col_index in range(mapped_audio_data.shape[1]):
                filtered_signal = convolve(mapped_audio_data[row_index, col_index, :], fir_coeffs[channel, row_index, col_index, :], mode='full')
                beamformed_data += filtered_signal

        return beamformed_data


    @staticmethod
    def generate_fir_coeffs(mic_coords, theta, phi, temp_F, array_config, beam_mix):
        time_delays = calculate_time_delays(mic_coords, theta, phi, temp_F, array_config, beam_mix)
        fir_filter = create_fir_filters(time_delays, beam_mix.num_taps)

        return fir_filter


