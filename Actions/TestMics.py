

from Controller.AudioReceiver import AudioReceiver


import numpy as np
import time
import keyboard  # You need to install the keyboard library


def calculate_rms(data):
    return np.sqrt(np.mean(np.square(data)))

def test_mic(audio_receiver, chan_index, sample_duration, rms_range):
    print(f"Testing mic {chan_index + 1}")
    collected_data = []

    start_time = time.time()
    while time.time() - start_time < sample_duration:
        data = audio_receiver.get_audio_data()
        if data is not None:
            collected_data.append(data[:, chan_index])

    if collected_data:
        collected_data = np.concatenate(collected_data)
        rms_value = calculate_rms(collected_data)
        print(f"Mic {chan_index + 1} RMS value: {rms_value}")
        if rms_range[0] <= rms_value <= rms_range[1]:
            print(f"Mic {chan_index + 1} test passed")
        else:
            print(f"Mic {chan_index + 1} test failed")

if __name__ == "__main__":
    chan_count = 8
    audio_receiver = AudioReceiver(chan_count)

    sample_duration = 2.0  # seconds
    rms_range = (0.1, 0.3)  # Example RMS range for pass/fail criteria

    mic_index = 0
    while mic_index < chan_count:
        print(f"Press 't' to test mic {mic_index + 1}")
        keyboard.wait('enter') # t
        test_mic(audio_receiver, mic_index, sample_duration, rms_range)
        mic_index += 1

    print("All mics tested.")
