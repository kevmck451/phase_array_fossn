
import matplotlib.pyplot as plt
import numpy as np

def generate_fir_coefficients(time_delay, num_taps):
    time_index = np.arange(-num_taps // 2, num_taps // 2)
    # print(time_index)

    # Calculate the ideal sinc filter centered at the delay
    sinc_func = np.sinc(time_index - time_delay)
    # plt.plot(time_index, sinc_func)
    # plt.show()

    # Apply a window function to smooth the sinc function
    window = np.blackman(num_taps)
    coefficients = sinc_func * window
    # print(f'FIR coefficient shape: {fir_coefficients.shape}')

    # Normalize the filter coefficients
    coefficients /= np.sum(coefficients)
    # print(fir_coefficients.shape)

    return coefficients


def create_fir_filters(time_delay_array, num_taps):
    # a cutoff at the Nyquist frequency,
    # you do not need to scale the sinc function
    # since the sinc function itself
    # represents an ideal low-pass filter with a cutoff
    # at half the sampling rate

    fir_coefficients = np.zeros((time_delay_array.shape[0] , time_delay_array.shape[1], num_taps))

    for row in range(fir_coefficients.shape[0]):
        for col in range(fir_coefficients.shape[1]):
            fir_coefficients[row, col, :] = generate_fir_coefficients(time_delay_array[row, col], num_taps)

    return fir_coefficients

