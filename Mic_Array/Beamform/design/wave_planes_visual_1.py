import numpy as np
import matplotlib.pyplot as plt

# Function to generate wavefront points
def generate_wavefront(distance, array_length, num_points=100):
    x = np.linspace(-array_length / 2, array_length / 2, num_points)
    if distance == float('inf'):
        # Plane wave
        y = np.zeros(num_points)
    else:
        # Circular wavefront
        y = np.sqrt(distance**2 - x**2) - distance
    return x, y

# Function to calculate the error metric
def calculate_error_metric(y_wavefront, y_plane):
    return np.linalg.norm(y_wavefront - y_plane)

# Parameters
array_length = 10.0  # Length of the array in meters
distances = [float('inf'), 50, 20, 10, 5, 2]  # Distances of the sound source in meters
num_points = 100  # Number of points on the wavefront

# Generate wavefronts and calculate errors
wavefronts = []
errors = []
x = np.linspace(-array_length / 2, array_length / 2, num_points)
y_plane = np.zeros(num_points)

for distance in distances:
    x_wavefront, y_wavefront = generate_wavefront(distance, array_length, num_points)
    wavefronts.append((x_wavefront, y_wavefront))
    error = calculate_error_metric(y_wavefront, y_plane)
    errors.append(error)

# Plotting
plt.figure(figsize=(12, 6))
for i, (distance, (x_wavefront, y_wavefront)) in enumerate(zip(distances, wavefronts)):
    plt.plot(x_wavefront, y_wavefront, label=f'Distance = {distance} m')

plt.axhline(0, color='black', linestyle='--', label='Plane wave')
plt.xlabel('Position along array (m)')
plt.ylabel('Wavefront displacement (m)')
plt.title('Wavefronts at Different Distances')
plt.legend()
plt.grid(True)
plt.show()

# Print errors
for distance, error in zip(distances, errors):
    print(f'Distance: {distance} m, Error: {error:.4f} m')
