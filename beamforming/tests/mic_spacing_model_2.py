import matplotlib.pyplot as plt
import numpy as np

def hexagon_points(center, radius):
    """Generate points for a hexagon given a center and radius."""
    return np.array([
        [center[0] + radius * np.cos(np.pi / 3 * i), center[1] + radius * np.sin(np.pi / 3 * i)]
        for i in range(6)
    ])

# Initial setup
center_point = np.array([0, 0])
radius = 0.08  # 0.08 meters or units
initial_hex = hexagon_points(center_point, radius)

# Add microphones
extended_mics = np.array([]).reshape(0, 2)  # Initialize as an empty 2D array
for i in [1, 4]:  # indices of the outer mics to extend from, can be adjusted as needed
    new_center = initial_hex[i]
    extended_hex = hexagon_points(new_center, radius)
    # Only add new points that are not overlapping with initial hexagon
    for point in extended_hex:
        if not any(np.all(np.isclose(point, p)) for p in np.vstack([initial_hex, extended_mics])):
            extended_mics = np.vstack([extended_mics, point])

# Combine all points
all_points = np.vstack([initial_hex, extended_mics])

# Plotting
plt.figure(figsize=(8, 8))
plt.scatter(initial_hex[:, 0], initial_hex[:, 1], color='blue', s=100, label='Initial Hexagon Mics')
if extended_mics.size > 0:
    plt.scatter(extended_mics[:, 0], extended_mics[:, 1], color='green', s=100, label='Extended Mics')
plt.title('17-Microphone Hexagonal Configuration')
plt.xlabel('Distance (meters)')
plt.ylabel('Distance (meters)')
plt.grid(True)
plt.legend()
plt.axis('equal')
plt.show()
