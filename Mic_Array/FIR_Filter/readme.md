# Mic Array / FIR Filter

1. setup mic_coordinates
2. calculate time delays
   - directional cosines
   - speed of sound
   - calculate time delays
   - convert to sample delay
3. generate fir_filter coeffs
   - generate sinc function
   - window function

   

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
 * set cutoff frequency higher than desired frequency range of interest, which naturally is the nyquist frequency
 * The sinc function sinc(t−di) where t is the time index and di is the delay.
 * Apply a window function (e.g., Hamming, Hann, blackman) to the sinc function to truncate it to a finite length and smooth the edges.
 * blackman provides better side lob suppression at the cost of main lobe resolution
 * increasing the number of taps can increase main lob resolution at the cost of computational complexity
 * The result is a set of FIR filter coefficients for each microphone.
 









