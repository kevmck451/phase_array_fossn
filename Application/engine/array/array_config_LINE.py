# Config file for Array: Line

from Application.engine.array.BeamMixConfig import BeamMixConfig

sample_rate = 48000

# for the actual array
rows = 1
cols = 16
num_mics = rows * cols
mic_spacing = 0.08  # meters - based on center freq


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
chunk_duration = 50 * 60  # 50 minutes in seconds

title = 'Line Array'

directory_name = 'Line'

Ltheta = -70
Rtheta = 70
increment = 5
default_theta_directions = list(range(Ltheta, Rtheta + 1, increment))

number_of_taps = 301

ip_address = '192.168.0.3'

server_port = 32492


beam_mix_1 = BeamMixConfig(
    name="Mix 1",
    center_frequency=2144,
    processing_chain={'hp': 1144, 'ds': 6288},
    mic_spacing=0.08,
    mics_to_use=[
        (0, 0),
        (0, 1),
        (0, 2),
        (0, 3),
        (0, 4),
        (0, 5),
        (0, 6),
        (0, 7),
        (0, 8),
        (0, 9),
        (0, 10),
        (0, 11),
        (0, 12),
        (0, 13),
        (0, 14),
        (0, 15)],
    rows=1,
    cols=16,
    num_mics=16,
    num_taps = number_of_taps
)

beam_mix_2 = BeamMixConfig(
    name="Mix 2",
    center_frequency=1072,
    processing_chain={'hp': 644, 'ds': 3142},
    mic_spacing=0.16,
    mics_to_use=[
        (0, 0),
        (0, 2),
        (0, 4),
        (0, 6),
        (0, 8),
        (0, 10),
        (0, 12),
        (0, 14)],
    rows=1,
    cols=8,
    num_mics=8,
    num_taps=number_of_taps
)

beam_mix_3 = BeamMixConfig(
    name="Mix 3",
    center_frequency=715,
    processing_chain={'hp': 465, 'ds': 1930},
    mic_spacing=0.24,
    mics_to_use=[
            (0, 0),
            (0, 3),
            (0, 6),
            (0, 9),
            (0, 12),
            (0, 15)],
    rows=1,
    cols=6,
    num_mics=6,
    num_taps=number_of_taps
)

beam_mix_4 = BeamMixConfig(
    name="Mix 4",
    center_frequency=429,
    processing_chain={'hp': 179, 'ds': 998},
    mic_spacing=0.4,
    mics_to_use=[
            (0, 0),
            (0, 4),
            (0, 8),
            (0, 12)],
    rows=1,
    cols=4,
    num_mics=4,
    num_taps=number_of_taps
)