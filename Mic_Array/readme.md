# Mic Array

2. mic_coordinates
3. time delays
   - directional cosines
   - speed of sound
   - calculate time delays
   - convert to sample delay
4. fir_filter
   - generate sinc function
   - window function
5. Convolution
6. Summation
7. Normalization


Beamforming Process:

## Microphone Array Grid:
 * Define the positions of the microphones in the array using an (x,y) coordinate system.
 * these grid coordinate are from the perspective of in front the array with (0,0) at the top left
 * the reference is from the center of the array

## Calculate Time Delays:
 * Use directional cosines to model the direction of arrival of the sound wave, assuming far-field conditions where the wavefronts are planar
 * For each microphone, calculate the time delay τi  based on the directional cosines and the positions of the microphones
 * This involves computing the path differences and converting them into time delays using the speed of sound
 * speed of sound changes depending on temperature
 * convert the time delay to sample delay by multiplying by sample rate
 * Since the calculated sample delays are not always integers, fractional delays need to be handled.
 * The most accurate way to implement fractional delays is by designing FIR filters that approximate these delays.

## Create FIR Filters:
 * For each microphone, create a sinc function centered at the delay di
 * The sinc function represents the ideal low-pass filter that will be used to create the FIR filter
 * set cutoff frequency higher than desired frequency range of interest
 * The sinc function sinc(t−di) where t is the time index and di is the delay.
 * Apply a window function (e.g., Hamming, Hann, blackman) to the sinc function to truncate it to a finite length and smooth the edges.
 * blackman provides better side lob suppression at the cost of main lobe resolution
 * increasing the number of taps can increase main lob resolution at the cost of computational complexity
 * The result is a set of FIR filter coefficients for each microphone.

## Convolution:
 * Convolve each microphone's input signal with its corresponding FIR filter coefficients.
 * Convolution is a process where the input signal is multiplied and summed with the FIR filter coefficients to produce a delayed output signal.

## Summation:
 * Sum the delayed signals from all microphones.
 * This summation aligns the signals from the desired direction (beamforming), enhancing them while attenuating signals from other directions.

## Normalization:
 * Bring values back into expected ranges









