import matplotlib.pyplot as plt
import numpy as np

# Define the central microphone and hexagonal pattern
center_point = np.array([0, 0])
angle_offset = np.pi / 6  # offset to start from the top of the hexagon
radius = 0.08  # 0.08 meters or units

# Generate points
points = [center_point]
for i in range(6):
    angle = angle_offset + i * 2 * np.pi / 6
    x = center_point[0] + radius * np.cos(angle)
    y = center_point[1] + radius * np.sin(angle)
    points.append([x, y])

points = np.array(points)

# Plotting
plt.figure(figsize=(6, 6))
plt.scatter(points[:, 0], points[:, 1], color='blue', s=100)
for point in points[1:]:
    plt.plot([center_point[0], point[0]], [center_point[1], point[1]], 'r-')
plt.title('7-Microphone Hexagonal Configuration')
plt.xlabel('Distance (meters)')
plt.ylabel('Distance (meters)')
plt.grid(True)
plt.axis('equal')
plt.show()
