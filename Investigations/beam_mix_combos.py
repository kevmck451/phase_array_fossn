import numpy as np
import pandas as pd

c = 343  # Speed of sound
d = 0.08  # base spacing

# Define exact subarrays you care about
subarrays = [
    [i for i in range(16)],        # 16 mics, 0.08 m spacing
    list(range(0, 16, 2)),         # 8 mics, 0.16 m
    list(range(0, 16, 4)),         # 4 mics, 0.32 m
    [0, 5, 10, 15],                # 4 mics, 0.40 m

]

results = []
for indices in subarrays:
    if len(indices) < 2:
        continue
    spacing = (indices[1] - indices[0]) * d
    fc = c / (2 * spacing)
    results.append((len(indices), spacing, fc, indices))

# Display
df = pd.DataFrame(results, columns=["Num Mics", "Spacing (m)", "Center Frequency (Hz)", "Mic Indices"])
df.sort_values(by="Center Frequency (Hz)", ascending=False, inplace=True)

print(df.to_string(index=False))
