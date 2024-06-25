import numpy as np
import beamform


# These values can change

c = 343.3 # speed of sound in air / depends on temp
filter_length = 101
synthetic_channels = 75
synthetic_shape_x = 5
synthetic_shape_y = 15


# Freq Configuration
frequency = 2000
lmbda = c / frequency

# Mic Configuration
m = 4 # Rows
n = 12 # Cols
num_microphones = n * m
d = 0.08  # distance of mics   # lmbda * 0.48
sample_rate = 48000
angle_res = 22.5 # Must be less than HPBW
fov = 180 #deg
fov_bound = fov/2

# 1 Generate distance array for each microphone wrt reference microphone

mic_dist_x = np.zeros([m,n])
mic_dist_y = np.zeros([m,n])
mic_dist_z = np.zeros([m,n]) # Keep 0s for 2D, to implement 3D populate with z offsets

# Generate mic matrix
for i in range(m): # rows
    for j in range(n): # cols
        mic_dist_y[i, j] = (n-j-1) * d
        mic_dist_z[i, j] = (m-i-1) * d # hard-computing y in the case of a non-square array. otherwise can just transpose x to form y matrix

dir_samples = int((fov/angle_res)+1) # +- 45 degree look angle

delay_mtx = np.zeros([m,n])

print(f'y: {mic_dist_y}')
print(f'z: {mic_dist_z}')

### Refresh block ----------------------------------------------

#x = n = b
#y = m = a


fir_taps = np.zeros([m, n, dir_samples, dir_samples, filter_length]) # ROW, COL, EL, AZ, TAPS

for i in range(dir_samples):
    el = -fov_bound + (angle_res*i) #+ 90
    for k in range(dir_samples):
        az = -fov_bound + (angle_res*k) #-180
        print(f'beamforming for {az} az and {el} el')
        for y in range(m):
            for x in range(n):
                # print(str(mic_dist_x[a,b]) + " " + str(mic_dist_y[a, b]) + " " + str(mic_dist_z[a, b]))
                fir_taps[y,x,i,k], *crap = beamform.delay(mic_dist_x[y,x], mic_dist_y[y,x], mic_dist_z[y,x], (az), (el),
                                                          sample_rate, filter_length, synthetic_channels)

print(fir_taps.shape)

# Dynamically determine the dimensions based on fir_taps
el_samples = fir_taps.shape[2]
az_samples = fir_taps.shape[3]

y_t = np.empty_like(fir_taps).reshape(num_microphones, el_samples, az_samples, filter_length)


# Flipped about Y origin
y_t[8] = fir_taps[0,0]
y_t[9] = fir_taps[0,1]
y_t[12] = fir_taps[0,2]
y_t[13] = fir_taps[0,3]
y_t[5] = fir_taps[1,0]
y_t[4] = fir_taps[1,1]
y_t[1] = fir_taps[1,2]
y_t[0] = fir_taps[1,3]
y_t[7] = fir_taps[2,0]
y_t[6] = fir_taps[2,1]
y_t[3] = fir_taps[2,2]
y_t[2] = fir_taps[2,3]
y_t[10] = fir_taps[3,0]
y_t[11] = fir_taps[3,1]
y_t[14] = fir_taps[3,2]
y_t[15] = fir_taps[3,3]

# squish square axes
x = y_t.reshape(num_microphones, synthetic_channels, filter_length)
# convert to fpga shape
y = x.transpose(1, 2, 0)
# linearize
z = y.reshape(-1)

print(y.shape)

print(y_t.shape)

f = open('coefficients.txt', 'w')
f.write("# the sexy and cool coefficients\n")
f.write(f"# for a FOV of {fov} for steps of {angle_res}")
f.write(f"# and a mic shape of mics={y.shape[2]}, taps={y.shape[1]}, chans={y.shape[0]}\n")
for nombre in z:
    f.write(f"{nombre}\n")
f.close()

XR = fir_taps[:, :, 3, 1].ravel()
print(XR[XR > 0.1])
print(XR.sum())


