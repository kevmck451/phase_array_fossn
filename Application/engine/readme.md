# Engine Pipeline


## Array
1. Array Configs: info specific to each array selected at runtime
2. AudioReceiver: connects to FPGA server to collect data
3. AudioStream: saves to data to disk and divides in user defined chunks for queue
4. AudioStreamSimulator: simulated stream from already collected array data


## Beamform
1. Beamform: facilities beamforming data from a given array
2. Mic_Coordinates: generates an arbitrary coordinate system for the array
3. Generate FIR Coeffs: time delays and FIR filters
4. Time Delays: calculate the time delays
5. FIR Filter: create the fir filter coefficients for each mic


## Filters
1. Processor: implements the processing pipeline for narrow band monitoring
2. High Pass: remove low frequencies below a cutoff
3. Down Sample: lower data size and low pass filter below cutoff(nyquist) / 2 
4. Normalize: min/max normalization - re-adjust data to fit inside the contain
5. Noise Reduction: possibility for noise reduction. not currently used


## Detectors
1. PCA Calculator: calculates the principal components from audio data using 'nperseg' and 'num'
2. Detectors: using pca data, a normal operation baseline is calculated and then new data is statistically compared for anomaly detection





















