from Controller.AudioReceiver import AudioReceiver

from datetime import datetime
import numpy as np
import time
import csv

def calculate_rms(data):
    data = data / 32768
    return np.round(np.sqrt(np.mean(np.square(data))), 5)

def test_mic(audio_receiver, chan_index, sample_duration, rms_range):
    print(f"Testing mic {chan_index + 1}")
    collected_data = []

    # Clear the queue to ensure fresh data
    while not audio_receiver.recv_q.empty():
        audio_receiver.recv_q.get()

    start_time = time.time()
    while time.time() - start_time < sample_duration:
        data = audio_receiver.get_audio_data()
        if data is not None:
            collected_data.append(data[:, chan_index])

    if collected_data:
        collected_data = np.concatenate(collected_data)
        rms_value = calculate_rms(collected_data)
        peak = np.round(np.max(collected_data/32768), 5)

        print(f"Mic {chan_index + 1} RMS value: {rms_value}")
        print(f"Mic {chan_index + 1} Peak value: {peak}")
        if rms_range[0] <= rms_value <= rms_range[1]:
            print()
            print(f"Mic {chan_index + 1}: +++++++ PASSED +++++++")
            print()
        else:
            print()
            print(f"Mic {chan_index + 1}: ------- FAILED -------")
            print()

        return rms_value, peak

    else:
        print('Error')
        return 0, 0

def export_to_csv(rms_values, peak_values, rms_range, mic_nums):
    filename = datetime.now().strftime("%m-%d-%Y %I-%M-%S")
    filename = f'results {filename}.csv'
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Channel', 'Status', 'RMS', 'Peak', 'MicNum'])
        for i, (r, p, m) in enumerate(zip(rms_values, peak_values, mic_nums)):
            status = 'PASSED' if rms_range[0] <= r <= rms_range[1] else 'FAILED'
            writer.writerow([f'Ch{i+1}', status, r, p, m])

if __name__ == "__main__":
    # for FPGA gain at 10
    # sudo server -r -g 10
    rms_mean = 0.2867 # from MasterMicTest.csv
    rms_std = 0.0326 # from MasterMicTest.csv
    rms_range = (rms_mean-rms_std, rms_mean+rms_std)

    iterations = 80
    counter = 0
    chan_count = 8
    audio_receiver = AudioReceiver(chan_count)
    sample_duration = 2.0  # seconds
    mic_index = 0
    rms_values = []
    peak_values = []
    mic_nums = []

    while counter < iterations:
        mic_num = input(f"Enter Mic Number & press 'Enter' to test mic {mic_index + 1}: ")
        mic_nums.append(mic_num)
        rms, peak = test_mic(audio_receiver, mic_index, sample_duration, rms_range)
        rms_values.append(rms)
        peak_values.append(peak)

        if mic_index == 7: mic_index = 0
        else: mic_index += 1
        counter += 1

    print("All mics tested")
    print()
    print()
    for i, (r, p) in enumerate(zip(rms_values, peak_values)):
        if rms_range[0] <= r <= rms_range[1]:
            status = 'PASSED'
        else: status = 'failed'
        print(f'Ch{i+1}:\t{status}\t|\tRMS={r}\t|\tPeak={p}')

    # if wanting to export results to csv file for comparison
    export_to_csv(rms_values, peak_values, rms_range, mic_nums)
