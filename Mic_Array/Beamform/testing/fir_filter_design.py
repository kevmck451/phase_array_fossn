import numpy as np
from Mic_Array.Beamform.papa import beamform

# Parameters
m, n = 4, 4  # Microphone array dimensions
frequency = 2000  # Frequency of interest
c = 343.3  # Speed of sound in air (m/s)
d = 0.082333  # Distance between microphones (m)
sample_rate = 48000  # Sampling rate
filter_length = 101  # FIR filter length
win_length = 25  # Window length for beamforming

# Target direction
target_azimuth = 30  # Target azimuth angle in degrees
target_elevation = 10  # Target elevation angle in degrees

# Initialize microphone position arrays
mic_positions_x = np.zeros([m, n])
mic_positions_y = np.zeros([m, n])
mic_positions_z = np.zeros([m, n])  # Assume 2D for simplicity

for i in range(m):
    for j in range(n):
        mic_positions_y[i, j] = j * d
        mic_positions_z[i, j] = i * d

# Calculate delays and weights for the specific target direction
fir_taps = np.zeros([m, n, filter_length])

for y in range(n):
    for x in range(m):
        # Calculate delay for each microphone to steer the beam towards the target angle
        fir_taps[x, y], *extras = beamform.delay(
            mic_positions_x[x, y], mic_positions_y[x, y], mic_positions_z[x, y],
            target_azimuth, target_elevation, sample_rate, filter_length, win_length)

# Prepare to output FIR taps in a specific format
fir_formatted = np.empty_like(fir_taps).reshape(m*n, filter_length)
for idx, (row, col) in enumerate(np.ndindex(m, n)):
    fir_formatted[idx] = fir_taps[row, col]

# Convert to format for FPGA or processing: shape should be [number of channels, filter_length]
fir_formatted = fir_formatted.reshape(m*n, filter_length).transpose()

# Write to file
with open('coefficients.txt', 'w') as f:
    f.write("# Coefficients for specific steering direction\n")
    f.write("# Each row corresponds to one channel's FIR taps\n")
    for taps in fir_formatted:
        f.write(' '.join(map(str, taps)) + '\n')

print(f"Output shape for FIR coefficients: {fir_formatted.shape}")
