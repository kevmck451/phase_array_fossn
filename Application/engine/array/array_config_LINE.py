# Config file for Array: Line

sample_rate = 48000
mic_spacing = 0.08  # meters - based on center freq

rows = 1
cols = 16
num_mics = rows * cols

# channel 1 through X in audacity
# where is its position in the array ((0,0) is reference)

mic_positions = [
        (0, 6),
        (0, 7),
        (0, 4),
        (0, 5),
        (0, 2),
        (0, 3),
        (0, 0),
        (0, 1),
        (0, 8),
        (0, 9),
        (0, 10),
        (0, 11),
        (0, 12),
        (0, 13),
        (0, 14),
        (0, 15),
    ]

# amount of data that can be collected with 4GB per .wav file standard in seconds
chunk_duration = 15 * 60  # 10 minutes in seconds

title = 'Line Array'

directory_name = 'Line'

Ltheta = -70
Rtheta = 70
increment = 10
default_theta_directions = list(range(Ltheta, Rtheta + 1, increment))

