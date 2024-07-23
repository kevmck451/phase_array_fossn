from Filters.audio import Audio
from Filters.save_to_wav import save_to_wav
from pathlib import Path
from tqdm import tqdm
from pydub import AudioSegment
from pydub.effects import compress_dynamic_range
import numpy as np


def compressor(data, threshold, ratio, attack_time, release_time, sample_rate):
    # Convert numpy array to AudioSegment
    audio_segment = AudioSegment(
        data.tobytes(),
        frame_rate=sample_rate,
        sample_width=data.dtype.itemsize,
        channels=1
    )

    # Apply compression
    compressed_segment = compress_dynamic_range(
        audio_segment,
        threshold=threshold,
        ratio=ratio,
        attack=attack_time * 1000,  # convert seconds to milliseconds
        release=release_time * 1000  # convert seconds to milliseconds
    )

    # Convert compressed AudioSegment back to numpy array
    compressed_data = np.array(compressed_segment.get_array_of_samples())

    # Normalize data to fit between 0 and 1
    max_val = np.max(np.abs(compressed_data))
    if max_val > 0:
        compressed_data = compressed_data / max_val

    return compressed_data.astype(np.float32)


if __name__ == '__main__':
    base_path = '/Users/KevMcK/Dropbox/2 Work/1 Optics Lab/2 FOSSN/Data'

    threshold = -6.0  # Example threshold in dB
    ratio = 2.0  # Example ratio
    attack_time = 0.01  # Example attack time in seconds
    release_time = 0.5 # Example release time in seconds

    export_tag = '_comp7'

    filepath = '/Users/KevMcK/Dropbox/2 Work/1 Optics Lab/2 FOSSN/Data/Tests/8_beamformed/07-15-2024_03-25-28_chunk_1_BF1_0-0_pr4.wav'
    audio = Audio(filepath=filepath, num_channels=1)

    # Apply the compressor
    audio.data = compressor(audio.data, threshold, ratio, attack_time, release_time, audio.sample_rate)

    # Create the new filename
    original_path = Path(filepath)
    new_filename = original_path.stem + export_tag + original_path.suffix
    filepath_save = f'{base_path}/Tests/8_beamformed'
    new_filepath = f'{filepath_save}/{new_filename}'

    # Save the filtered audio to the new file
    save_to_wav(audio.data, audio.sample_rate, audio.num_channels, new_filepath)
