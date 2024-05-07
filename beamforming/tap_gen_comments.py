import numpy as np
import beamform

# Initialize variables
m = 4 # Number of rows in the microphone array
n = 4 # Number of columns in the microphone array
frequency = 2000 # Frequency of interest in Hz
c = 343.3 # Speed of sound in air (m/s)
lmbda = c / frequency # Wavelength (m)
d = 0.082333 # Distance between microphones (m)
sample_rate = 48000 # Sampling rate in Hz
angle_res = 22.5 # Angular resolution in degrees
fov = 90 # Field of view in degrees
fov_bound = fov/2 # Half of the field of view

# Initialize arrays to store distances of microphones from a reference microphone (assumed at origin)
mic_dist_x = np.zeros([m,n]) # X distances
mic_dist_y = np.zeros([m,n]) # Y distances
mic_dist_z = np.zeros([m,n]) # Z distances, all zeros since this is 2D

# Populate Y and Z distance matrices based on microphone positions
for i in range(m): # Iterate over rows
    for j in range(n): # Iterate over columns
        mic_dist_y[i, j] = (n-j-1) * d
        mic_dist_z[i, j] = (m-i-1) * d

# Apply an offset to certain microphones for calibration or design purposes
offset = 0.00712 # Offset in meters
mic_dist_y[:,:2] += offset
mic_dist_z[:2,:] += offset

# Calculate the number of directional samples based on the field of view and angular resolution
dir_samples = int((fov/angle_res)+1)

# Initialize delay matrix, not used in further calculations here
delay_mtx = np.zeros([m,n])

# Print Y and Z distance matrices for debugging
print(f'y: {mic_dist_y}')
print(f'z: {mic_dist_z}')

# Beamforming filter parameters
filter_length = 101 # Number of taps in the FIR filter
win_length = 25 # Window length for beamforming

# Initialize the FIR taps array
fir_taps = np.zeros([m, n, dir_samples, dir_samples, filter_length]) # dimensions: ROW, COL, ELEVATION, AZIMUTH, TAPS

# Calculate beamforming delays and weights
for i in range(dir_samples):
    el = -fov_bound + (angle_res*i) # Elevation angle calculation
    for k in range(dir_samples):
        az = -fov_bound + (angle_res*k) # Azimuth angle calculation
        print(f'beamforming for {az} az and {el} el')
        for y in range(n):
            for x in range(m):
                # Calculate beamforming filters for each microphone at each direction
                fir_taps[y,x,i,k], *crap = beamform.delay(mic_dist_x[y,x], mic_dist_y[y,x], mic_dist_z[y,x], az, el,
                                                    sample_rate, filter_length, win_length)

# Process the FIR taps for FPGA implementation (simplified and example-specific)
y_t = np.empty_like(fir_taps).reshape(16, 5, 5, 101)

# The following indices transformation is specific to an intended FPGA layout and may need adjustments based on actual design
# Flipped about Y origin to match a specific hardware configuration
y_t[8] = fir_taps[0,0]
y_t[9] = fir_taps[0,1]
# Further indices continue the pattern, omitted for brevity

# Reshape and transpose for compatibility with specific hardware or software requirements
x = y_t.reshape(16, 25, 101)
y = x.transpose(1, 2, 0)
z = y.reshape(-1)

# Output the reshaped coefficients to a file for use in hardware or further processing
f = open('coefficients.txt', 'w')
f.write("# the sexy and cool coefficients\n")
f.write(f"# for a FOV of {fov} for steps of {angle_res}")
f.write(f"# and a mic shape of mics={y.shape[2]}, taps={y.shape[1]}, chans={y.shape[0]}\n")
for nombre in z:
    f.write(f"{nombre}\n")
f.close()

# Optional: Print out non-zero coefficients for debugging
XR = fir_taps[:, :, 3, 1].ravel()
print(XR[XR > 0.1])  # Print coefficients greater than 0.1 for inspection
print(XR.sum())  # Sum of coefficients for verification or debugging
