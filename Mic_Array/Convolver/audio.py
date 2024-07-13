
from scipy.signal import resample
import matplotlib.pyplot as plt
from pathlib import Path
import soundfile as sf
import numpy as np
import librosa
import wave


class Audio:
    def __init__(self, **kwargs):
        filepath = kwargs.get('filepath', None)
        self.path = Path(str(filepath)) if filepath is not None else None
        self.sample_rate = kwargs.get('sample_rate', 48000)
        self.num_channels = kwargs.get('num_channels', 1)
        self.sample_length = kwargs.get('sample_length', None)
        self.data = kwargs.get('data', None)
        self.num_samples = kwargs.get('num_samples', None)
        if self.path:
            self.name = kwargs.get('name', self.path.stem)
        else:
            self.name = kwargs.get('name', '')

        # If given a filepath
        if self.path is not None:
            # with wave.open(str(hardware.path), 'rb') as wav_file:
            #     hardware.num_channels = wav_file.getnchannels()
            # hardware.load_data(hardware.path, hardware.num_channels)
            # if hardware.num_channels != hardware.num_channels:
            #     hardware.data = hardware.data[:hardware.num_channels]
            #     hardware.data = np.squeeze(hardware.data)

            info = sf.info(self.path)
            self.load_data(self.path, info.channels)
            if self.num_channels != info.channels:
                self.data = self.data[:self.num_channels]
                self.data = np.squeeze(self.data)

        if not np.isfinite(self.data).all():
            self.data[np.isnan(self.data)] = 0
            self.data[np.isinf(self.data)] = 0

        max_value = np.max(self.data).round(5)
        if max_value == 0:
            print(self.path)
            raise Exception('Max Value is Zero')

    def __str__(self):
        return f'---------Audio Object---------\n' \
               f'path: {self.path}\n' \
               f'name: {self.name}\n' \
               f'sample_rate: {self.sample_rate} Hz\n' \
               f'num_channels: {self.num_channels}\n' \
               f'sample_length: {self.sample_length} s\n' \
               f'num_samples: {self.num_samples}\n' \
               f'data type: {self.data.dtype}\n' \
               f'data shape: {self.data.shape}\n' \
               f'data: {self.data}'

    # Function that loads data from filepath
    def load_data(self, filepath, num_ch):
        if num_ch > 1:
            self.data, samplerate = sf.read(str(filepath), dtype='float32')
            if samplerate != self.sample_rate:
                # hardware.data = librosa.resample(y=hardware.data, orig_sr=samplerate, target_sr=hardware.sample_rate)
                num_samples = int((self.sample_rate / samplerate) * len(self.data))
                self.data = resample(self.data, num_samples)

            # try:
            #     hardware.data = hardware.data.reshape(-1, hardware.num_channels)  # Reshape to match the number of channels
            # except ValueError:
            #     # print("The audio data cannot be reshaped to match the number of channels.")
            #     # print(f'Path: {hardware.path}')
            #     # print(f'Num Channels: {hardware.num_channels}')
            #     return


            # Convert the interleaved data to deinterleaved format
            self.data = np.transpose(self.data.copy())  # Rows are channels / columns are data
            # print(f'Data Shape: {hardware.data.shape} / Sample Rate: {hardware.sample_rate}')
            self.sample_length = round((self.data.shape[1] / self.sample_rate), 2)
            self.num_samples = len(self.data[1])

        else:
            self.data, samplerate = sf.read(str(filepath), dtype='float32')
            # average = np.mean(audio.data)
            # hardware.data = hardware.data - average
            if samplerate != self.sample_rate:
                self.data = librosa.resample(y=self.data, orig_sr=samplerate, target_sr=self.sample_rate)
                # hardware.data = resampy.resample(hardware.data, samplerate, hardware.sample_rate)
            self.sample_length = round((len(self.data) / self.sample_rate), 2)
            self.num_samples = len(self.data)

    # Function that returns stats from the audio file
    def stats(self):
        stat_names = ['Max', 'Min', 'Mean', 'RMS', 'Range']

        max_value = np.max(self.data).round(3)
        min_value = np.min(self.data).round(3)
        mean = np.mean(self.data).round(3)
        rms = np.sqrt(np.mean(np.square(self.data)))
        dynamic_range = (max_value - min_value).round(3)  # Calculate dynamic range
        channel_stats = {
            stat_names[0]: max_value,
            stat_names[1]: min_value,
            stat_names[2]: mean,
            stat_names[3]: rms,
            stat_names[4]: dynamic_range
            }

        return channel_stats

    # Function to export an object
    def export(self, **kwargs):
        filepath = kwargs.get('filepath', None)
        name = kwargs.get('name', self.name)
        # Save/export the audio object
        if filepath is not None:
            if Path(name).suffix != '.wav':
                filepath = f'{filepath}/{name}.wav'
            else: filepath = f'{filepath}/{name}'
            sf.write(f'{filepath}', self.data, self.sample_rate)
        else: sf.write(f'{name}_export.wav', self.data, self.sample_rate)

    # Function to display the waveform of audio
    def waveform(self, **kwargs):
        # Calculate the time axis in seconds
        if self.num_channels > 1:
            time_axis = np.arange(len(self.data[0])) / self.sample_rate
        else:
            time_axis = np.arange(len(self.data)) / self.sample_rate
        # Create the figure and axis objects, with subplots equal to number of channels
        fig, axs = plt.subplots(self.num_channels, figsize=(14, (4+self.num_channels)))

        # If only one channel, make axs a list to handle indexing
        if self.num_channels == 1:
            axs = [axs]

        # Plot the audio data for each channel
        for i in range(self.num_channels):
            if self.num_channels > 1:
                axs[i].plot(time_axis, self.data[i], linewidth=0.5)
            else: axs[i].plot(time_axis, self.data, linewidth=0.5)
            axs[i].set_ylabel('Amplitude')
            axs[i].set_ylim([-1, 1])  # set the y-axis limits to -1 and 1
            axs[i].axhline(y=0, color='black', linewidth=0.5, linestyle='--')  # add horizontal line at y=0
            axs[i].set_xlabel('Time (s)')
            axs[i].set_title(f'Waveform: {self.name} - Channel {i + 1}')

        # Make the layout tight to avoid overlap of subplots
        fig.tight_layout(pad=1)

        save = kwargs.get('save', False)
        display = kwargs.get('display', False)
        ret = kwargs.get('ret', False)
        save_path = kwargs.get('save_path', str(self.path))
        if save:
            plt.savefig(f'{save_path}/{self.name}.png')
        if display:
            plt.show()
        if ret:
            return fig




