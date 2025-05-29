# Config file for Array: Rectangular

from Application.engine.array.BeamMixConfig import BeamMixConfig

sample_rate = 48000

# for the actual array
rows = 4
cols = 12
num_mics = rows * cols
mic_spacing = 0.08  # meters - based on center freq

# channel 1 through X in audacity
# channel 1 through X, where is it's position in the array ((0,0) is reference)
mic_positions = [
        (1, 0), (0, 0), (1, 1), (0, 1), (3, 0), (2, 0), (3, 1), (2, 1),
        (1, 2), (0, 2), (1, 3), (0, 3), (3, 2), (2, 2), (3, 3), (2, 3),
        (1, 4), (0, 4), (1, 5), (0, 5), (3, 4), (2, 4), (3, 5), (2, 5),
        (1, 6), (0, 6), (1, 7), (0, 7), (3, 6), (2, 6), (3, 7), (2, 7),
        (1, 8), (0, 8), (1, 9), (0, 9), (3, 8), (2, 8), (3, 9), (2, 9),
        (1, 10), (0, 10), (1, 11), (0, 11), (3, 10), (2, 10), (3, 11), (2, 11)
    ]

# amount of data that can be collected with 4GB per .wav file standard in seconds
chunk_duration = 15 * 60  # 10 minutes in seconds

title = 'Rectangular Array'

directory_name = 'Rect'

Ltheta = -70
Rtheta = 70
increment = 10
default_theta_directions = list(range(Ltheta, Rtheta + 1, increment))

number_of_taps = 201

ip_address = '192.168.0.2'

server_port = 21197

# for beamforming
beam_mix_1 = BeamMixConfig(
    name="Mix 1",
    center_frequency=2144,
    processing_chain={'hp': 1144, 'ds': 6288},
    mic_spacing=0.08,
    mics_to_use = mic_positions,
    rows=4,
    cols=12,
    num_mics=48,
    num_taps = 301
)