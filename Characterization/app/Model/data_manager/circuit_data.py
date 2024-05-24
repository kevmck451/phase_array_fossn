
from app.Model.data_manager.csv_class import CSVFile
import numpy as np
import random
import os

from app.Model.data_manager.audio_abstract import Audio_Abstract

def base_path(relative_path):
    current_script_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(current_script_dir)))
    new_path = os.path.join(base_dir, relative_path)
    return new_path


# -------------------------------------------------
# LOADING DATA   ----------------------------------
# _________________________________________________
# Build list of exp names
def load_audio_names(experiment_number):

    audio_csv_filepath = base_path('experiment files/samples.csv')
    audio_csv = CSVFile(file_path=audio_csv_filepath)
    sample_numbers = audio_csv.get_column(column_name=f'ex{experiment_number}')

    sample_names = {'1': 'cactus',
                    '2': 'donkey',
                    '3': 'dove',
                    '4': 'envelope',
                    '5': 'glove',
                    '6': 'glue',
                    '7': 'grass',
                    '8': 'grasshopper',
                    '9': 'guitar',
                    '10': 'ice',
                    '11': 'lemon',
                    '12': 'lettuce',
                    '13': 'nail',
                    '14': 'orange',
                    '15': 'owl',
                    '16': 'vegetable',
                    '17': 'violin',
                    '18': 'window',
                    '19': 'woodpecker',
                    '20': 'zebra'}

    sample_names_list = []
    for number in sample_numbers:
        sample_name = sample_names.get(number)
        sample_names_list.append(sample_name)

    return sample_names_list

# Build list of audio objects in correct order from file
def load_audio_samples(experiment_number):

    audio_csv_filepath = base_path('experiment files/samples.csv')
    audio_csv = CSVFile(file_path=audio_csv_filepath)
    sample_numbers = audio_csv.get_column(column_name=f'ex{experiment_number}')

    sample_names = {'1': 'cactus',
                    '2': 'donkey',
                    '3': 'dove',
                    '4': 'envelope',
                    '5': 'glove',
                    '6': 'glue',
                    '7': 'grass',
                    '8': 'grasshopper',
                    '9': 'guitar',
                    '10': 'ice',
                    '11': 'lemon',
                    '12': 'lettuce',
                    '13': 'nail',
                    '14': 'orange',
                    '15': 'owl',
                    '16': 'vegetable',
                    '17': 'violin',
                    '18': 'window',
                    '19': 'woodpecker',
                    '20': 'zebra'}
    audio_sample_buffer = []

    for number in sample_numbers:
        sample_name = sample_names.get(number)

        # print(sample_name)
        for i in range(1, 6):
            audio_name = f'{sample_name}_{i}.wav'
            # print(audio_name)
            filepath = base_path('experiment files/audio')
            audio = Audio_Abstract(filepath=f'{filepath}/{audio_name}')
            # print(audio.num_channels)
            audio_sample_buffer.append(audio)

    return audio_sample_buffer

# Build list of channels to play samples from
def load_channel_numbers(experiment_number):

    channel_csv_filepath = base_path('experiment files/channels.csv')
    channel_csv = CSVFile(file_path=channel_csv_filepath)
    channel_numbers = channel_csv.get_column(column_name=f'ex{experiment_number}')

    return channel_numbers

# Build list of test data
def load_warmup_data():
    sample_name = 'lakes'
    audio_sample_buffer = []

    for i in range(1, 6):
        audio_name = f'{sample_name}_{i}.wav'
        # print(audio_name)

        filepath = base_path('experiment files/audio')
        audio = Audio_Abstract(filepath=f'{filepath}/{audio_name}')
        # print(audio.num_channels)
        audio_sample_buffer.append(audio)

    channel_buffer = list(np.random.choice(range(1,10), size=5, replace=False))
    random.shuffle(audio_sample_buffer)

    return audio_sample_buffer, channel_buffer


def load_calibration_sample(time):
    filepath = base_path('experiment files/audio')
    audio_name = 'pink_noise.wav'
    audio = Audio_Abstract(filepath=f'{filepath}/{audio_name}')
    audio.crop(time)

    return audio

# -------------------------------------------------
# TESTS -------------------------------------------
# _________________________________________________

# Shows output of audio samples and channels match
def test_num_audio_channels():
    for i in range(1, 21):
        sample_buffer = load_audio_samples(experiment_number=i)
        channel_buffer = load_channel_numbers(experiment_number=i)
        print(f'{i}: Audio: {len(sample_buffer)} / Chan: {len(channel_buffer)}')

# Shows output of warm up data
def test_warmup_data():
    test_audio_buffer, test_channel_buffer = load_warmup_data()

    for audio, channel in zip(test_audio_buffer, test_channel_buffer):
        print(f'Audio: {audio.name} / Chan: {channel}')


if __name__ == '__main__':

    # Experiment is selected from program
    experiment = 1
    # sample_buffer = load_audio_samples(experiment_number=experiment)
    # channel_buffer = load_channel_numbers(experiment_number=experiment)
    # test_audio_buffer, test_channel_buffer = load_warmup_data()

    # test_num_audio_channels()
    # test_warmup_data()