if __name__ == '__main__':

    # a = Audio_Abstract(stats=True)
    #
    # print('-' * 50)
    #
    # filepath = '/Users/KevMcK/Dropbox/2 Work/1 Optics Lab/1 Acoustic/Data/ML Model Data/Orlando/mission 5/Hex_FullFlight_5.wav'
    # b = Audio_Abstract(filepath=filepath, stats=True)
    #
    # print('-'*50)
    #
    # filepath = '/Users/KevMcK/Dropbox/2 Work/1 Optics Lab/1 Acoustic/Data/ML Model Data/Orlando/dataset 5/1/5_target_1_a.wav'
    # c = Audio_Abstract(filepath=filepath, stats=True)


    filepath = '/Users/KevMcK/Dropbox/2 Work/1 Optics Lab/1 Acoustic/Data/Isolated Samples/Hex/hex_hover_8_thin.wav'
    audio = Audio(filepath=filepath)
    print(audio)
    # # audio.waveform(display=True)
    # max = np.max(audio.data)
    # min = np.min(audio.data)
    # mean = np.mean(audio.data)
    #
    # print(f'Max: {max}\nMin: {min}\nMean: {mean}')
    #
    # audio.data = audio.data - mean
    #
    # max = np.max(audio.data)
    # min = np.min(audio.data)
    # mean = np.round(np.mean(audio.data), 7)
    #
    # print(f'Max: {max}\nMin: {min}\nMean: {mean}')
    #
    # absolute = np.abs(audio.data)
    # print(absolute)
    # audio.data = absolute
    #
    # audio.waveform(display=True)



