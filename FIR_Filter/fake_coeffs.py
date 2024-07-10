# Define parameters
num_mics = 48
num_chans = 25
taps = 101
total_lines = num_mics * num_chans * taps

# Open the file in write mode
with open('coefficients.txt', 'w') as file:
    # Write the first two lines
    file.write("# the sexy and cool FAKE coefficients for testing\n")
    file.write("# THESE ARE FAKE VALUES AND ONLY USED FOR TESTING RAW MICS\n")

    # Write the coefficient lines
    for _ in range(total_lines):
        file.write("0.01\n")

print(f"File 'fake_coefficients.txt' created with {total_lines} coefficient lines.")
