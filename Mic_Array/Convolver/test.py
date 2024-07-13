import numpy as np
from scipy.signal import lfilter

# Parameters
num_mics = 16  # 4x4 array
grid_size = 5  # 5x5 beamformed grid
sample_rate = 16000  # Example sample rate in Hz
num_taps = 100  # Number of FIR filter taps
mic_spacing = 0.08  # Distance between mics in meters

# Example microphone array data (random data for demonstration)
np.random.seed(0)
mic_data = np.random.randn(4, 4, sample_rate)  # 1 second of audio data for each mic in a 4x4 array


# Function to generate FIR tap coefficients for a given delay
def generate_delay_fir_taps(num_taps, delay_samples):
    taps = np.zeros(num_taps)
    if 0 <= delay_samples < num_taps:
        taps[delay_samples] = 1.0
    return taps


# Function to apply FIR filter to microphone data
def apply_fir_filter(mic_data, fir_coefficients):
    num_mics, num_samples = mic_data.shape
    filtered_data = np.zeros((num_mics, num_samples))
    for i in range(num_mics):
        filtered_data[i] = lfilter(fir_coefficients[i], 1.0, mic_data[i])
    return filtered_data


# Function to compute delays for each microphone for a given beam direction
def compute_delays(mic_positions, target_position, sound_speed=343.0):
    delays = np.zeros(len(mic_positions))
    for i, (x, y) in enumerate(mic_positions):
        distance = np.sqrt((x - target_position[0]) ** 2 + (y - target_position[1]) ** 2)
        delays[i] = distance / sound_speed
    return delays


# Define microphone positions for a 4x4 array
mic_positions = [(i % 4 * mic_spacing, i // 4 * mic_spacing) for i in range(num_mics)]

# Define target positions for the 5x5 beamformed grid (normalized to center of 4x4 array)
grid_range = np.linspace(-0.2, 0.2, grid_size)  # Example range, adjust as needed
beamformed_positions = [(x, y) for x in grid_range for y in grid_range]

# Initialize beamformed data array
beamformed_data = np.zeros((grid_size, grid_size, sample_rate))

for idx, target_position in enumerate(beamformed_positions):
    # Compute delays for current beam position
    delays = compute_delays(mic_positions, target_position)
    delay_samples = np.round(delays * sample_rate).astype(int)

    # Generate FIR coefficients for each microphone
    fir_coefficients = [generate_delay_fir_taps(num_taps, delay) for delay in delay_samples]

    # Apply FIR filters to microphone data
    filtered_mic_data = np.zeros((4, 4, sample_rate))
    for i in range(4):
        for j in range(4):
            mic_idx = i * 4 + j
            filtered_mic_data[i, j] = lfilter(fir_coefficients[mic_idx], 1.0, mic_data[i, j])

    # Sum the delayed signals to create beamformed output
    beamformed_channel = np.sum(filtered_mic_data, axis=(0, 1))
    grid_x, grid_y = divmod(idx, grid_size)
    beamformed_data[grid_x, grid_y] = beamformed_channel

# Print the shapes of the data arrays to verify
print("Original Mic Data Shape:", mic_data.shape)
print("Beamformed Data Shape:", beamformed_data.shape)
