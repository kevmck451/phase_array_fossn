import numpy as np
from scipy.signal import firwin, freqz, group_delay
import matplotlib.pyplot as plt

# Desired specifications
fs = 48000  # Sampling rate
nyquist = fs / 2
cutoff = [3000, 5000]  # Cutoff frequencies for a bandpass filter
initial_num_taps = 51  # Initial guess for the number of taps

# Initial filter design
b = firwin(initial_num_taps, cutoff, pass_zero=False, fs=fs)

# Analyze the initial design
w, h = freqz(b, worN=8000, fs=fs)
w_gd, gd = group_delay((b, 1), fs=fs)

# Plot initial results
plt.figure(figsize=(12, 6))
plt.subplot(1, 2, 1)
plt.title('Initial Frequency Response')
plt.plot(w, 20 * np.log10(abs(h)), label='Amplitude')
plt.xlabel('Frequency (Hz)')
plt.ylabel('Amplitude (dB)')
plt.grid(True)

plt.subplot(1, 2, 2)
plt.title('Initial Group Delay')
plt.plot(w_gd, gd, label='Group Delay', color='red')
plt.xlabel('Frequency (Hz)')
plt.ylabel('Delay (samples)')
plt.grid(True)
plt.tight_layout()
plt.show()

# Evaluation and adjustment
# If the group delay is not acceptable, adjust num_taps and re-calculate
