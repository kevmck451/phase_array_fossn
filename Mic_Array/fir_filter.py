
import matplotlib.pyplot as plt
import numpy as np
import math

def generate_fir_coefficients(time_delay, num_taps):
    time_index = np.arange(-num_taps // 2, num_taps // 2 + 1)
    # print(time_index)

    # Calculate the ideal sinc filter centered at the delay
    sinc_func = np.sinc(time_index - time_delay)
    # plt.plot(time_index, sinc_func)
    # plt.show()

    # Apply a window function to smooth the sinc function
    window = np.blackman(num_taps + 1)
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

    fir_coefficients = np.zeros((time_delay_array.shape[0] , time_delay_array.shape[1], num_taps+1))

    for row in range(fir_coefficients.shape[0]):
        for col in range(fir_coefficients.shape[1]):
            fir_coefficients[row, col, :] = generate_fir_coefficients(time_delay_array[row, col], num_taps)

    return fir_coefficients


if __name__ == '__main__':
    # Parameters
    delay = 20.25  # desired fractional delay in samples
    num_taps = 201  # number of filter taps (should be even)

    # Design the FIR filter
    fir_filter = generate_fir_coefficients(delay, num_taps)

    # Define the time index for plotting with higher resolution
    t_high_res = np.linspace(-num_taps // 2, num_taps // 2, 1000)
    sinc_func_high_res = np.sinc(t_high_res - delay)

    # Define the original time index for plotting window and FIR filter
    t = np.arange(-num_taps // 2, num_taps // 2 + 1)
    window = np.blackman(num_taps + 1)

    # Plot the sinc function, window, and the resulting FIR filter
    plt.figure(figsize=(12, 6))

    plt.subplot(3, 1, 1)
    plt.plot(t_high_res, sinc_func_high_res, label='Sinc Function')
    plt.legend()
    plt.grid()

    plt.subplot(3, 1, 2)
    plt.plot(t, window, label='Blackman Window Function')
    plt.legend()
    plt.grid()

    plt.subplot(3, 1, 3)
    plt.plot(t, fir_filter, label='Windowed Sinc (FIR Filter)')
    plt.legend()
    plt.grid()

    plt.tight_layout()
    plt.show()


    # Compare Hamming and Blackman windows
    hamming_window = np.hamming(num_taps + 1)
    blackman_window = np.blackman(num_taps + 1)

    plt.figure(figsize=(12, 6))
    plt.plot(t, hamming_window, label='Hamming Window')
    plt.plot(t, blackman_window, label='Blackman Window')
    plt.legend()
    plt.grid()
    # plt.show()


