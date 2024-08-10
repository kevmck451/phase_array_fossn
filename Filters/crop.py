from Filters.save_to_wav import save_to_wav
from Filters.audio import Audio

from pathlib import Path
import numpy as np

def crop(audio_object, start_time_s, end_time_s):

    def crop(data, start_time_s, end_time_s, sample_rate):
        start_sample = int(start_time_s * sample_rate)
        end_sample = int(end_time_s * sample_rate)
        cropped_data = data[start_sample:end_sample]
        return cropped_data

    if audio_object.num_channels == 1:
        cropped_data = crop(audio_object.data, start_time_s, end_time_s, audio_object.sample_rate)
    else:
        cropped_data = np.zeros((audio_object.num_channels,
                                 int((end_time_s - start_time_s) * audio_object.sample_rate)))
        for i in range(audio_object.data.shape[0]):
            cropped_data[i, :] = crop(audio_object.data[i, :], start_time_s, end_time_s, audio_object.sample_rate)

    return cropped_data


if __name__ == '__main__':
    base_path = '/Users/KevMcK/Dropbox/2 Work/1 Optics Lab/2 FOSSN/Data'
    filepath = f'{base_path}/Tests/17_outdoor_testing/08-07-2024_04-40-36_chunk_1.wav'
    # filepath = f'{base_path}/Tests/10_beamformed/07-16-2024_03-25-22_chunk_1_BF_(-40, 40)-(0).wav'
    num_channels = 48
    audio = Audio(filepath=filepath, num_channels=num_channels)
    start_time = 543 # s
    end_time = 701 # s audio.sample_length
    cropped_data = crop(audio, start_time, end_time)

    original_path = Path(filepath)
    # filepath_save = f'{base_path}/Tests/13_beamformed'
    export_tag = f'_cropped'
    new_filename = original_path.stem + export_tag + original_path.suffix
    new_filepath = f'{original_path.parent}/{new_filename}'

    cropped_audio_object = Audio(data=cropped_data, num_channels=num_channels, sample_rate=48000)
    cropped_audio_object.path = Path(new_filepath)

    save_to_wav(cropped_audio_object.data, cropped_audio_object.sample_rate, cropped_audio_object.num_channels, new_filepath)