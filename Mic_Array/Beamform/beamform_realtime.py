

from Mic_Array.FIR_Filter.mic_coordinates import generate_mic_coordinates
from Mic_Array.FIR_Filter.generate_fir_coeffs import generate_fir_coeffs
from Mic_Array.AudioStreamSimulator import AudioStreamSimulator
import Mic_Array.array_config as array_config
from Filters.save_to_wav import save_to_wav
from Filters.audio import Audio



from scipy.signal import convolve
from queue import Queue
import numpy as np
import time


from pathlib import Path



class Beamform:
    def __init__(self, thetas, phis, initial_temp):
        self.num_mics = array_config.num_mics
        self.sample_rate = array_config.sample_rate
        self.mic_coordinates = generate_mic_coordinates()
        self.thetas = thetas
        self.phis = phis
        self.temperature = initial_temp
        self.temperature_current = initial_temp
        self.fir_coeffs = self.compile_all_fir_coeffs()
        self.desired_channels = self.fir_coeffs.shape[0]
        self.num_coeffs = self.fir_coeffs.shape[3]

        print(f'FIR Coeffs Shape: {self.fir_coeffs.shape}')

        self.queue = Queue()
        self.data_list = []

        self.tag_index = 2

    def compile_all_fir_coeffs(self):
        fir_coeffs_list = []
        for phi in self.phis:
            for theta in self.thetas:
                fir_coeffs = generate_fir_coeffs(self.mic_coordinates, theta, phi, self.temperature_current)
                # print(f'FIR C Shape: {fir_coeffs.shape}')
                fir_coeffs_list.append(fir_coeffs)

        return np.stack(fir_coeffs_list, axis=0)


    def map_channels_to_positions(self, audio_data):
        num_samples = audio_data.shape[1]

        mapped_data = np.zeros((array_config.rows, array_config.cols, num_samples))

        for ch_index in range(self.num_mics):
            mic_x, mic_y = array_config.mic_positions[ch_index]
            mapped_data[mic_x, mic_y, :] = audio_data[ch_index, :]

        return mapped_data


    def beamform_data(self, data):
        mapped_audio_data = self.map_channels_to_positions(data)
        # print(f'Mapped Data Shape: {mapped_audio_data.shape}')

        rows, cols, num_samples = mapped_audio_data.shape
        assert rows * cols == self.fir_coeffs.shape[1] * self.fir_coeffs.shape[2], "Mismatch between audio data and FIR coefficients shape."

        if self.temperature != self.temperature_current:
            print(f'Temp Changed => old: {self.temperature} | new: {self.temperature_current}')
            self.fir_coeffs = self.compile_all_fir_coeffs()
            self.temperature = self.temperature_current

        beamformed_data = np.zeros(num_samples + self.num_coeffs - 1)

        # todo: not doing all output channels yet, just one
        for row_index in range(rows):
            for col_index in range(cols):
                filtered_signal = convolve(mapped_audio_data[row_index, col_index, :], self.fir_coeffs[7, row_index, col_index, :], mode='full')
                beamformed_data += filtered_signal


        self.queue.put(beamformed_data)
        self.data_list.extend(beamformed_data)

        # print('packing audio')
        # original_path = Path(filepath)
        # export_tag = f'_BF{self.tag_index}'
        # new_filename = original_path.stem + export_tag + original_path.suffix
        # filepath_save = f'{base_path}/Tests/20_beamformed_RT'
        # new_filepath = f'{filepath_save}/{new_filename}'
        # save_to_wav(beamformed_data, self.sample_rate, 1, new_filepath)
        # self.tag_index += 1


    def save_file(self):
        beamformed_data = np.array(self.data_list)

        # Normalize the beamformed data
        max_val = np.max(np.abs(beamformed_data))
        if max_val != 0:
            beamformed_data = beamformed_data / max_val

        print('packing audio')
        original_path = Path(filepath)
        export_tag = f'_BF{self.tag_index}'
        new_filename = original_path.stem + export_tag + original_path.suffix
        filepath_save = f'{base_path}/Tests/20_beamformed_RT'
        new_filepath = f'{filepath_save}/{new_filename}'
        save_to_wav(beamformed_data, self.sample_rate, 1, new_filepath)





if __name__ == '__main__':


    # initial set up
    # 1. Set up Mic Coordinates (WILL ONLY HAPPEN ONCE)
    # 2. generate a set of coeffs for a particular set of angles based on a temp (WILL HAPPEN PERIODICALLY)
        # save those values because they will be used until temp goes outside some range
    # 3. Beamform (HAPPENING WHEN DATA IS AVAILABLE TO BEAMFORM)
        # will beamforming small chunks and then appending the end affect it?

    thetas = [-90,-80,-70,-60,-50,-40,-30,-20,-10,0,10,20,30,40,50,60,70,80,90]
    phis = [0]  # azimuth angle: neg is below and pos is above


    base_path = '/Users/KevMcK/Dropbox/2 Work/1 Optics Lab/2 FOSSN/Data'
    filename = 'cars_drive_by_150m'
    filepath = f'{base_path}/Tests/17_outdoor_testing/{filename}.wav'
    audio = Audio(filepath=filepath, num_channels=array_config.num_mics)
    chunk_size_seconds = 1

    temp_F = 86  # temperature in Fahrenheit
    beamform = Beamform(thetas, phis, temp_F)


    stream = AudioStreamSimulator(audio, chunk_size_seconds)
    stream.start_stream()
    index = 1

    while stream.running:
        if not stream.queue.empty():
            print()
            print('BEAMFORMING------------------')
            print(f'Audio Stream Queue Size: {stream.queue.qsize()}')
            current_audio_data = stream.queue.get()
            print(f'Current Data Size: {current_audio_data.shape}')
            # -------------------------
            beamform.beamform_data(current_audio_data)

            if index % 5 == 0:
                beamform.temperature_current = beamform.temperature_current + 1
            index += 1

        time.sleep(0.5)

    beamform.save_file()