import numpy as np
import pandas as pd
from scipy import fft


def next_pow_2(x):
    return 1 << (x - 1).bit_length()


def spectral_whitening(audio_object, N=None, epsilon=1e-10):
    def whiten(data):
        # Step 1: Zero-mean the signal
        data = data - np.mean(data)

        # Step 2: Compute the next power of 2 for FFT
        n = len(data)
        nfft = next_pow_2(n)

        # Step 3: Compute the FFT of the data
        spec = fft.fft(data, nfft)

        # Step 4: Compute the amplitude spectrum
        spec_ampl = np.sqrt(np.abs(np.multiply(spec, np.conjugate(spec))))

        # Step 5: Optional smoothing with a rolling window
        if N is not None:
            shift = N // 2
            spec = spec[shift:-shift]
            spec_ampl = pd.Series(spec_ampl).rolling(N, center=True).mean().to_numpy()[shift:-shift]

        # Step 6: Smooth the amplitude spectrum to avoid division by very small values
        spec_ampl = np.maximum(spec_ampl, epsilon)

        # Step 7: Whiten the spectrum by dividing by the smoothed amplitude spectrum
        spec = np.true_divide(spec, spec_ampl)

        # Step 8: Inverse FFT to convert back to time domain
        whitened_data = np.real(fft.ifft(spec, nfft))

        return whitened_data

    whitened_data = np.zeros_like(audio_object.data)

    if audio_object.num_channels == 1:
        whitened_data = whiten(audio_object.data)
    else:
        for i in range(audio_object.data.shape[0]):
            whitened_data[i, :] = whiten(audio_object.data[i, :])

    return whitened_data















