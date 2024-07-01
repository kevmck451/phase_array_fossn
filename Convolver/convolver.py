from audio import Audio


basepath = '/Users/KevMcK/Dropbox/2 Work/1 Optics Lab/2 FOSSN/Data'
audio_filepath = f'{basepath}/Tests/initial_tests/6_mic_tests/twoantennas4.wav'

audio = Audio(filepath=audio_filepath, num_channels=16)

print(audio)

# audio.waveform(display=True)

# using 16 mics and beamforming to create a single audio channel of a focused area in space









