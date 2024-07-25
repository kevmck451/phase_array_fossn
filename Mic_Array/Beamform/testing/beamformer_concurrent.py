from Mic_Array.FIR_Filter.mic_coordinates import generate_mic_coordinates
from Mic_Array.FIR_Filter.generate_fir_coeffs import generate_fir_coeffs

import concurrent.futures
import time

# Assuming generate_mic_coordinates and generate_fir_coeffs are already defined
# Import necessary modules and functions if not included

def compute_fir(mic_coords, theta, phi, temp_F, sample_rate):
    return generate_fir_coeffs(mic_coords, theta, phi, temp_F, sample_rate)

if __name__ == '__main__':
    mic_coords = generate_mic_coordinates()
    temp_F = 95  # temperature in Fahrenheit
    sample_rate = 48000

    thetas = list(range(-90, 91, 1))
    phis = list(range(-90, 91, 1))

    start_time = time.time()

    with concurrent.futures.ProcessPoolExecutor() as executor:
        futures = [
            executor.submit(compute_fir, mic_coords, theta, phi, temp_F, sample_rate)
            for theta in thetas
            for phi in phis
        ]
        results = [future.result() for future in concurrent.futures.as_completed(futures)]

    end_time = time.time()
    total_time = end_time - start_time
    print(f'Total Time: {total_time}s')



