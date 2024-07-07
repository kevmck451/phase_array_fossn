import numpy as np
from scipy.signal import firwin, convolve
import matplotlib.pyplot as plt


# FIR Coefficient Generation
def generate_fir_coeffs(R, C, R_out, C_out, num_taps=100):
    coeffs = []
    for r in range(R_out):
        row_coeffs = []
        for c in range(C_out):
            fir_coeff = firwin(num_taps, cutoff=0.5, window='hamming', pass_zero=True)
            delay = (r * C_out + c) % (R * C)
            if delay != 0:
                row_coeffs.append(fir_coeff * delay)
            else:
                row_coeffs.append(fir_coeff)
        coeffs.append(row_coeffs)
    return np.array(coeffs)


# Generate Specific Audio Data
def generate_test_signal(target_row, target_col, R, C, length=1000):
    audio_data = np.zeros((length, R * C))
    peak_position = (target_row % R) * C + (target_col % C)
    t = np.linspace(0, 20 * np.pi, length)
    audio_data[:, peak_position] = np.sin(t)  # Distinct sine wave
    return audio_data


# Calculate RMS
def calculate_rms(audio):
    return np.sqrt(np.mean(audio ** 2))


# Visualize RMS Values
def visualize_rms(rms_values, R_out, C_out):
    fig, ax = plt.subplots()
    cax = ax.matshow(rms_values, cmap='viridis')
    fig.colorbar(cax)
    for i in range(R_out):
        for j in range(C_out):
            c = rms_values[i, j]
            ax.text(j, i, f'{c:.2f}', va='center', ha='center')
    plt.show()


# Beamform Audio
def beamform_audio(audio_data, fir_coeffs, R, C, R_out, C_out):
    beamformed_audio = np.zeros((audio_data.shape[0], R_out * C_out))
    for r in range(R_out):
        for c in range(C_out):
            mic_index = (r % R) * C + (c % C)
            mic_data = audio_data[:, mic_index]
            beamformed_audio[:, r * C_out + c] = convolve(mic_data, fir_coeffs[r, c], mode='same')
    return beamformed_audio


# Main Testing Process
R, C = 4, 4
R_out, C_out = 5, 5
num_taps = 100

# Generate FIR Coefficients
fir_coeffs = generate_fir_coeffs(R, C, R_out, C_out, num_taps)

# Generate Test Signals
test_signals = [generate_test_signal(r, c, R, C) for r in range(R_out) for c in range(C_out)]

# Process Each Test Signal
for i, audio_data in enumerate(test_signals):
    target_row = i // C_out
    target_col = i % C_out

    # Beamform Audio
    beamformed_audio = beamform_audio(audio_data, fir_coeffs, R, C, R_out, C_out)

    # Calculate RMS Values
    rms_values = np.zeros((R_out, C_out))
    for r in range(R_out):
        for c in range(C_out):
            rms_values[r, c] = calculate_rms(beamformed_audio[:, r * C_out + c])

    # Print Results
    max_rms = np.max(rms_values)
    max_pos = np.unravel_index(np.argmax(rms_values), rms_values.shape)
    print(f'Target square ({target_row}, {target_col}):')
    print(f'Highest RMS Value: {max_rms:.2f} at position {max_pos}')
    print('---')

    # Visualize RMS (optional)
    visualize_rms(rms_values, R_out, C_out)
