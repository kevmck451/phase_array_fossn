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

    # Split audio into chunks for progress tracking
    chunk_size = 1000  # milliseconds per chunk
    total_chunks = len(audio_segment) // chunk_size
    chunks = [audio_segment[i * chunk_size:(i + 1) * chunk_size] for i in range(total_chunks + 1)]

    compressed_data = []

    # Apply compression to each chunk
    for chunk in tqdm(chunks, desc="Processing", unit="chunk"):
        compressed_chunk = compress_dynamic_range(
            chunk,
            threshold=threshold,
            ratio=ratio,
            attack=attack_time * 1000,  # convert seconds to milliseconds
            release=release_time * 1000  # convert seconds to milliseconds
        )
        compressed_data.append(np.array(compressed_chunk.get_array_of_samples()))

    # Combine compressed chunks
    compressed_data = np.concatenate(compressed_data)

    # Normalize data to fit between 0 and 1
    max_val = np.max(np.abs(compressed_data))
    if max_val > 0:
        compressed_data = compressed_data / max_val

    return compressed_data.astype(np.float32)


def compressor(data, threshold, ratio, attack_time, release_time, sample_rate):
    from pippi import fx

    fx.compressor(
            snd,
            ratio=4.0,
            threshold=-30.0,
            attack=0.2,
            release=0.2
    )



if __name__ == '__main__':
    base_path = '/Users/KevMcK/Dropbox/2 Work/1 Optics Lab/2 FOSSN/Data'

    threshold = -20.0  # Example threshold in dB
    ratio = 4.0  # Example ratio
    attack_time = 0.01  # Example attack time in seconds
    release_time = 1  # Example release time in seconds

    export_tag = '_comp5'

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
