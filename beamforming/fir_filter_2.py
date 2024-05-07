import numpy as np
from scipy.signal import firwin, group_delay, freqz
import matplotlib.pyplot as plt

def design_bandpass_delay_filter(numtaps, lowcut, highcut, fs, delay):
    # Design a bandpass filter using the window method
    taps = firwin(numtaps, [lowcut, highcut], pass_zero=False, fs=fs)

    # Introduce delay by modifying the phase response
    # This shifts the filter coefficients in time
    n = np.arange(numtaps)
    delayed_taps = taps * np.exp(-1j * 2 * np.pi * delay / fs * n)

    return delayed_taps

# Filter specifications
numtaps = 101  # Number of taps in the FIR filter
fs = 48000  # Sampling rate in Hz
lowcut = 300  # Low frequency of the bandpass filter in Hz
highcut = 3000  # High frequency of the bandpass filter in Hz
delay = 0.001  # Delay in seconds

# Design the filter
taps = design_bandpass_delay_filter(numtaps, lowcut, highcut, fs, delay)

# Frequency and phase response
w, h = freqz(taps, worN=8000, fs=fs)
plt.figure()
plt.title('Frequency and Phase Response')
plt.plot(w, 20 * np.log10(np.abs(h)), 'b')
plt.ylabel('Amplitude [dB]', color='b')
plt.xlabel('Frequency [Hz]')
plt.grid()

# Group delay
delays = group_delay((taps, 1), fs=fs)
plt.twinx()
plt.plot(delays[0], delays[1], 'r')
plt.ylabel('Delay [samples]', color='r')
plt.show()
