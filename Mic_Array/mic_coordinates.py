import numpy as np

# Array Configuration
rows = 4
cols = 12
mic_spacing = 0.08  # meters - based on center freq
num_mics = rows * cols

def generate_mic_coordinates():
    '''
        these grid coordinate are from the perspective of in front the array with (0,0) at the top left
        the reference is from the center of the array
    '''
    mic_coords = np.zeros((num_mics, 3))  # Initialize coordinates array

    idx = 0
    for row in range(rows):
        for col in range(cols):
            # Calculate the position centered around (0, 0)
            x = (col - (cols - 1) / 2) * mic_spacing
            y = ((rows - 1) / 2 - row) * mic_spacing  # Flip the sign to correct y-coordinate
            z = 0  # For a 2D array, z is always 0
            mic_coords[idx] = [x, y, z]
            idx += 1

    return mic_coords

if __name__ == '__main__':
    mic_coordinates = generate_mic_coordinates()

    # Print the coordinates as a 4x12 grid
    print("Microphone coordinates in a 4x12 grid:")
    for row in range(rows):
        for col in range(cols):
            idx = row * cols + col
            x, y, z = mic_coordinates[idx]
            print(f'({x:.3f}, {y:.3f})', end='\t ')
        print()